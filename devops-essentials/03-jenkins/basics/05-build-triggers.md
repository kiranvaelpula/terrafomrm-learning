# Build Triggers

## What are Build Triggers?

Build triggers define WHEN a Jenkins pipeline should run. Instead of manually clicking "Build Now" every time, you set up triggers so builds happen automatically based on events.

---

## Types of Build Triggers

| Trigger | When it fires | Use case |
|---|---|---|
| Webhook (Push) | Instantly when code is pushed | Most common, fastest feedback |
| SCM Polling | Jenkins checks Git every X minutes | When webhooks aren't possible |
| Scheduled (Cron) | At specific times | Nightly builds, weekly reports |
| Manual | Human clicks button | Production deploys with approval |
| Upstream job | After another job finishes | Chained pipelines |
| Remote trigger | API call from external tool | External systems trigger builds |

---

## 1. Webhook (GitHub/GitLab Push Event)

**Best method.** GitHub/GitLab sends a notification to Jenkins the instant code is pushed. No delay, no polling overhead.

### How it works:
```
Developer pushes code → GitHub sends HTTP POST to Jenkins → Pipeline starts immediately
```

### Setup in Jenkinsfile:
```groovy
pipeline {
    agent any
    triggers {
        githubPush()    // Triggered by GitHub webhook
    }
    stages {
        stage('Build') {
            steps {
                sh 'npm install && npm run build'
            }
        }
    }
}
```

### Setup in GitHub:
1. Go to your repo → Settings → Webhooks → Add webhook
2. Payload URL: `http://your-jenkins-url/github-webhook/`
3. Content type: `application/json`
4. Events: "Just the push event" (or select specific events)

### Setup in GitLab:
1. Go to your repo → Settings → Webhooks
2. URL: `http://your-jenkins-url/project/your-job-name`
3. Trigger: Push events, Merge request events

**When to use:** Always. This is the standard for any project.

---

## 2. SCM Polling (Poll SCM)

Jenkins periodically checks your Git repo for changes. If something changed since last check, it triggers a build.

```groovy
pipeline {
    agent any
    triggers {
        pollSCM('H/5 * * * *')    // Check every 5 minutes
    }
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
    }
}
```

**How it works:**
```
Every 5 minutes: Jenkins runs "git fetch" → any new commits? → Yes → Build
                                                              → No  → Do nothing
```

**When to use:**
- Webhooks can't reach Jenkins (firewall restrictions)
- Jenkins is behind a VPN with no public URL
- Quick setup without configuring webhooks

**Downside:** Wastes resources checking when nothing changed. Delay between push and build (up to polling interval).

---

## 3. Scheduled (Cron Trigger)

Run builds at specific times, regardless of code changes.

```groovy
pipeline {
    agent any
    triggers {
        cron('0 2 * * *')         // Every day at 2:00 AM
    }
    stages {
        stage('Nightly Tests') {
            steps {
                sh 'npm run test:integration'
                sh 'npm run test:e2e'
            }
        }
    }
}
```

### Cron Syntax:
```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-7, Sunday=0 or 7)
│ │ │ │ │
* * * * *

Examples:
H/15 * * * *        → Every 15 minutes (H = hash for load spreading)
0 2 * * *           → Daily at 2:00 AM
0 0 * * 0           → Weekly on Sunday at midnight
0 9 * * 1-5         → Weekdays at 9:00 AM
H 2 * * *           → Sometime between 2:00-2:59 AM (H spreads load)
```

**The `H` symbol:** Jenkins-specific. Instead of all jobs running at exactly minute 0, `H` picks a consistent but spread-out minute per job to avoid thundering herd.

**When to use:**
- Nightly integration/E2E tests (too slow for every push)
- Daily security scans
- Weekly reports
- Scheduled deployments

---

## 4. Manual Trigger (Build Now / Input)

