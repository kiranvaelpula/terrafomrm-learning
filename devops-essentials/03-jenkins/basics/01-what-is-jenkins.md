# What is Jenkins and CI/CD

## What is CI/CD?

**CI (Continuous Integration):** Every time a developer pushes code, it's automatically built and tested. Catch bugs early, not in production.

**CD (Continuous Delivery):** After CI passes, the code is automatically ready to deploy (but a human clicks the button).

**CD (Continuous Deployment):** Same as Delivery, but it deploys automatically — no human approval needed.

```
Developer pushes code
    ↓
CI: Build → Run Tests → Code Quality Check
    ↓ (if all pass)
CD: Deploy to Staging → (optional approval) → Deploy to Production
```

**Without CI/CD:**
- Developer pushes code → someone manually builds → manually tests → manually deploys
- Errors found days later, blame game, slow releases

**With CI/CD:**
- Developer pushes code → everything happens automatically in minutes
- Errors caught in minutes, fast feedback, deploy multiple times per day

---

## What is Jenkins?

Jenkins is an open-source automation server that runs your CI/CD pipelines. It's the most widely used CI/CD tool in the industry.

**In plain English:** Jenkins is a robot that watches your Git repo. When you push code, it automatically builds your app, runs tests, and deploys it — based on instructions you write in a `Jenkinsfile`.

### Why Jenkins?

| Feature | Benefit |
|---|---|
| Free & open-source | No licensing costs |
| 1800+ plugins | Integrates with everything (Git, Docker, AWS, Slack, etc.) |
| Pipeline as Code | Jenkinsfile lives in your repo (version controlled) |
| Distributed builds | Run builds on multiple machines in parallel |
| Huge community | Every problem has been solved by someone |
| Self-hosted | Full control, runs on your infrastructure |

### Jenkins vs Other CI/CD Tools

| Tool | Type | Best for |
|---|---|---|
| Jenkins | Self-hosted, open-source | Full control, complex pipelines, legacy |
| GitHub Actions | Cloud, tied to GitHub | GitHub repos, simpler setup |
| GitLab CI | Cloud/self-hosted | GitLab repos, built-in |
| CircleCI | Cloud | Fast builds, Docker-native |
| ArgoCD | GitOps | Kubernetes deployments |
| AWS CodePipeline | Cloud | AWS-native workflows |

---

## How Jenkins Works

```
┌─────────────────────────────────────────────┐
│               Jenkins Server                 │
│                                             │
│  1. Watches Git repo for changes            │
│  2. Triggers pipeline (Jenkinsfile)         │
│  3. Runs stages: Build → Test → Deploy      │
│  4. Reports result (pass/fail)              │
│                                             │
│  Can distribute work to Agent nodes:        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │ Agent 1 │ │ Agent 2 │ │ Agent 3 │      │
│  │ (Linux) │ │(Windows)│ │ (Docker)│      │
│  └─────────┘ └─────────┘ └─────────┘      │
└─────────────────────────────────────────────┘
```

**Key components:**
- **Controller (Master)** — the main Jenkins server, manages everything, schedules jobs
- **Agent (Slave/Node)** — worker machines that actually run the builds
- **Job/Project** — a task Jenkins performs (build, test, deploy)
- **Pipeline** — a series of stages defined in a Jenkinsfile
- **Jenkinsfile** — the code that defines your pipeline (lives in your Git repo)

---

## What is a Jenkinsfile?

A Jenkinsfile tells Jenkins what to do. It lives in the root of your Git repo.

```groovy
pipeline {
    agent any                    // Run on any available agent

    stages {
        stage('Build') {         // Step 1: Build the app
            steps {
                sh 'npm install'
                sh 'npm run build'
            }
        }
        stage('Test') {          // Step 2: Run tests
            steps {
                sh 'npm test'
            }
        }
        stage('Deploy') {        // Step 3: Deploy
            steps {
                sh 'docker build -t myapp:latest .'
                sh 'docker push myapp:latest'
            }
        }
    }

    post {                       // After all stages
        success {
            echo 'Pipeline passed!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
```

**In plain English:** "Build my app, run tests, if tests pass then deploy. Tell me if it worked or not."

---

## Jenkins Pipeline Concepts

| Term | Meaning |
|---|---|
| **Pipeline** | The entire CI/CD workflow |
| **Stage** | A logical step (Build, Test, Deploy) |
| **Step** | An individual action within a stage (`sh 'npm test'`) |
| **Agent** | Where the pipeline runs (which machine) |
| **Post** | Actions after pipeline completes (notify, cleanup) |
| **Trigger** | What starts the pipeline (push, schedule, manual) |

---

## A Real-World Jenkins Pipeline

```groovy
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'mycompany/myapp'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/myorg/myapp.git'
            }
        }

        stage('Build') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }

        stage('Unit Tests') {
            steps {
                sh 'mvn test'
            }
            post {
                always {
                    junit 'target/surefire-reports/*.xml'   // Publish test results
                }
            }
        }

        stage('Code Quality') {
            steps {
                sh 'mvn sonar:sonar'                       // SonarQube scan
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
            }
        }

        stage('Deploy to Staging') {
            steps {
                sh "kubectl set image deployment/myapp myapp=${DOCKER_IMAGE}:${DOCKER_TAG} -n staging"
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'                              // Only deploy main to prod
            }
            input {
                message 'Deploy to production?'            // Manual approval
            }
            steps {
                sh "kubectl set image deployment/myapp myapp=${DOCKER_IMAGE}:${DOCKER_TAG} -n production"
            }
        }
    }

    post {
        success {
            slackSend channel: '#deployments', message: "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER} deployed"
        }
        failure {
            slackSend channel: '#deployments', message: "❌ ${env.JOB_NAME} #${env.BUILD_NUMBER} failed"
        }
    }
}
```

---

## Build Triggers (What Starts a Pipeline)

| Trigger | When it runs |
|---|---|
| SCM Polling | Jenkins checks Git every X minutes |
| Webhook | Git pushes event to Jenkins instantly |
| Scheduled (Cron) | At specific times (nightly builds) |
| Manual | Human clicks "Build Now" |
| Upstream job | After another job completes |

**Best practice:** Use webhooks (instant, no polling overhead).

---

## Interview Tips

**Q: What is Jenkins?**
> "Jenkins is an open-source automation server used for CI/CD. It automates building, testing, and deploying code through pipelines defined in a Jenkinsfile."

**Q: What is CI/CD?**
> "CI automatically builds and tests code on every push — catching bugs early. CD automatically deploys passing builds to staging or production — enabling fast, reliable releases."

**Q: What is a Jenkinsfile?**
> "A Jenkinsfile is a text file in the repo that defines the pipeline as code — stages like Build, Test, Deploy. It's version-controlled with the application code."

**Q: Jenkins vs GitHub Actions?**
> "Jenkins is self-hosted with full control and works with any Git provider. GitHub Actions is cloud-hosted, simpler to set up, but tied to GitHub. Jenkins is better for complex enterprise pipelines; GitHub Actions is better for simplicity."

---

## Next Steps

Continue to: [02 - Installation & Setup →](./02-installation.md)
