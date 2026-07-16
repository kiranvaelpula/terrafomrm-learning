# Blue Ocean - Modern Jenkins UI

## Overview

Blue Ocean is Jenkins' modern, intuitive user interface designed to make CI/CD more accessible. It provides a visual pipeline editor, better pipeline visualization, and improved user experience compared to the classic Jenkins UI.

## Why Blue Ocean?

### Classic UI vs Blue Ocean

| Feature | Classic UI | Blue Ocean |
|---------|-----------|------------|
| **Pipeline Visualization** | Text-based logs | Visual pipeline flow |
| **Pipeline Editor** | Manual Jenkinsfile | Visual drag-and-drop |
| **Branch Management** | List view | Cards with status |
| **Pull Request Integration** | Basic | Native support |
| **Modern Design** | Utilitarian | Clean, intuitive |
| **Mobile Friendly** | No | Yes |

### Key Features

✅ **Visual Pipeline Editor** - Create pipelines without writing code  
✅ **Personalized Dashboard** - Focus on your work  
✅ **Pipeline Visualization** - See execution flow clearly  
✅ **Instant Feedback** - Real-time updates  
✅ **Branch & PR Support** - Native GitHub/Bitbucket integration  
✅ **Easy Diagnosis** - Quickly identify failures  

## Installation

### Method 1: Plugin Manager

1. Navigate to **Manage Jenkins** → **Manage Plugins**
2. Go to **Available** tab
3. Search for "Blue Ocean"
4. Install "Blue Ocean" plugin suite
5. Restart Jenkins

### Method 2: Docker

```bash
docker run -d \
  --name jenkins-blueocean \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins-data:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkinsci/blueocean:latest
```

### Method 3: Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jenkins
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jenkins
  template:
    metadata:
      labels:
        app: jenkins
    spec:
      containers:
      - name: jenkins
        image: jenkinsci/blueocean:latest
        ports:
        - containerPort: 8080
        - containerPort: 50000
        volumeMounts:
        - name: jenkins-home
          mountPath: /var/jenkins_home
      volumes:
      - name: jenkins-home
        persistentVolumeClaim:
          claimName: jenkins-pvc
```

## Accessing Blue Ocean

**URL:** `http://your-jenkins-url/blue`

Or click "Open Blue Ocean" from classic Jenkins sidebar.

## Dashboard Overview

### Main Dashboard

**Components:**
- **Pipeline Cards** - Visual representation of each pipeline
- **Branch Overview** - See all active branches
- **Activity Feed** - Recent builds and changes
- **Favorites** - Star important pipelines

**Pipeline Card Shows:**
- Pipeline name
- Latest build status
- Branch count
- Last run time
- Quick actions

### Pipeline View

**Features:**
- **Stage Visualization** - See all pipeline stages
- **Real-time Updates** - Watch builds execute live
- **Log Integration** - Click any stage to see logs
- **Failure Highlighting** - Failed stages in red
- **Parallel Stages** - Visualized side-by-side

## Visual Pipeline Editor

### Creating a Pipeline

**Step 1: Start New Pipeline**
1. Click "New Pipeline"
2. Choose source (GitHub, Bitbucket, Git)
3. Connect and authorize
4. Select repository

**Step 2: Build with Visual Editor**
1. Add stages
2. Add steps to each stage
3. Configure parameters
4. Save (creates Jenkinsfile)

### Example: Node.js Build Pipeline

**Visual Editor Creates:**

```groovy
pipeline {
    agent any
    
    stages {
        stage('Install') {
            steps {
                sh 'npm install'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
        
        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh './deploy.sh'
            }
        }
    }
}
```

### Available Steps in Editor

**Build Steps:**
- Shell script
- Batch script
- Groovy script
- Docker build
- Maven/Gradle

**Source Control:**
- Git checkout
- Git push
- Git tag

**Notifications:**
- Email
- Slack
- Teams

**Deployment:**
- SSH
- Kubernetes
- Cloud providers

## Branch & Pull Request Visualization

### Multibranch Pipeline

**Automatic Detection:**
```groovy
// Jenkinsfile in repository
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo "Building branch: ${env.BRANCH_NAME}"
                sh 'make build'
            }
        }
    }
}
```

