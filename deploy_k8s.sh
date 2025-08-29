#!/bin/bash
# deploy_k8s.sh

echo "🚀 Deploying Instagram ML Pipeline to Kubernetes..."

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Enable Kubernetes in Docker Desktop (if using Docker Desktop)
echo "📋 Make sure Kubernetes is enabled in Docker Desktop"

# Build Docker images
echo "🏗️ Building Docker images..."

# Data Ingestion
echo "Building data-ingestion image..."
docker build -f Dockerfile.data-ingestion -t instagram-ml/data-ingestion:latest .

# Data Processing  
echo "Building data-processing image..."
docker build -f Dockerfile.data-processing -t instagram-ml/data-processing:latest .

# Models
echo "Building models image..."
docker build -f Dockerfile.models -t instagram-ml/models:latest .

echo "✅ Docker images built successfully"

# Apply Kubernetes manifests
echo "🎯 Deploying to Kubernetes..."

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy Kafka infrastructure
echo "📡 Deploying Kafka..."
kubectl apply -f k8s/kafka-deployment.yaml

# Wait for Kafka to be ready
echo "⏳ Waiting for Kafka to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/kafka -n instagram-ml-pipeline

# Deploy ML pipeline components
echo "🧠 Deploying ML Pipeline..."
kubectl apply -f k8s/ml-pipeline-deployment.yaml

# Deploy auto-scaling
echo "📊 Setting up auto-scaling..."
kubectl apply -f k8s/autoscaling.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=180s deployment/data-ingestion -n instagram-ml-pipeline
kubectl wait --for=condition=available --timeout=180s deployment/data-processing -n instagram-ml-pipeline
kubectl wait --for=condition=available --timeout=180s deployment/model-training -n instagram-ml-pipeline

echo "✅ Deployment completed!"

# Show status
echo "📋 Deployment Status:"
kubectl get pods -n instagram-ml-pipeline
echo ""
kubectl get services -n instagram-ml-pipeline
echo ""
kubectl get hpa -n instagram-ml-pipeline

echo ""
echo "🎉 Instagram ML Pipeline deployed successfully!"
echo ""
echo "📊 Monitoring commands:"
echo "  kubectl get pods -n instagram-ml-pipeline -w"
echo "  kubectl logs -f deployment/data-ingestion -n instagram-ml-pipeline"
echo "  kubectl logs -f deployment/data-processing -n instagram-ml-pipeline"
echo "  kubectl logs -f deployment/model-training -n instagram-ml-pipeline"
echo ""
echo "📈 Auto-scaling status:"
echo "  kubectl get hpa -n instagram-ml-pipeline -w"
echo ""
echo "🗑️ To cleanup:"
echo "  kubectl delete namespace instagram-ml-pipeline"