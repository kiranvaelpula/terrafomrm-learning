# Lab 07: CI/CD for Machine Learning

## Overview
Implement continuous integration and continuous deployment pipelines for ML models. Automate testing, validation, and deployment processes.

**Duration:** 1.5 hours  
**Difficulty:** Advanced  
**Prerequisites:** Labs 01-06, Git, GitHub Actions/GitLab CI basics

## Learning Objectives
- Build CI/CD pipelines for ML
- Automate model testing
- Implement deployment gates
- Version control everything
- Enable continuous training

## Why CI/CD for ML?

```
Manual Process:
- Train locally
- Test manually
- Deploy by hand
- Hope nothing breaks
❌ Error-prone, slow

Automated CI/CD:
- Automatic testing
- Validation gates
- Automated deployment
- Reproducible builds
✅ Reliable, fast, consistent
```

## Setup

### 1. Project Structure

```
ml-project/
├── .github/
│   └── workflows/
│       ├── test.yml
│       ├── train.yml
│       └── deploy.yml
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── deploy/
├── tests/
│   ├── test_data.py
│   ├── test_model.py
│   └── test_api.py
├── dvc.yaml
├── params.yaml
└── requirements.txt
```

## Implementation

### Step 1: GitHub Actions Workflow for Testing

Create `.github/workflows/test.yml`:

```yaml
name: ML Model Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    
    - name: Install dependencies
      run: |
        pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8
    
    - name: Lint code
      run: |
        flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 src/ --count --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Run data tests
      run: |
        pytest tests/test_data.py -v --cov=src/data
    
    - name: Run model tests
      run: |
        pytest tests/test_model.py -v --cov=src/models
    
    - name: Run API tests
      run: |
        pytest tests/test_api.py -v
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```

### Step 2: Automated Training Pipeline

Create `.github/workflows/train.yml`:

```yaml
name: Model Training

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM
  workflow_dispatch:  # Manual trigger
    inputs:
      experiment_name:
        description: 'Experiment name'
        required: false
        default: 'weekly_training'

jobs:
  train:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      with:
        fetch-depth: 0
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install dvc[s3] mlflow
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Pull data with DVC
      run: |
        dvc remote modify myremote access_key_id ${{ secrets.AWS_ACCESS_KEY_ID }}
        dvc remote modify myremote secret_access_key ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        dvc pull
    
    - name: Run DVC pipeline
      run: |
        dvc repro
    
    - name: Train model
      env:
        MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        MLFLOW_TRACKING_USERNAME: ${{ secrets.MLFLOW_USERNAME }}
        MLFLOW_TRACKING_PASSWORD: ${{ secrets.MLFLOW_PASSWORD }}
      run: |
        python src/train.py --experiment-name "${{ github.event.inputs.experiment_name || 'weekly_training' }}"
    
    - name: Validate model
      run: |
        python tests/validate_model.py --min-accuracy 0.75
    
    - name: Register model
      if: success()
      env:
        MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
      run: |
        python src/register_model.py --stage Staging
    
    - name: Push DVC changes
      run: |
        dvc push
    
    - name: Commit metrics
      run: |
        git config user.name github-actions
        git config user.email github-actions@github.com
        git add metrics/*.json dvc.lock
        git commit -m "Update model metrics [skip ci]" || echo "No changes"
        git push
```

### Step 3: Model Tests

Create `tests/test_model.py`:

