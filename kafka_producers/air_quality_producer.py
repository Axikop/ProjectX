import os
import time
import json
import requests
from confluent_kafka import Producer
import socket

# IMPORTANT: I should probably hide this later i forgor
MY_API_KEY = '1ba853092dca2ec126962b7024890d3832213404' 

CITIES_TO_CHECK = ['delhi', 'mumbai', 'bangalore', 'jaipur']

KAFKA_SERVER_ADDRESS = 'localhost:29092'
KAFKA_TOPIC_NAME = 'air_quality_data'

# This function gets the data for one city from the API
def get_data_for_one_city(city, api_key):
    url = f"https://api.waqi.info/feed/{city}/?token={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        json_data = response.json()
        
        if json_data.get('status') == 'ok':
            return json_data['data']
        else:
            print(f"API had an error for {city}: {json_data.get('data')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Could not get data for {city}: {e}")
        return None

if __name__ == "__main__":
    
    kafka_settings = {
        'bootstrap.servers': KAFKA_SERVER_ADDRESS,
        'client.id': socket.gethostname()
    }

    kafka_producer = Producer(kafka_settings)
    print("Connected to Kafka!")

    try:
        while True:
            for city in CITIES_TO_CHECK:
                print(f"\nGetting data for {city.title()}...")
                
                air_quality_info = get_data_for_one_city(city, MY_API_KEY)

                if air_quality_info:
                    
                    message_to_send = {}
                    message_to_send['city'] = air_quality_info.get('city', {}).get('name')
                    message_to_send['aqi'] = air_quality_info.get('aqi')
                    message_to_send['dominant_pollutant'] = air_quality_info.get('dominentpol')
                    
                    iaqi_data = air_quality_info.get('iaqi', {})
                    message_to_send['pm25'] = iaqi_data.get('pm25', {}).get('v')
                    message_to_send['o3'] = iaqi_data.get('o3', {}).get('v')
                    message_to_send['no2'] = iaqi_data.get('no2', {}).get('v')
                    message_to_send['so2'] = iaqi_data.get('so2', {}).get('v')
                    
                    message_to_send['timestamp'] = air_quality_info.get('time', {}).get('s')

                    json_message = json.dumps(message_to_send)
                    
                    kafka_producer.produce(
                        topic=KAFKA_TOPIC_NAME,
                        value=json_message.encode('utf-8')
                    )
                    
                    kafka_producer.poll(0)
                    
                    print(f"Sent: {message_to_send['city']} - AQI: {message_to_send['aqi']}")

                time.sleep(2)

            print("\nFinished a cycle. Waiting 10 seconds...")
            time.sleep(10)

    except KeyboardInterrupt:
        print("Stopping the producer...")
    finally:
        kafka_producer.flush()
        print("Kafka connection closed.")
