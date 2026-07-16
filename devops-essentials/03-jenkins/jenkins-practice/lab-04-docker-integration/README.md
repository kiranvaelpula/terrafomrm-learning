# Lab 4: Docker Integration

Master Docker integration with Jenkins for containerized builds and deployments.

## Learning Objectives

- Use Docker agents in pipelines
- Build Docker images in Jenkins
- Push images to registries
- Run multi-container tests
- Implement container-based CI/CD

## Prerequisites

- Labs 1-3 completed
- Docker installed on Jenkins host
- Docker Hub account (or other registry)

## Lab Duration

**Estimated Time:** 60-90 minutes

---

## Exercise 1: Configure Docker in Jenkins

**Objective:** Enable Docker for Jenkins

### Step 1: Install Docker Pipeline Plugin

**Manage Jenkins** > **Manage Plugins** > **Available**
- Search: "Docker Pipeline"
- Install and restart

### Step 2: Configure Docker

**Manage Jenkins** > **Configure System**
- Scroll to "Docker"
- Docker Builder: (configure if needed)

### Step 3: Test Docker Access

```groovy
pipeline {
    agent any
    stages {
        stage('Test Docker') {
            steps {
                sh 'docker --version'
                sh 'docker ps'
                sh 'docker images'
            }
        }
    }
}
```

✅ **Checkpoint:** Jenkins can execute Docker commands

---

## Exercise 2: Use Docker as Build Agent

**Objective:** Run builds in Docker containers

```groovy
pipeline {
    agent {
        docker {
            image 'node:16-alpine'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }
    
    stages {
        stage('Environment') {
            steps {
                sh 'node --version'
                sh 'npm --version'
                sh 'cat /etc/os-release'
            }
        }
        
        stage('Build') {
            steps {
                sh '''
                    echo '{"name":"test-app","version":"1.0.0"}' > package.json
                    npm install express
                    echo "console.log('Hello from Docker agent!')" > index.js
                    node index.js
                '''
            }
        }
    }
}
```

**Try different images:**
```groovy
// Python
agent {
    docker { image 'python:3.9-slim' }
}

// Maven
agent {
    docker { image 'maven:3.8-jdk-11' }
}

// Multiple containers
pipeline {
    agent none
    stages {
        stage('Build Java') {
            agent { docker 'maven:3.8-jdk-11' }
            steps { sh 'mvn --version' }
        }
        stage('Build Node') {
            agent { docker 'node:16' }
            steps { sh 'node --version' }
        }
    }
}
```

✅ **Checkpoint:** Docker agents provide clean build environments

---

## Exercise 3: Build Docker Images

**Objective:** Create Docker images in pipeline

### Create Sample Application

```bash
# Create app directory
mkdir docker-app && cd docker-app

# Create app.py
cat > app.py <<EOF
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Dockerized Flask App!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# Create requirements.txt
echo "flask==2.3.0" > requirements.txt

# Create Dockerfile
cat > Dockerfile <<EOF
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
EOF

# Create Jenkinsfile
cat > Jenkinsfile <<EOF
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
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }
        
        stage('Test Image') {
            steps {
                script {
                    docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").inside {
                        sh 'python --version'
                        sh 'pip list | grep -i flask'
                    }
                }
            }
        }
        
        stage('Tag Latest') {
            steps {
                sh """
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                """
            }
        }
    }
    
    post {
        always {
            sh 'docker images | grep ${DOCKER_IMAGE}'
        }
    }
}
EOF

# Initialize Git and push to repository
git init
git add .
git commit -m "Docker app"
git push
```

✅ **Checkpoint:** Docker images built successfully

---

## Exercise 4: Push to Docker Registry

**Objective:** Publish images to Docker Hub

### Step 1: Add Docker Hub Credentials

**Manage Jenkins** > **Manage Credentials**

Add:
- Kind: Username with password
- Username: Docker Hub username
- Password: Docker Hub password/token
- ID: dockerhub-credentials

### Step 2: Pipeline with Registry Push

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_IMAGE = 'YOUR_DOCKERHUB_USERNAME/myapp'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Build') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }
        
        stage('Test') {
            steps {
                script {
                    dockerImage.inside {
                        sh 'echo "Running tests inside container"'
                        sh 'python -c "import flask; print(flask.__version__)"'
                    }
                }
            }
        }
        
        stage('Push') {
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'dockerhub-credentials') {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }
        
        stage('Verify') {
            steps {
                sh """
                    docker pull ${DOCKER_IMAGE}:${DOCKER_TAG}
                    docker inspect ${DOCKER_IMAGE}:${DOCKER_TAG}
                """
            }
        }
    }
    
    post {
        always {
            sh """
                docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                docker rmi ${DOCKER_IMAGE}:latest || true
            """
        }
    }
}
```

✅ **Checkpoint:** Images pushed to Docker Hub

---

## Exercise 5: Multi-Stage Docker Builds

**Objective:** Optimize image sizes

### Create Multi-Stage Dockerfile

```dockerfile
# Build stage
FROM node:16 AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage
FROM node:16-alpine

WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Pipeline for Multi-Stage Build

```groovy
pipeline {
    agent any
    
    stages {
        stage('Build Multi-Stage') {
            steps {
                script {
                    // Build with build args
                    def buildArgs = "--build-arg NODE_ENV=production"
                    sh """
                        docker build ${buildArgs} \
                          -t myapp:optimized \
                          -f Dockerfile .
                    """
                    
                    // Compare sizes
                    sh """
                        echo "Regular build:"
                        docker images myapp:${BUILD_NUMBER}
                        echo "Optimized build:"
                        docker images myapp:optimized
                    """
                }
            }
        }
    }
}
```

✅ **Checkpoint:** Multi-stage builds reduce image size

---

## Exercise 6: Docker Compose in Pipeline

**Objective:** Test with multiple containers

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://db:5432/mydb
    depends_on:
      - db
      
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_PASSWORD=secret
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

### Pipeline with Docker Compose

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
        
        stage('Wait for Services') {
            steps {
                sh '''
                    echo "Waiting for services..."
                    sleep 10
                    docker-compose logs
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    # Test web service
                    docker-compose exec -T web curl http://localhost:5000/health || true
                    
                    # Test database
                    docker-compose exec -T db pg_isready
                '''
            }
        }
        
        stage('Integration Tests') {
            steps {
                sh '''
                    docker-compose exec -T web python -m pytest tests/
                '''
            }
        }
    }
    
    post {
        always {
            sh '''
                docker-compose logs
                docker-compose down -v
            '''
        }
    }
}
```

✅ **Checkpoint:** Multi-container testing works

---

## Exercise 7: Complete Docker CI/CD Pipeline

**Objective:** End-to-end containerized workflow

```groovy
pipeline {
    agent any
    
    environment {
        APP_NAME = 'myapp'
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_IMAGE = "${DOCKER_REGISTRY}/username/${APP_NAME}"
        VERSION = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            agent {
                docker {
                    image 'maven:3.8-jdk-11'
                    args '-v $HOME/.m2:/root/.m2'
                }
            }
            steps {
                sh 'mvn clean package -DskipTests'
                stash name: 'artifact', includes: 'target/*.jar'
            }
        }
        
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    agent { docker 'maven:3.8-jdk-11' }
                    steps {
                        unstash 'artifact'
                        sh 'mvn test'
                    }
                }
                
                stage('Integration Tests') {
                    agent { docker 'maven:3.8-jdk-11' }
                    steps {
                        unstash 'artifact'
                        sh 'mvn verify -P integration-tests'
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                unstash 'artifact'
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${VERSION}")
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                sh """
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                      aquasec/trivy image --severity HIGH,CRITICAL \
                      ${DOCKER_IMAGE}:${VERSION}
                """
            }
        }
        
        stage('Push Image') {
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'dockerhub-credentials') {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                sh """
                    docker stop ${APP_NAME} || true
                    docker rm ${APP_NAME} || true
                    docker run -d \
                      --name ${APP_NAME} \
                      -p 8080:8080 \
                      ${DOCKER_IMAGE}:${VERSION}
                """
                
                // Verify deployment
                sh '''
                    sleep 5
                    curl -f http://localhost:8080/health || exit 1
                '''
            }
        }
    }
    
    post {
        success {
            echo "✅ Docker CI/CD completed successfully!"
            echo "Image: ${DOCKER_IMAGE}:${VERSION}"
        }
        failure {
            sh "docker stop ${APP_NAME} || true"
        }
    }
}
```

✅ **Checkpoint:** Complete CI/CD pipeline with Docker

---

## Validation

Verify all Docker operations:

```bash
# 1. Images built
docker images | grep myapp

# 2. Containers running
docker ps | grep myapp

# 3. Registry access
docker pull YOUR_USERNAME/myapp:latest

# 4. Cleanup
docker system prune -af
```

---

## Troubleshooting

**Issue:** Permission denied for Docker socket  
**Solution:**
```bash
# Add jenkins user to docker group
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

**Issue:** Image build fails  
**Solution:** Check Dockerfile syntax and build context

**Issue:** Registry push fails  
**Solution:** Verify credentials and network access

---

## Summary

What you learned:
- ✅ Use Docker as build agents
- ✅ Build Docker images in pipelines
- ✅ Push to Docker registries
- ✅ Implement multi-stage builds
- ✅ Use Docker Compose for testing
- ✅ Create complete CI/CD with containers
- ✅ Perform security scans

---

**Previous:** [Git Integration](../lab-03-git-integration/) | **Next:** [Complete CI/CD](../lab-05-complete-cicd/)

