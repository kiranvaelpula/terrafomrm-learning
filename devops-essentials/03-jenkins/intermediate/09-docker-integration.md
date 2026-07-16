# Docker Integration with Jenkins

## Overview

Docker integration enables Jenkins to build, test, and deploy containerized applications. This guide covers Docker-in-Docker, multi-stage builds, registry operations, and best practices for container-based CI/CD.

## Prerequisites

### Install Docker

**On Jenkins Server:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins

# Verify
docker --version
```

### Install Docker Plugin

```
Manage Jenkins → Manage Plugins → Available
Search: Docker Plugin, Docker Pipeline
Install without restart
```

**Essential Docker Plugins:**
- Docker Plugin
- Docker Pipeline Plugin
- Docker Commons Plugin
- Docker Build Step Plugin
- CloudBees Docker Build and Publish

## Docker in Jenkins Pipeline

### Method 1: Docker Agent

Run entire pipeline in Docker container:

```groovy
pipeline {
    agent {
        docker {
            image 'node:16-alpine'
            args '-v $HOME/.npm:/root/.npm'
        }
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'node --version'
                sh 'npm --version'
                sh 'npm install'
                sh 'npm run build'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
    }
}
```

### Method 2: Stage-Specific Docker Agent

Different containers for different stages:

```groovy
pipeline {
    agent none
    
    stages {
        stage('Build') {
            agent {
                docker {
                    image 'node:16'
                    reuseNode true
                }
            }
            steps {
                sh 'npm install && npm run build'
            }
        }
        
        stage('Test') {
            agent {
                docker {
                    image 'node:16-alpine'
                    reuseNode true
                }
            }
            steps {
                sh 'npm test'
            }
        }
        
        stage('Security Scan') {
            agent {
                docker {
                    image 'aquasec/trivy:latest'
                    reuseNode true
                }
            }
            steps {
                sh 'trivy fs .'
            }
        }
    }
}
```

### Method 3: Dockerfile Agent

Build custom image from Dockerfile:

```groovy
pipeline {
    agent {
        dockerfile {
            filename 'Dockerfile.build'
            dir 'build'
            additionalBuildArgs '--build-arg VERSION=1.0'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
    }
}
```

**Dockerfile.build:**
```dockerfile
FROM node:16
RUN npm install -g typescript
WORKDIR /app
```

## Building Docker Images

### Basic Docker Build

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'myapp'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Build Image') {
            steps {
                script {
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                }
            }
        }
        
        stage('Tag Image') {
            steps {
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
            }
        }
    }
}
```

### Using Docker Pipeline Plugin

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'myapp'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Build Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }
        
        stage('Test Image') {
            steps {
                script {
                    dockerImage.inside {
                        sh 'npm test'
                    }
                }
            }
        }
    }
}
```

### Multi-Stage Docker Build

**Dockerfile:**
```dockerfile
# Build stage
FROM node:16 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:16-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**Jenkinsfile:**
```groovy
pipeline {
    agent any
    
    environment {
        APP_NAME = 'myapp'
        VERSION = "1.0.${BUILD_NUMBER}"
    }
    
    stages {
        stage('Build') {
            steps {
                script {
                    dockerImage = docker.build(
                        "${APP_NAME}:${VERSION}",
                        "--build-arg VERSION=${VERSION} ."
                    )
                }
            }
        }
        
        stage('Verify') {
            steps {
                script {
                    dockerImage.inside {
                        sh 'node --version'
                        sh 'ls -la /app'
                    }
                }
            }
        }
    }
}
```

## Docker Registry Operations

### Push to Docker Hub

```groovy
pipeline {
    agent any
    
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        IMAGE_NAME = 'username/myapp'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Build') {
            steps {
                script {
                    dockerImage = docker.build("${IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }
        
        stage('Push') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials') {
                        dockerImage.push("${IMAGE_TAG}")
                        dockerImage.push("latest")
                    }
                }
            }
        }
    }
    
    post {
        always {
            sh "docker rmi ${IMAGE_NAME}:${IMAGE_TAG} || true"
            sh "docker rmi ${IMAGE_NAME}:latest || true"
        }
    }
}
```

### Push to Private Registry

```groovy
pipeline {
    agent any
    
    environment {
        REGISTRY = 'registry.company.com'
        IMAGE_NAME = 'myapp'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Build') {
            steps {
                script {
                    dockerImage = docker.build("${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }
        
        stage('Push') {
            steps {
                script {
                    docker.withRegistry("https://${REGISTRY}", 'registry-credentials') {
                        dockerImage.push("${IMAGE_TAG}")
                        dockerImage.push("latest")
                    }
                }
            }
        }
    }
}
```

### Push to AWS ECR

```groovy
pipeline {
    agent any
    
    environment {
        AWS_REGION = 'us-east-1'
        ECR_REGISTRY = '123456789.dkr.ecr.us-east-1.amazonaws.com'
        IMAGE_NAME = 'myapp'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Login to ECR') {
            steps {
                script {
                    sh """
                        aws ecr get-login-password --region ${AWS_REGION} | \\
                        docker login --username AWS --password-stdin ${ECR_REGISTRY}
                    """
                }
            }
        }
        
        stage('Build') {
            steps {
                script {
                    dockerImage = docker.build("${ECR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }
        
        stage('Push') {
            steps {
                script {
                    dockerImage.push("${IMAGE_TAG}")
                    dockerImage.push("latest")
                }
            }
        }
    }
}
```