Human manually starts the build or approves a stage.

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t myapp .'
            }
        }
        stage('Deploy to Production') {
            input {
                message 'Deploy to production?'
                ok 'Yes, deploy!'
                submitter 'admin,deploy-team'    // Only these users can approve
            }
            steps {
                sh 'kubectl apply -f k8s/production/'
            }
        }
    }
}
```

**When to use:**
- Production deployments that need human approval
- Destructive operations (database migrations)
- Compliance requirements (audit trail of who approved)

---

## 5. Upstream Job Trigger

Run after another job completes successfully.

```groovy
pipeline {
    agent any
    triggers {
        upstream(
            upstreamProjects: 'build-job',
            threshold: hudson.model.Result.SUCCESS    // Only if build-job passed
        )
    }
    stages {
        stage('Deploy') {
            steps {
                sh 'deploy.sh'
            }
        }
    }
}
```

**When to use:**
- Build job → Deploy job → Integration test job (chained)
- Shared library updated → rebuild all dependent projects

---

## 6. Remote Trigger (API/Token)

Trigger a build from outside Jenkins via HTTP request.

### Setup:
1. Job → Configure → "Trigger builds remotely"
2. Set an authentication token: `my-secret-token`

### Call from anywhere:
```bash
curl -X POST "http://jenkins-url/job/my-job/build?token=my-secret-token"

# With parameters
curl -X POST "http://jenkins-url/job/my-job/buildWithParameters?token=my-secret-token&ENV=production"
```

**When to use:**
- External monitoring detects an issue → triggers auto-fix pipeline
- Another CI system needs to trigger Jenkins
- Chat bot triggers a deploy (`/deploy production` in Slack)

---

## 7. Branch-Specific Triggers

Different triggers for different branches:

```groovy
pipeline {
    agent any
    triggers {
        // Only poll for the main branch
        pollSCM(env.BRANCH_NAME == 'main' ? 'H/5 * * * *' : '')
    }
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
        stage('Deploy to Prod') {
            when {
                branch 'main'       // Only main branch deploys to prod
            }
            steps {
                sh 'make deploy-prod'
            }
        }
        stage('Deploy to Staging') {
            when {
                branch 'develop'    // Develop branch deploys to staging
            }
            steps {
                sh 'make deploy-staging'
            }
        }
    }
}
```

---

## Combining Multiple Triggers

```groovy
pipeline {
    agent any
    triggers {
        githubPush()                    // On every push
        cron('0 2 * * *')              // Also run nightly
        pollSCM('H/10 * * * *')        // Backup: poll every 10 min
    }
    stages {
        stage('Build & Test') {
            steps {
                sh 'make all'
            }
        }
    }
}
```

---

## Best Practices

1. **Use webhooks as primary trigger** — instant feedback, no wasted resources
2. **Add pollSCM as backup** — catches pushes if webhook fails
3. **Use `H` in cron** — spreads load across Jenkins
4. **Require approval for production** — never auto-deploy to prod without review
5. **Set quiet period** — wait a few seconds after trigger before building (batches rapid pushes)

```groovy
options {
    quietPeriod(30)    // Wait 30 seconds — catches multiple rapid pushes into one build
}
```

---

## Common Pitfalls

- **Webhook not firing:** Check firewall, Jenkins URL must be reachable from GitHub/GitLab
- **Too frequent polling:** `* * * * *` (every minute) is excessive, use `H/5 * * * *`
- **Missing `H`:** All jobs at `0 2 * * *` spike at exactly 2:00 AM. Use `H 2 * * *`
- **No backup trigger:** If webhook breaks, builds stop. Add pollSCM as fallback
- **Auto-deploying to prod:** Always use `input` or a separate manual trigger for production

---

## Interview Tips

**Q: What build triggers have you used?**
> "I primarily use GitHub webhooks for instant feedback on every push. For nightly integration tests and security scans, I use cron triggers. Production deployments use manual approval via the `input` step."

**Q: Webhook vs Polling?**
> "Webhooks are better — instant, no resource waste. Polling is a backup when webhooks can't reach Jenkins due to network restrictions."

**Q: How do you prevent accidental production deploys?**
> "I use the `input` directive with a `submitter` list so only authorized team members can approve production deployments. Combined with branch protection — only the main branch can deploy to production."

---

## Next Steps

Continue to: [Interview Questions - Basics →](./interview-questions-basics.md)
