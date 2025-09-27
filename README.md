# Appointment Service - DevOps Setup

This document provides a comprehensive guide to the DevOps setup for the Appointment Service, including local development, containerization, and Kubernetes deployment.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [Docker Setup](#docker-setup)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Troubleshooting](#troubleshooting)
9. [Useful Commands](#useful-commands)

## Project Overview
The Appointment Service is a FastAPI-based microservice that handles appointment scheduling and management. It uses PostgreSQL as its database and is containerized using Docker.

## Prerequisites
- Docker Desktop
- Minikube
- kubectl
- Python 3.10+
- Git

## Local Development Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd appointment-service
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file with the following variables:
```env
DATABASE_URL=postgresql://postgres:anil@localhost:5432/appointment_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Docker Setup

### Build the Docker image
```bash
docker build -t appointment-service:latest .
```

### Run the container
```bash
docker run -p 8007:8007 --env-file .env appointment-service:latest
```

## Kubernetes Deployment

### 1. Start Minikube
```bash
minikube start --cpus=4 --memory=8192mb --disk-size=20g
```

### 2. Enable required addons
```bash
minikube addons enable ingress
minikube addons enable metrics-server
```

### 3. Build image in Minikube's Docker daemon
```bash
minikube image build -t appointment-service:latest .
```

### 4. Deploy to Kubernetes
```bash
cd k8s/staging
kubectl apply -k .
```

### 5. Verify deployment
```bash
kubectl get all -n appointment-staging
```

## CI/CD Pipeline

The project includes a Jenkins pipeline for continuous integration and deployment. The pipeline includes:

1. Code checkout
2. Unit testing
3. Docker image build
4. Image push to container registry
5. Kubernetes deployment
6. Integration testing

## Monitoring and Logging

### View logs
```bash
# View application logs
kubectl logs -l app=appointment-service -n appointment-staging

# View PostgreSQL logs
kubectl logs -l app=postgres -n appointment-staging
```

### Monitor resources
```bash
# Get resource usage
kubectl top pods -n appointment-staging

# Get cluster events
kubectl get events -n appointment-staging
```

## Troubleshooting

### Common Issues

1. **Image Pull Errors**
   - Ensure you've built the image in Minikube's Docker daemon
   - Verify the image name and tag in your deployment files

2. **Database Connection Issues**
   - Check if PostgreSQL is running
   - Verify the connection string in secrets

3. **Port Forwarding**
   - If you can't access the service, check if the service is exposed correctly

## Useful Commands

### Minikube
```bash
# Start Minikube
minikube start

# Access the Kubernetes dashboard
minikube dashboard

# Get Minikube IP
minikube ip
```

### Kubernetes
```bash
# Get all resources in namespace
kubectl get all -n appointment-staging

# Describe a resource
kubectl describe <resource-type> <resource-name> -n appointment-staging

# Delete all resources in namespace
kubectl delete all --all -n appointment-staging

# Port forward a service
kubectl port-forward svc/appointment-service 8000:8000 -n appointment-staging
```

### Docker
```bash
# List all containers
docker ps -a

# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune -a
```

## License
[Your License Here]

# Appointment Management Microservice

## Overview 
Enterprise-grade microservice for managing medical appointments in a healthcare system, built with FastAPI and following clean architecture principles.

## Features
- Schedule, update, and cancel appointments
- Check doctor availability with smart time slot management
- Manage appointment statuses (Scheduled, Completed, Cancelled)
- Comprehensive API documentation with Swagger UI
- Containerized with Docker
- CI/CD pipeline with Jenkins
- Unit and integration tests

## Tech Stack
- Python 3.10+
- FastAPI
- SQLAlchemy + SQLModel
- PostgreSQL
- Docker + Docker Compose
- Jenkins
- Pytest
- Alembic (Database migrations)

## Getting Started

### Prerequisites
- Docker and Docker Compose (recommended)
  or
- Python 3.10+ and PostgreSQL

### With Docker (Recommended)

1. Clone the repository
2. Run the application:
   ```bash
   docker-compose up --build
   ```
3. Access the API at `http://localhost:8007`
4. Access API documentation at `http://localhost:8007/docs`
5. Access pgAdmin at `http://localhost:5050` (email: admin@example.com, password: admin)

### Without Docker

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env` file (copy from `.env.example`)
4. Run migrations:
   ```bash
   alembic upgrade head
   ```
5. Start the server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8007
   ```