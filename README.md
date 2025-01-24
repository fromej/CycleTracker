# Menstrual Cycle Tracker Application

## Local Development

### Prerequisites
- Python 3.9+
- Docker (optional)

### Setup and Run
1. Clone the repository
2. Create a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Run the application
   ```
   uvicorn app.main:app --reload
   ```

### Docker Deployment
```
docker-compose up --build
```

## Kubernetes Deployment
1. Build Docker image
   ```
   docker build -t menstrual-tracker:latest .
   ```
2. Install Helm Chart
   ```
   helm install menstrual-tracker ./helm
   ```

## Data Persistence
- Uses SQLite with database file stored in `app/data/menstrual_tracker.db`
- Persistent volume mounts this directory in Kubernetes deployments

## Features
- User Authentication
- Menstrual Cycle Tracking
- Dashboard for Cycle Management

## Security Considerations
- Passwords are hashed using bcrypt
- JWT for authentication
```