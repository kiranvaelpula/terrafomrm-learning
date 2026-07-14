# Data Versioning

## Overview

Data versioning tracks changes to datasets over time, enabling reproducibility and collaboration. It's Git for data.

## Why Version Data?

**The Problem:**
- Can't reproduce model from 6 months ago
- Don't know which data was used
- Data changes break models
- Team uses different datasets

**The Solution:**
- Every dataset has a version
- Models linked to data versions
- Reproducible training
- Easy rollback

## DVC (Data Version Control)

### Installation
```bash
pip install dvc
pip install dvc[s3]  # For S3 remote storage
```

### Basic Workflow

```bash
# 1. Initialize DVC
dvc init

# 2. Track data file
dvc add data/train.csv

# 3. Commit DVC file to Git
git add data/train.csv.dvc .gitignore
git commit -m "Add training data v1"

# 4. Setup remote storage
dvc remote add -d myremote s3://my-bucket/dvc-storage

# 5. Push data to remote
dvc push
```

### Version Control

```bash
# Update data
cp new_data.csv data/train.csv

# Track new version
dvc add data/train.csv
git add data/train.csv.dvc
git commit -m "Update training data v2"
git tag -a v2.0 -m "Data version 2.0"

# Push new version
dvc push
```

### Switching Versions

```bash
# Checkout old version
git checkout v1.0
dvc checkout

# Back to latest
git checkout main
dvc checkout
```

## DVC Pipelines

Define reproducible workflows:

```yaml
# dvc.yaml
stages:
  preprocess:
    cmd: python preprocess.py
    deps:
      - data/raw/train.csv
      - preprocess.py
    outs:
      - data/processed/train.csv

  train:
    cmd: python train.py
    deps:
      - data/processed/train.csv
      - train.py
    outs:
      - models/model.pkl
    metrics:
      - metrics/accuracy.json:
          cache: false
```

Run pipeline:
```bash
dvc repro  # Runs all stages
dvc dag    # Visualize pipeline
```

## Data Metrics

Track data statistics:

```python
import pandas as pd
import json

df = pd.read_csv('data/train.csv')

metrics = {
    'rows': len(df),
    'columns': len(df.columns),
    'missing_values': df.isnull().sum().sum(),
    'target_distribution': df['target'].value_counts().to_dict()
}

with open('data_metrics.json', 'w') as f:
    json.dump(metrics, f)
```

## Best Practices

✅ Version data with code  
✅ Use remote storage  
✅ Tag important versions  
✅ Document data changes  
✅ Automate with pipelines  
✅ Track data quality metrics

## Key Takeaways

✅ DVC versions data like Git versions code  
✅ Pipelines ensure reproducibility  
✅ Remote storage enables collaboration  
✅ Data and model versions linked  
✅ Essential for production ML

---

**Next:** [Model Monitoring & Observability](../03-advanced/13-model-monitoring.md)  
**Practice:** [Lab 02 - Data Versioning](../mlops-practice/lab-02-data-versioning/)
