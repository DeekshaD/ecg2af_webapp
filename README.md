# ECG2AF Web Application Technical Documentation

## Requirements

- Git with LFS (Large File Storage) support
- Docker
- Internet connection to pull Docker images and dependencies
- Linux based Operating system

## Setup and Running Instructions

### 1. Install Git LFS (if not already installed)

```bash
# For Ubuntu/Debian
sudo apt-get install git-lfs
```

After installation, initialize Git LFS:
```bash
git lfs install
```


### 2. Clone the Application Repository
```bash
git clone https://github.com/DeekshaD/ecg2af_webapp.git
cd ecg2af_webapp
```


### 3. Set up ML4H Repository for Required Libraries
```bash
git clone https://github.com/broadinstitute/ml4h.git
git lfs pull --include model_zoo/ECG2AF/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5
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

## Data Processing Assumptions 

   - ECG data is properly formatted in HD5 files
   - ECG signals contain all 12 leads as specified
   - Data is normalized using mean centering and standard scaling

## Scaling Solution

For scaling the ECG2AF web application to handle 10,000 ECGs and multiple users, there are two practical approaches using AWS services.

The first approach leverages AWS EC2 instances with AWS Elastic Load Balancing. In this setup, multiple EC2 instances would host the Streamlit application, with an Application Load Balancer distributing incoming traffic across these instances. The EC2 instances can be part of an Auto Scaling group that automatically adjusts the number of instances based on demand. This solution provides fine-grained control over the infrastructure and allows for custom configuration of each instance, though it requires more manual management of the underlying infrastructure.

The second approach utilizes AWS Fargate with Amazon Elastic Container Service (ECS). This serverless solution involves uploading our Docker container to Amazon ECR (Elastic Container Registry) and letting Fargate handle the underlying infrastructure. Fargate automatically manages the provisioning and scaling of the virtual machines, networking, and other resources needed to run our containerized application.In this solution AWS manages the infrastructure, the trade-off is less direct control over the underlying infrastructure, but this is often outweighed by the reduced maintenance burden and improved deployment simplicity.

## AI tools

In developing the ECG2AF web application, I leveraged Claude, an AI assistant by Anthropic, to enhance development efficiency. Claude helped generate the initial structure of the Streamlit application and assisted with error handling patterns. I validate all AI-generated code, particularly ensuring proper integration with the ML4H libraries and correct handling of the ECG data tensors. 
