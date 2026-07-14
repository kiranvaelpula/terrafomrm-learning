# Lab 10: End-to-End MLOps Project

## Overview
Build a complete, production-ready MLOps system integrating all concepts from previous labs. Deploy a real-world ML application with full automation, monitoring, and governance.

**Duration:** 4-6 hours  
**Difficulty:** Advanced  
**Prerequisites:** Labs 01-09, DevOps fundamentals

## Learning Objectives
- Integrate all MLOps components
- Build production-ready infrastructure
- Implement complete CI/CD pipeline
- Deploy with monitoring and governance
- Handle the full ML lifecycle

## Project: Customer Churn Prediction Platform

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  Raw Data → DVC → Feature Store → Training Data                 │
│  (S3)       (Git)  (Feast/Redis)   (Parquet)                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      TRAINING PIPELINE                           │
├─────────────────────────────────────────────────────────────────┤
│  Data Validation → Feature Engineering → Model Training         │
│  (Great Expectations) (Feast)           (MLflow + DVC)         │
│         ↓                                      ↓                 │
│  Model Evaluation → Model Registry → Model Staging              │
│  (MLflow)           (MLflow)         (Approval Gate)           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT PIPELINE                           │
├─────────────────────────────────────────────────────────────────┤
│  Containerization → A/B Testing → Production Deployment         │
│  (Docker)           (Redis)       (Kubernetes/ECS)              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING & FEEDBACK                         │
├─────────────────────────────────────────────────────────────────┤
│  Performance → Data Drift → Concept Drift → Retraining Trigger │
│  (Prometheus) (Evidently)   (Evidently)      (Airflow)         │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
mlops-e2e-project/
├── .github/
│   └── workflows/
│       ├── test.yml
│       ├── train.yml
│       ├── deploy-staging.yml
│       └── deploy-production.yml
├── data/
│   ├── raw/
│   ├── processed/
│   └── features/
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── ingestion.py
│   │   ├── validation.py
│   │   └── preprocessing.py
│   ├── features/
│   │   ├── __init__.py
│   │   ├── engineering.py
│   │   └── feast_features.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── predict.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── dependencies.py
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── performance.py
│   │   ├── drift.py
│   │   └── alerts.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── logging.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── infrastructure/
│   ├── terraform/
│   ├── kubernetes/
│   └── docker/
├── notebooks/
│   └── exploration.ipynb
├── feast/
│   ├── feature_store.yaml
│   └── features.py
├── monitoring/
│   ├── grafana/
│   └── prometheus/
├── dvc.yaml
├── params.yaml
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Implementation

### Step 1: Data Pipeline

Create `src/data/ingestion.py`:

```python
import pandas as pd
import boto3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataIngestion:
    def __init__(self, s3_bucket='ml-data-bucket'):
        self.s3_client = boto3.client('s3')
        self.s3_bucket = s3_bucket
    
    def fetch_data(self, data_source='database'):
        """Fetch data from source"""
        logger.info(f"Fetching data from {data_source}")
        
        if data_source == 'database':
            # In production, connect to actual database
            df = self._fetch_from_database()
        elif data_source == 's3':
            df = self._fetch_from_s3()
        else:
            raise ValueError(f"Unknown data source: {data_source}")
        
        logger.info(f"Fetched {len(df)} records")
        return df
    
    def _fetch_from_database(self):
        """Fetch from database (simulated)"""
        # In production: Use SQLAlchemy or similar
        df = pd.read_csv('data/raw/customers.csv')
        return df
    
    def _fetch_from_s3(self):
        """Fetch from S3"""
        response = self.s3_client.get_object(
            Bucket=self.s3_bucket,
            Key='data/customers.csv'
        )
        df = pd.read_csv(response['Body'])
        return df
    
    def save_snapshot(self, df, path='data/raw/snapshot.csv'):
        """Save data snapshot with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        snapshot_path = path.replace('.csv', f'_{timestamp}.csv')
        df.to_csv(snapshot_path, index=False)
        logger.info(f"Saved snapshot to {snapshot_path}")
        return snapshot_path
```

Create `src/data/validation.py`:

```python
import great_expectations as ge
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self):
        self.expectations = []
    
    def validate_schema(self, df: pd.DataFrame) -> bool:
        """Validate data schema"""
        required_columns = [
            'customer_id', 'age', 'tenure_months',
            'monthly_charges', 'total_charges', 'churn'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Missing required column: {col}")
                return False
        
        return True
    
    def validate_data_quality(self, df: pd.DataFrame) -> dict:
        """Validate data quality"""
        results = {
            'passed': True,
            'checks': []
        }
        
        # Check 1: No excessive missing values
        missing_pct = df.isnull().sum() / len(df)
        for col, pct in missing_pct.items():
            if pct > 0.1:
                results['checks'].append({
                    'check': f'missing_values_{col}',
                    'passed': False,
                    'message': f'{col} has {pct:.1%} missing values'
                })
                results['passed'] = False
        
        # Check 2: Reasonable value ranges
        if 'age' in df.columns:
            if not df['age'].between(18, 100).all():
                results['checks'].append({
                    'check': 'age_range',
                    'passed': False,
                    'message': 'Invalid age values detected'
                })
                results['passed'] = False
        
        # Check 3: No duplicates
        if df.duplicated(subset=['customer_id']).any():
            results['checks'].append({
                'check': 'duplicates',
                'passed': False,
                'message': 'Duplicate customer IDs found'
            })
            results['passed'] = False
        
        # Check 4: Target distribution
        if 'churn' in df.columns:
            churn_rate = df['churn'].mean()
            if churn_rate < 0.05 or churn_rate > 0.5:
                results['checks'].append({
                    'check': 'target_distribution',
                    'passed': False,
                    'message': f'Unusual churn rate: {churn_rate:.2%}'
                })
                results['passed'] = False
        
        logger.info(f"Data validation: {'PASSED' if results['passed'] else 'FAILED'}")
        return results
```