**Blue Ocean Shows:**
- All branches as cards
- PR builds automatically
- Merge status
- Branch health

### Pull Request Builder

**GitHub Integration:**

1. **Configure GitHub Server**
   - Manage Jenkins → Configure System
   - Add GitHub Server
   - Create access token
   - Test connection

2. **Create Multibranch Pipeline**
   ```groovy
   // Automatically builds PRs
   pipeline {
       agent any
       stages {
           stage('PR Validation') {
               when {
                   changeRequest()
               }
               steps {
                   sh 'npm run lint'
                   sh 'npm test'
               }
           }
       }
   }
   ```

3. **View in Blue Ocean**
   - PRs appear as branches
   - Status updates GitHub
   - Inline comments on failures

## Pipeline Run Details

### Execution View

**Components:**
1. **Pipeline Graph** - Visual stage flow
2. **Changes** - Git commits in this build
3. **Tests** - Test results and trends
4. **Artifacts** - Build outputs
5. **Logs** - Console output

### Stage Details

Click any stage to see:
- **Duration** - How long it took
- **Status** - Success/failure/unstable
- **Logs** - Stage-specific output
- **Steps** - Individual step results

**Example Visual Flow:**
```
[Checkout] ✅ 5s
    ↓
[Build] ✅ 45s
    ↓
[Test] ⚠️ 120s
    ↓
[Deploy] ❌ (skipped)
```

## Test Results & Trends

### Test Visualization

**Supported Formats:**
- JUnit XML
- TestNG
- NUnit
- Pytest
- Jest/Mocha

**Example Pipeline:**
```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'npm test'
            }
            post {
                always {
                    junit 'test-results/**/*.xml'
                }
            }
        }
    }
}
```

**Blue Ocean Shows:**
- Pass/fail counts
- Test duration trends
- Flaky test detection
- Failure details

### Test Trends

**Metrics Displayed:**
- Total tests
- Pass rate over time
- Average duration
- Slowest tests
- Most unstable tests

## Customizing Blue Ocean

### Pipeline Configuration

**Per-Pipeline Settings:**
```groovy
pipeline {
    agent any
    
    options {
        // Blue Ocean respects these
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
    }
    
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
    }
    
    post {
        failure {
            // Blue Ocean shows this
            mail to: 'team@example.com',
                 subject: "Build Failed: ${env.JOB_NAME}",
                 body: "Check Blue Ocean: ${env.RUN_DISPLAY_URL}"
        }
    }
}
```

### Custom Stage Naming

```groovy
pipeline {
    agent any
    stages {
        stage('🔨 Build') {
            steps {
                sh 'make build'
            }
        }
        
        stage('🧪 Test') {
            steps {
                sh 'make test'
            }
        }
        
        stage('🚀 Deploy') {
            steps {
                sh 'make deploy'
            }
        }
    }
}
```

## Advanced Features

### Parallel Stages Visualization

```groovy
pipeline {
    agent any
    stages {
        stage('Parallel Tests') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'npm run test:unit'
                    }
                }
                stage('Integration Tests') {
                    steps {
                        sh 'npm run test:integration'
                    }
                }
                stage('E2E Tests') {
                    steps {
                        sh 'npm run test:e2e'
                    }
                }
            }
        }
    }
}
```

**Blue Ocean displays parallel stages side-by-side with individual status.**

### Input Steps

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy to Prod') {
            steps {
                input {
                    message "Deploy to production?"
                    ok "Deploy"
                    submitter "admin,release-manager"
                    parameters {
                        string(name: 'VERSION', description: 'Version to deploy')
                    }
                }
                
                script {
                    echo "Deploying version ${VERSION}"
                    sh "./deploy.sh ${VERSION}"
                }
            }
        }
    }
}
```

**Blue Ocean shows approval dialog inline.**

### Credentials

```groovy
pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'aws-creds',
                        usernameVariable: 'AWS_KEY',
                        passwordVariable: 'AWS_SECRET'
                    )
                ]) {
                    sh 'aws s3 sync dist/ s3://bucket/'
                }
            }
        }
    }
}
```

## REST API

### Endpoints

**Pipeline Runs:**
```bash
# Get all runs
curl -u user:token \
  http://jenkins/blue/rest/organizations/jenkins/pipelines/my-pipeline/runs/

