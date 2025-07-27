# 🚀 Project X: Live Air Quality Data Pipeline with Kafka and Spark

This project is a complete, end-to-end data engineering pipeline that demonstrates a real-world data processing architecture. It captures live air quality data from major Indian cities, processes it in real-time using Apache Spark, and stores the historical trends in a PostgreSQL database. The final, cleaned data is presented in an interactive Streamlit dashboard.

---

## 📊 Project in Action

### Live Streamlit Dashboard
The final output is a clean, auto-refreshing dashboard that displays the latest air quality metrics and visualizes historical trends for each city.

![Streamlit Dashboard](https://github.com/Axikop/ProjectX/blob/main/demo1.png?raw=true)
![Streamlit Dashboard](https://github.com/Axikop/ProjectX/blob/main/demo2.png?raw=true)

### Spark Streaming UI
The Spark UI shows the live processing of data batches as they arrive from the Kafka stream.

![SPARK UI](https://github.com/Axikop/ProjectX/blob/main/sparkui.png?raw=true)

---

## 🏗️ Architecture

The pipeline follows a modern, decoupled, and scalable architecture:

`Live API -> Kafka Producer -> Kafka Topic -> Spark Streaming (PySpark) -> PostgreSQL Database -> Streamlit Dashboard`

1.  A **Python Producer** continuously fetches data from the World Air Quality Index API for multiple cities.
2.  This data is sent as JSON messages to an **Apache Kafka** topic, which acts as a durable, real-time message bus.
3.  An **Apache Spark** streaming job, running locally, connects to the Kafka topic, consumes the data in micro-batches, and performs real-time transformations and aggregations (calculating average AQI, determining health status).
4.  The processed, insightful data is then appended to a **PostgreSQL** database, creating a historical log of air quality trends.
5.  A **Streamlit** web application queries the PostgreSQL database and presents the data in an interactive, user-friendly dashboard that auto-refreshes.
6.  The entire backend infrastructure (Kafka, Zookeeper, PostgreSQL) is containerized and managed with **Docker and Docker Compose** for easy setup and portability.

---

## ✨ Key Features
* **End-to-End Data Flow:** Demonstrates the full data lifecycle, from raw API data to a polished user dashboard.
* **Real-Time Processing:** Utilizes Spark Structured Streaming to process data with low latency.
* **Historical Trend Analysis:** Persists data in a database, enabling time-series analysis and visualization.
* **Scalable & Decoupled:** Each component (ingestion, processing, storage, presentation) is independent, making the system robust and easy to maintain.

---

## 🛠️ Technologies Used

* **Data Ingestion:** Python (`requests`, `confluent-kafka`)
* **Data Transport / Streaming:** Apache Kafka & Zookeeper
* **Data Processing:** Apache Spark (PySpark)
* **Data Storage:** PostgreSQL
* **Dashboarding:** Streamlit, Pandas, Altair
* **Infrastructure:** Docker & Docker Compose

---

## 🚀 How to Run This Project

### Prerequisites
* Docker and Docker Compose must be installed.
* You need a free API key from the [World Air Quality Index Project](https://aqicn.org/data-platform/token/).

### Step 1: Clone and Configure
1.  Clone this repository to your local machine.
2.  Open the `kafka_producers/air_quality_producer.py` script.
3.  Inside the script, replace the placeholder API key with your actual key.

### Step 2: Launch the Backend Infrastructure
From the project's root directory, start the Kafka and PostgreSQL containers.
```bash
docker-compose up -d

Important: Wait for about 45-60 seconds after running this command to allow the services to fully initialize.

Step 3: Start the Data Producer
This script will fetch data from the API and send it to Kafka.

Open a new terminal.

Install the required Python libraries:

pip install -r kafka_producers/requirements.txt

Run the producer script:

python kafka_producers/air_quality_producer.py

Step 4: Start the Spark Processing Job
This script will read from Kafka, process the data, and save it to PostgreSQL.

Open a third terminal.

Install the required Python libraries:

pip install pyspark==3.4.1

Run the Spark Streaming script:

python spark/app/stream_air_quality_processor.py

Step 5: Launch the Streamlit Dashboard
This is the final step to view the results.

Open a fourth terminal.

Install the required Python libraries:

pip install -r dashboard/requirements.txt

Run the Streamlit app:

streamlit run dashboard/app.py
