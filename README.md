A non trivial ds project.

Project X: Real-Time Air Quality Data Pipeline
This project is a complete, end-to-end data engineering pipeline that ingests, processes, and stores live air quality data from major Indian cities. The system is built using industry-standard tools including Kafka, Apache Spark, and PostgreSQL, demonstrating a full data lifecycle from raw, real-time events to structured, actionable insights.

The final output is stored in a PostgreSQL database, making it ready for analysis or visualization with tools like the included Streamlit dashboard.


Architecture
The pipeline follows a modern, decoupled architecture:

Live API -> Kafka Producer (Python) -> Kafka Topic -> Spark Streaming (PySpark) -> PostgreSQL Database


Technologies Used
Data Ingestion: Python (using requests, confluent-kafka)
Data Transport: Apache Kafka & Zookeeper
Data Processing: Apache Spark (PySpark)
Data Storage: PostgreSQL
Orchestration: Docker 
Dashboard: Streamlit