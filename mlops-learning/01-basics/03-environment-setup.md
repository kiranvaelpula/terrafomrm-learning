# Development Environment Setup

## Learning Objectives
- Set up a complete MLOps development environment
- Install and configure essential ML tools
- Create reproducible environments
- Understand best practices for ML development

---

## 📖 Understanding Environment Setup (Intuition First)

Imagine a professional kitchen where every chef brings their own random set of knives, uses a different oven brand, and measures ingredients in whatever units they feel like. A dish that turns out perfectly for one chef would be a disaster when another tries to recreate it. Now picture a well-run restaurant: standardized equipment, calibrated ovens, the same measuring cups, a written mise en place. Anyone can step in and produce the same result. Setting up an MLOps environment is building that standardized kitchen for machine learning.

In ML, the "different ovens" problem is very real. Code that runs on your laptop can silently break on a teammate's machine or in production because of a different Python version, a mismatched library, or a package that got upgraded. This is the infamous "works on my machine" trap. The whole point of a deliberate environment setup is to make the environment itself reproducible — so the machine stops being a hidden variable in your experiments.

This is why the toolkit looks the way it does. **Virtual environments** (venv/conda) isolate each project's dependencies so they don't collide. **Pinned versions** in `requirements.txt` or `environment.yml` freeze the exact library versions so today's results survive tomorrow. **Docker** goes one level deeper, packaging the OS libraries too, so the whole environment travels intact from laptop to cloud. Each tool removes a different source of "it worked here but not there."

The rest of the stack maps directly onto the three artifacts MLOps cares about: **code, data, and models**. Git versions the code. DVC versions the data and model files that are too big for Git. MLflow tracks the experiments and models. Cloud CLIs connect it all to shared storage and compute. A consistent project structure ties them together so a newcomer can find things without asking.

The payoff is subtle but huge: reproducibility, fast onboarding, and fewer late-night debugging sessions chasing a bug that turns out to be a version mismatch. Investing an hour in setup up front saves days of confusion later — and it's the foundation everything else in MLOps is built on.

---

## Why Environment Setup Matters

A proper MLOps environment ensures:
- **Reproducibility**: Same results across different machines
- **Collaboration**: Team members use consistent tools
- **Efficiency**: Quick onboarding for new team members
- **Isolation**: Avoid dependency conflicts

---

## Essential Tools for MLOps

### Core Components
```
┌─────────────────────────────────────────┐
│  Development Environment                │
├─────────────────────────────────────────┤
│  • Python + Virtual Environments        │
│  • Jupyter Notebooks                    │
│  • Git + Version Control                │
│  • ML Libraries (sklearn, pandas, etc.) │
│  • MLflow (Experiment Tracking)         │
│  • Docker (Containerization)            │
│  • Cloud CLI (AWS/GCP/Azure)            │
└─────────────────────────────────────────┘
```

---

## Python Environment Setup

### Option 1: Using venv (Built-in)
```bash
# Create virtual environment
python -m venv mlops-env

# Activate (Linux/Mac)
source mlops-env/bin/activate

# Activate (Windows)
mlops-env\Scripts\activate

# Install packages
pip install numpy pandas scikit-learn matplotlib

# Save dependencies
pip freeze > requirements.txt

# Deactivate
deactivate
```

### Option 2: Using conda (Recommended)
```bash
# Install Miniconda
# Download from: https://docs.conda.io/en/latest/miniconda.html

# Create environment with specific Python version
conda create -n mlops-env python=3.9

# Activate environment
conda activate mlops-env

# Install packages
conda install numpy pandas scikit-learn matplotlib jupyter

# Or use pip for packages not in conda
pip install mlflow

# Export environment
conda env export > environment.yml

# Create from environment file
conda env create -f environment.yml

# Deactivate
conda deactivate
```

### environment.yml Example
```yaml
name: mlops-env
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.9
  - numpy=1.24.3
  - pandas=2.0.2
  - scikit-learn=1.3.0
  - matplotlib=3.7.1
  - jupyter=1.0.0
  - pip:
    - mlflow==2.4.1
    - dvc==2.58.0
```

---

## Installing ML Libraries

### Essential Libraries
```bash
# Data manipulation
pip install pandas numpy scipy

# Machine Learning
pip install scikit-learn xgboost lightgbm

# Deep Learning (choose one)
pip install tensorflow  # or
pip install torch torchvision

# Visualization
pip install matplotlib seaborn plotly

# MLOps Tools
pip install mlflow dvc

# Jupyter
pip install jupyter jupyterlab

# Testing
pip install pytest
```

### requirements.txt Example
```txt
# Core ML
numpy==1.24.3
pandas==2.0.2
scikit-learn==1.3.0

# Deep Learning
tensorflow==2.13.0
# torch==2.0.1

# Visualization
matplotlib==3.7.1
seaborn==0.12.2

# MLOps
mlflow==2.4.1
dvc==2.58.0

# Utilities
jupyter==1.0.0
pytest==7.4.0
```