### Step 2: Complete Training Pipeline

Create `src/models/train.py`:

```python
import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
import joblib
import yaml
from pathlib import Path

class ModelTrainer:
    def __init__(self, config_path='params.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        mlflow.set_tracking_uri(self.config['mlflow']['tracking_uri'])
        mlflow.set_experiment(self.config['mlflow']['experiment_name'])
    
    def train(self, X_train, X_test, y_train, y_test):
        """Train model with hyperparameter tuning"""
        
        with mlflow.start_run(run_name='training'):
            
            # Log parameters
            mlflow.log_params(self.config['model']['params'])
            
            # Hyperparameter tuning
            if self.config['model'].get('tune_hyperparameters', False):
                model = self._tune_hyperparameters(X_train, y_train)
            else:
                model = RandomForestClassifier(**self.config['model']['params'])
                model.fit(X_train, y_train)
            
            # Evaluate
            metrics = self._evaluate(model, X_test, y_test)
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log model
            mlflow.sklearn.log_model(
                model,
                "model",
                registered_model_name=self.config['model']['name']
            )
            
            # Save locally
            joblib.dump(model, 'models/model.pkl')
            
            return model, metrics
    
    def _tune_hyperparameters(self, X_train, y_train):
        """Tune hyperparameters with grid search"""
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5, 10]
        }
        
        grid_search = GridSearchCV(
            RandomForestClassifier(random_state=42),
            param_grid,
            cv=5,
            scoring='f1',
            n_jobs=-1
        )
        
        grid_search.fit(X_train, y_train)
        
        mlflow.log_params(grid_search.best_params_)
        
        return grid_search.best_estimator_
    
    def _evaluate(self, model, X_test, y_test):
        """Evaluate model"""
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        return {
            'accuracy': accuracy_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_proba),
            'test_size': len(y_test)
        }
```

### Step 3: Production API

Create `src/api/main.py`:

```python
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
import mlflow
import pandas as pd
from typing import List
import logging
from .schemas import PredictionRequest, PredictionResponse
from .dependencies import get_model, get_feature_store

# Metrics
PREDICTION_COUNTER = Counter('predictions_total', 'Total predictions')
PREDICTION_LATENCY = Histogram('prediction_latency_seconds', 'Prediction latency')

app = FastAPI(
    title="Churn Prediction API",
    version="1.0.0",
    description="Production ML API for customer churn prediction"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics"""
    return Response(generate_latest(), media_type="text/plain")

@app.post("/predict", response_model=PredictionResponse)
@PREDICTION_LATENCY.time()
async def predict(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    model = Depends(get_model),
    feature_store = Depends(get_feature_store)
):
    """Make prediction"""
    
    try:
        # Get features from feature store
        features = feature_store.get_online_features(
            entity_rows=[{'customer': request.customer_id}],
            features=['customer_features:*']
        ).to_dict()
        
        # Prepare data
        df = pd.DataFrame([features])
        
        # Predict
        prediction = model.predict(df)[0]
        probability = model.predict_proba(df)[0][1]
        
        # Log prediction
        background_tasks.add_task(
            log_prediction,
            request.customer_id,
            prediction,
            probability
        )
        
        PREDICTION_COUNTER.inc()
        
        return PredictionResponse(
            customer_id=request.customer_id,
            churn_prediction=int(prediction),
            churn_probability=float(probability),
            risk_level=classify_risk(probability)
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def classify_risk(probability: float) -> str:
    """Classify churn risk level"""
    if probability >= 0.7:
        return "HIGH"
    elif probability >= 0.4:
        return "MEDIUM"
    else:
        return "LOW"

def log_prediction(customer_id: str, prediction: int, probability: float):
    """Log prediction for monitoring"""
    # In production: Save to database or monitoring system
    logger.info(f"Prediction logged: {customer_id}, {prediction}, {probability}")
```

### Step 4: Monitoring System