```python
import pytest
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

@pytest.fixture
def trained_model():
    """Load trained model"""
    return joblib.load('models/model.pkl')

@pytest.fixture
def test_data():
    """Load test data"""
    df = pd.read_csv('data/processed/customers_processed.csv')
    X = df.drop('churn', axis=1)
    y = df['churn']
    return X, y

def test_model_exists():
    """Test that model file exists"""
    import os
    assert os.path.exists('models/model.pkl'), "Model file not found"

def test_model_accuracy(trained_model, test_data):
    """Test model achieves minimum accuracy"""
    X, y = test_data
    predictions = trained_model.predict(X[:1000])  # Test on subset
    
    accuracy = accuracy_score(y[:1000], predictions)
    assert accuracy >= 0.70, f"Model accuracy {accuracy:.4f} below threshold 0.70"

def test_model_f1_score(trained_model, test_data):
    """Test model achieves minimum F1 score"""
    X, y = test_data
    predictions = trained_model.predict(X[:1000])
    
    f1 = f1_score(y[:1000], predictions)
    assert f1 >= 0.65, f"Model F1 score {f1:.4f} below threshold 0.65"

def test_model_prediction_shape(trained_model, test_data):
    """Test prediction output shape"""
    X, _ = test_data
    predictions = trained_model.predict(X[:10])
    
    assert predictions.shape == (10,), "Prediction shape mismatch"
    assert predictions.dtype == np.int64 or predictions.dtype == np.int32

def test_model_prediction_range(trained_model, test_data):
    """Test predictions are in valid range"""
    X, _ = test_data
    predictions = trained_model.predict(X[:100])
    
    assert np.all((predictions == 0) | (predictions == 1)), "Predictions not in {0, 1}"

def test_model_no_nan_predictions(trained_model, test_data):
    """Test model doesn't produce NaN predictions"""
    X, _ = test_data
    predictions = trained_model.predict(X[:100])
    
    assert not np.any(np.isnan(predictions)), "Model produced NaN predictions"

def test_model_inference_speed(trained_model, test_data):
    """Test prediction latency"""
    import time
    X, _ = test_data
    
    start = time.time()
    _ = trained_model.predict(X[:1000])
    duration = time.time() - start
    
    latency_per_sample = duration / 1000
    assert latency_per_sample < 0.01, f"Inference too slow: {latency_per_sample:.6f}s per sample"

def test_model_deterministic(trained_model, test_data):
    """Test model produces consistent predictions"""
    X, _ = test_data
    
    pred1 = trained_model.predict(X[:100])
    pred2 = trained_model.predict(X[:100])
    
    assert np.array_equal(pred1, pred2), "Model predictions not deterministic"
```

Create `tests/test_data.py`:

```python
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def raw_data():
    """Load raw data"""
    return pd.read_csv('data/raw/customers.csv')

@pytest.fixture
def processed_data():
    """Load processed data"""
    return pd.read_csv('data/processed/customers_processed.csv')

def test_raw_data_exists():
    """Test raw data file exists"""
    import os
    assert os.path.exists('data/raw/customers.csv'), "Raw data not found"

def test_raw_data_not_empty(raw_data):
    """Test data is not empty"""
    assert len(raw_data) > 0, "Raw data is empty"
    assert len(raw_data.columns) > 0, "Raw data has no columns"

def test_raw_data_has_target(raw_data):
    """Test target column exists"""
    assert 'churn' in raw_data.columns, "Target column 'churn' missing"

def test_target_values_valid(raw_data):
    """Test target values are binary"""
    assert raw_data['churn'].isin([0, 1]).all(), "Target values not in {0, 1}"

def test_no_excessive_missing_values(raw_data):
    """Test missing values are within acceptable threshold"""
    missing_pct = raw_data.isnull().sum() / len(raw_data)
    assert (missing_pct < 0.10).all(), "Excessive missing values detected"

def test_no_duplicate_ids(raw_data):
    """Test no duplicate customer IDs"""
    if 'customer_id' in raw_data.columns:
        assert not raw_data['customer_id'].duplicated().any(), "Duplicate customer IDs found"

def test_numeric_ranges(raw_data):
    """Test numeric columns have reasonable ranges"""
    if 'age' in raw_data.columns:
        assert raw_data['age'].between(18, 100).all(), "Invalid age values"
    
    if 'monthly_charges' in raw_data.columns:
        assert (raw_data['monthly_charges'] >= 0).all(), "Negative charges found"

def test_processed_data_shape(processed_data):
    """Test processed data shape"""
    assert len(processed_data) > 1000, "Processed data too small"
    assert len(processed_data.columns) >= 10, "Too few features"

def test_no_missing_in_processed(processed_data):
    """Test no missing values in processed data"""
    assert processed_data.isnull().sum().sum() == 0, "Missing values in processed data"

def test_feature_scaling(processed_data):
    """Test features are scaled appropriately"""
    # Check if numerical features are standardized (approximately)
    numeric_cols = processed_data.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        if col != 'churn':
            mean = processed_data[col].mean()
            std = processed_data[col].std()
            
            # Should be approximately standardized
            assert abs(mean) < 1.0, f"{col} not centered properly"
            assert 0.5 < std < 2.0, f"{col} not scaled properly"
```