---

## MLflow Setup

### Installation and Configuration
```bash
# Install MLflow
pip install mlflow

# Start MLflow tracking server
mlflow server --host 0.0.0.0 --port 5000

# Access UI at: http://localhost:5000
```

### Configure MLflow in Your Project
```python
# mlflow_config.py
import mlflow
import os

# Set tracking URI
mlflow.set_tracking_uri("http://localhost:5000")

# Or use local filesystem
# mlflow.set_tracking_uri("file:./mlruns")

# Set experiment
mlflow.set_experiment("my-ml-project")

# Example usage
with mlflow.start_run(run_name="baseline-model"):
    mlflow.log_param("model_type", "random_forest")
    mlflow.log_metric("accuracy", 0.85)
    mlflow.sklearn.log_model(model, "model")
```

---

## Docker Setup for MLOps

### Install Docker
```bash
# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verify installation
docker --version

# Run hello-world
docker run hello-world
```

### Create ML Development Container
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Jupyter port
EXPOSE 8888

# Start Jupyter
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
```

### Build and Run Container
```bash
# Build image
docker build -t mlops-dev:latest .

# Run container with volume mount
docker run -p 8888:8888 -v $(pwd):/app mlops-dev:latest

# Or use docker-compose
```

### docker-compose.yml Example
```yaml
version: '3.8'

services:
  jupyter:
    build: .
    ports:
      - "8888:8888"
    volumes:
      - .:/app
    environment:
      - JUPYTER_ENABLE_LAB=yes
  
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    volumes:
      - ./mlruns:/mlruns
    command: mlflow server --host 0.0.0.0 --backend-store-uri file:///mlruns
```

---

## Jupyter Notebook Setup

### Installation
```bash
# Install Jupyter
pip install jupyter jupyterlab

# Or with conda
conda install jupyter jupyterlab
```

### Launch Jupyter
```bash
# Start Jupyter Notebook
jupyter notebook

# Start JupyterLab (recommended)
jupyter lab

# With specific port
jupyter lab --port 8888

# Allow remote access
jupyter lab --ip=0.0.0.0 --no-browser
```

### Configure Jupyter
```bash
# Generate config file
jupyter lab --generate-config

# Edit config file
# ~/.jupyter/jupyter_lab_config.py

# Set password
jupyter lab password
```

### Useful Jupyter Extensions
```bash
# Install extensions
pip install jupyterlab-git
pip install jupyterlab-lsp
pip install python-lsp-server

# Enable extensions
jupyter labextension list
```

---

## Git and Version Control Setup

### Install Git
```bash
# Linux
sudo apt-get install git

# Mac
brew install git

# Windows
# Download from: https://git-scm.com/download/win

# Verify
git --version
```

### Configure Git
```bash
# Set user info
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch name
git config --global init.defaultBranch main

# Set default editor
git config --global core.editor "code --wait"

# View configuration
git config --list
```

### Initialize ML Project Repository
```bash
# Create new repo
git init

# Create .gitignore for ML projects
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Jupyter
.ipynb_checkpoints/
*.ipynb

# ML artifacts
*.pkl
*.h5
*.model
mlruns/
models/

# Data
data/raw/
data/processed/
*.csv
*.parquet

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
EOF

# First commit
git add .
git commit -m "Initial commit: MLOps project setup"
```

---

## DVC (Data Version Control) Setup

### Installation
```bash
# Install DVC
pip install dvc

# Install cloud storage support
pip install 'dvc[s3]'      # AWS S3
pip install 'dvc[gs]'      # Google Cloud Storage
pip install 'dvc[azure]'   # Azure Blob Storage
```

### Initialize DVC
```bash
# Initialize DVC in your repo
dvc init

# Add remote storage
dvc remote add -d myremote s3://my-bucket/dvc-storage

# Configure credentials
dvc remote modify myremote access_key_id YOUR_ACCESS_KEY
dvc remote modify myremote secret_access_key YOUR_SECRET_KEY
```

### Track Data with DVC
```bash
# Add data file to DVC
dvc add data/train.csv

# Git track the .dvc file
git add data/train.csv.dvc .gitignore
git commit -m "Add training data"

# Push data to remote storage
dvc push

# Pull data
dvc pull
```

---

## Cloud CLI Setup

### AWS CLI
```bash
# Install
pip install awscli

# Configure
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format

# Test
aws s3 ls
```

### Google Cloud SDK
```bash
# Install (Linux/Mac)
curl https://sdk.cloud.google.com | bash

# Initialize
gcloud init

# Authenticate
gcloud auth login

