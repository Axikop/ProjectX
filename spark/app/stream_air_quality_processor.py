
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

def get_health_status(aqi_value):
    if aqi_value <= 50:
        return "Good"
    elif aqi_value > 50 and aqi_value <= 100:
        return "Meh"
    elif aqi_value > 100 and aqi_value <= 150:
        return "god save the king"
    else:
        return "Cooked💀"

def process_each_batch(data_frame, batch_id):
    """
   this func() takes some small data does some calculation and writes to our db
    """
    if data_frame.count() == 0:
        return

    print(f"--- Starting processing for batch number: {batch_id} ---")

    
    # ez SQL query
    grouped_by_city = data_frame.groupBy("city")

    city_averages = grouped_by_city.agg(
        avg("aqi").alias("average_aqi"),
        avg("pm25").alias("average_pm25")
    )

    # I need to tell Spark how to use my python function.
    health_status_udf = udf(get_health_status, StringType())

    city_with_status = city_averages.withColumn("health_status", health_status_udf(col("average_aqi")))

    # Need to add a timestamp so we know when we processed this batch.
    final_data_batch = city_with_status.withColumn("processing_timestamp", current_timestamp())

    print("Here's the data I calculated for this batch:")
    final_data_batch.show(truncate=False)

    final_data_batch.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://localhost:5433/project_x_db") \
        .option("dbtable", "live_air_quality_trends") \
        .option("user", "user") \
        .option("password", "password") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()
    
    print(f"--- Finished saving batch {batch_id} to the database! ---")

#driver code
if __name__ == "__main__":
    
    #locally running spark engine with older ver of java11
    spark_session = SparkSession.builder \
        .appName("AirQualityETL") \
        .master("local[*]") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,org.postgresql:postgresql:42.6.0") \
        .getOrCreate()

    spark_session.sparkContext.setLogLevel("WARN")
    print("Spark Session is created. Trying to read from Kafka...")

    # custom data structure from kafka
    json_schema = StructType([
        StructField("city", StringType()),
        StructField("aqi", IntegerType()),
        StructField("pm25", DoubleType()),
        StructField("timestamp", StringType())
    ])

    #1. read OP
    kafka_reader = spark_session.readStream
    kafka_reader_with_format = kafka_reader.format("kafka")

    #2. address 
    kafka_reader_with_server = kafka_reader_with_format.option("kafka.bootstrap.servers", "localhost:29092")

    #3.topic name
    kafka_reader_with_topic = kafka_reader_with_server.option("subscribe", "air_quality_data")

    kafka_stream_df = kafka_reader_with_topic.load()

    # The data from Kafka is in a column called "value". I need to convert it from binary to a string.
    json_strings_df = kafka_stream_df.selectExpr("CAST(value AS STRING) as json_string")
    
    # parsing the JSON string using the schema defined before
    structured_data_df = json_strings_df.select(from_json(col("json_string"), json_schema).alias("data")).select("data.*")
    
    # For each batch of data that comes in, it will call my "process_each_batch" function.
    # 30 seconds.
    streaming_query = structured_data_df.writeStream \
        .foreachBatch(process_each_batch) \
        .trigger(processingTime='30 seconds') \
        .start()

    print("Streaming query has started! It will now process data every 30 seconds...")
    
    streaming_query.awaitTermination()