### Step 4: Deployment Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Model

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        type: choice
        options:
          - staging
          - production
      model_version:
        description: 'Model version to deploy'
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install mlflow boto3
    
    - name: Validate model version
      env:
        MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
      run: |
        python scripts/validate_model_version.py \
          --model-name churn-predictor \
          --version ${{ github.event.inputs.model_version }}
    
    - name: Build Docker image
      run: |
        docker build -t churn-api:${{ github.event.inputs.model_version }} .
    
    - name: Run smoke tests
      run: |
        docker run -d -p 8000:8000 --name test-api churn-api:${{ github.event.inputs.model_version }}
        sleep 10
        curl -f http://localhost:8000/health || exit 1
        docker stop test-api
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Push to ECR
      run: |
        aws ecr get-login-password | docker login --username AWS --password-stdin ${{ secrets.ECR_REGISTRY }}
        docker tag churn-api:${{ github.event.inputs.model_version }} ${{ secrets.ECR_REGISTRY }}/churn-api:${{ github.event.inputs.model_version }}
        docker push ${{ secrets.ECR_REGISTRY }}/churn-api:${{ github.event.inputs.model_version }}
    
    - name: Deploy to ECS
      run: |
        aws ecs update-service \
          --cluster ml-cluster \
          --service churn-api-${{ github.event.inputs.environment }} \
          --force-new-deployment
    
    - name: Wait for deployment
      run: |
        aws ecs wait services-stable \
          --cluster ml-cluster \
          --services churn-api-${{ github.event.inputs.environment }}
    
    - name: Run integration tests
      run: |
        pytest tests/test_integration.py \
          --api-url ${{ secrets.API_URL_STAGING if github.event.inputs.environment == 'staging' else secrets.API_URL_PROD }}
    
    - name: Notify deployment
      if: always()
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        text: 'Deployment to ${{ github.event.inputs.environment }}: ${{ job.status }}'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Step 5: Model Validation Script

Create `scripts/validate_model_version.py`:

```python
import argparse
import mlflow
from mlflow.tracking import MlflowClient
import sys

def validate_model(model_name, version):
    """Validate model version before deployment"""
    
    client = MlflowClient()
    
    try:
        # Get model version
        model_version = client.get_model_version(model_name, version)
        
        # Check if model is in correct stage
        if model_version.current_stage not in ['Staging', 'Production']:
            print(f"❌ Model must be in Staging or Production (current: {model_version.current_stage})")
            sys.exit(1)
        
        # Get run metrics
        run = client.get_run(model_version.run_id)
        metrics = run.data.metrics
        
        # Validate metrics
        min_accuracy = 0.75
        if 'accuracy' in metrics and metrics['accuracy'] < min_accuracy:
            print(f"❌ Model accuracy {metrics['accuracy']:.4f} below threshold {min_accuracy}")
            sys.exit(1)
        
        print(f"✅ Model validation passed")
        print(f"   Version: {version}")
        print(f"   Stage: {model_version.current_stage}")
        print(f"   Accuracy: {metrics.get('accuracy', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-name', required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    
    validate_model(args.model_name, args.version)
```

## Key Practices

✅ **Automate everything** - From testing to deployment  
✅ **Version control all code and config** - Infrastructure as code  
✅ **Test rigorously** - Data, models, APIs  
✅ **Use deployment gates** - Validate before deploying  
✅ **Enable rollback** - Quick recovery from issues  
✅ **Monitor deployments** - Track success/failure

## Testing Locally

```bash
# Run tests locally
pytest tests/ -v

# Test specific component
pytest tests/test_model.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Lint code
flake8 src/

# Format code
black src/ tests/
```

## Key Takeaways

✅ CI/CD automates the ML lifecycle  
✅ Automated testing catches issues early  
✅ Deployment gates ensure quality  
✅ Version control enables reproducibility  
✅ Continuous training keeps models fresh

## Next Steps

- **Lab 08**: Feature Store implementation
- **Lab 09**: A/B Testing strategies
- Add canary deployments
- Implement blue-green deployment

## Resources

- [GitHub Actions](https://docs.github.com/en/actions)
- [CI/CD for ML](https://ml-ops.org/content/ci-cd-mlops)
- [DVC in CI/CD](https://dvc.org/doc/use-cases/ci-cd-for-machine-learning)
