# Lab 03: ML Pipeline Automation

## Overview
Build automated, reproducible ML pipelines using orchestration tools. Learn to schedule training, handle dependencies, and monitor pipeline execution.

**Duration:** 1.5-2 hours  
**Difficulty:** Intermediate  
**Prerequisites:** Labs 01-02, Python, basic ML

## Learning Objectives
- Build automated ML pipelines
- Handle task dependencies
- Schedule recurring training
- Monitor pipeline execution
- Implement error handling and retries

## Why Pipeline Automation?

```
Without Automation:
- Manual data downloads
- Manual preprocessing
- Manual training
- Manual evaluation
- Manual deployment
❌ Error-prone, slow, not reproducible

With Automation:
- Scheduled execution
- Automatic dependencies
- Parallel processing
- Failure recovery
✅ Reliable, fast, reproducible
```

## Setup

### 1. Install Dependencies

```bash
pip install apache-airflow pandas scikit-learn mlflow
pip install prefect  # Alternative to Airflow
pip install kedro    # Alternative framework
```

### 2. Initialize Airflow

```bash
# Set Airflow home
export AIRFLOW_HOME=~/airflow

# Initialize database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# Start Airflow
airflow webserver --port 8080  # Terminal 1
airflow scheduler              # Terminal 2
```

## Implementation

### Step 1: Simple ML Pipeline with Python