### Push to Google Container Registry (GCR)

```groovy
pipeline {
    agent any
    
    environment {
        GCR_PROJECT = 'my-project'
        IMAGE_NAME = 'myapp'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Login to GCR') {
            steps {
                script {
                    sh 'gcloud auth configure-docker'
                }
            }
        }
        
        stage('Build and Push') {
            steps {
                script {
                    def imageName = "gcr.io/${GCR_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG}"
                    dockerImage = docker.build(imageName)
                    dockerImage.push()
                }
            }
        }
    }
}
```

## Docker-in-Docker (DinD)

### Jenkins with Docker Socket

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  jenkins:
    image: jenkins/jenkins:lts
    container_name: jenkins
    privileged: true
    user: root
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker
    environment:
      - DOCKER_HOST=unix:///var/run/docker.sock

volumes:
  jenkins_home:
```

### DinD Sidecar (Kubernetes)

```groovy
pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: docker
    image: docker:20-dind
    securityContext:
      privileged: true
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run
  - name: maven
    image: maven:3.8-openjdk-11
    command: ['cat']
    tty: true
    env:
    - name: DOCKER_HOST
      value: tcp://localhost:2375
  volumes:
  - name: docker-sock
    emptyDir: {}
            '''
        }
    }
    
    stages {
        stage('Build') {
            steps {
                container('maven') {
                    sh 'mvn package'
                }
            }
        }
        
        stage('Docker Build') {
            steps {
                container('docker') {
                    sh 'docker build -t myapp:latest .'
                }
            }
        }
    }
}
```

## Docker Compose in Jenkins

### Basic Docker Compose

```groovy
pipeline {
    agent any
    
    stages {
        stage('Start Services') {
            steps {
                sh 'docker-compose up -d'
                sh 'docker-compose ps'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'docker-compose exec -T app npm test'
            }
        }
        
        stage('Integration Tests') {
            steps {
                sh '''
                    docker-compose exec -T app npm run test:integration
                '''
            }
        }
    }
    
    post {
        always {
            sh 'docker-compose logs'
            sh 'docker-compose down -v'
        }
    }
}
```

### Dynamic Compose Files

```groovy
pipeline {
    agent any
    
    stages {
        stage('Generate Compose File') {
            steps {
                script {
                    def composeContent = """
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=${params.ENVIRONMENT}
      - VERSION=${BUILD_NUMBER}
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=testdb
                    """
                    writeFile file: 'docker-compose.yml', text: composeContent
                }
            }
        }
        
        stage('Deploy') {
            steps {
                sh 'docker-compose up -d'
            }
        }
    }
}
```

## Advanced Docker Operations

### Image Scanning with Trivy

```groovy
stage('Security Scan') {
    steps {
        script {
            sh """
                docker run --rm \\
                  -v /var/run/docker.sock:/var/run/docker.sock \\
                  aquasec/trivy:latest image \\
                  --severity HIGH,CRITICAL \\
                  --exit-code 1 \\
                  ${DOCKER_IMAGE}:${DOCKER_TAG}
            """
        }
    }
}
```

### Image Scanning with Anchore

```groovy
stage('Image Analysis') {
    steps {
        script {
            sh """
                docker run --rm \\
                  -v /var/run/docker.sock:/var/run/docker.sock \\
                  anchore/grype:latest \\
                  ${DOCKER_IMAGE}:${DOCKER_TAG}
            """
        }
    }
}
```

### Layer Caching

```groovy
stage('Build with Cache') {
    steps {
        script {
            sh """
                docker build \\
                  --cache-from ${DOCKER_IMAGE}:latest \\
                  --tag ${DOCKER_IMAGE}:${BUILD_NUMBER} \\
                  --tag ${DOCKER_IMAGE}:latest \\
                  .
            """
        }
    }
}
```

### BuildKit Features

```groovy
stage('BuildKit Build') {
    environment {
        DOCKER_BUILDKIT = '1'
    }
    steps {
        sh """
            docker build \\
              --progress=plain \\
              --secret id=npmrc,src=.npmrc \\
              --tag ${DOCKER_IMAGE}:${BUILD_NUMBER} \\
              .
        """
    }
}
```

## Real-World Examples

### Example 1: Node.js Application

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'registry.company.com'
        APP_NAME = 'nodejs-app'
        VERSION = "1.0.${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Application') {
            agent {
                docker {
                    image 'node:16'
                    reuseNode true
                }
            }
            steps {
                sh 'npm ci'
                sh 'npm run build'
                sh 'npm test'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_REGISTRY}/${APP_NAME}:${VERSION}")
                }
            }
        }
        
        stage('Scan Image') {
            steps {
                sh """
                    docker run --rm \\
                      -v /var/run/docker.sock:/var/run/docker.sock \\
                      aquasec/trivy:latest image \\
                      ${DOCKER_REGISTRY}/${APP_NAME}:${VERSION}
                """
            }
        }
        
        stage('Push Image') {
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'registry-creds') {
                        dockerImage.push("${VERSION}")
                        dockerImage.push("latest")
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                sh """
                    kubectl set image deployment/${APP_NAME} \\
                      ${APP_NAME}=${DOCKER_REGISTRY}/${APP_NAME}:${VERSION}
                """
            }
        }
    }
    
    post {
        always {
            sh "docker rmi ${DOCKER_REGISTRY}/${APP_NAME}:${VERSION} || true"
        }
    }
}
```

### Example 2: Java Spring Boot

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'springboot-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Build JAR') {
            agent {
                docker {
                    image 'maven:3.8-openjdk-11'
                    args '-v $HOME/.m2:/root/.m2'
                }
            }
            steps {
                sh 'mvn clean package -DskipTests'
                stash includes: 'target/*.jar', name: 'jar-file'
            }
        }
        
        stage('Test') {
            agent {
                docker {
                    image 'maven:3.8-openjdk-11'
                    args '-v $HOME/.m2:/root/.m2'
                }
            }
            steps {
                sh 'mvn test'
                junit 'target/surefire-reports/*.xml'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                unstash 'jar-file'
                script {
                    dockerImage = docker.build(
                        "${DOCKER_IMAGE}:${DOCKER_TAG}",
                        "--build-arg JAR_FILE=target/*.jar ."
                    )
                }
            }
        }
        
        stage('Push & Deploy') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub') {
                        dockerImage.push("${DOCKER_TAG}")
                        dockerImage.push("latest")
                    }
                }
            }
        }
    }
}
```

**Dockerfile:**
```dockerfile
FROM openjdk:11-jre-slim
ARG JAR_FILE
COPY ${JAR_FILE} app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

### Example 3: Python Flask API

```groovy
pipeline {
    agent any
    
    environment {
        IMAGE_NAME = 'flask-api'
        IMAGE_TAG = "${GIT_COMMIT.take(7)}"
    }
    
    stages {
        stage('Lint') {
            agent {
                docker {
                    image 'python:3.9'
                    reuseNode true
                }
            }
            steps {
                sh '''
                    pip install flake8
                    flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
                '''
            }
        }
        
        stage('Test') {
            agent {
                docker {
                    image 'python:3.9'
                    reuseNode true
                }
            }
            steps {
                sh '''
                    pip install -r requirements.txt
                    pytest tests/ --junit-xml=results.xml
                '''
                junit 'results.xml'
            }
        }
        
        stage('Build') {
            steps {
                script {
                    dockerImage = docker.build("${IMAGE_NAME}:${IMAGE_TAG}")
                }
            }
        }
        
        stage('Integration Test') {
            steps {
                script {
                    dockerImage.withRun('-p 5000:5000') { container ->
                        sh 'sleep 5'
                        sh 'curl http://localhost:5000/health'
                    }
                }
            }
        }
    }
}
```

## Best Practices

### 1. Use Multi-Stage Builds

```dockerfile
# Build stage
FROM node:16 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:16-alpine
WORKDIR /app
COPY --from=builder /app/dist ./
CMD ["node", "index.js"]
```

### 2. Minimize Image Size

```dockerfile
# Use alpine variants
FROM node:16-alpine

# Clean up in same layer
RUN apk add --no-cache python3 && \\
    npm install && \\
    apk del python3
```

### 3. Secure Credentials

```groovy
environment {
    DOCKER_CREDS = credentials('docker-credentials')
}

steps {
    sh 'echo $DOCKER_CREDS_PSW | docker login -u $DOCKER_CREDS_USR --password-stdin'
}
```

### 4. Clean Up Images

```groovy
post {
    always {
        sh '''
            docker system prune -f
            docker image prune -f
        '''
    }
}
```

### 5. Use .dockerignore

```.dockerignore
node_modules
.git
.env
*.md
tests
.dockerignore
Dockerfile
```

## Troubleshooting

### Issue: Permission Denied

**Solution:**
```bash
# Add jenkins user to docker group
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Issue: Docker Socket Not Found

**Solution:**
```yaml
# Mount docker socket
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

### Issue: Out of Disk Space

**Solution:**
```groovy
stage('Cleanup') {
    steps {
        sh '''
            docker system prune -af --volumes
            docker builder prune -af
        '''
    }
}
```

### Issue: Build Cache Not Working

**Solution:**
```groovy
sh """
    docker build \\
      --cache-from ${IMAGE}:latest \\
      --build-arg BUILDKIT_INLINE_CACHE=1 \\
      -t ${IMAGE}:${TAG} .
"""
```

## Summary

Comprehensive Docker integration with Jenkins enables:
- Containerized build environments
- Docker image building and testing
- Multi-registry support
- Security scanning
- Kubernetes deployment

**Key Points:**
- Use docker agents for consistent builds
- Implement multi-stage builds
- Scan images for vulnerabilities
- Clean up regularly
- Secure credentials properly

---

**Previous:** [← Git Integration](08-git-integration.md) | **Next:** [Testing in Pipelines →](10-testing.md)
