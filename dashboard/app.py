import streamlit as st
import pandas as pd
import psycopg2
import time
import altair as alt

st.set_page_config(
    page_title="Project X AQI",
    page_icon="💨",
    layout="wide",
)

# Found this online, it makes the whole page reload every 15 seconds
# so the data stays fresh. It's a bit of a hack but it works.
st.components.v1.html("<meta http-equiv='refresh' content='15'>", height=0)


def connect_to_database():
    connection = psycopg2.connect(
        host="localhost",
        port="5433",
        dbname="project_x_db",
        user="user",
        password="password"
    )
    return connection

def get_data_from_db(db_connection, sql_query):
    # Using pandas to read the sql query is pretty easy.
    dataframe = pd.read_sql_query(sql_query, db_connection)
    return dataframe

st.title("💨 Live Air Quality Dashboard")
st.markdown("A dashboard to show the live air quality data from my Kafka and Spark pipeline.")

try:
    db_conn = connect_to_database()
    
    all_historical_data = get_data_from_db(db_conn, "SELECT * FROM live_air_quality_trends ORDER BY processing_timestamp;")
    
    # I'll sort all the data by time and then drop the older duplicates for each city.
    latest_data_per_city = all_historical_data.sort_values("processing_timestamp").drop_duplicates(subset=['city'], keep='last')

    st.header("Current AQI in Major Cities")
    
    if not latest_data_per_city.empty:
        columns = st.columns(len(latest_data_per_city))
        
        latest_data_per_city = latest_data_per_city.sort_values(by="city").reset_index(drop=True)

        for i, data_row in latest_data_per_city.iterrows():
            with columns[i]:
                if data_row['health_status'] == 'Good':
                    box_color = 'green'
                elif data_row['health_status'] == 'Meh': 
                    box_color = 'orange'
                else:
                    box_color = 'red'

                st.markdown(
                    f"""
                    <div style="background-color: #262730; border-radius: 10px; padding: 20px; text-align: center; border: 2px solid {box_color};">
                        <h3 style="color: white;">{data_row['city'].split(',')[1].strip()}</h3>
                        <h1 style="color: {box_color};">{int(data_row['average_aqi'])}</h1>
                        <p style="color: white;">AQI ({data_row['health_status']})</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.header("AQI Trend Over Time")
    
    if not all_historical_data.empty:
        list_of_cities = all_historical_data['city'].unique()
        
        # Make a dropdown menu so the user can pick a city
        city_to_show = st.selectbox('Select a city to see its past record', list_of_cities)
        
        # If the user has picked a city maybe?
        if city_to_show:
            city_specific_data = all_historical_data[all_historical_data['city'] == city_to_show]
            
            trend_chart = alt.Chart(city_specific_data).mark_line(
                point=True, 
                color='cyan'
            ).encode(
                x=alt.X('processing_timestamp:T', title='Time'),
                y=alt.Y('average_aqi:Q', title='Average AQI', scale=alt.Scale(zero=False)),
                tooltip=['processing_timestamp', 'average_aqi', 'health_status']
            ).properties(
                title=f'AQI Trend for {city_to_show.split(",")[1].strip()}'
            ).interactive()

            st.altair_chart(trend_chart, use_container_width=True)

    # full table
    st.header("Complete Historical Data Log")
    st.dataframe(all_historical_data, use_container_width=True)
    
    st.info("This page automatically refreshes every 15 seconds.")

except Exception as e:
    st.error(f"Something went wrong: {e}")