# Get specific run
curl -u user:token \
  http://jenkins/blue/rest/organizations/jenkins/pipelines/my-pipeline/runs/42/

# Get run logs
curl -u user:token \
  http://jenkins/blue/rest/organizations/jenkins/pipelines/my-pipeline/runs/42/log/
```

**Branches:**
```bash
# List branches
curl -u user:token \
  http://jenkins/blue/rest/organizations/jenkins/pipelines/my-pipeline/branches/

# Branch details
curl -u user:token \
  http://jenkins/blue/rest/organizations/jenkins/pipelines/my-pipeline/branches/main/
```

### Python Client Example

```python
import requests
from requests.auth import HTTPBasicAuth

class BlueOceanClient:
    def __init__(self, base_url, username, token):
        self.base_url = f"{base_url}/blue/rest/organizations/jenkins"
        self.auth = HTTPBasicAuth(username, token)
    
    def get_pipelines(self):
        response = requests.get(
            f"{self.base_url}/pipelines/",
            auth=self.auth
        )
        return response.json()
    
    def get_runs(self, pipeline_name):
        response = requests.get(
            f"{self.base_url}/pipelines/{pipeline_name}/runs/",
            auth=self.auth
        )
        return response.json()
    
    def get_run_status(self, pipeline_name, run_id):
        response = requests.get(
            f"{self.base_url}/pipelines/{pipeline_name}/runs/{run_id}/",
            auth=self.auth
        )
        return response.json()

# Usage
client = BlueOceanClient(
    "http://jenkins:8080",
    "admin",
    "api-token"
)

runs = client.get_runs("my-pipeline")
for run in runs:
    print(f"Run {run['id']}: {run['result']}")
```

## Integration with Tools

### GitHub

**Automatic Status Updates:**
```groovy
pipeline {
    agent any
    
    options {
        githubProjectProperty(
            projectUrlStr: 'https://github.com/user/repo'
        )
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }
    }
}
```

**Blue Ocean automatically:**
- Updates commit status
- Comments on PRs
- Links to build results

### Slack

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
    }
    post {
        success {
            slackSend(
                color: 'good',
                message: "Build succeeded: ${env.RUN_DISPLAY_URL}"
            )
        }
        failure {
            slackSend(
                color: 'danger',
                message: "Build failed: ${env.RUN_DISPLAY_URL}"
            )
        }
    }
}
```

**Note:** `RUN_DISPLAY_URL` links to Blue Ocean view.

### JIRA

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
    }
    post {
        success {
            jiraComment(
                issueKey: 'PROJ-123',
                body: "Build completed: ${env.RUN_DISPLAY_URL}"
            )
        }
    }
}
```

## Best Practices

### 1. Keep Stages Meaningful

```groovy
// GOOD - Clear stages
pipeline {
    agent any
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Build') { steps { sh 'make' } }
        stage('Unit Test') { steps { sh 'make test' } }
        stage('Integration Test') { steps { sh 'make integration' } }
        stage('Deploy Dev') { steps { sh 'deploy dev' } }
    }
}

// BAD - Too granular
pipeline {
    agent any
    stages {
        stage('Step 1') { steps { sh 'echo 1' } }
        stage('Step 2') { steps { sh 'echo 2' } }
        // ... 50 more stages
    }
}
```

### 2. Use Descriptive Names

```groovy
// GOOD
stage('Build Docker Image') {
    steps {
        sh 'docker build -t myapp:${BUILD_NUMBER} .'
    }
}

