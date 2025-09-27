# Appointment Management Service

A FastAPI-based microservice for managing appointments in an enterprise healthcare system. This service provides RESTful APIs for scheduling, rescheduling, and canceling appointments, as well as querying appointment details.

## ✨ Features

- **RESTful API**: Fully documented with OpenAPI (Swagger) and ReDoc
- **Asynchronous Processing**: Built with FastAPI for high performance
- **Database**: PostgreSQL with SQLModel for ORM
- **Containerized**: Ready for Docker deployment
- **Testing**: Comprehensive test suite including unit and integration tests
- **CI/CD**: Jenkins pipeline for automated testing and deployment
- **Monitoring**: Health check endpoints and logging

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+ (for local development without Docker)
- Git
- Jenkins (for CI/CD pipeline)

## 🛠️ Local Development

### Option 1: With Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/appointment-service.git
   cd appointment-service
   ```

2. **Set up environment variables**
   Create a `.env` file:
   ```env
   # Database
   DATABASE_URL=postgresql://postgres:anil@db:5432/appointment_db
   
   # Security
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Application
   DEBUG=True
   ENVIRONMENT=development
   ```

3. **Start the application with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - API: http://localhost:8007
   - API Documentation: http://localhost:8007/docs
   - pgAdmin: http://localhost:5050 (email: admin@example.com, password: admin)
   - PostgreSQL: localhost:5433 (username: postgres, password: anil)

### Option 2: Without Docker

1. **Set up Python environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL**
   - Install PostgreSQL 13+
   - Create a database named `appointment_db`
   - Update the `DATABASE_URL` in `.env` to point to your local PostgreSQL instance

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the development server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8007
   ```

## 🚀 CI/CD with Jenkins

The project includes a Jenkins pipeline for automated testing and deployment:

### Pipeline Stages
1. **Checkout**: Fetches the latest code
2. **Setup**: Installs Python and dependencies
3. **Lint**: Runs flake8 for code quality
4. **Unit Tests**: Runs unit tests with coverage
5. **Integration Tests**: Runs integration tests with test database
6. **Docker Build**: Builds the Docker image
7. **Deploy**: Deploys to the target environment

### Jenkinsfile Configuration
```groovy
pipeline {
    agent {
        docker {
            image 'python:3.10-slim'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }
    
    environment {
        PYTHONUNBUFFERED = '1'
        TEST_DATABASE_URL = 'postgresql://postgres:anil@postgres:5432/appointment_test_db'
    }
    
    stages {
        // Pipeline stages as defined in Jenkinsfile
    }
}
```

### Required Jenkins Plugins
- Docker Pipeline
- Git
- Pipeline
- Blue Ocean (optional, for better visualization)

## 📊 Monitoring and Logging

### View Logs with Docker
```bash
# View application logs
docker-compose logs app

# View database logs
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f app
```

### Health Check
```bash
# Check application health
curl http://localhost:8007/health
```

## 🛠️ Troubleshooting

### Common Issues

1. **Docker Compose Errors**
   - Ensure Docker Desktop is running
   - Check if required ports (8007, 5433, 5050) are available
   - Run `docker-compose down` and then `docker-compose up --build` to rebuild containers

2. **Database Connection Issues**
   - Verify PostgreSQL is running: `docker-compose ps`
   - Check database logs: `docker-compose logs db`
   - Ensure the `DATABASE_URL` in `.env` matches the service name in docker-compose.yml

3. **Application Not Starting**
   - Check logs: `docker-compose logs app`
   - Verify all environment variables are set in `.env`
   - Ensure no other service is using the same ports

## 🔧 Useful Commands

### Docker Compose
```bash
# Start services in detached mode
docker-compose up -d

# Stop all services
docker-compose down

# Rebuild and restart a specific service
docker-compose up -d --build <service_name>

# View running containers
docker-compose ps

# Execute a command in a running container
docker-compose exec app <command>
```

### Database Management
```bash
# Access PostgreSQL shell
docker-compose exec db psql -U postgres

# Run database migrations
docker-compose exec app alembic upgrade head

# Create a new migration
docker-compose exec app alembic revision --autogenerate -m "description of changes"
```

### Development
```bash
# Run tests
docker-compose exec app pytest tests/

# Run tests with coverage
docker-compose exec app pytest --cov=app tests/

# Format code with black
docker-compose exec app black .

# Check code style with flake8
docker-compose exec app flake8 .
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the awesome web framework
- [SQLModel](https://sqlmodel.tiangolo.com/) for the ORM layer
- [Docker](https://www.docker.com/) for containerization
- [Jenkins](https://www.jenkins.io/) for CI/CD automation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Changelog

- **1.0.0**
  - Initial release of the Appointment Service
  - Basic CRUD operations for appointments
  - Docker and Docker Compose support
  - Jenkins CI/CD pipeline
  - Unit and integration tests