# Lab 02: Data Versioning with DVC

## Overview
Learn to version control datasets, track data pipelines, and ensure reproducibility using Data Version Control (DVC).

**Duration:** 45-60 minutes  
**Difficulty:** Beginner  
**Prerequisites:** Git basics, Python

## Learning Objectives
- Version large datasets with DVC
- Track data transformations
- Share data with remote storage
- Reproduce data pipelines
- Handle data dependencies

## Why Data Versioning?

```
Problem: "Model performance dropped!"
Question: "Which version of the data was used?"
Answer: ??? (without versioning)

With DVC: Exact data version tracked with code
```

## Setup

### 1. Install DVC

```bash
pip install dvc dvc-s3  # or dvc-gs, dvc-azure
```

### 2. Initialize DVC

```bash
# Create project
mkdir ml-project
cd ml-project
git init
dvc init

# Verify
git status  # You'll see .dvc/ files
```

### 3. Sample Data

Create `scripts/generate_data.py`:

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_customer_data(n_samples=10000):
    """Generate synthetic customer churn dataset"""
    np.random.seed(42)
    
    # Generate features
    data = {
        'customer_id': [f'C{i:06d}' for i in range(n_samples)],
        'age': np.random.randint(18, 80, n_samples),
        'tenure_months': np.random.randint(1, 72, n_samples),
        'monthly_charges': np.random.uniform(20, 120, n_samples),
        'total_charges': np.random.uniform(100, 8000, n_samples),
        'contract_type': np.random.choice(['Month-to-month', 'One year', 'Two year'], n_samples),
        'payment_method': np.random.choice(['Electronic check', 'Mailed check', 'Bank transfer', 'Credit card'], n_samples),
        'internet_service': np.random.choice(['DSL', 'Fiber optic', 'No'], n_samples),
        'online_security': np.random.choice(['Yes', 'No', 'No internet'], n_samples),
        'tech_support': np.random.choice(['Yes', 'No', 'No internet'], n_samples),
        'num_support_calls': np.random.poisson(2, n_samples),
        'satisfaction_score': np.random.randint(1, 6, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Generate target (churn) based on features
    churn_prob = (
        0.05 * (df['tenure_months'] < 12) +
        0.03 * (df['contract_type'] == 'Month-to-month') +
        0.02 * (df['num_support_calls'] > 3) +
        0.02 * (df['satisfaction_score'] < 3) +
        0.01 * (df['monthly_charges'] > 80)
    )
    
    df['churn'] = (np.random.random(n_samples) < churn_prob).astype(int)
    
    return df

if __name__ == "__main__":
    # Generate data
    df = generate_customer_data(10000)
    
    # Save to CSV
    df.to_csv('data/raw/customers.csv', index=False)
    print(f"✅ Generated {len(df)} customer records")
    print(f"   Churn rate: {df['churn'].mean():.2%}")
    print(f"   File size: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
```

Run it:
```bash
mkdir -p data/raw
python scripts/generate_data.py
```

## Implementation

### Step 1: Track Data with DVC

```bash
# Add data file to DVC
dvc add data/raw/customers.csv

# This creates:
# - data/raw/customers.csv.dvc (metadata)
# - data/raw/.gitignore (ignores actual data)

# Commit DVC file (not the actual data)
git add data/raw/customers.csv.dvc data/raw/.gitignore
git commit -m "Add raw customer data v1"
```

What just happened?
- DVC created a hash of your data
- Actual data stays in `.dvc/cache/`
- Only metadata is tracked in Git
- Data file is in `.gitignore`

### Step 2: Create Data Processing Pipeline

Create `src/preprocess.py`:

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import yaml

def load_config(config_path='params.yaml'):
    """Load configuration"""
    with open(config_path) as f:
        return yaml.safe_load(f)

def preprocess_data(input_path, output_path, config):
    """Preprocess raw data"""
    print(f"📥 Loading data from {input_path}")
    df = pd.read_csv(input_path)
    
    # Handle missing values
    df = df.dropna()
    
    # Encode categorical variables
    categorical_cols = df.select_dtypes(include=['object']).columns
    categorical_cols = [col for col in categorical_cols if col != 'customer_id']
    
    le = LabelEncoder()
    for col in categorical_cols:
        df[col] = le.fit_transform(df[col])
    
    # Scale numerical features
    numerical_cols = ['age', 'tenure_months', 'monthly_charges', 
                      'total_charges', 'num_support_calls', 'satisfaction_score']
    
    scaler = StandardScaler()
    df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
    
    # Split features and target
    X = df.drop(['customer_id', 'churn'], axis=1)
    y = df['churn']
    
    # Save processed data
    processed_df = pd.concat([X, y], axis=1)
    processed_df.to_csv(output_path, index=False)
    
    # Save preprocessing artifacts
    joblib.dump(scaler, 'models/scaler.pkl')
    
    print(f"✅ Processed {len(df)} records")
    print(f"   Features: {len(X.columns)}")
    print(f"   Saved to: {output_path}")
    
    return processed_df

if __name__ == "__main__":
    config = load_config()
    
    preprocess_data(
        input_path='data/raw/customers.csv',
        output_path='data/processed/customers_processed.csv',
        config=config
    )
```

Create `params.yaml`:

```yaml
preprocess:
  missing_value_strategy: drop
  scaling_method: standard

train:
  model_type: random_forest
  test_size: 0.2
  random_state: 42
  
  hyperparameters:
    n_estimators: 100
    max_depth: 10
    min_samples_split: 5
```

### Step 3: Define DVC Pipeline

Create `dvc.yaml`:

```yaml
stages:
  preprocess:
    cmd: python src/preprocess.py
    deps:
      - data/raw/customers.csv
      - src/preprocess.py
    params:
      - preprocess
    outs:
      - data/processed/customers_processed.csv
      - models/scaler.pkl

  train:
    cmd: python src/train.py
    deps:
      - data/processed/customers_processed.csv
      - src/train.py
    params:
      - train
    outs:
      - models/model.pkl
    metrics:
      - metrics/train_metrics.json:
          cache: false
```

Create `src/train.py`:

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import json
import yaml

def load_config(config_path='params.yaml'):
    with open(config_path) as f:
        return yaml.safe_load(f)

def train_model(data_path, config):
    """Train classification model"""
    print(f"📊 Training model...")
    
    # Load data
    df = pd.read_csv(data_path)
    X = df.drop('churn', axis=1)
    y = df['churn']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=config['train']['test_size'],
        random_state=config['train']['random_state']
    )
    
    # Train model
    model = RandomForestClassifier(
        **config['train']['hyperparameters'],
        random_state=config['train']['random_state']
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    
    metrics = {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred)),
        'recall': float(recall_score(y_test, y_pred)),
        'f1_score': float(f1_score(y_test, y_pred)),
        'train_size': len(X_train),
        'test_size': len(X_test)
    }
    
    # Save model
    joblib.dump(model, 'models/model.pkl')
    
    # Save metrics
    with open('metrics/train_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✅ Model trained")
    print(f"   Accuracy: {metrics['accuracy']:.4f}")
    print(f"   F1 Score: {metrics['f1_score']:.4f}")
    
    return model, metrics

if __name__ == "__main__":
    config = load_config()
    train_model('data/processed/customers_processed.csv', config)
```

### Step 4: Run DVC Pipeline

```bash
# Create directories
mkdir -p data/processed models metrics src

# Run the entire pipeline
dvc repro

# What happens:
# 1. DVC checks which stages need to run
# 2. Runs preprocess stage
# 3. Runs train stage
# 4. Caches all outputs
```

### Step 5: Version Everything

```bash
# Add pipeline and outputs to DVC
git add dvc.yaml dvc.lock params.yaml
git add src/preprocess.py src/train.py
git commit -m "Add ML pipeline v1"

# Your data and models are versioned!
```

### Step 6: Setup Remote Storage

```bash
# Add remote storage (S3 example)
dvc remote add -d myremote s3://my-bucket/dvc-storage

# Or use local directory for testing
dvc remote add -d myremote /tmp/dvc-storage

# Push data to remote
dvc push

# Now your data is backed up!
```

## Common Workflows

### Update Dataset

```bash
# Get new data
python scripts/generate_data.py  # with new parameters

# Track new version
dvc add data/raw/customers.csv

# Reproduce pipeline with new data
dvc repro

# Commit changes
git add data/raw/customers.csv.dvc dvc.lock
git commit -m "Update dataset to v2"
git tag -a "data-v2" -m "Dataset version 2"
```

### Switch Between Data Versions

```bash
# List versions
git log --oneline

# Checkout old version
git checkout data-v1
dvc checkout

# Back to latest
git checkout main
dvc checkout
```

### Share Your Work

```bash
# Collaborator clones repo
git clone <repo-url>
cd ml-project

# Pull data from remote
dvc pull

# Reproduce results
dvc repro
```

### Compare Pipeline Runs

```bash
# Show metrics across commits
dvc metrics show

# Compare two versions
dvc metrics diff HEAD~1 HEAD

# Show parameters
dvc params diff HEAD~1 HEAD
```

## Advanced: Data Registry

Create separate repo for datasets:

```bash
# Create data registry
mkdir data-registry
cd data-registry
git init
dvc init

# Add datasets
dvc add datasets/customers-v1.csv
dvc add datasets/customers-v2.csv
dvc push

git add -A
git commit -m "Add customer datasets"
git push
```

Use in ML project:

```bash
# Import data from registry
dvc import https://github.com/myorg/data-registry \
    datasets/customers-v1.csv \
    -o data/raw/customers.csv

# Update when registry changes
dvc update data/raw/customers.csv.dvc
```

## Exercises

### Exercise 1: Create Data Transformation
Add a feature engineering stage to the pipeline:

```python
# src/feature_engineering.py
def create_features(df):
    # Add derived features
    df['charges_per_month'] = df['total_charges'] / df['tenure_months']
    df['is_high_value'] = (df['monthly_charges'] > df['monthly_charges'].median()).astype(int)
    return df
```

Add to `dvc.yaml` and run.

### Exercise 2: Track Experiments
Change hyperparameters in `params.yaml` and run multiple experiments:

```bash
# Experiment 1
dvc repro
git add . && git commit -m "Exp 1: n_estimators=100"

# Experiment 2
# Edit params.yaml
dvc repro
git add . && git commit -m "Exp 2: n_estimators=200"

# Compare
dvc metrics diff HEAD~1 HEAD
```

### Exercise 3: Data Validation
Add data quality checks:

```python
# src/validate_data.py
def validate_data(df):
    assert df['age'].between(18, 100).all(), "Invalid ages"
    assert df['churn'].isin([0, 1]).all(), "Invalid churn values"
    assert df.isnull().sum().sum() == 0, "Missing values found"
    print("✅ Data validation passed")
```

## Key Commands Reference

```bash
# Tracking
dvc add <file>           # Track file with DVC
dvc push                 # Upload to remote storage
dvc pull                 # Download from remote storage

# Pipeline
dvc run                  # Run single stage
dvc repro                # Reproduce entire pipeline
dvc dag                  # Show pipeline DAG

# Versioning
dvc checkout             # Checkout data for current Git version
dvc diff                 # Show changes in data

# Metrics
dvc metrics show         # Show all metrics
dvc metrics diff         # Compare metrics between versions
dvc params show          # Show parameters
dvc params diff          # Compare parameters
```

## Best Practices

✅ **Always version data with code** - Commit `.dvc` files with code changes  
✅ **Use remote storage** - Don't rely on local cache only  
✅ **Tag important versions** - Use Git tags for datasets  
✅ **Document changes** - Add meaningful commit messages  
✅ **Validate data** - Add quality checks in pipeline  
✅ **Keep data immutable** - Create new versions, don't modify existing  

## Validation

Test your setup:

```bash
# Check pipeline status
dvc status

# Validate pipeline
dvc dag

# Verify remote
dvc remote list

# Test reproduction
dvc repro --dry
```

## Troubleshooting

**Issue:** `dvc repro` doesn't run stages  
**Solution:** Stages are cached. Use `dvc repro -f` to force run

**Issue:** Large files slow down Git  
**Solution:** Ensure files are in `.gitignore` and only `.dvc` files are committed

**Issue:** `dvc push` fails  
**Solution:** Check remote configuration with `dvc remote list -v`

## Key Takeaways

✅ DVC versions data like Git versions code  
✅ Pipelines ensure reproducibility  
✅ Remote storage enables collaboration  
✅ Metrics tracking shows model evolution  
✅ Data dependencies prevent stale outputs

## Next Steps

- **Lab 03**: ML Pipeline Automation with orchestration tools
- **Lab 04**: Model Registry for production deployment
- Explore DVC experiments: `dvc exp run`
- Set up CI/CD with DVC

## Resources

- [DVC Documentation](https://dvc.org/doc)
- [DVC Tutorial](https://dvc.org/doc/start)
- [Iterative.ai Blog](https://iterative.ai/blog)