Create `src/pipeline_simple.py`:

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
import joblib
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLPipeline:
    def __init__(self, config):
        self.config = config
        self.model = None
        
    def extract_data(self):
        """Step 1: Extract data"""
        logger.info("📥 Extracting data...")
        
        # Simulate data extraction
        df = pd.read_csv(self.config['data_path'])
        
        logger.info(f"   Loaded {len(df)} records")
        return df
    
    def transform_data(self, df):
        """Step 2: Transform data"""
        logger.info("🔄 Transforming data...")
        
        # Handle missing values
        df = df.dropna()
        
        # Feature engineering
        df['charges_per_month'] = df['total_charges'] / (df['tenure_months'] + 1)
        df['is_high_value'] = (df['monthly_charges'] > df['monthly_charges'].median()).astype(int)
        
        # Encode categoricals (simplified)
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col != 'customer_id':
                df[col] = pd.Categorical(df[col]).codes
        
        logger.info(f"   Transformed to {df.shape[1]} features")
        return df
    
    def train_model(self, df):
        """Step 3: Train model"""
        logger.info("🎯 Training model...")
        
        # Split data
        X = df.drop(['churn', 'customer_id'], axis=1, errors='ignore')
        y = df['churn']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train
        self.model = RandomForestClassifier(**self.config['model_params'])
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
        
        logger.info(f"   Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"   F1 Score: {metrics['f1_score']:.4f}")
        
        return self.model, metrics
    
    def save_model(self, model, metrics):
        """Step 4: Save model"""
        logger.info("💾 Saving model...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_path = f"models/model_{timestamp}.pkl"
        
        joblib.dump(model, model_path)
        
        # Save metrics
        with open(f"metrics/metrics_{timestamp}.json", 'w') as f:
            import json
            json.dump(metrics, f, indent=2)
        
        logger.info(f"   Saved to {model_path}")
        return model_path
    
    def run(self):
        """Run complete pipeline"""
        logger.info("🚀 Starting ML Pipeline")
        logger.info("=" * 50)
        
        try:
            # Execute pipeline steps
            df = self.extract_data()
            df = self.transform_data(df)
            model, metrics = self.train_model(df)
            model_path = self.save_model(model, metrics)
            
            logger.info("=" * 50)
            logger.info("✅ Pipeline completed successfully!")
            
            return {
                'status': 'success',
                'model_path': model_path,
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

# Run pipeline
if __name__ == "__main__":
    config = {
        'data_path': 'data/raw/customers.csv',
        'model_params': {
            'n_estimators': 100,
            'max_depth': 10,
            'random_state': 42
        }
    }
    
    pipeline = MLPipeline(config)
    result = pipeline.run()
    print(f"\nResult: {result['status']}")
```

### Step 2: Airflow DAG

Create `airflow/dags/ml_training_dag.py`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import logging

# Default arguments
default_args = {
    'owner': 'mlops-team',
    'depends_on_past': False,
    'email': ['alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Define DAG
dag = DAG(
    'ml_training_pipeline',
    default_args=default_args,
    description='Automated ML training pipeline',
    schedule_interval='0 2 * * *',  # Run daily at 2 AM
    start_date=days_ago(1),
    catchup=False,
    tags=['ml', 'training', 'production'],
)

# Task functions
def extract_data(**context):
    """Extract data from source"""
    logging.info("Extracting data...")
    
    df = pd.read_csv('/data/raw/customers.csv')
    
    # Save to intermediate location
    df.to_csv('/tmp/extracted_data.csv', index=False)
    
    # Push metrics to XCom
    context['ti'].xcom_push(key='record_count', value=len(df))
    
    logging.info(f"Extracted {len(df)} records")

def validate_data(**context):
    """Validate data quality"""
    logging.info("Validating data...")
    
    df = pd.read_csv('/tmp/extracted_data.csv')
    
    # Data quality checks
    assert df.isnull().sum().sum() < len(df) * 0.05, "Too many missing values"
    assert len(df) > 1000, "Insufficient data"
    assert 'churn' in df.columns, "Target column missing"
    
    logging.info("Data validation passed")

def preprocess_data(**context):
    """Preprocess and feature engineering"""
    logging.info("Preprocessing data...")
    
    df = pd.read_csv('/tmp/extracted_data.csv')
    
    # Drop missing values
    df = df.dropna()
    
    # Feature engineering
    df['charges_per_month'] = df['total_charges'] / (df['tenure_months'] + 1)
    
    # Encode categoricals
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if col not in ['customer_id']:
            df[col] = pd.Categorical(df[col]).codes
    
    # Save processed data
    df.to_csv('/tmp/processed_data.csv', index=False)
    
    logging.info(f"Preprocessed {len(df)} records with {len(df.columns)} features")

def train_model(**context):
    """Train ML model"""
    logging.info("Training model...")
    
    # Load data
    df = pd.read_csv('/tmp/processed_data.csv')
    X = df.drop(['churn', 'customer_id'], axis=1, errors='ignore')
    y = df['churn']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Save model
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_path = f'/models/model_{timestamp}.pkl'
    joblib.dump(model, model_path)
    
    # Push metrics
    context['ti'].xcom_push(key='accuracy', value=accuracy)
    context['ti'].xcom_push(key='model_path', value=model_path)
    
    logging.info(f"Model trained with accuracy: {accuracy:.4f}")

def evaluate_model(**context):
    """Evaluate model and decide on deployment"""
    ti = context['ti']
    accuracy = ti.xcom_pull(key='accuracy', task_ids='train_model')
    
    logging.info(f"Evaluating model with accuracy: {accuracy:.4f}")
    
    # Deployment threshold
    if accuracy < 0.75:
        raise ValueError(f"Model accuracy {accuracy:.4f} below threshold 0.75")
    
    logging.info("Model passed evaluation")

def deploy_model(**context):
    """Deploy model to production"""
    ti = context['ti']
    model_path = ti.xcom_pull(key='model_path', task_ids='train_model')
    
    logging.info(f"Deploying model from {model_path}")
    
    # Copy to production location
    import shutil
    shutil.copy(model_path, '/models/production/model_latest.pkl')
    
    logging.info("Model deployed successfully")

# Define tasks
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

validate_task = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    dag=dag,
)

preprocess_task = PythonOperator(
    task_id='preprocess_data',
    python_callable=preprocess_data,
    dag=dag,
)

train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

evaluate_task = PythonOperator(
    task_id='evaluate_model',
    python_callable=evaluate_model,
    dag=dag,
)

deploy_task = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy_model,
    dag=dag,
)

# Notification task
notify_task = BashOperator(
    task_id='send_notification',
    bash_command='echo "Pipeline completed successfully" | mail -s "ML Pipeline Success" team@company.com',
    dag=dag,
)

# Define dependencies
extract_task >> validate_task >> preprocess_task >> train_task >> evaluate_task >> deploy_task >> notify_task
```

### Step 3: Prefect Alternative (Simpler)

Create `src/pipeline_prefect.py`:

```python
from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
from datetime import datetime

@task(name="Extract Data", retries=3, retry_delay_seconds=60)
def extract_data(data_path: str) -> pd.DataFrame:
    """Extract data from source"""
    print("📥 Extracting data...")
    df = pd.read_csv(data_path)
    print(f"   Loaded {len(df)} records")
    return df

@task(name="Validate Data")
def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate data quality"""
    print("✅ Validating data...")
    
    assert df.isnull().sum().sum() < len(df) * 0.05, "Too many missing values"
    assert len(df) > 1000, "Insufficient data"
    
    print("   Data validation passed")
    return df

@task(name="Preprocess Data")
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform and engineer features"""
    print("🔄 Preprocessing data...")
    
    df = df.dropna()
    
    # Feature engineering
    df['charges_per_month'] = df['total_charges'] / (df['tenure_months'] + 1)
    
    # Encode categoricals
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if col not in ['customer_id']:
            df[col] = pd.Categorical(df[col]).codes
    
    print(f"   Created {len(df.columns)} features")
    return df

@task(name="Train Model")
def train_model(df: pd.DataFrame, params: dict) -> tuple:
    """Train ML model"""
    print("🎯 Training model...")
    
    X = df.drop(['churn', 'customer_id'], axis=1, errors='ignore')
    y = df['churn']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"   Accuracy: {accuracy:.4f}")
    
    return model, accuracy

@task(name="Save Model")
def save_model(model, accuracy: float) -> str:
    """Save model to disk"""
    print("💾 Saving model...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_path = f"models/model_{timestamp}_acc{accuracy:.4f}.pkl"
    
    joblib.dump(model, model_path)
    print(f"   Saved to {model_path}")
    
    return model_path

@flow(name="ML Training Pipeline", task_runner=SequentialTaskRunner())
def ml_training_flow(data_path: str, model_params: dict):
    """Complete ML training pipeline"""
    
    # Execute tasks
    df = extract_data(data_path)
    df = validate_data(df)
    df = preprocess_data(df)
    model, accuracy = train_model(df, model_params)
    model_path = save_model(model, accuracy)
    
    print(f"\n✅ Pipeline completed!")
    print(f"   Model: {model_path}")
    print(f"   Accuracy: {accuracy:.4f}")
    
    return model_path

# Run pipeline
if __name__ == "__main__":
    result = ml_training_flow(
        data_path="data/raw/customers.csv",
        model_params={
            'n_estimators': 100,
            'max_depth': 10,
            'random_state': 42
        }
    )
    print(f"\nModel saved at: {result}")
```

Run it:
```bash
python src/pipeline_prefect.py
```

### Step 4: Pipeline Monitoring Dashboard

Create `src/monitor_pipeline.py`:

```python
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

class PipelineMonitor:
    def __init__(self, logs_path='logs/pipeline_runs.json'):
        self.logs_path = logs_path
        self.runs = []
        
    def log_run(self, pipeline_id, status, metrics, duration):
        """Log pipeline run"""
        run = {
            'timestamp': datetime.now().isoformat(),
            'pipeline_id': pipeline_id,
            'status': status,
            'metrics': metrics,
            'duration_seconds': duration
        }
        
        self.runs.append(run)
        
        # Save to file
        with open(self.logs_path, 'a') as f:
            f.write(json.dumps(run) + '\n')
    
    def load_runs(self):
        """Load historical runs"""
        runs = []
        try:
            with open(self.logs_path, 'r') as f:
                for line in f:
                    runs.append(json.loads(line))
        except FileNotFoundError:
            pass
        return pd.DataFrame(runs)
    
    def generate_report(self):
        """Generate pipeline monitoring report"""
        df = self.load_runs()
        
        if len(df) == 0:
            print("No pipeline runs found")
            return
        
        print("\n" + "="*60)
        print("📊 PIPELINE MONITORING REPORT")
        print("="*60)
        
        # Success rate
        success_rate = (df['status'] == 'success').mean()
        print(f"\n✅ Success Rate: {success_rate:.1%}")
        
        # Average duration
        avg_duration = df['duration_seconds'].mean()
        print(f"⏱️  Average Duration: {avg_duration:.1f} seconds")
        
        # Recent runs
        print(f"\n📋 Recent Runs ({len(df.tail(5))} most recent):")
        for _, run in df.tail(5).iterrows():
            status_icon = "✅" if run['status'] == 'success' else "❌"
            print(f"   {status_icon} {run['timestamp'][:19]} - {run['duration_seconds']:.1f}s")
        
        print("="*60)

# Usage in pipeline
if __name__ == "__main__":
    import time
    from pipeline_simple import MLPipeline
    
    monitor = PipelineMonitor()
    
    # Run pipeline with monitoring
    start_time = time.time()
    
    config = {
        'data_path': 'data/raw/customers.csv',
        'model_params': {'n_estimators': 100, 'max_depth': 10, 'random_state': 42}
    }
    
    pipeline = MLPipeline(config)
    result = pipeline.run()
    
    duration = time.time() - start_time
    
    # Log run
    monitor.log_run(
        pipeline_id='ml_training_v1',
        status=result['status'],
        metrics=result.get('metrics', {}),
        duration=duration
    )
    
    # Show report
    monitor.generate_report()
```

## Exercises

### Exercise 1: Add Parallel Processing
Modify pipeline to process multiple datasets in parallel:

```python
@flow
def parallel_training_flow(datasets: list):
    results = train_model.map(datasets)  # Parallel execution
    return results
```

### Exercise 2: Implement Checkpointing
Add checkpoints to resume failed pipelines:

```python
def checkpoint(step_name, data):
    joblib.dump(data, f'checkpoints/{step_name}.pkl')

def resume_from_checkpoint(step_name):
    return joblib.load(f'checkpoints/{step_name}.pkl')
```

### Exercise 3: Add Data Drift Detection
Check for data drift before training:

```python
@task
def check_data_drift(new_data, reference_data):
    # Compare distributions
    # Fail if significant drift detected
    pass
```

## Testing Airflow DAG

```bash
# Test tasks individually
airflow tasks test ml_training_pipeline extract_data 2024-01-01

# Run full DAG
airflow dags trigger ml_training_pipeline

# Monitor in UI
open http://localhost:8080
```

## Key Takeaways

✅ Pipelines ensure reproducibility and automation  
✅ Task dependencies prevent errors  
✅ Retries handle transient failures  
✅ Monitoring tracks pipeline health  
✅ Scheduling enables regular retraining

## Next Steps

- **Lab 04**: Model Registry for versioning
- **Lab 05**: Model Deployment with APIs
- Add more validation steps
- Implement A/B testing in pipeline

## Resources

- [Apache Airflow](https://airflow.apache.org/)
- [Prefect](https://www.prefect.io/)
- [Kedro](https://kedro.org/)
- [MLOps Pipeline Patterns](https://ml-ops.org/content/mlops-principles)
