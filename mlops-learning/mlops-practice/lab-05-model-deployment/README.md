# Lab 05: Model Deployment with REST APIs

## Overview
Deploy ML models as production-ready REST APIs using FastAPI. Learn containerization, health checks, logging, and load testing.

**Duration:** 1.5-2 hours  
**Difficulty:** Intermediate  
**Prerequisites:** Labs 01-04, Docker basics, REST API concepts

## Learning Objectives
- Build REST APIs with FastAPI
- Containerize models with Docker
- Implement health checks and monitoring
- Handle prediction requests at scale
- Load test deployed models

## Why API Deployment?

```
Model in Notebook:
- Requires Python environment
- Manual execution
- Not accessible to other systems
❌ Limited usefulness

Model as API:
- HTTP endpoint
- Language-agnostic
- Scalable and monitored
✅ Production-ready
```

## Setup

### 1. Install Dependencies

```bash
pip install fastapi uvicorn pydantic mlflow scikit-learn
pip install python-multipart requests
pip install locust  # For load testing
```

### 2. Project Structure

```
deployment/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── config.py
│   └── utils.py
├── models/
│   └── model.pkl
├── tests/
│   ├── test_api.py
│   └── load_test.py
├── Dockerfile
├── requirements.txt
└── docker-compose.yml
```

## Implementation

### Step 1: FastAPI Application

Create `app/main.py`:

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import mlflow
import mlflow.pyfunc
import pandas as pd
import logging
from datetime import datetime
from typing import List, Optional
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Churn Prediction API",
    description="ML model for predicting customer churn",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable
model = None
model_version = None
model_loaded_at = None

# Request/Response models
class Customer(BaseModel):
    customer_id: str = Field(..., description="Unique customer ID")
    age: int = Field(..., ge=18, le=100, description="Customer age")
    tenure_months: int = Field(..., ge=0, description="Months as customer")
    monthly_charges: float = Field(..., ge=0, description="Monthly charges")
    total_charges: float = Field(..., ge=0, description="Total charges")
    contract_type: int = Field(..., ge=0, le=2, description="Contract type (0-2)")
    payment_method: int = Field(..., ge=0, le=3, description="Payment method (0-3)")
    internet_service: int = Field(..., ge=0, le=2, description="Internet service (0-2)")
    online_security: int = Field(..., ge=0, le=2, description="Online security (0-2)")
    tech_support: int = Field(..., ge=0, le=2, description="Tech support (0-2)")
    num_support_calls: int = Field(..., ge=0, description="Number of support calls")
    satisfaction_score: int = Field(..., ge=1, le=5, description="Satisfaction score (1-5)")
    
    class Config:
        schema_extra = {
            "example": {
                "customer_id": "C000001",
                "age": 45,
                "tenure_months": 24,
                "monthly_charges": 75.50,
                "total_charges": 1812.00,
                "contract_type": 1,
                "payment_method": 2,
                "internet_service": 1,
                "online_security": 1,
                "tech_support": 0,
                "num_support_calls": 2,
                "satisfaction_score": 4
            }
        }

class PredictionResponse(BaseModel):
    customer_id: str
    churn_probability: float
    churn_prediction: int
    risk_level: str
    prediction_timestamp: str

class BatchPredictionRequest(BaseModel):
    customers: List[Customer]

# Startup event
@app.on_event("startup")
async def load_model():
    """Load model on startup"""
    global model, model_version, model_loaded_at
    
    try:
        logger.info("Loading model...")
        
        # Load from MLflow registry (or local file)
        try:
            mlflow.set_tracking_uri("http://localhost:5000")
            model_uri = "models:/churn-predictor-rf/Production"
            model = mlflow.pyfunc.load_model(model_uri)
            model_version = "Production"
        except:
            # Fallback to local model
            import joblib
            model = joblib.load("models/model.pkl")
            model_version = "Local"
        
        model_loaded_at = datetime.now().isoformat()
        logger.info(f"Model loaded successfully: {model_version}")
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check API health"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_version": model_version,
        "model_loaded_at": model_loaded_at,
        "timestamp": datetime.now().isoformat()
    }

# Readiness check
@app.get("/ready")
async def readiness_check():
    """Check if API is ready to serve requests"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {"status": "ready"}

# Model info endpoint
@app.get("/model/info")
async def model_info():
    """Get model information"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_version": model_version,
        "loaded_at": model_loaded_at,
        "model_type": type(model).__name__
    }

