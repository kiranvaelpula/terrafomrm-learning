# Lab 5: Complete CI/CD Pipeline

Build a production-ready CI/CD pipeline integrating everything learned: Git, Docker, testing, security, deployment, and monitoring.

## Learning Objectives

- Design end-to-end CI/CD workflow
- Integrate testing at all levels
- Implement security scanning
- Deploy to multiple environments
- Add monitoring and notifications
- Handle rollbacks

## Prerequisites

- Labs 1-4 completed
- Kubernetes cluster (optional, can use Docker)
- Monitoring tools access
- Notification channels setup

## Lab Duration

**Estimated Time:** 90-120 minutes

---

## Exercise 1: Project Setup

**Objective:** Create complete application structure

```bash
# Create project
mkdir complete-cicd-app && cd complete-cicd-app

# Application code
cat > app.py <<'EOF'
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Hello from Complete CI/CD!',
        'version': os.getenv('APP_VERSION', '1.0.0'),
        'environment': os.getenv('ENVIRONMENT', 'dev')
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# Tests
cat > test_app.py <<'EOF'
import pytest
import app as application

@pytest.fixture
def client():
    application.app.config['TESTING'] = True
    with application.app.test_client() as client:
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
EOF

# Requirements
cat > requirements.txt <<'EOF'
flask==2.3.0
pytest==7.3.1
gunicorn==20.1.0
EOF

# Dockerfile
cat > Dockerfile <<'EOF'
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.9-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app.py .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
EOF

# Kubernetes manifests
mkdir -p k8s
cat > k8s/deployment.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cicd-app
  labels:
    app: cicd-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cicd-app
  template:
    metadata:
      labels:
        app: cicd-app
        version: "${VERSION}"
    spec:
      containers:
      - name: app
        image: ${DOCKER_IMAGE}:${VERSION}
        ports:
        - containerPort: 5000
        env:
        - name: APP_VERSION
          value: "${VERSION}"
        - name: ENVIRONMENT
          value: "${ENVIRONMENT}"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 3
---
apiVersion: v1
kind: Service
metadata:
  name: cicd-app
spec:
  selector:
    app: cicd-app
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
EOF

# Initialize Git
git init
git add .
git commit -m "Initial complete CI/CD setup"
```

✅ **Checkpoint:** Project structure created

---


## Exercise 2: Complete CI/CD Jenkinsfile

**Objective:** Production-grade pipeline

