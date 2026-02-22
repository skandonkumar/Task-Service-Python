# Task Service - Python (Flask)

ACID-compliant task management API built with Flask and PostgreSQL.

## Overview

This service implements the task management API using:
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL (Relational SQL)
- **Cache**: Redis
- **Purpose**: Strict ACID compliance, structured schemas, complex queries

## Architecture

```
Flask Routes → SQLAlchemy ORM → PostgreSQL
      ↓
    Redis (Cache Layer)
```

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 7.0+
- pip or Poetry
- Docker (for containerized deployment)

## Local Development

### 1. Start Dependencies

```bash
# Start PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15-alpine

# Start Redis
docker run -d --name redis -p 6379:6379 redis:alpine

# Create database
docker exec -it postgres psql -U postgres -c "CREATE DATABASE tasks_db;"
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Locally

```bash
python app.py
```

The service will start on `http://localhost:5000`

## Configuration

Set environment variables:

```bash
# Flask
FLASK_ENV=development
PORT=5000

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

Or create a `.env` file and load with `python-dotenv`.

## API Endpoints

### Create Task

```bash
POST /api/python/v1/tasks
Content-Type: application/json

{
  "title": "My Task",
  "description": "Task description"
}
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "My Task",
  "description": "Task description",
  "status": "PENDING"
}
```

### Get Task

```bash
GET /api/python/v1/tasks/{id}
```

### Update Task

```bash
PUT /api/python/v1/tasks/{id}
Content-Type: application/json

{
  "status": "IN_PROGRESS",
  "title": "Updated Title"
}
```

### Delete Task

```bash
DELETE /api/python/v1/tasks/{id}
```

## Docker Deployment

### Build Image

```bash
docker build -t task-service-python:1.0.0 .
```

### Run Container

```bash
docker run -d \
  --name python-backend \
  --network task-network \
  -p 5000:5000 \
  -e POSTGRES_HOST=postgres \
  -e REDIS_HOST=redis \
  task-service-python:1.0.0
```

## Kubernetes Deployment

```bash
kubectl apply -f /path/to/infrastructure/dev/python-backend.yaml
```

Monitor startup:

```bash
kubectl get pods -n dev -l app=python-backend -w
kubectl logs -n dev -l app=python-backend
```

## Project Structure

```
├── app.py                # Flask app, routes, models
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container image
├── .env.example         # Environment template
└── .gitignore          # Git ignore rules
```

## Database Schema

### Task Table (PostgreSQL)

```sql
CREATE TABLE tasks (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Database initialization happens automatically on first run via `db.create_all()`.

## Caching Strategy

- Tasks are cached in Redis with key: `tasks::{task_id}`
- Cache TTL: 10 minutes (600s)
- Cache is invalidated on update/delete
- First read populates the cache from PostgreSQL

## Development Scripts

```bash
# Run locally
python app.py

# Run with Gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Test PostgreSQL connection
python -c "from app import db; db.create_all(); print('DB OK')"
```

## Troubleshooting

### PostgreSQL Connection Refused

Ensure PostgreSQL is running and accessible:

```bash
# Docker
docker logs postgres

# Kubernetes
kubectl logs -n dev -l app=postgres

# Test connection
psql -h localhost -U postgres -d tasks_db
```

### Database "tasks_db" Does Not Exist

Create it manually:

```bash
# Docker
docker exec -it postgres psql -U postgres -c "CREATE DATABASE tasks_db;"

# Direct PostgreSQL
psql -U postgres -c "CREATE DATABASE tasks_db;"
```

### Redis Connection Failed

Check Redis availability:

```bash
# Docker
docker logs redis

# Test connection
redis-cli ping
```

### Port Already in Use

Change PORT or kill the process:

```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

## Performance Notes

- PostgreSQL ensures ACID compliance for critical transactions
- SQLAlchemy ORM provides query optimization and connection pooling
- Redis cache dramatically reduces database read load
- Consider adding database indexes on frequently queried fields
- Connection pooling is configured via SQLAlchemy

## Dependencies

Key packages in `requirements.txt`:
- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM and database integration
- **PostgreSQL psycopg2**: Database driver
- **redis**: Cache client
- **python-dotenv**: Environment variable management

## License

MIT
