# Appointment Management Service

A FastAPI-based microservice for managing medical appointments in a healthcare system. This service provides RESTful APIs for scheduling, rescheduling, and canceling appointments, as well as querying appointment details.

## ✨ Features

- **RESTful API**: Fully documented with OpenAPI (Swagger) and ReDoc
- **Appointment Management**: Schedule, update, and cancel appointments
- **Doctor Availability**: Check available time slots for doctors
- **Patient Management**: Manage patient appointment history
- **Search & Filter**: Find appointments by various criteria
- **Validation**: Comprehensive input validation and error handling

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 13 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/appointment-service.git
   cd appointment-service
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL**
   - Install PostgreSQL if not already installed
   - Create a new database named `appointment_db`
   - Create a `.env` file in the project root with the following content:
     ```env
     # Database Configuration
     DATABASE_URL=postgresql://postgres:your_password@localhost:5432/appointment_db
     
     # Security
     SECRET_KEY=your-secret-key-here
     ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     
     # Application
     DEBUG=True
     ENVIRONMENT=development
     ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8007
   ```

7. **Access the API**
   - API Documentation (Swagger UI): http://localhost:8007/docs
   - Alternative Documentation (ReDoc): http://localhost:8007/redoc
   - Health Check: http://localhost:8007/health

## 🛠️ API Endpoints

### Appointments
- `GET /appointments` - List all appointments
- `GET /appointments/{appointment_id}` - Get appointment details
- `POST /appointments` - Create a new appointment
- `PUT /appointments/{appointment_id}` - Update an appointment
- `DELETE /appointments/{appointment_id}` - Cancel an appointment
- `GET /appointments/doctor/{doctor_id}` - Get appointments by doctor
- `GET /appointments/patient/{patient_id}` - Get appointments by patient
- `GET /appointments/available-slots` - Get available time slots

### Authentication
All endpoints (except `/` and `/health`) require authentication using JWT tokens.

## 📚 Data Models

### Appointment
```json
{
  "id": "string",
  "patient_id": "string",
  "doctor_id": "string",
  "scheduled_time": "2025-09-27T10:00:00",
  "duration_minutes": 30,
  "status": "scheduled",
  "notes": "string",
  "created_at": "2025-09-26T15:30:00",
  "updated_at": "2025-09-26T15:30:00"
}
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_appointments.py

# Run with coverage report
pytest --cov=app --cov-report=html
```

## 📝 API Documentation

### Create an Appointment
```http
POST /appointments
Content-Type: application/json
Authorization: Bearer your-jwt-token

{
  "patient_id": "patient-123",
  "doctor_id": "doctor-456",
  "scheduled_time": "2025-10-01T14:30:00",
  "duration_minutes": 30,
  "notes": "Routine checkup"
}
```

### Get Available Time Slots
```http
GET /appointments/available-slots?doctor_id=doctor-456&date=2025-10-01
Authorization: Bearer your-jwt-token
```

## 🔍 Examples

### Using the API with Python
```python
import requests
from datetime import datetime, timedelta

# Base URL
BASE_URL = "http://localhost:8007"

# Get available time slots
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
response = requests.get(
    f"{BASE_URL}/appointments/available-slots",
    params={"doctor_id": "doctor-456", "date": tomorrow},
    headers={"Authorization": "Bearer your-jwt-token"}
)
print("Available slots:", response.json())

# Schedule an appointment
appointment_data = {
    "patient_id": "patient-123",
    "doctor_id": "doctor-456",
    "scheduled_time": "2025-10-01T14:30:00",
    "duration_minutes": 30,
    "notes": "Annual physical examination"
}

response = requests.post(
    f"{BASE_URL}/appointments",
    json=appointment_data,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer your-jwt-token"
    }
)

if response.status_code == 201:
    print("Appointment created:", response.json())
else:
    print("Error:", response.json())
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the awesome web framework
- [SQLModel](https://sqlmodel.tiangolo.com/) for the ORM layer
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
