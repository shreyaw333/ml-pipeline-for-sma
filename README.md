ML Pipeline for Social Media Analysis
Overview
This project provides an end-to-end ML pipeline for continuous social media analysis. The pipeline automates the ingestion, processing, and analysis of social media data to:
Perform sentiment analysis


Detect emerging trends


Provide real-time monitoring & visualization


Scale automatically to optimize cost & performance


It integrates big data processing, machine learning, container orchestration, and monitoring tools into one cohesive system.

Architecture

(Replace with generated diagram — currently a placeholder)
Workflow:
Data Ingestion


Social media API connectors (e.g., Reddit, Instagram, Twitter/X)


Streaming via Kafka / Redis


Stored in PostgreSQL / MongoDB


Data Processing


Batch + streaming ETL


Apache Spark for large-scale transformations & feature engineering


Model Training & Inference


TensorFlow models for:


Sentiment Analysis (positive, negative, neutral)


Trend Detection (hashtags & topics)


Supports versioning and continuous retraining


Pipeline Orchestration


Apache Airflow DAGs to schedule, trigger, and monitor workflows


Task parallelization via Celery


Deployment & Scaling


Docker containers for reproducibility


Kubernetes for orchestration + auto-scaling


Monitoring & Visualization


Prometheus & Grafana for system metrics


Flask Dashboard for live pipeline insights


Integration with BI tools (Tableau, Power BI, Looker Studio)



Technologies
Workflow Orchestration: Apache Airflow


Data Streaming: Kafka, Redis


Data Processing: Apache Spark


Machine Learning: TensorFlow


Storage: PostgreSQL, MongoDB


Containerization: Docker


Orchestration: Kubernetes (with autoscaling)


Monitoring: Prometheus, Grafana


Dashboard: Flask + HTML frontend



Getting Started
Prerequisites
Python 3.9+


Docker & Docker Compose


Kubernetes (minikube or cloud-managed)


Social media API credentials (e.g., Reddit, Instagram, Twitter/X)


Setup
# Clone repository
git clone https://github.com/shreyaw333/ml-pipeline-for-sma.git
cd ml-pipeline-for-sma

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

Running Locally
# Start Airflow + services
docker-compose up -d

# Run the ML pipeline
bash start_pipeline.sh

# Launch Flask dashboard
cd dashboard/backend
python app.py

Dashboard runs at: http://localhost:5002

Example Metrics
Total posts processed


Average engagement rate


Sentiment distribution (positive / negative / neutral)


Top trending hashtags


Processing throughput