# Prediction endpoint
@app.post("/predict", response_model=PredictionResponse)
async def predict(customer: Customer, background_tasks: BackgroundTasks):
    """Make churn prediction for a single customer"""
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert to DataFrame
        data = pd.DataFrame([customer.dict()])
        
        # Remove customer_id for prediction
        customer_id = data['customer_id'].values[0]
        X = data.drop('customer_id', axis=1)
        
        # Make prediction
        prediction = model.predict(X)[0]
        
        # Get probability (if available)
        try:
            proba = model._model_impl.python_model.predict_proba(X)[0][1]
        except:
            proba = float(prediction)
        
        # Determine risk level
        if proba >= 0.7:
            risk_level = "HIGH"
        elif proba >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        response = PredictionResponse(
            customer_id=customer_id,
            churn_probability=float(proba),
            churn_prediction=int(prediction),
            risk_level=risk_level,
            prediction_timestamp=datetime.now().isoformat()
        )
        
        # Log prediction (background task)
        background_tasks.add_task(log_prediction, customer_id, prediction, proba)
        
        return response
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch prediction endpoint
@app.post("/predict/batch")
async def predict_batch(request: BatchPredictionRequest):
    """Make predictions for multiple customers"""
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert to DataFrame
        data = pd.DataFrame([c.dict() for c in request.customers])
        customer_ids = data['customer_id'].values
        X = data.drop('customer_id', axis=1)
        
        # Make predictions
        predictions = model.predict(X)
        
        # Get probabilities
        try:
            probas = model._model_impl.python_model.predict_proba(X)[:, 1]
        except:
            probas = predictions.astype(float)
        
        # Build responses
        responses = []
        for i, customer_id in enumerate(customer_ids):
            proba = float(probas[i])
            
            if proba >= 0.7:
                risk_level = "HIGH"
            elif proba >= 0.4:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            responses.append({
                "customer_id": customer_id,
                "churn_probability": proba,
                "churn_prediction": int(predictions[i]),
                "risk_level": risk_level
            })
        
        return {
            "predictions": responses,
            "total_count": len(responses),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task for logging
def log_prediction(customer_id: str, prediction: int, probability: float):
    """Log prediction to file/database"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "customer_id": customer_id,
        "prediction": prediction,
        "probability": probability
    }
    logger.info(f"Prediction logged: {log_entry}")

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Get API metrics"""
    # In production, use Prometheus or similar
    return {
        "total_predictions": 0,  # Track this
        "average_latency_ms": 0,
        "error_rate": 0
    }

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 2: Docker Container

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY models/ ./models/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `requirements.txt`:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
mlflow==2.8.1
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
python-multipart==0.0.6
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  model-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
  
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    command: >
      mlflow server
      --host 0.0.0.0
      --port 5000
      --backend-store-uri sqlite:///mlflow.db
      --default-artifact-root /mlflow/artifacts
    volumes:
      - mlflow-data:/mlflow
    restart: unless-stopped

volumes:
  mlflow-data:
```

### Step 3: API Testing

Create `tests/test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    print("✅ Health check passed")

def test_readiness():
    """Test readiness endpoint"""
    response = requests.get(f"{BASE_URL}/ready")
    assert response.status_code == 200
    print("✅ Readiness check passed")

def test_prediction():
    """Test single prediction"""
    customer = {
        "customer_id": "C000001",
        "age": 45,
        "tenure_months": 24,
        "monthly_charges": 75.50,
        "total_charges": 1812.00,
        "contract_type": 1,
        "payment_method": 2,
        "internet_service": 1,
        "online_security": 1,
        "tech_support": 0,
        "num_support_calls": 2,
        "satisfaction_score": 4
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=customer)
    assert response.status_code == 200
    
    data = response.json()
    assert 'churn_probability' in data
    assert 'churn_prediction' in data
    assert data['customer_id'] == customer['customer_id']
    
    print(f"✅ Prediction: {data['churn_prediction']} (probability: {data['churn_probability']:.4f})")
    print(f"   Risk level: {data['risk_level']}")

def test_batch_prediction():
    """Test batch prediction"""
    customers = [
        {
            "customer_id": f"C00000{i}",
            "age": 45 + i,
            "tenure_months": 24,
            "monthly_charges": 75.50,
            "total_charges": 1812.00,
            "contract_type": 1,
            "payment_method": 2,
            "internet_service": 1,
            "online_security": 1,
            "tech_support": 0,
            "num_support_calls": 2,
            "satisfaction_score": 4
        }
        for i in range(5)
    ]
    
    response = requests.post(
        f"{BASE_URL}/predict/batch",
        json={"customers": customers}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data['total_count'] == 5
    print(f"✅ Batch prediction: {data['total_count']} customers processed")

if __name__ == "__main__":
    print("🧪 Running API tests...\n")
    
    test_health()
    test_readiness()
    test_prediction()
    test_batch_prediction()
    
    print("\n✅ All tests passed!")
```

### Step 4: Load Testing

Create `tests/load_test.py`:

```python
from locust import HttpUser, task, between
import random

class ModelAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def predict_single(self):
        """Test single prediction endpoint"""
        customer = {
            "customer_id": f"C{random.randint(100000, 999999)}",
            "age": random.randint(25, 70),
            "tenure_months": random.randint(1, 72),
            "monthly_charges": round(random.uniform(20, 120), 2),
            "total_charges": round(random.uniform(100, 8000), 2),
            "contract_type": random.randint(0, 2),
            "payment_method": random.randint(0, 3),
            "internet_service": random.randint(0, 2),
            "online_security": random.randint(0, 2),
            "tech_support": random.randint(0, 2),
            "num_support_calls": random.randint(0, 10),
            "satisfaction_score": random.randint(1, 5)
        }
        
        self.client.post("/predict", json=customer)
    
    @task(1)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/health")
    
    @task(1)
    def batch_predict(self):
        """Test batch prediction"""
        customers = [
            {
                "customer_id": f"C{random.randint(100000, 999999)}",
                "age": random.randint(25, 70),
                "tenure_months": random.randint(1, 72),
                "monthly_charges": round(random.uniform(20, 120), 2),
                "total_charges": round(random.uniform(100, 8000), 2),
                "contract_type": random.randint(0, 2),
                "payment_method": random.randint(0, 3),
                "internet_service": random.randint(0, 2),
                "online_security": random.randint(0, 2),
                "tech_support": random.randint(0, 2),
                "num_support_calls": random.randint(0, 10),
                "satisfaction_score": random.randint(1, 5)
            }
            for _ in range(10)
        ]
        
        self.client.post("/predict/batch", json={"customers": customers})

# Run with:
# locust -f tests/load_test.py --host=http://localhost:8000
```

## Deployment

### Local Deployment

```bash
# Run FastAPI directly
uvicorn app.main:app --reload --port 8000

# Access API docs: http://localhost:8000/docs
```

### Docker Deployment

```bash
# Build image
docker build -t churn-prediction-api .

# Run container
docker run -p 8000:8000 churn-prediction-api

# Or use docker-compose
docker-compose up -d
```

### Cloud Deployment (AWS ECS example)

```bash
# Tag image
docker tag churn-prediction-api:latest <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/churn-api:latest

# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <ecr-url>
docker push <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/churn-api:latest

# Deploy to ECS (using task definition)
```

## Testing Deployed API

```bash
# Test health
curl http://localhost:8000/health

# Test prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "C000001",
    "age": 45,
    "tenure_months": 24,
    "monthly_charges": 75.50,
    "total_charges": 1812.00,
    "contract_type": 1,
    "payment_method": 2,
    "internet_service": 1,
    "online_security": 1,
    "tech_support": 0,
    "num_support_calls": 2,
    "satisfaction_score": 4
  }'

# Run load test
locust -f tests/load_test.py --host=http://localhost:8000 --users 100 --spawn-rate 10
```

## Key Takeaways

✅ FastAPI provides fast, documented REST APIs  
✅ Docker ensures consistent deployment environments  
✅ Health checks enable monitoring and orchestration  
✅ Load testing validates performance requirements  
✅ Background tasks handle async operations

## Next Steps

- **Lab 06**: Model Monitoring and drift detection
- **Lab 07**: CI/CD for automated deployment
- Add authentication (JWT)
- Implement rate limiting
- Add caching layer

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [REST API Design](https://restfulapi.net/)
