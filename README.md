# Instagram Analytics ML Pipeline

<div align="center">
  <h3>🚀 Automated Machine Learning Pipeline for Instagram Social Media Analysis</h3>
  <p>Real-time sentiment analysis and trend detection with automatic scaling and cost optimization</p>
  
  ![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
  ![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)
  ![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.x-red.svg)
  ![Kubernetes](https://img.shields.io/badge/Kubernetes-1.25+-326CE5.svg)
  ![License](https://img.shields.io/badge/License-MIT-green.svg)
</div>

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Dashboard](#dashboard)
- [API Documentation](#api-documentation)
- [Monitoring](#monitoring)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The **Instagram Analytics ML Pipeline** is a comprehensive, automated machine learning system designed to continuously process Instagram social media data for real-time sentiment analysis and trend detection. The pipeline features automatic scaling, cost optimization, and a beautiful real-time dashboard for monitoring insights.

### End Goal
Build an enterprise-grade ML pipeline that:
- ✅ Continuously processes Instagram data streams
- ✅ Performs real-time sentiment analysis on posts and comments
- ✅ Detects emerging trends and hashtag patterns
- ✅ Automatically scales based on data volume
- ✅ Provides cost-optimized infrastructure management
- ✅ Delivers insights through an interactive dashboard

## ✨ Features

### 🔄 Real-time Processing
- Continuous Instagram data ingestion
- Stream processing with sub-second latency
- Live sentiment analysis using BERT models
- Dynamic trend detection algorithms

### 📊 Analytics Dashboard
- **Real-time Engagement Metrics** - Live charts showing likes, comments, shares per minute
- **Sentiment Distribution** - Interactive doughnut chart with positive/neutral/negative breakdown
- **Live Activity Feed** - Scrolling activity score visualization
- **Trending Topics** - Dynamic hashtag trending with mention counts
- **System Performance** - CPU, memory, network, and pipeline health monitoring

### 🤖 Machine Learning
- Advanced sentiment analysis with TensorFlow/BERT
- Trend detection using time-series analysis
- Hashtag popularity prediction
- Anomaly detection for unusual activity patterns

### 🏗️ Infrastructure
- Kubernetes-based auto-scaling
- Docker containerization
- Horizontal pod autoscaling (HPA)
- Cost optimization through resource management

### 📈 Monitoring & Observability
- Real-time performance metrics
- Model version tracking
- Data quality monitoring
- Alert system for anomalies

## 🏛️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Instagram     │    │   Data Ingestion │    │   Stream        │
│   API           │───▶│   (Kafka/Redis)  │───▶│   Processing    │
│                 │    │                  │    │   (Spark)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                          │
┌─────────────────┐    ┌──────────────────┐              ▼
│   Dashboard     │    │   Data Storage   │    ┌─────────────────┐
│   (HTML/JS)     │◀───│ PostgreSQL/Mongo│◀───│   ML Pipeline   │
│                 │    │                  │    │  (TensorFlow)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
          │                       │                       │
          ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Monitoring    │    │   Orchestration  │    │   Kubernetes    │
│ Prometheus/     │    │   (Airflow)      │    │   Cluster       │
│ Grafana         │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🛠️ Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Orchestration** | Apache Airflow | Workflow scheduling and management |
| **Data Processing** | Apache Spark | Large-scale data processing and ETL |
| **ML Framework** | TensorFlow/Keras | Model training and inference |
| **Container Orchestration** | Kubernetes | Auto-scaling and deployment |
| **Containerization** | Docker | Application packaging |
| **Message Queue** | Redis/Apache Kafka | Real-time data streaming |
| **Database** | PostgreSQL/MongoDB | Structured and unstructured data storage |
| **Monitoring** | Prometheus/Grafana | Performance monitoring and alerting |
| **Frontend** | HTML/CSS/JavaScript | Real-time analytics dashboard |
| **API** | FastAPI/Flask | RESTful API services |

## 📋 Prerequisites

- **Python 3.9+**
- **Docker & Docker Compose**
- **Kubernetes cluster** (local or cloud)
- **Instagram API access** (Business/Developer account)
- **Git** for version control

### System Requirements
- **RAM**: 8GB minimum, 16GB recommended
- **CPU**: 4 cores minimum
- **Storage**: 50GB available space
- **Network**: Stable internet connection for API calls

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/instagram-analytics-ml-pipeline.git
cd instagram-analytics-ml-pipeline
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Docker Setup
```bash
# Build Docker images
docker-compose build

# Start services
docker-compose up -d
```

### 4. Kubernetes Deployment
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n instagram-analytics
```

## ⚙️ Configuration

### 1. Environment Variables
Create a `.env` file in the root directory:

```bash
# Instagram API Configuration
INSTAGRAM_ACCESS_TOKEN=your_access_token_here
INSTAGRAM_CLIENT_ID=your_client_id
INSTAGRAM_CLIENT_SECRET=your_client_secret

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=instagram_analytics
POSTGRES_USER=admin
POSTGRES_PASSWORD=your_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Model Configuration
MODEL_VERSION=v2.1
SENTIMENT_MODEL_PATH=/models/bert_sentiment
BATCH_SIZE=32
PROCESSING_INTERVAL=30

# Kubernetes Configuration
NAMESPACE=instagram-analytics
REPLICAS=3
AUTO_SCALING=true
```

### 2. Airflow Configuration
```python
# airflow/dags/config.py
AIRFLOW_CONFIG = {
    'schedule_interval': '@hourly',
    'max_active_runs': 1,
    'catchup': False,
    'email_on_failure': True,
    'email_on_retry': False,
}
```

## 🎮 Usage

### 1. Start the Pipeline
```bash
# Start all services
docker-compose up -d

# Check service health
curl http://localhost:8080/health
```

### 2. Access the Dashboard
Open your browser and navigate to: `http://localhost:3000`

### 3. Monitor Pipeline
```bash
# View logs
kubectl logs -f deployment/ml-pipeline -n instagram-analytics

# Check metrics
curl http://localhost:9090/metrics
```

### 4. API Usage
```python
import requests

# Get real-time metrics
response = requests.get('http://localhost:8000/api/metrics')
metrics = response.json()

# Get sentiment analysis
data = {"text": "I love this new Instagram feature!"}
response = requests.post('http://localhost:8000/api/analyze', json=data)
result = response.json()
```

## 📊 Dashboard

The real-time analytics dashboard provides comprehensive insights:

### Main Features
- **📈 Real-time Engagement Metrics**: Live line charts showing engagement trends
- **🎯 Sentiment Distribution**: Interactive doughnut chart with sentiment breakdown
- **⚡ Live Activity Feed**: Scrolling activity score with real-time updates
- **📱 Trending Topics**: Dynamic hashtag trends with mention counts
- **🖥️ System Performance**: Infrastructure health monitoring

### Navigation
- **Dashboard**: Main overview with real-time metrics
- **Analytics**: Advanced performance statistics
- **Reports**: Generated insights and trend reports  
- **Trends**: Detailed trend analysis and predictions
- **Settings**: Configuration and system preferences

### Key Metrics Displayed
```javascript
// Example metrics structure
{
  "total_posts": 15847,
  "sentiment_score": "68%",
  "engagement_rate": 42,
  "processing_rate": 18,
  "top_hashtags": [
    {"hashtag": "#instagram", "count": 1205},
    {"hashtag": "#photooftheday", "count": 987}
  ]
}
```

## 📚 API Documentation

### Endpoints

#### Health Check
```http
GET /health
```

#### Real-time Metrics
```http
GET /api/metrics
```

#### Sentiment Analysis
```http
POST /api/analyze
Content-Type: application/json

{
  "text": "Text to analyze",
  "language": "en"
}
```

#### Trending Topics
```http
GET /api/trends
```

#### Historical Data
```http
GET /api/historical?start_date=2024-01-01&end_date=2024-01-31
```

## 📈 Monitoring

### Metrics Collected
- **Processing Metrics**: Throughput, latency, error rates
- **Model Performance**: Accuracy, precision, recall, F1-score
- **Infrastructure**: CPU, memory, disk, network usage
- **Business Metrics**: Engagement rates, sentiment trends

### Alerting Rules
```yaml
# prometheus/alerts.yml
groups:
  - name: instagram-analytics
    rules:
      - alert: HighErrorRate
        expr: error_rate > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
```

## 🚀 Deployment

### Production Deployment
```bash
# Set production environment
export ENVIRONMENT=production

# Deploy to Kubernetes
helm install instagram-analytics ./helm/instagram-analytics \
  --namespace production \
  --values helm/values-prod.yaml
```

### Scaling Configuration
```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-pipeline-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-pipeline
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 📝 Project Structure

```
instagram-analytics-ml-pipeline/
├── 📁 airflow/              # Airflow DAGs and configuration
│   ├── dags/
│   └── config/
├── 📁 src/                  # Source code
│   ├── data_ingestion/
│   ├── preprocessing/
│   ├── models/
│   └── api/
├── 📁 dashboard/            # Real-time dashboard
│   ├── index.html
│   ├── styles/
│   └── scripts/
├── 📁 k8s/                  # Kubernetes manifests
│   ├── deployments/
│   ├── services/
│   └── configmaps/
├── 📁 docker/               # Docker configurations
├── 📁 monitoring/           # Prometheus & Grafana configs
├── 📁 tests/                # Unit and integration tests
├── 📁 docs/                 # Additional documentation
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write comprehensive tests
- Update documentation for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Instagram API** for providing access to social media data
- **TensorFlow** team for the excellent ML framework
- **Apache Foundation** for Spark and Airflow
- **Kubernetes** community for container orchestration
- **Chart.js** for beautiful dashboard visualizations

## 📞 Support

- 📧 **Email**: support@instagram-analytics.com
- 💬 **Discord**: [Join our community](https://discord.gg/instagram-analytics)
- 📖 **Documentation**: [Full docs](https://docs.instagram-analytics.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/instagram-analytics-ml-pipeline/issues)

---

<div align="center">
  <p>⭐ Star this repo if you found it helpful!</p>
</div>