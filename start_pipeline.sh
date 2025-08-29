#!/bin/bash
# start_pipeline.sh

echo "🚀 Starting Instagram ML Pipeline..."

# Create necessary directories
mkdir -p airflow/{dags,plugins,config}
mkdir -p data/{raw,processed,models,checkpoints}

# Copy DAG to Airflow directory
cp airflow/dags/ml_pipeline_dag.py airflow/dags/ 2>/dev/null || echo "DAG file already in place"

# Start Kafka infrastructure (if not running)
echo "📡 Starting Kafka infrastructure..."
docker-compose up -d zookeeper kafka redis kafka-ui

# Wait for Kafka to be ready
echo "⏳ Waiting for Kafka to be ready..."
sleep 15

# Create Kafka topic if it doesn't exist
echo "📝 Creating Kafka topic..."
docker exec kafka kafka-topics --create --topic social_media_posts --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists

# Start Airflow
echo "🌪️ Starting Airflow..."
docker-compose -f docker-compose-airflow.yml up -d

echo "⏳ Waiting for Airflow to initialize..."
sleep 30

echo "✅ Pipeline infrastructure started!"
echo ""
echo "🌐 Access points:"
echo "  - Airflow Web UI: http://localhost:8082 (admin/admin)"
echo "  - Kafka UI: http://localhost:8081"
echo ""
echo "📋 Next steps:"
echo "  1. Visit Airflow Web UI"
echo "  2. Enable the 'instagram_ml_pipeline' DAG"
echo "  3. Trigger a manual run to test"
echo ""
echo "🔄 The pipeline will automatically run daily"
echo "📊 Check data/models/ for outputs"