```groovy
@Library('shared-library') _

pipeline {
    agent any
    
    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'production'], description: 'Target environment')
        booleanParam(name: 'SKIP_TESTS', defaultValue: false, description: 'Skip test execution')
        booleanParam(name: 'SKIP_SECURITY_SCAN', defaultValue: false, description: 'Skip security scanning')
    }
    
    environment {
        APP_NAME = 'complete-cicd-app'
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_IMAGE = "${DOCKER_REGISTRY}/username/${APP_NAME}"
        VERSION = "${BUILD_NUMBER}"
        GIT_COMMIT_SHORT = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_MSG = sh(returnStdout: true, script: 'git log -1 --pretty=%B').trim()
                    env.GIT_AUTHOR = sh(returnStdout: true, script: 'git log -1 --pretty=%an').trim()
                }
                echo "Commit: ${GIT_COMMIT_SHORT}"
                echo "Message: ${GIT_COMMIT_MSG}"
                echo "Author: ${GIT_AUTHOR}"
            }
        }
        
        stage('Code Quality') {
            when {
                not { branch 'main' }
            }
            steps {
                sh '''
                    echo "Running linters..."
                    python -m py_compile app.py test_app.py
                    echo "✅ Code quality check passed"
                '''
            }
        }
        
        stage('Unit Tests') {
            when {
                expression { !params.SKIP_TESTS }
            }
            steps {
                sh '''
                    pip install -r requirements.txt
                    pytest test_app.py -v --junitxml=test-results.xml
                '''
                junit 'test-results.xml'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${VERSION}")
                    sh "docker tag ${DOCKER_IMAGE}:${VERSION} ${DOCKER_IMAGE}:${GIT_COMMIT_SHORT}"
                }
            }
        }
        
        stage('Security Scan') {
            when {
                expression { !params.SKIP_SECURITY_SCAN }
            }
            parallel {
                stage('Vulnerability Scan') {
                    steps {
                        sh """
                            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                              aquasec/trivy image \
                              --severity HIGH,CRITICAL \
                              --exit-code 0 \
                              ${DOCKER_IMAGE}:${VERSION}
                        """
                    }
                }
                
                stage('Secret Detection') {
                    steps {
                        sh '''
                            echo "Scanning for secrets..."
                            grep -r "password\|secret\|key" . --exclude-dir=.git || echo "No secrets found"
                        '''
                    }
                }
            }
        }
        
        stage('Integration Tests') {
            when {
                expression { !params.SKIP_TESTS }
            }
            steps {
                sh """
                    docker run -d --name test-container-${BUILD_NUMBER} -p 5001:5000 ${DOCKER_IMAGE}:${VERSION}
                    sleep 5
                    
                    # Test endpoints
                    curl -f http://localhost:5001/ || exit 1
                    curl -f http://localhost:5001/health || exit 1
                    
                    docker stop test-container-${BUILD_NUMBER}
                    docker rm test-container-${BUILD_NUMBER}
                """
            }
        }
        
        stage('Push to Registry') {
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'dockerhub-credentials') {
                        dockerImage.push()
                        dockerImage.push("${GIT_COMMIT_SHORT}")
                        
                        if (env.BRANCH_NAME == 'main') {
                            dockerImage.push('latest')
                        }
                    }
                }
            }
        }
        
        stage('Deploy to Dev') {
            when {
                expression { params.ENVIRONMENT == 'dev' || env.BRANCH_NAME == 'develop' }
            }
            steps {
                echo 'Deploying to development...'
                sh """
                    export VERSION=${VERSION}
                    export DOCKER_IMAGE=${DOCKER_IMAGE}
                    export ENVIRONMENT=dev
                    
                    envsubst < k8s/deployment.yaml | kubectl apply -f - -n dev || \
                    docker run -d --name ${APP_NAME}-dev -p 5000:5000 \
                      -e ENVIRONMENT=dev ${DOCKER_IMAGE}:${VERSION}
                """
            }
        }
        
        stage('Deploy to Staging') {
            when {
                expression { params.ENVIRONMENT == 'staging' || env.BRANCH_NAME == 'staging' }
            }
            steps {
                input message: 'Deploy to staging?', ok: 'Deploy'
                
                echo 'Deploying to staging...'
                sh """
                    export VERSION=${VERSION}
                    export DOCKER_IMAGE=${DOCKER_IMAGE}
                    export ENVIRONMENT=staging
                    
                    envsubst < k8s/deployment.yaml | kubectl apply -f - -n staging || \
                    docker run -d --name ${APP_NAME}-staging -p 5001:5000 \
                      -e ENVIRONMENT=staging ${DOCKER_IMAGE}:${VERSION}
                """
                
                // Smoke tests
                sh '''
                    sleep 10
                    curl -f http://staging-url/health || exit 1
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                allOf {
                    branch 'main'
                    expression { params.ENVIRONMENT == 'production' }
                }
            }
            steps {
                script {
                    // Multi-step approval
                    input(
                        message: '🚨 Deploy to PRODUCTION?',
                        ok: 'Yes, Deploy',
                        submitter: 'admin,prod-deployers',
                        parameters: [
                            string(name: 'APPROVER', description: 'Your name'),
                            text(name: 'REASON', description: 'Deployment reason')
                        ]
                    )
                    
                    echo "Approved by: ${APPROVER}"
                    echo "Reason: ${REASON}"
                    
                    // Blue-Green Deployment
                    sh """
                        # Get current version
                        CURRENT=\$(kubectl get service ${APP_NAME} -n production \
                          -o jsonpath='{.spec.selector.version}' || echo 'none')
                        
                        # Deploy new version (green)
                        export VERSION=${VERSION}
                        export DOCKER_IMAGE=${DOCKER_IMAGE}
                        export ENVIRONMENT=production
                        
                        envsubst < k8s/deployment.yaml | kubectl apply -f - -n production
                        
                        # Wait for rollout
                        kubectl rollout status deployment/${APP_NAME} -n production --timeout=5m
                        
                        # Switch traffic
                        kubectl patch service ${APP_NAME} -n production \
                          -p '{"spec":{"selector":{"version":"${VERSION}"}}}'
                        
                        echo "Switched from \$CURRENT to ${VERSION}"
                    """
                }
            }
        }
        
        stage('Post-Deployment Tests') {
            when {
                expression { params.ENVIRONMENT == 'production' }
            }
            steps {
                sh '''
                    echo "Running production smoke tests..."
                    
                    # Health check
                    for i in {1..5}; do
                        curl -f https://prod-url/health && break
                        sleep 5
                    done
                    
                    # Basic functionality
                    curl -f https://prod-url/ | grep -q "Hello"
                    
                    echo "✅ Production tests passed"
                '''
            }
        }
        
        stage('Performance Tests') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    echo "Running performance tests..."
                    
                    # Simple load test
                    for i in {1..100}; do
                        curl -s http://localhost:5000/ > /dev/null &
                    done
                    wait
                    
                    echo "✅ Performance tests completed"
                '''
            }
        }
    }
    
    post {
        always {
            // Archive artifacts
            archiveArtifacts artifacts: '*.xml', allowEmptyArchive: true
            
            // Cleanup
            sh """
                docker rmi ${DOCKER_IMAGE}:${VERSION} || true
                docker system prune -f || true
            """
        }
        
        success {
            script {
                def message = """
                    ✅ *Build Successful* #${BUILD_NUMBER}
                    
                    *Project:* ${APP_NAME}
                    *Branch:* ${env.BRANCH_NAME}
                    *Commit:* ${GIT_COMMIT_SHORT}
                    *Author:* ${GIT_AUTHOR}
                    *Environment:* ${params.ENVIRONMENT}
                    *Version:* ${VERSION}
                    
                    *Image:* ${DOCKER_IMAGE}:${VERSION}
                    
                    ${env.BUILD_URL}
                """.stripIndent()
                
                // Slack notification
                // slackSend(color: 'good', message: message)
                echo message
            }
        }
        
        failure {
            script {
                def message = """
                    ❌ *Build Failed* #${BUILD_NUMBER}
                    
                    *Project:* ${APP_NAME}
                    *Branch:* ${env.BRANCH_NAME}
                    *Commit:* ${GIT_COMMIT_SHORT}
                    
                    ${env.BUILD_URL}console
                """.stripIndent()
                
                // slackSend(color: 'danger', message: message)
                echo message
                
                // Rollback if production deployment failed
                if (params.ENVIRONMENT == 'production') {
                    echo "⚠️ Consider rollback to previous version"
                }
            }
        }
    }
}
```

