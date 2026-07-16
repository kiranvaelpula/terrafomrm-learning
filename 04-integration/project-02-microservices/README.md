# Project 2: Microservices CI/CD

Build a complete microservices architecture with independent CI/CD pipelines for each service.

## 📋 Overview

This project demonstrates:
- **Multiple Services:** Frontend, API, Database service
- **Independent Pipelines:** Each service has its own CI/CD
- **Service Communication:** Inter-service communication
- **Container Orchestration:** Docker Compose for local development
- **API Gateway:** Centralized entry point

## 🏗️ Architecture

```
                    ┌─────────────┐
                    │   Client    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Frontend  │
                    │   Service   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ API Gateway │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
    │   Users     │ │  Products  │ │   Orders   │
    │   Service   │ │  Service   │ │  Service   │
    └──────┬──────┘ └─────┬──────┘ └─────┬──────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                    ┌──────▼──────┐
                    │  PostgreSQL │
                    │  Database   │
                    └─────────────┘
```

## 📁 Project Structure

```
project-02-microservices/
├── README.md
├── docker-compose.yml
├── api-gateway/
│   ├── app.py
│   ├── Dockerfile
│   ├── Jenkinsfile
│   └── requirements.txt
├── user-service/
│   ├── app.py
│   ├── Dockerfile
│   ├── Jenkinsfile
│   ├── requirements.txt
│   └── test_app.py
├── product-service/
│   ├── app.py
│   ├── Dockerfile
│   ├── Jenkinsfile
│   ├── requirements.txt
│   └── test_app.py
└── order-service/
    ├── app.py
    ├── Dockerfile
    ├── Jenkinsfile
    ├── requirements.txt
    └── test_app.py
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Jenkins with Docker support
- Python 3.9+

### Start All Services

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Test services
curl http://localhost:8080/users
curl http://localhost:8080/products
curl http://localhost:8080/orders
```

### Access Points
- **API Gateway:** http://localhost:8080
- **Users Service:** http://localhost:8081
- **Products Service:** http://localhost:8082
- **Orders Service:** http://localhost:8083

## 🔧 Service Details

### API Gateway (Port 8080)

Routes requests to appropriate microservices.

**Endpoints:**
- `GET /` - Gateway status
- `GET /users` - Route to user service
- `GET /products` - Route to product service
- `GET /orders` - Route to order service

### User Service (Port 8081)

Manages user data and authentication.

**Endpoints:**
- `GET /health` - Health check
- `GET /users` - List all users
- `GET /users/<id>` - Get user by ID
- `POST /users` - Create new user

### Product Service (Port 8082)

Manages product catalog.

**Endpoints:**
- `GET /health` - Health check
- `GET /products` - List all products
- `GET /products/<id>` - Get product by ID
- `POST /products` - Create new product

### Order Service (Port 8083)

Manages customer orders.

**Endpoints:**
- `GET /health` - Health check
- `GET /orders` - List all orders
- `GET /orders/<id>` - Get order by ID
- `POST /orders` - Create new order

## 📝 CI/CD Pipeline

Each service has its own Jenkins pipeline:

```groovy
// Example for any service
pipeline {
    agent any
    stages {
        stage('Test') { /* test service */ }
        stage('Build') { /* build Docker image */ }
        stage('Deploy') { /* deploy service */ }
    }
}
```

### Pipeline Features:
- ✅ Independent deployment
- ✅ Service-specific tests
- ✅ Isolated builds
- ✅ Version tagging
- ✅ Health checks

## 🧪 Testing

### Test Individual Service

```bash
# Test user service
cd user-service
python -m pytest test_app.py -v

# Test with Docker
docker build -t user-service:test .
docker run -p 8081:8081 user-service:test
curl http://localhost:8081/health
```

### Test All Services

```bash
# Start all services
docker-compose up -d

# Run integration tests
./run-integration-tests.sh
```

## 🐛 Troubleshooting

**Services won't start:**
```bash
docker-compose down -v
docker-compose up --build
```

**Port conflicts:**
```bash
# Check ports
netstat -tulpn | grep :808

# Stop conflicting services
docker ps
docker stop <container>
```

**Service communication issues:**
```bash
# Check network
docker network inspect project-02-microservices_default

# Check service logs
docker-compose logs user-service
```

## 📈 Scaling

```bash
# Scale specific service
docker-compose up -d --scale user-service=3

# View running instances
docker-compose ps
```

## ✅ What You Learned

- ✅ Microservices architecture design
- ✅ Independent service deployment
- ✅ Service-to-service communication
- ✅ API Gateway pattern
- ✅ Container orchestration
- ✅ Distributed CI/CD pipelines

## 📚 Next Steps

- Add service mesh (Istio)
- Implement distributed tracing
- Add centralized logging
- Implement circuit breakers
- Move to [Project 3: Multi-Environment](../project-03-multi-env/)

---

**Congratulations!** You've built a microservices architecture with CI/CD! 🎉