// BETTER - With emojis for visual cues
stage('🐳 Build Docker Image') {
    steps {
        sh 'docker build -t myapp:${BUILD_NUMBER} .'
    }
}
```

### 3. Parallelize When Possible

```groovy
pipeline {
    agent any
    stages {
        stage('Tests') {
            parallel {
                stage('Unit') {
                    steps { sh 'npm run test:unit' }
                }
                stage('Lint') {
                    steps { sh 'npm run lint' }
                }
                stage('Security') {
                    steps { sh 'npm audit' }
                }
            }
        }
    }
}
```

### 4. Add Meaningful Post Actions

```groovy
post {
    always {
        junit 'test-results/**/*.xml'
        archiveArtifacts artifacts: 'dist/**', fingerprint: true
    }
    success {
        echo 'Pipeline succeeded!'
    }
    failure {
        echo 'Pipeline failed!'
        // Send notifications
    }
}
```

### 5. Use Input for Manual Gates

```groovy
stage('Deploy to Production') {
    steps {
        input message: 'Deploy to production?',
              ok: 'Deploy',
              submitter: 'release-team'
        
        sh './deploy-prod.sh'
    }
}
```

## Troubleshooting

### Issue 1: Blue Ocean Not Loading

**Symptoms:**
- Blank page
- "Loading..." forever

**Solutions:**
```bash
# Check browser console for errors
# Clear browser cache
# Restart Jenkins
sudo systemctl restart jenkins

# Check plugin compatibility
# Update Blue Ocean plugins
```

### Issue 2: Pipelines Not Showing

**Solutions:**
1. Verify pipeline has Jenkinsfile
2. Check branch detection
3. Scan repository manually
4. Check credentials

### Issue 3: Visual Editor Not Working

**Solutions:**
1. Check pipeline type (must be multibranch or standalone)
2. Verify write permissions
3. Update Blue Ocean plugins
4. Check browser compatibility

## Limitations

### What Blue Ocean Can't Do

❌ **Configure System Settings** - Use classic UI  
❌ **Manage Plugins** - Use classic UI  
❌ **Freestyle Jobs** - Not supported  
❌ **Complex Scripted Pipelines** - Limited editing  
❌ **Matrix Projects** - Not visualized well  

### When to Use Classic UI

- System configuration
- Plugin management
- Freestyle job configuration
- Advanced security settings
- Node/agent configuration

## Real-World Example

**Complete CI/CD Pipeline:**

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'registry.company.com'
        APP_NAME = 'myapp'
    }
    
    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
    }
    
    stages {
        stage('🔍 Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('🔨 Build') {
            steps {
                sh 'npm install'
                sh 'npm run build'
            }
        }
        
        stage('🧪 Test & Analysis') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'npm run test:unit'
                    }
                }
                stage('Lint') {
                    steps {
                        sh 'npm run lint'
                    }
                }
                stage('Security Scan') {
                    steps {
                        sh 'npm audit'
                    }
                }
            }
        }
        
        stage('🐳 Docker Build') {
            steps {
                script {
                    docker.build("${DOCKER_REGISTRY}/${APP_NAME}:${BUILD_NUMBER}")
                }
            }
        }
        
        stage('🚀 Deploy Dev') {
            steps {
                sh 'kubectl apply -f k8s/dev/'
            }
        }
        
        stage('🎯 Deploy Prod') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?',
                      ok: 'Deploy',
                      submitter: 'release-managers'
                
                sh 'kubectl apply -f k8s/prod/'
            }
        }
    }
    
    post {
        always {
            junit 'test-results/**/*.xml'
            archiveArtifacts artifacts: 'dist/**', fingerprint: true
        }
        success {
            slackSend color: 'good',
                      message: "✅ Build succeeded: ${env.RUN_DISPLAY_URL}"
        }
        failure {
            slackSend color: 'danger',
                      message: "❌ Build failed: ${env.RUN_DISPLAY_URL}"
        }
    }
}
```

**Blue Ocean visualizes this as clean, intuitive pipeline flow.**

## Summary

Blue Ocean provides:
- Modern, intuitive interface
- Visual pipeline editor
- Better pipeline visualization
- Native branch/PR support
- Improved user experience
- Mobile-friendly design

**Best for:**
- New users learning Jenkins
- Visual pipeline creation
- Branch/PR workflows
- Quick pipeline diagnosis

**Use Classic UI for:**
- System administration
- Plugin management
- Advanced configuration
- Freestyle jobs

## Next Steps

- **Performance Tuning** → Optimize Jenkins
- **Enterprise Patterns** → Scale for teams
- **Practice Labs** → Hands-on exercises

---

**Previous:** [Monitoring](16-monitoring.md)  
**Next:** [Configuration as Code](18-configuration-as-code.md)