✅ **Checkpoint:** Complete CI/CD pipeline created

---

## Exercise 3: Implement Monitoring

**Objective:** Add observability

### Add Prometheus Metrics

Update app.py:
```python
from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)

# Metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.route('/metrics')
def metrics():
    return generate_latest()

# Add to requirements.txt
# prometheus-client==0.16.0
```

### Monitoring Stage in Pipeline

```groovy
stage('Setup Monitoring') {
    steps {
        sh '''
            # Deploy Prometheus config
            kubectl apply -f monitoring/prometheus-config.yaml
            
            # Verify metrics endpoint
            curl http://localhost:5000/metrics
        '''
    }
}
```

✅ **Checkpoint:** Monitoring integrated

---

## Exercise 4: Implement Rollback

**Objective:** Quick recovery from failures

```groovy
stage('Rollback') {
    when {
        expression { currentBuild.result == 'FAILURE' && params.ENVIRONMENT == 'production' }
    }
    steps {
        script {
            def previousVersion = sh(
                returnStdout: true,
                script: 'kubectl rollout history deployment/${APP_NAME} -n production | tail -2 | head -1'
            ).trim()
            
            input message: "Rollback to ${previousVersion}?", ok: 'Rollback'
            
            sh """
                kubectl rollout undo deployment/${APP_NAME} -n production
                kubectl rollout status deployment/${APP_NAME} -n production
            """
            
            echo "✅ Rolled back to ${previousVersion}"
        }
    }
}
```

✅ **Checkpoint:** Rollback mechanism works

---

## Exercise 5: Multi-Environment Management

**Objective:** Handle dev/staging/prod

Create environment-specific configs:

```bash
# dev.env
REPLICAS=1
RESOURCES_CPU=100m
RESOURCES_MEMORY=128Mi

# staging.env
REPLICAS=2
RESOURCES_CPU=200m
RESOURCES_MEMORY=256Mi

# production.env
REPLICAS=5
RESOURCES_CPU=500m
RESOURCES_MEMORY=512Mi
```

Pipeline integration:
```groovy
stage('Load Environment Config') {
    steps {
        script {
            def config = readProperties file: "${params.ENVIRONMENT}.env"
            env.REPLICAS = config.REPLICAS
            env.RESOURCES_CPU = config.RESOURCES_CPU
            env.RESOURCES_MEMORY = config.RESOURCES_MEMORY
        }
    }
}
```

✅ **Checkpoint:** Environment-specific configurations work

---

## Validation

**Complete Pipeline Checklist:**

- [ ] Code checkout from Git
- [ ] Unit tests execute
- [ ] Docker image builds
- [ ] Security scanning completes
- [ ] Integration tests pass
- [ ] Image pushes to registry
- [ ] Dev deployment succeeds
- [ ] Staging requires approval
- [ ] Production requires approval
- [ ] Smoke tests run post-deployment
- [ ] Monitoring metrics available
- [ ] Notifications sent
- [ ] Rollback capability tested

---

## Troubleshooting

**Issue:** Deployment fails  
**Solution:** Check logs: `kubectl logs deployment/${APP_NAME}`

**Issue:** Tests failing  
**Solution:** Run tests locally first

**Issue:** Image push fails  
**Solution:** Verify registry credentials

---

## Summary

What you learned:
- ✅ Design complete CI/CD pipeline
- ✅ Integrate all testing levels
- ✅ Implement security scanning
- ✅ Deploy to multiple environments
- ✅ Add monitoring and observability
- ✅ Implement rollback mechanisms
- ✅ Handle approvals and governance
- ✅ Send notifications
- ✅ Manage environment-specific configs

**Congratulations!** You've built a production-ready CI/CD pipeline!

---

## Next Steps

- Explore Jenkins X or Tekton
- Implement GitOps with ArgoCD
- Add advanced monitoring (Grafana dashboards)
- Implement feature flags
- Add automated rollback triggers
- Explore service mesh (Istio)

---

**Previous:** [Docker Integration](../lab-04-docker-integration/)

**You've completed all Jenkins labs!** 🎉

