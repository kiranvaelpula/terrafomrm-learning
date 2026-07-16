# Project 1: Simple CI/CD Pipeline

Build a complete CI/CD pipeline integrating Git, Docker, and Jenkins from scratch.

## 📋 Overview

This project demonstrates a basic but complete CI/CD workflow:
- **Source Control:** Git repository
- **Build & Test:** Automated testing
- **Containerization:** Docker image creation
- **CI/CD:** Jenkins pipeline automation
- **Deployment:** Automated container deployment

## 🎯 Learning Objectives

- Integrate Git, Docker, and Jenkins
- Build automated CI/CD pipelines
- Containerize applications
- Deploy with automation
- Understand end-to-end workflows

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   GitHub    │────▶│   Jenkins    │────▶│   Docker    │
│ Repository  │     │   Pipeline   │     │  Container  │
└─────────────┘     └──────────────┘     └─────────────┘
      │                     │                     │
      │                     │                     │
      ▼                     ▼                     ▼
  Git Webhook         Build & Test           Deployment
```

## 📁 Project Structure

```
project-01-simple-cicd/
├── README.md (this file)
├── app/
│   ├── app.py (Flask application)
│   ├── requirements.txt
│   └── test_app.py
├── Dockerfile
├── Jenkinsfile
├── docker-compose.yml
└── .gitignore
```

## 🚀 Quick Start

### Prerequisites

- Git installed
- Docker installed
- Jenkins running (see devops-essentials/03-jenkins/basics/)
- GitHub account

### Step 1: Clone Repository

```bash
# Clone this project
git clone <your-repo-url>
cd project-01-simple-cicd

# Or start fresh
mkdir simple-cicd-app && cd simple-cicd-app
git init
```

### Step 2: Create Application Files

See the `app/` directory for complete application code.

### Step 3: Setup Jenkins

1. Create new Pipeline job in Jenkins
2. Configure Git repository
3. Set up webhook (optional)
4. Point to Jenkinsfile in repo

### Step 4: Run Pipeline

```bash
# Push code to trigger build
git add .
git commit -m "Initial commit"
git push origin main

# Or trigger manually in Jenkins UI
```

## 📝 Detailed Setup Guide

### Application Code (app/app.py)

Simple Flask web application:

```python
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Hello from Simple CI/CD!',
        'version': os.getenv('APP_VERSION', '1.0.0'),
        'status': 'running'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Tests (app/test_app.py)

```python
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'healthy'
```

### Requirements (app/requirements.txt)

```
flask==2.3.0
pytest==7.3.1
gunicorn==20.1.0
```

### Dockerfile

```dockerfile
# Build stage
FROM python:3.9-slim as builder

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.9-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app/ .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

### Jenkinsfile

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'simple-cicd-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh '''
                    cd app
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'
                sh '''
                    cd app
                    pytest test_app.py -v
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }
        
        stage('Test Docker Image') {
            steps {
                echo 'Testing Docker image...'
                sh """
                    docker run -d --name test-${BUILD_NUMBER} -p 5001:5000 ${DOCKER_IMAGE}:${DOCKER_TAG}
                    sleep 5
                    curl -f http://localhost:5001/health || exit 1
                    docker stop test-${BUILD_NUMBER}
                    docker rm test-${BUILD_NUMBER}
                """
            }
        }
        
        stage('Tag Image') {
            steps {
                sh """
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                """
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh """
                    docker stop simple-cicd-app || true
                    docker rm simple-cicd-app || true
                    docker run -d --name simple-cicd-app -p 5000:5000 ${DOCKER_IMAGE}:${DOCKER_TAG}
                """
            }
        }
        
        stage('Verify Deployment') {
            steps {
                echo 'Verifying deployment...'
                sh '''
                    sleep 5
                    curl -f http://localhost:5000/health
                    echo "✅ Deployment successful!"
                '''
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo "Application running at: http://localhost:5000"
        }
        failure {
            echo '❌ Pipeline failed!'
            sh 'docker stop simple-cicd-app || true'
        }
        always {
            sh """
                docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true
            """
        }
    }
}
```

### Docker Compose (docker-compose.yml)

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: simple-cicd-app
    ports:
      - "5000:5000"
    environment:
      - APP_VERSION=1.0.0
    restart: unless-stopped
```

### .gitignore

```
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
*.log
.env
venv/
```

## 🔧 Configuration

### Jenkins Setup

1. **Install Required Plugins:**
   - Pipeline
   - Git
   - Docker Pipeline

2. **Create Pipeline Job:**
   - New Item → Pipeline
   - Name: simple-cicd-app
   - Pipeline script from SCM
   - SCM: Git
   - Repository URL: your-repo-url
   - Script Path: Jenkinsfile

3. **Configure Webhook (Optional):**
   - GitHub Settings → Webhooks
   - Payload URL: `http://jenkins-url/github-webhook/`
   - Content type: application/json
   - Events: Just the push event

