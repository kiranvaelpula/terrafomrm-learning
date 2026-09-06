# Data Versioning

## Overview

Data versioning tracks changes to datasets over time, enabling reproducibility and collaboration. It's Git for data.

## 📖 Understanding Data Versioning (Intuition First)

Imagine trying to reproduce a science experiment, but the ingredients silently changed since last time — different purity, different batch, different supplier. You'd run the "same" experiment and get different results, with no way to explain why. In ML, the *data* is the ingredient, and it changes constantly. Data versioning is labeling and preserving each exact "batch" of data so you can always reproduce which data produced which model.

Here's the core problem: you version your code with Git, so you can always get back the exact code from six months ago. But if the data has changed since then, running that old code gives you a *different* model. Your reproducibility is only as good as your ability to recover the *exact data* used. Without data versioning, "reproducible ML" is a myth — you can rebuild the recipe but not the ingredients.

Why not just put data in Git? Because Git is built for text files measured in kilobytes, and ML datasets are gigabytes or terabytes of images, parquet files, and CSVs. Git chokes on large binary files. Tools like **DVC (Data Version Control)** solve this cleverly: they store a tiny *pointer* file in Git (which Git handles fine) while the actual large data lives in cheap object storage like S3. Git tracks *which version* of the data you're on; the storage holds the bytes. You get Git-like versioning without bloating your repo.

The payoff is threefold. **Reproducibility**: any past model can be recreated because you know its exact data. **Collaboration**: teammates pull the same data version instead of "works with my copy of the dataset." **Debugging**: when a model breaks, you can diff data versions to see what changed — often the culprit is a silent data shift, not the code. In regulated industries, data versioning is also a compliance requirement — you must prove what data trained a model that made a decision.

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

## 🎯 Interview Quick Points

- Data versioning = "Git for data" — track exact dataset versions over time
- Essential for reproducibility: same code + different data = different model
- Without it, "reproducible ML" is impossible — you can recover code but not the ingredients
- Can't just use Git — it chokes on GB/TB binary data files
- **DVC** stores a small pointer in Git while actual data lives in S3/object storage
- Git tracks *which version*; object storage holds the bytes
- Enables: reproducibility, team collaboration, and debugging via data diffs
- Often the cause of a broken model is a silent **data shift**, not code
- In regulated industries, data versioning is a **compliance requirement**
- Tools: DVC, Pachyderm, LakeFS, Delta Lake

**Next:** [Model Monitoring & Observability](../03-advanced/13-model-monitoring.md)  
**Practice:** [Lab 02 - Data Versioning](../mlops-practice/lab-02-data-versioning/)