# Set project
gcloud config set project PROJECT_ID
```

### Azure CLI
```bash
# Install
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Set subscription
az account set --subscription SUBSCRIPTION_ID
```

---

## IDE Setup

### VS Code Configuration
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./mlops-env/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  },
  "jupyter.notebookFileRoot": "${workspaceFolder}"
}
```

### Recommended VS Code Extensions
- Python
- Jupyter
- GitLens
- Docker
- YAML
- Pylance

---

## Project Structure

### Standard MLOps Project Layout
```
my-ml-project/
├── .dvc/                   # DVC configuration
├── .git/                   # Git repository
├── data/
│   ├── raw/               # Original data
│   ├── processed/         # Cleaned data
│   └── train.csv.dvc      # DVC tracked file
├── notebooks/
│   ├── 01-exploration.ipynb
│   └── 02-modeling.ipynb
├── src/
│   ├── __init__.py
│   ├── data/
│   │   └── make_dataset.py
│   ├── features/
│   │   └── build_features.py
│   ├── models/
│   │   ├── train_model.py
│   │   └── predict_model.py
│   └── utils/
│       └── helpers.py
├── tests/
│   ├── test_data.py
│   └── test_model.py
├── models/                 # Saved models
├── mlruns/                 # MLflow experiments
├── .gitignore
├── requirements.txt
├── environment.yml
├── setup.py
├── README.md
└── Dockerfile
```

---

## Verification Checklist

Run these commands to verify your setup:

```bash
# Python
python --version  # Should be 3.8+

# Virtual environment
which python  # Should point to venv

# Packages
pip list | grep -E "pandas|scikit-learn|mlflow"

# MLflow
mlflow --version

# Docker
docker --version

# Git
git --version

# DVC
dvc version

# Cloud CLI (if needed)
aws --version
gcloud --version
az --version

# Jupyter
jupyter --version
```

---

## Quick Start Script

Create a setup script to automate environment creation:

```bash
#!/bin/bash
# setup_mlops_env.sh

echo "Setting up MLOps environment..."

# Create conda environment
conda create -n mlops-env python=3.9 -y
conda activate mlops-env

# Install packages
pip install -r requirements.txt

# Initialize DVC
dvc init

# Start MLflow
echo "Starting MLflow server..."
mlflow server --host 0.0.0.0 --port 5000 &

echo "✅ Environment setup complete!"
echo "Run: conda activate mlops-env"
echo "MLflow UI: http://localhost:5000"
```

---

## Troubleshooting

### Common Issues

**Issue: Package conflicts**
```bash
# Solution: Use fresh environment
conda deactivate
conda env remove -n mlops-env
conda create -n mlops-env python=3.9 -y
```

**Issue: MLflow not starting**
```bash
# Solution: Check if port is in use
lsof -i :5000
# Kill process if needed
kill -9 PID
```

**Issue: Jupyter kernel not found**
```bash
# Solution: Install ipykernel
pip install ipykernel
python -m ipykernel install --user --name mlops-env
```

---

## Best Practices

1. **Use virtual environments** - Always isolate project dependencies
2. **Pin versions** - Specify exact package versions
3. **Document setup** - Maintain clear README with setup instructions
4. **Automate** - Create setup scripts for reproducibility
5. **Use containers** - Docker for consistent environments
6. **Version data** - Use DVC for data and model versioning
7. **Track experiments** - Use MLflow from the start

---

## 🎯 Interview Quick Points

- The goal of environment setup is **reproducibility** — remove the machine as a hidden variable ("works on my machine")
- **Virtual environments** (venv/conda) isolate per-project dependencies to prevent version conflicts
- Always **pin exact versions** in `requirements.txt` / `environment.yml` so results are reproducible over time
- **conda** manages non-Python system deps too, which is why it's often preferred for ML over plain venv
- **Docker** packages the OS + libraries + code, guaranteeing the same environment from laptop to production
- **docker-compose** lets you run multi-service stacks (e.g., Jupyter + MLflow) together locally
- The stack maps to MLOps' three artifacts: **Git** (code), **DVC** (data + large model files), **MLflow** (experiments/models)
- **DVC** handles large files Git can't, storing them in remote object storage (S3/GCS/Azure) while Git tracks small `.dvc` pointers
- A **standard project structure** (data/, notebooks/, src/, tests/, models/) speeds onboarding and enforces separation of concerns
- **Cloud CLIs** (aws/gcloud/az) connect local work to shared storage and compute
- Automate setup with a **script** and verify with a checklist so onboarding is fast and consistent
- Time spent on setup up front prevents costly, hard-to-debug environment mismatches later

## Summary

You now have a complete MLOps development environment with:
- Python and virtual environments
- Essential ML libraries
- MLflow for experiment tracking
- Docker for containerization
- Git and DVC for version control
- Cloud CLI tools
- Proper project structure

---

**Next**: [First ML Pipeline →](04-first-ml-pipeline.md)