### Docker Configuration

Ensure Docker is accessible to Jenkins:

```bash
# Add jenkins user to docker group
sudo usermod -aG docker jenkins

# Restart Jenkins
sudo systemctl restart jenkins
```

## 📊 Pipeline Stages Explained

### 1. Checkout
Pulls latest code from Git repository.

### 2. Install Dependencies
Installs Python packages required by application.

### 3. Run Tests
Executes pytest to validate application functionality.

### 4. Build Docker Image
Creates Docker image with application and dependencies.

### 5. Test Docker Image
Runs container and validates health endpoint.

### 6. Tag Image
Tags successful build as 'latest' for easy reference.

### 7. Deploy
Stops old container and starts new one with latest image.

### 8. Verify Deployment
Checks that deployed application responds correctly.

## 🧪 Testing

### Manual Testing

```bash
# Test application locally
cd app
python app.py

# In another terminal
curl http://localhost:5000/
curl http://localhost:5000/health

# Run tests
pytest test_app.py -v
```

### Docker Testing

```bash
# Build image
docker build -t simple-cicd-app:test .

# Run container
docker run -d -p 5000:5000 simple-cicd-app:test

# Test endpoints
curl http://localhost:5000/
curl http://localhost:5000/health

# View logs
docker logs simple-cicd-app

# Stop container
docker stop simple-cicd-app
```

### Using Docker Compose

```bash
# Start application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down
```

## 🐛 Troubleshooting

### Issue: Tests Fail

**Symptoms:** pytest fails during test stage

**Solution:**
```bash
# Check Python version
python --version

# Install dependencies
pip install -r app/requirements.txt

# Run tests manually
cd app && pytest test_app.py -v
```

### Issue: Docker Build Fails

**Symptoms:** Docker image build fails

**Solution:**
```bash
# Check Dockerfile syntax
docker build -t test .

# Build with no cache
docker build --no-cache -t simple-cicd-app .

# Check disk space
df -h
```

### Issue: Port Already in Use

**Symptoms:** Cannot bind to port 5000

**Solution:**
```bash
# Find process using port
lsof -i :5000

# Stop conflicting container
docker ps
docker stop <container-id>

# Use different port
docker run -p 5001:5000 simple-cicd-app
```

### Issue: Jenkins Cannot Access Docker

**Symptoms:** Permission denied while trying to connect to Docker daemon

**Solution:**
```bash
# Add jenkins to docker group
sudo usermod -aG docker jenkins

# Restart Jenkins
sudo systemctl restart jenkins

# Verify
sudo -u jenkins docker ps
```

## 📈 Enhancement Ideas

### 1. Add Code Quality Checks

```groovy
stage('Code Quality') {
    steps {
        sh 'pylint app/*.py || true'
        sh 'flake8 app/*.py || true'
    }
}
```

### 2. Add Security Scanning

```groovy
stage('Security Scan') {
    steps {
        sh 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image ${DOCKER_IMAGE}:${DOCKER_TAG}'
    }
}
```

### 3. Push to Docker Registry

```groovy
stage('Push to Registry') {
    steps {
        script {
            docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-creds') {
                dockerImage.push()
                dockerImage.push('latest')
            }
        }
    }
}
```

### 4. Add Notifications

```groovy
post {
    success {
        slackSend color: 'good', message: "Build ${BUILD_NUMBER} succeeded!"
    }
    failure {
        mail to: 'team@example.com', subject: "Build Failed: ${BUILD_NUMBER}"
    }
}
```

## ✅ Validation Checklist

- [ ] Application runs locally
- [ ] Tests pass
- [ ] Docker image builds successfully
- [ ] Container runs and responds to requests
- [ ] Jenkins pipeline executes without errors
- [ ] Deployment successful
- [ ] Health check passes

## 🎓 What You Learned

- ✅ Git repository setup and workflow
- ✅ Writing Dockerfile for Python application
- ✅ Creating Jenkins pipeline from scratch
- ✅ Integrating automated testing
- ✅ Building and deploying Docker containers
- ✅ End-to-end CI/CD workflow
- ✅ Troubleshooting integration issues

## 📚 Next Steps

1. **Extend the Application:**
   - Add database connection
   - Add more API endpoints
   - Implement caching

2. **Improve Pipeline:**
   - Add staging environment
   - Implement blue-green deployment
   - Add performance testing

3. **Move to Next Project:**
   - [Project 2: Microservices](../project-02-microservices/)

## 🔗 References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)

---

**Congratulations!** You've built your first complete CI/CD pipeline! 🎉

