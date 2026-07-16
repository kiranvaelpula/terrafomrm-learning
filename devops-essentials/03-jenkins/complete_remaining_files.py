#!/usr/bin/env python3
"""
Complete all remaining Jenkins documentation files
Generates comprehensive content for interview questions and all labs
"""

import os

# Advanced Interview Questions Content
interview_content = """# Jenkins Advanced - Interview Questions

## Overview

Advanced Jenkins interview questions covering distributed builds, shared libraries, security, monitoring, performance optimization, and enterprise patterns. These questions are commonly asked for Senior DevOps Engineer and Jenkins Administrator roles.

---

## Distributed Builds & Scaling

### Q1: Explain Jenkins Master-Agent architecture and benefits

**Answer:**

**Architecture Components:**
- **Master**: Schedules builds, monitors agents, records results, serves UI
- **Agents**: Execute build jobs in isolated environments

**Benefits:**
- Horizontal scalability (add more agents)
- Parallel execution (multiple concurrent builds)
- Platform diversity (Linux, Windows, macOS agents)
- Resource isolation (builds don't affect each other)
- Cost optimization (use cloud/spot instances)

**Example Configuration:**
```groovy
pipeline {
    agent {
        label 'linux && docker && high-memory'
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

**Best Practices:**
- Master: 0 executors (scheduling only)
- Agents: Ephemeral (Docker/Kubernetes)
- Use labels for targeting
- Implement resource limits

---

### Q2: How do you implement dynamic agent provisioning with Kubernetes?

**Answer:**

```groovy
pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins: agent
spec:
  containers:
  - name: maven
    image: maven:3.8-jdk-11
    command: ['cat']
    tty: true
    resources:
      requests:
        memory: "2Gi"
        cpu: "1000m"
      limits:
        memory: "4Gi"
        cpu: "2000m"
  - name: docker
    image: docker:latest
    command: ['cat']
    tty: true
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run/docker.sock
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
'''
        }
    }
    stages {
        stage('Build') {
            steps {
                container('maven') {
                    sh 'mvn clean package'
                }
            }
        }
        stage('Docker Build') {
            steps {
                container('docker') {
                    sh 'docker build -t myapp .'
                }
            }
        }
    }
}
```

**Benefits:**
- Auto-scaling based on queue
- Clean environment per build
- Cost-effective
- No manual agent management

---

## Shared Libraries & Code Reuse

### Q3: Design a comprehensive shared library structure

**Answer:**

**Directory Structure:**
```
my-shared-library/
├── vars/
│   ├── standardPipeline.groovy
│   ├── buildDocker.groovy
│   ├── deployApp.groovy
│   └── notifyTeam.groovy
├── src/
│   └── com/company/jenkins/
│       ├── BuildHelper.groovy
│       ├── DeployHelper.groovy
│       └── SecurityScanner.groovy
├── resources/
│   ├── scripts/
│   │   ├── deploy.sh
│   │   └── cleanup.sh
│   └── templates/
│       ├── Dockerfile.template
│       └── k8s-deployment.yaml
└── test/
    └── groovy/
        └── StandardPipelineTest.groovy
```

**Implementation Example:**
```groovy
// vars/standardPipeline.groovy
def call(Map config) {
    pipeline {
        agent { kubernetes { yaml libraryResource('pod-templates/build.yaml') } }
        
        options {
            buildDiscarder(logRotator(numToKeepStr: '30'))
            timeout(time: config.timeout ?: 60, unit: 'MINUTES')
        }
        
        stages {
            stage('Build') {
                steps {
                    script {
                        def builder = new com.company.jenkins.BuildHelper(this)
                        builder.build(config.language)
                    }
                }
            }
            
            stage('Test') {
                when { expression { config.runTests != false } }
                steps {
                    sh "${config.testCommand ?: 'make test'}"
                }
            }
            
            stage('Security Scan') {
                steps {
                    script {
                        def scanner = new com.company.jenkins.SecurityScanner(this)
                        scanner.scan()
                    }
                }
            }
            
            stage('Deploy') {
                when { branch 'main' }
                steps {
                    deployApp(
                        environment: config.environment,
                        version: env.BUILD_NUMBER
                    )
                }
            }
        }
        
        post {
            always {
                notifyTeam(
                    status: currentBuild.result,
                    channel: config.slackChannel
                )
            }
        }
    }
}
```

**Usage:**
```groovy
@Library('my-shared-library@v2.0') _

standardPipeline {
    language = 'java'
    environment = 'production'
    slackChannel = '#deployments'
    timeout = 45
}
```

---

## Security & Compliance

### Q4: Implement comprehensive security scanning in pipelines

**Answer:**

```groovy
pipeline {
    agent any
    
    stages {
        stage('Security Scans') {
            parallel {
                stage('Secret Detection') {
                    steps {
                        sh '''
                            # TruffleHog for secrets
                            trufflehog --regex --entropy=False . --json > secrets-report.json
                            
                            # GitLeaks
                            gitleaks detect --source . --report-format json --report-path gitleaks-report.json
                        '''
                    }
                }
                
                stage('Dependency Scan') {
                    steps {
                        sh '''
                            # NPM audit
                            npm audit --audit-level=high --json > npm-audit.json || true
                            
                            # Snyk
                            snyk test --severity-threshold=high --json > snyk-report.json || true
                            
                            # OWASP Dependency Check
                            dependency-check.sh --project myapp --scan . --format JSON
                        '''
                    }
                }
                
                stage('SAST') {
                    steps {
                        withSonarQubeEnv('SonarQube') {
                            sh 'sonar-scanner'
                        }
                        
                        script {
                            def qg = waitForQualityGate()
                            if (qg.status != 'OK') {
                                error "Quality gate failed: ${qg.status}"
                            }
                        }
                    }
                }
                
                stage('Container Scan') {
                    steps {
                        sh '''
                            # Trivy scan
                            trivy image --severity HIGH,CRITICAL myapp:${BUILD_NUMBER}
                            
                            # Anchore scan
                            anchore-cli image add myapp:${BUILD_NUMBER}
                            anchore-cli image wait myapp:${BUILD_NUMBER}
                            anchore-cli image vuln myapp:${BUILD_NUMBER} all
                        '''
                    }
                }
                
                stage('License Scan') {
                    steps {
                        sh 'license-checker --production --json > licenses.json'
                    }
                }
            }
        }
        
        stage('Security Gate') {
            steps {
                script {
                    // Fail if critical vulnerabilities found
                    def scanResults = readJSON file: 'snyk-report.json'
                    if (scanResults.vulnerabilities.findAll { it.severity == 'critical' }.size() > 0) {
                        error "Critical vulnerabilities detected!"
                    }
                }
            }
        }
    }
    
    post {
        always {
            publishHTML([
                reportDir: '.',
                reportFiles: 'security-report.html',
                reportName: 'Security Scan Report'
            ])
        }
    }
}
```

---

## Performance Optimization

### Q5: How do you optimize Jenkins build performance?

**Answer:**

**1. Parallel Execution:**
```groovy
stage('Tests') {
    parallel {
        stage('Unit') { steps { sh 'npm run test:unit' } }
        stage('Integration') { steps { sh 'npm run test:integration' } }
        stage('E2E') { steps { sh 'npm run test:e2e' } }
        stage('Lint') { steps { sh 'npm run lint' } }
        stage('Security') { steps { sh 'npm audit' } }
    }
}
```

**2. Caching Dependencies:**
```groovy
pipeline {
    agent {
        docker {
            image 'maven:3.8'
            args '-v maven-cache:/root/.m2'
        }
    }
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'  // Uses cached dependencies
            }
        }
    }
}
```

**3. Incremental Builds:**
```groovy
script {
    def changedFiles = sh(
        script: 'git diff --name-only HEAD~1',
        returnStdout: true
    ).trim().split('\\n')
    
    def modules = [
        frontend: changedFiles.any { it.startsWith('frontend/') },
        backend: changedFiles.any { it.startsWith('backend/') },
        api: changedFiles.any { it.startsWith('api/') }
    ]
    
    modules.each { module, changed ->
        if (changed) {
            echo "Building ${module}"
            sh "cd ${module} && make build"
        } else {
            echo "Skipping ${module} - no changes"
        }
    }
}
```

**4. Shallow Git Clone:**
```groovy
checkout([
    $class: 'GitSCM',
    extensions: [[
        $class: 'CloneOption',
        depth: 1,
        shallow: true,
        noTags: true
    ]]
])
```

**Results:**
- 50-70% faster builds
- Reduced resource usage
- Higher throughput

---

## Monitoring & Observability

### Q6: Design comprehensive monitoring for Jenkins

**Answer:**

**Components:**

**1. Metrics Collection (Prometheus):**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'jenkins'
    metrics_path: '/prometheus'
    static_configs:
      - targets: ['jenkins:8080']
```

**2. Key Metrics:**
```promql
# Build success rate
rate(jenkins_builds_success_build_count_total[5m]) /
(rate(jenkins_builds_success_build_count_total[5m]) +
 rate(jenkins_builds_failed_build_count_total[5m])) * 100

# Average build duration
rate(jenkins_builds_duration_milliseconds_summary_sum[5m]) /
rate(jenkins_builds_duration_milliseconds_summary_count[5m])

# Queue length
jenkins_queue_size_value

# Agent utilization
(jenkins_executor_in_use_value / jenkins_executor_count_value) * 100
```

**3. Alerting:**
```yaml
groups:
  - name: jenkins_alerts
    rules:
      - alert: HighFailureRate
        expr: |
          (rate(jenkins_builds_failed_build_count_total[10m]) /
           rate(jenkins_builds_total_build_count[10m])) > 0.2
        for: 5m
        annotations:
          summary: "Build failure rate > 20%"
      
      - alert: LongQueueTime
        expr: jenkins_queue_waiting_duration_milliseconds > 300000
        annotations:
          summary: "Builds waiting > 5 minutes"
```

**4. Pipeline Instrumentation:**
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                script {
                    def startTime = System.currentTimeMillis()
                    
                    sh 'make build'
                    
                    def duration = System.currentTimeMillis() - startTime
                    
                    // Send custom metric
                    sh """
                        echo 'build_duration_ms{job="${env.JOB_NAME}",stage="build"} ${duration}' | \
                        curl --data-binary @- http://pushgateway:9091/metrics/job/jenkins
                    """
                }
            }
        }
    }
}
```

---

## Enterprise Patterns

### Q7: Implement multi-tenancy in Jenkins

**Answer:**

**Strategy 1: Folder-Based Isolation**
```groovy
folder('team-a') {
    description('Team A Projects')
    authorization {
        permission('hudson.model.Item.Read', 'team-a-users')
        permission('hudson.model.Item.Build', 'team-a-users')
        permission('hudson.model.Item.Configure', 'team-a-leads')
    }
    properties {
        throttleJobProperty {
            maxConcurrentPerNode(5)
            maxConcurrentTotal(10)
        }
    }
}
```

**Strategy 2: Namespace Isolation (Kubernetes)**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: jenkins-team-a
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-a-quota
  namespace: jenkins-team-a
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    persistentvolumeclaims: "10"
    pods: "100"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: team-a-limits
  namespace: jenkins-team-a
spec:
  limits:
  - max:
      cpu: "4"
      memory: "8Gi"
    min:
      cpu: "100m"
      memory: "128Mi"
    type: Container
```

**Strategy 3: Label-Based Agent Isolation**
```groovy
pipeline {
    agent {
        kubernetes {
            label 'team-a-agent'
            namespace 'jenkins-team-a'
        }
    }
}
```

---

## Configuration as Code

### Q8: Implement complete JCasC configuration

**Answer:**

```yaml
jenkins:
  systemMessage: "Production Jenkins - Managed by Code"
  numExecutors: 0
  mode: EXCLUSIVE
  
  securityRealm:
    ldap:
      configurations:
        - server: "ldaps://ldap.company.com:636"
          rootDN: "dc=company,dc=com"
          userSearchBase: "ou=users"
          userSearch: "uid={0}"
          groupSearchBase: "ou=groups"
          groupSearchFilter: "(member={0})"
          
  authorizationStrategy:
    projectMatrix:
      permissions:
        - "Overall/Administer:admins"
        - "Overall/Read:authenticated"
        - "Job/Read:authenticated"
        - "Job/Build:developers"
        - "Job/Configure:leads"
        - "Job/Delete:admins"
        
  clouds:
    - kubernetes:
        name: "kubernetes"
        serverUrl: "https://kubernetes.default"
        namespace: "jenkins-agents"
        jenkinsUrl: "http://jenkins:8080"
        jenkinsTunnel: "jenkins-agent:50000"
        maxRequestsPerHostStr: "32"
        retentionTimeout: 5
        connectTimeout: 10
        readTimeout: 20
        templates:
          - name: "maven"
            label: "maven build java"
            containers:
              - name: "maven"
                image: "maven:3.8-jdk-11"
                command: "/bin/sh -c"
                args: "cat"
                ttyEnabled: true
                resourceRequestCpu: "500m"
                resourceLimitCpu: "2000m"
                resourceRequestMemory: "1Gi"
                resourceLimitMemory: "4Gi"

credentials:
  system:
    domainCredentials:
      - credentials:
          - usernamePassword:
              scope: GLOBAL
              id: "github-token"
              username: "jenkins-bot"
              password: "${GITHUB_TOKEN}"
              description: "GitHub Access Token"
          - aws:
              scope: GLOBAL
              id: "aws-prod"
              accessKey: "${AWS_ACCESS_KEY}"
              secretKey: "${AWS_SECRET_KEY}"
              description: "AWS Production Credentials"
          - basicSSHUserPrivateKey:
              scope: GLOBAL
              id: "deploy-key"
              username: "deploy"
              privateKeySource:
                directEntry:
                  privateKey: "${SSH_PRIVATE_KEY}"

unclassified:
  location:
    url: "https://jenkins.company.com"
    adminAddress: "jenkins-admin@company.com"
  
  slackNotifier:
    teamDomain: "company"
    tokenCredentialId: "slack-token"
    room: "#ci-cd"
  
  githubpluginconfig:
    configs:
      - name: "GitHub"
        apiUrl: "https://api.github.com"
        credentialsId: "github-token"

tool:
  git:
    installations:
      - name: "Default"
        home: "/usr/bin/git"
  
  maven:
    installations:
      - name: "Maven 3.8"
        properties:
          - installSource:
              installers:
                - maven:
                    id: "3.8.6"
  
  jdk:
    installations:
      - name: "JDK11"
        properties:
          - installSource:
              installers:
                - jdkInstaller:
                    id: "11.0.12+7"
```

---

## Real-World Scenarios

### Q9: Design blue-green deployment pipeline

**Answer:**

```groovy
pipeline {
    agent any
    
    parameters {
        choice(name: 'ACTION', choices: ['deploy', 'rollback'], description: 'Action to perform')
    }
    
    environment {
        BLUE_DEPLOYMENT = 'app-blue'
        GREEN_DEPLOYMENT = 'app-green'
        SERVICE_NAME = 'app-service'
    }
    
    stages {
        stage('Determine Target') {
            steps {
                script {
                    // Get current active deployment
                    env.CURRENT = sh(
                        script: "kubectl get service ${SERVICE_NAME} -o jsonpath='{.spec.selector.version}'",
                        returnStdout: true
                    ).trim()
                    
                    env.TARGET = (env.CURRENT == 'blue') ? 'green' : 'blue'
                    env.TARGET_DEPLOYMENT = "app-${env.TARGET}"
                    
                    echo "Current: ${env.CURRENT}, Target: ${env.TARGET}"
                }
            }
        }
        
        stage('Deploy to Target') {
            when { expression { params.ACTION == 'deploy' } }
            steps {
                sh """
                    # Update target deployment
                    kubectl set image deployment/${env.TARGET_DEPLOYMENT} \\
                        app=myapp:${BUILD_NUMBER}
                    
                    # Wait for rollout
                    kubectl rollout status deployment/${env.TARGET_DEPLOYMENT} --timeout=5m
                    
                    # Verify health
                    kubectl wait --for=condition=available \\
                        deployment/${env.TARGET_DEPLOYMENT} --timeout=2m
                """
            }
        }
        
        stage('Run Smoke Tests') {
            when { expression { params.ACTION == 'deploy' } }
            steps {
                sh """
                    # Get target pod IP
                    POD_IP=\$(kubectl get pod -l app=${env.TARGET_DEPLOYMENT} -o jsonpath='{.items[0].status.podIP}')
                    
                    # Run smoke tests
                    curl -f http://\$POD_IP:8080/health
                    ./run-smoke-tests.sh \$POD_IP
                """
            }
        }
        
        stage('Switch Traffic') {
            when { expression { params.ACTION == 'deploy' } }
            steps {
                input message: "Switch traffic to ${env.TARGET}?", ok: 'Proceed'
                
                sh """
                    # Update service selector
                    kubectl patch service ${SERVICE_NAME} -p \\
                        '{"spec":{"selector":{"version":"${env.TARGET}"}}}'
                    
                    # Verify
                    sleep 10
                    curl -f http://${SERVICE_NAME}/health
                """
            }
        }
        
        stage('Monitor') {
            when { expression { params.ACTION == 'deploy' } }
            steps {
                script {
                    timeout(time: 10, unit: 'MINUTES') {
                        input message: 'Traffic looks good?', ok: 'Confirm'
                    }
                }
            }
        }
        
        stage('Cleanup Old Deployment') {
            when { expression { params.ACTION == 'deploy' } }
            steps {
                sh "kubectl scale deployment/app-${env.CURRENT} --replicas=0"
            }
        }
        
        stage('Rollback') {
            when { expression { params.ACTION == 'rollback' } }
            steps {
                sh """
                    kubectl patch service ${SERVICE_NAME} -p \\
                        '{"spec":{"selector":{"version":"${env.CURRENT}"}}}'
                """
            }
        }
    }
    
    post {
        failure {
            script {
                if (params.ACTION == 'deploy') {
                    // Auto-rollback on failure
                    sh """
                        kubectl patch service ${SERVICE_NAME} -p \\
                            '{"spec":{"selector":{"version":"${env.CURRENT}"}}}'
                    """
                }
            }
        }
    }
}
```

---

## Best Practices

### Q10: What are critical Jenkins best practices?

**Answer:**

**Architecture:**
1. Master: 0 executors (scheduling only)
2. Ephemeral agents (Docker/K8s)
3. Multi-master for team isolation
4. High availability setup

**Security:**
1. RBAC with folder-based isolation
2. Vault for secrets management
3. Security scanning in all pipelines
4. Audit logging enabled
5. Network policies (K8s)

**Performance:**
1. Parallel execution where possible
2. Dependency caching
3. Incremental builds
4. Shallow Git clones
5. External artifact storage
6. Optimize JVM settings

**Code Quality:**
1. Pipeline as Code (Jenkinsfile)
2. Shared libraries for reusability
3. Template pipelines
4. Version control everything
5. Code review for pipeline changes

**Monitoring:**
1. Prometheus metrics
2. Grafana dashboards
3. Alert on key metrics
4. Centralized logging (ELK)
5. Distributed tracing

**Operations:**
1. Configuration as Code (JCasC)
2. Automated backups
3. Disaster recovery plan
4. Regular updates
5. Capacity planning

---

## Summary

Advanced topics covered:
- Distributed architecture & scaling
- Shared pipeline libraries
- Security & compliance
- Performance optimization
- Monitoring & observability
- Enterprise patterns
- Configuration as Code
- Real-world scenarios

**Key Skills Demonstrated:**
- Design scalable architecture
- Implement security best practices
- Optimize for performance
- Monitor effectively
- Apply enterprise patterns
- Automate everything

---

**Previous:** [Enterprise Patterns](20-enterprise-patterns.md)  
**Next:** [Practice Labs](../jenkins-practice/)
"""

print("Advanced interview questions content ready")
print(f"Length: {len(interview_content)} characters")

# Save to file
output_path = "advanced/interview-questions-advanced.md"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(interview_content)

print(f"✅ Created: {output_path}")