Create `src/monitoring/drift.py`:

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DriftMonitor:
    def __init__(self, reference_data_path='data/reference/baseline.csv'):
        self.reference_data = pd.read_csv(reference_data_path)
    
    def check_drift(self, current_data: pd.DataFrame) -> dict:
        """Check for data drift"""
        
        report = Report(metrics=[
            DataDriftPreset(),
            DataQualityPreset()
        ])
        
        report.run(
            reference_data=self.reference_data,
            current_data=current_data
        )
        
        # Extract results
        results = report.as_dict()
        
        drift_detected = results['metrics'][0]['result']['dataset_drift']
        
        if drift_detected:
            logger.warning("⚠️ Data drift detected!")
            # Trigger alert
            self._send_alert("Data drift detected")
        
        return {
            'drift_detected': drift_detected,
            'report': results
        }
    
    def _send_alert(self, message: str):
        """Send alert (Slack, email, PagerDuty, etc.)"""
        # Implementation depends on your alerting system
        logger.info(f"Alert: {message}")
```

### Step 5: Infrastructure as Code

Create `infrastructure/terraform/main.tf`:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 Bucket for data
resource "aws_s3_bucket" "ml_data" {
  bucket = "ml-churn-prediction-data"
  
  tags = {
    Name        = "ML Data Bucket"
    Environment = var.environment
  }
}

# ECR Repository for Docker images
resource "aws_ecr_repository" "ml_api" {
  name                 = "churn-prediction-api"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "ml_cluster" {
  name = "ml-ops-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "api_task" {
  family                   = "churn-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  
  container_definitions = jsonencode([{
    name  = "api"
    image = "${aws_ecr_repository.ml_api.repository_url}:latest"
    
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    
    environment = [
      {
        name  = "ENVIRONMENT"
        value = var.environment
      }
    ]
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/churn-api"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# Load Balancer
resource "aws_lb" "api_lb" {
  name               = "ml-api-lb"
  internal           = false
  load_balancer_type = "application"
  subnets            = var.public_subnet_ids
  
  enable_deletion_protection = false
}

# Output URLs
output "api_url" {
  value = aws_lb.api_lb.dns_name
}
```

### Step 6: Kubernetes Deployment

Create `infrastructure/kubernetes/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: churn-prediction-api
  labels:
    app: churn-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: churn-api
  template:
    metadata:
      labels:
        app: churn-api
    spec:
      containers:
      - name: api
        image: <your-registry>/churn-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: MLFLOW_TRACKING_URI
          valueFrom:
            secretKeyRef:
              name: mlflow-config
              key: tracking-uri
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: churn-api-service
spec:
  selector:
    app: churn-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: churn-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: churn-prediction-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Step 7: Complete CI/CD Pipeline

Create `.github/workflows/complete-pipeline.yml`:

```yaml
name: Complete MLOps Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest tests/ -v --cov=src
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  train:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Train model
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: python src/models/train.py
      
      - name: Validate model
        run: python tests/validate_model.py

  deploy-staging:
    needs: train
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t churn-api:${{ github.sha }} .
      
      - name: Deploy to staging
        run: |
          # Deploy to staging environment
          echo "Deploying to staging..."

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to production
        run: |
          # Deploy to production with blue-green
          echo "Deploying to production..."
```

## Deployment Guide

### Local Development

```bash
# 1. Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Start services
docker-compose up -d

# 3. Run pipeline
dvc repro

# 4. Start API
uvicorn src.api.main:app --reload
```

### Production Deployment

```bash
# 1. Deploy infrastructure
cd infrastructure/terraform
terraform init
terraform apply

# 2. Build and push Docker image
docker build -t <registry>/churn-api:v1.0.0 .
docker push <registry>/churn-api:v1.0.0

# 3. Deploy to Kubernetes
kubectl apply -f infrastructure/kubernetes/

# 4. Verify deployment
kubectl get pods
kubectl get svc
```

## Monitoring Dashboard

Access monitoring at:
- Grafana: http://localhost:3000
- MLflow: http://localhost:5000
- API Docs: http://localhost:8000/docs

## Key Takeaways

✅ End-to-end MLOps requires integration of many components  
✅ Automation is critical for reliability and scale  
✅ Monitoring enables proactive problem detection  
✅ Infrastructure as Code ensures reproducibility  
✅ CI/CD pipelines accelerate development cycles  
✅ Feature stores prevent training-serving skew  
✅ Model registry provides governance  
✅ A/B testing validates improvements

## Next Steps

- Add multi-cloud support
- Implement federated learning
- Add explainability (SHAP, LIME)
- Implement model versioning API
- Add cost optimization
- Implement shadow mode deployment

## Resources

- [MLOps Principles](https://ml-ops.org/)
- [Google MLOps Guide](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [AWS MLOps](https://aws.amazon.com/sagemaker/mlops/)
- [Azure MLOps](https://azure.microsoft.com/en-us/products/machine-learning/mlops)

## Conclusion

Congratulations! You've built a complete, production-ready MLOps system. This end-to-end project demonstrates how to:

- Manage the complete ML lifecycle
- Automate training and deployment
- Monitor models in production
- Handle data and model versioning
- Implement governance and compliance
- Scale ML systems effectively

You now have the skills to build and operate ML systems in production!
