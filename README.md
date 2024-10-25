# ECG2AF Web Application Technical Documentation

## Requirements

- Git with LFS (Large File Storage) support
- Docker
- Internet connection to pull Docker images and dependencies

## Setup and Running Instructions

### 1. Install Git LFS (if not already installed)

```bash
# For Ubuntu/Debian
sudo apt-get install git-lfs

# For macOS using Homebrew
brew install git-lfs

# For Windows using Chocolatey
choco install git-lfs
```

After installation, initialize Git LFS:
```bash
git lfs install
```

### 2. Set up ML4H Repository for Required Libraries
```bash
git clone https://github.com/broadinstitute/ml4h.git
git lfs pull --include model_zoo/ECG2AF/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5
```

### 3. Clone the Application Repository
```bash
git clone https://github.com/DeekshaD/ecg2af_webapp.git
cd ecg2af_webapp
```

### 4. Pull the Base Docker Image
```bash
docker pull ghcr.io/broadinstitute/ml4h:tf2.9-latest-cpu
```

### 5. Build and Run the Application
```bash
# Build the Docker image
docker build -t ecg2af-webapp .

# Run the container
docker run -p 8501:8501 ecg2af-webapp
```

The application will be accessible at `http://localhost:8501`

## User Interface Components

The web application provides a clean, intuitive interface with the following elements:

1. **Title Header**: "ECG2AF Model Web Application"

2. **File Upload Section**: 
   - File uploader component accepting .h5/.hd5 format files
   - Clear instructions for file format requirements

3. **Prediction Results Display**:
   - AF Risk Score (numerical value between 0-1)
   - Sex Prediction (probability for Male/Female - assumed 1st probability returned is for class 0 - Male)
   - Age Prediction
   - AF Classification (probability of AF presence/absence - assumed 1st probability returned is for class 0 - no AF)

4. **Visualization Section**:
   - Interactive survival curve plot showing AF probability over time
   - Check box option to view raw survival data in tabular format

## Assumptions and Design Decisions

1. **Data Processing**:
   - ECG data is properly formatted in HD5 files
   - ECG signals contain all 12 leads as specified
   - Data is normalized using mean centering and standard scaling

2. **Result Display**:
   - Age predictions are kept in normalized form
   - Survival curve focuses on the most relevant probability range (0.7-1.0)
   - Raw probabilities are displayed to 4 decimal places for precision

## Framework Choice: Streamlit

Streamlit was chosen as the web framework for several reasons:

1. **Rapid Development**:
   - Built-in components for file uploading and data visualization
   - Simple Python-first approach requiring minimal frontend code
   - Quick prototyping capabilities

2. **ML/Data Science Integration**:
   - Native support for data science libraries (Pandas, NumPy)
   - Seamless integration with Plotly for interactive visualizations
   - Built-in caching mechanisms for model loading

3. **User Experience**:
   - Automatic responsive design
   - Real-time updates without page refreshes
   - Clean, modern UI out of the box

4. **Deployment Simplicity**:
   - Single command deployment
   - Built-in development server
   - Docker-friendly architecture

## Scaling Solution for 10,000 ECGs

To scale the application for processing 10,000 ECGs, here's a detailed technical architecture:

### 1. Infrastructure Components

1. **Load Balancer**:
   - Use AWS ELastic load balancing
   - Implement health checks and automatic scaling policies
   - Configure SSL/TLS termination

2. **Web Server Layer**:
   - Deploy multiple Streamlit instances behind the load balancer
   - Use Kubernetes for container orchestration
   - Implement auto-scaling based on CPU/memory metrics

3. **Queue System**:
   - Implement Apache Kafka or RabbitMQ for message queuing
   - Configure separate queues for different processing stages
   - Implement dead letter queues for failed processing

4. **Processing Layer**:
   - Deploy worker nodes using Kubernetes StatefulSets
   - Implement batch processing for multiple ECGs
   - Use GPU instances for model inference (if needed)

### 2. Storage Solutions

1. **Object Storage**:
   - Store uploaded ECG files in S3 or Google Cloud Storage
   - Implement lifecycle policies for data retention
   - Use CDN for faster file delivery

2. **Results Database**:
   - Use MongoDB for storing prediction results
   - Implement sharding for horizontal scaling
   - Set up replica sets for high availability

### 3. Monitoring and Logging

1. **Metrics Collection**:
   - Use Prometheus for metrics collection
   - Set up Grafana dashboards for visualization
   - Monitor key performance indicators:
     - Processing time per ECG
     - Queue lengths
     - Error rates
     - Resource utilization

2. **Distributed Tracing**:
   - Implement OpenTelemetry for request tracing
   - Use Jaeger or Zipkin for visualization
   - Track processing pipeline stages

### 4. Error Handling

1. **Retry Mechanism**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def process_with_retry(ecg_file):
    try:
        return await process_single_ecg(ecg_file)
    except Exception as e:
        logger.error(f"Processing failed for {ecg_file}: {str(e)}")
        raise
```

2. **Circuit Breaker**:
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
async def protected_processing(ecg_file):
    return await process_with_retry(ecg_file)
```

This architecture ensures:
- High availability and fault tolerance
- Horizontal scalability
- Efficient resource utilization
- Robust error handling and monitoring
- Cost-effective processing of large ECG batches
