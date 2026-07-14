# MLOps Practice Labs

Hands-on exercises to build practical MLOps skills with real-world ML projects.

## 🎯 Overview

This directory contains practical labs covering the complete ML lifecycle from experimentation to production deployment.

## 📚 Lab Structure

### Lab 1: Experiment Tracking & Versioning
**Duration**: 45 minutes  
**Skills**: MLflow, experiment management  
**Folder**: `lab-01-experiment-tracking/`

### Lab 2: Data Versioning with DVC
**Duration**: 45 minutes  
**Skills**: DVC, data pipelines, reproducibility  
**Folder**: `lab-02-data-versioning/`

### Lab 3: ML Pipeline Automation
**Duration**: 1.5 hours  
**Skills**: Pipeline orchestration, automation  
**Folder**: `lab-03-ml-pipeline/`

### Lab 4: Model Registry & Versioning
**Duration**: 1 hour  
**Skills**: Model management, staging, production  
**Folder**: `lab-04-model-registry/`

### Lab 5: Model Deployment
**Duration**: 1.5 hours  
**Skills**: REST APIs, containerization, serving  
**Folder**: `lab-05-model-deployment/`

### Lab 6: Model Monitoring
**Duration**: 1 hour  
**Skills**: Performance tracking, drift detection  
**Folder**: `lab-06-model-monitoring/`

### Lab 7: CI/CD for ML
**Duration**: 1.5 hours  
**Skills**: Automated training, testing, deployment  
**Folder**: `lab-07-cicd-ml/`

### Lab 8: Feature Store
**Duration**: 1 hour  
**Skills**: Feast, feature engineering, serving  
**Folder**: `lab-08-feature-store/`

### Lab 9: A/B Testing
**Duration**: 1 hour  
**Skills**: Model comparison, gradual rollout  
**Folder**: `lab-09-ab-testing/`

### Lab 10: End-to-End Project
**Duration**: 4 hours  
**Skills**: Complete MLOps pipeline  
**Folder**: `lab-10-e2e-project/`

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Navigate to a lab
cd lab-01-experiment-tracking

# Read instructions
cat README.md

# Run exercises
jupyter notebook exercises.ipynb

# Verify your work
python verify.py
```

## 📋 Prerequisites

- Python 3.8+
- Docker
- Git
- Jupyter Notebook
- Basic ML knowledge (scikit-learn)

## 🛠️ Required Tools

Install all tools at once:

```bash
# Core MLOps tools
pip install mlflow dvc[s3] scikit-learn pandas numpy
pip install jupyter notebook matplotlib seaborn

# Model serving
pip install fastapi uvicorn bentoml

# Monitoring
pip install evidently whylabs-client

# Feature store
pip install feast

# Additional utilities
pip install click pytest black flake8
```

## 📊 Sample Dataset

All labs use the **Customer Churn Prediction** dataset:
- 10,000 customer records
- Features: demographics, usage patterns, support calls
- Target: Churn (Yes/No)
- Located in: `data/customer-churn.csv`

## 🏗️ Project Structure

```
mlops-practice/
├── data/                      # Datasets
│   ├── raw/                  # Original data
│   ├── processed/            # Cleaned data
│   └── customer-churn.csv    # Sample dataset
├── notebooks/                 # Jupyter notebooks
│   ├── exploration.ipynb
│   └── training.ipynb
├── src/
│   ├── data/                 # Data processing
│   ├── features/             # Feature engineering
│   ├── models/               # Model code
│   ├── serving/              # API code
│   └── monitoring/           # Monitoring code
├── models/                    # Trained models
├── mlruns/                    # MLflow tracking
├── tests/                     # Unit tests
└── lab-XX-*/                  # Individual labs
```

## 🏆 Completion Checklist

Track your progress:

- [ ] Lab 1: Experiment Tracking & Versioning
- [ ] Lab 2: Data Versioning with DVC
- [ ] Lab 3: ML Pipeline Automation
- [ ] Lab 4: Model Registry & Versioning
- [ ] Lab 5: Model Deployment
- [ ] Lab 6: Model Monitoring
- [ ] Lab 7: CI/CD for ML
- [ ] Lab 8: Feature Store
- [ ] Lab 9: A/B Testing
- [ ] Lab 10: End-to-End Project

## 🎓 Learning Path

**Beginner** (Start here):
1. Lab 1: Experiment Tracking
2. Lab 2: Data Versioning
3. Lab 4: Model Registry

**Intermediate**:
4. Lab 3: ML Pipeline
5. Lab 5: Model Deployment
6. Lab 6: Model Monitoring

**Advanced**:
7. Lab 7: CI/CD for ML
8. Lab 8: Feature Store
9. Lab 9: A/B Testing
10. Lab 10: End-to-End Project

## 📈 Success Metrics

After completing these labs, you should be able to:

✅ Track experiments systematically  
✅ Version data and models  
✅ Build automated ML pipelines  
✅ Deploy models to production  
✅ Monitor model performance  
✅ Detect and handle data drift  
✅ Implement CI/CD for ML  
✅ Use feature stores effectively  
✅ Run A/B tests on models  

## 🎓 Certification Prep

These labs align with:
- **AWS Certified Machine Learning - Specialty**
- **Google Professional Machine Learning Engineer**
- **Microsoft Azure AI Engineer Associate**
- **MLOps Professional Certification** (Linux Foundation)

## 📖 Additional Resources

- [MLflow Documentation](https://mlflow.org/docs/latest/)
- [DVC Documentation](https://dvc.org/doc)
- [MLOps Principles](https://ml-ops.org/)
- [Google MLOps Guide](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

## 🤝 Contributing

Found an issue or want to add a lab? See `CONTRIBUTING.md`

## 📝 License

These practice materials are for educational purposes.
