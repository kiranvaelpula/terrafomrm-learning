# Jenkins Performance Optimization

## Overview

As Jenkins usage grows, performance becomes critical. Slow builds, long queues, and resource exhaustion impact developer productivity. This guide covers proven strategies to optimize Jenkins performance.

## Performance Metrics

### Key Indicators

**Build Performance:**
- Build queue wait time
- Build execution time
- Concurrent build capacity
- Build success rate

**System Resources:**
- CPU utilization
- Memory usage
- Disk I/O
- Network throughput

**Jenkins Specific:**
- Plugin load time
- SCM polling frequency
- Artifact storage size
- Log file size

### Measuring Performance

**Install Monitoring Plugin:**
```bash
# Prometheus metrics endpoint
http://jenkins/prometheus/

# Key metrics
jenkins_queue_size_value
jenkins_executor_in_use_value
jenkins_builds_duration_milliseconds_summary
```

## JVM Tuning

### Heap Size Configuration

**Default (often insufficient):**
```bash
java -jar jenkins.war
```

**Optimized:**
```bash
java -Xms2g -Xmx4g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=100 \
  -XX:+ParallelRefProcEnabled \
  -XX:+UseStringDeduplication \
  -jar jenkins.war
```

### G1 Garbage Collector

**Why G1GC:**
- Lower pause times
- Better for large heaps
- Predictable performance

**Configuration:**
```bash
# /etc/default/jenkins or systemd service
JAVA_OPTS="-Xms2048m -Xmx4096m \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=100 \
  -XX:G1HeapRegionSize=16m \
  -XX:+ParallelRefProcEnabled \
  -XX:+UseStringDeduplication \
  -XX:+DisableExplicitGC \
  -Djava.awt.headless=true"
```

### Memory Recommendations

| Jenkins Usage | Heap Size | Total RAM |
|---------------|-----------|-----------|
| Small (<50 jobs) | 2-4GB | 4GB |
| Medium (50-200 jobs) | 4-8GB | 8-16GB |
| Large (200-500 jobs) | 8-16GB | 16-32GB |
| Enterprise (500+ jobs) | 16-32GB | 32-64GB+ |

### Monitoring JVM

```groovy
// Script Console (Manage Jenkins → Script Console)
import java.lang.management.*

def runtime = ManagementFactory.getRuntimeMXBean()
def memory = ManagementFactory.getMemoryMXBean()

println "JVM Uptime: ${runtime.uptime / 1000 / 60 / 60} hours"
println "Heap Usage: ${memory.heapMemoryUsage}"
println "Non-Heap Usage: ${memory.nonHeapMemoryUsage}"

// GC stats
ManagementFactory.getGarbageCollectorMXBeans().each { gc ->
    println "${gc.name}: ${gc.collectionCount} collections, ${gc.collectionTime}ms"
}
```

## Build Optimization

### 1. Parallel Execution

**Bad - Sequential:**
```groovy
pipeline {
    agent any
    stages {
        stage('Unit Tests') {
            steps { sh 'npm run test:unit' }  // 5 min
        }
        stage('Integration Tests') {
            steps { sh 'npm run test:integration' }  // 10 min
        }
        stage('E2E Tests') {
            steps { sh 'npm run test:e2e' }  // 15 min
        }
    }
}
// Total: 30 minutes
```

**Good - Parallel:**
```groovy
pipeline {
    agent any
    stages {
        stage('Tests') {
            parallel {
                stage('Unit') {
                    steps { sh 'npm run test:unit' }
                }
                stage('Integration') {
                    steps { sh 'npm run test:integration' }
                }
                stage('E2E') {
                    steps { sh 'npm run test:e2e' }
                }
            }
        }
    }
}
// Total: 15 minutes (longest stage)
```

### 2. Optimize Checkout

**Shallow Clone:**
```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    extensions: [[
                        $class: 'CloneOption',
                        depth: 1,  // Shallow clone
                        noTags: true,
                        shallow: true
                    ]],
                    userRemoteConfigs: [[url: 'https://github.com/user/repo.git']]
                ])
            }
        }
    }
}
```

**Skip Checkout When Not Needed:**
```groovy
pipeline {
    agent any
    options {
        skipDefaultCheckout()  // Skip automatic checkout
    }
    stages {
        stage('Build') {
            steps {
                // Only checkout if needed
                script {
                    if (needsCheckout()) {
                        checkout scm
                    }
                }
            }
        }
    }
}
```

### 3. Cache Dependencies

**Maven:**
```groovy
pipeline {
    agent {
        docker {
            image 'maven:3.8-jdk-11'
            args '-v $HOME/.m2:/root/.m2'  // Cache Maven repo
        }
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

**Node.js:**
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                dir('app') {
                    // Cache node_modules
                    sh '''
                        if [ -d "node_modules" ]; then
                            npm ci  // Faster than npm install
                        else
                            npm install
                        fi
                    '''
                }
            }
        }
    }
}
```

**Docker Layer Caching:**
```dockerfile
# Optimize Docker build
FROM node:16-alpine

# Install dependencies first (cached layer)
COPY package*.json ./
RUN npm ci

# Copy source (changes frequently)
COPY . .
RUN npm run build
```

### 4. Incremental Builds

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                script {
                    // Only build changed modules
                    def changedFiles = sh(
                        script: 'git diff --name-only HEAD~1',
                        returnStdout: true
                    ).trim().split('\n')
                    
                    if (changedFiles.any { it.startsWith('module-a/') }) {
                        sh 'cd module-a && make build'
                    }
                    if (changedFiles.any { it.startsWith('module-b/') }) {
                        sh 'cd module-b && make build'
                    }
                }
            }
        }
    }
}
```

## Agent Optimization

### 1. Use Ephemeral Agents

**Docker Agents:**
```groovy
pipeline {
    agent {
        docker {
            image 'node:16'
            reuseNode false  // Don't reuse, faster cleanup
        }
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

**Kubernetes Agents:**
```groovy
pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: maven
    image: maven:3.8-jdk-11
    command: ['cat']
    tty: true
    resources:
      requests:
        memory: "1Gi"
        cpu: "500m"
      limits:
        memory: "2Gi"
        cpu: "1000m"
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
    }
}
```

### 2. Agent Labels & Load Balancing

```groovy
pipeline {
    agent none
    stages {
        stage('Build') {
            agent { label 'linux && docker' }  // Specific requirements
            steps {
                sh 'make build'
            }
        }
        stage('Test') {
            agent { label 'test-runner' }  // Different agent type
            steps {
                sh 'make test'
            }
        }
    }
}
```

### 3. Resource Limits

**Configure Node:**
```groovy
// In node configuration
Number of executors: 4  // Based on CPU cores
Labels: linux docker high-memory

// Set resource limits
hudson.model.Node.Mode.EXCLUSIVE  // For dedicated builds
```

## Pipeline Optimization

### 1. Minimize Pipeline Steps

**Bad - Too Many Steps:**
```groovy
stage('Build') {
    steps {
        sh 'echo step 1'
        sh 'echo step 2'
        sh 'echo step 3'
        // ... 50 more sh steps
    }
}
```

**Good - Combined:**
```groovy
stage('Build') {
    steps {
        sh '''
            echo step 1
            echo step 2
            echo step 3
        '''
    }
}
```

### 2. Use @NonCPS for Complex Logic

```groovy
@NonCPS
def processData(List data) {
    return data.collect { it * 2 }.findAll { it > 10 }
}

pipeline {
    agent any
    stages {
        stage('Process') {
            steps {
                script {
                    def result = processData([1, 5, 10, 15, 20])
                    echo "Result: ${result}"
                }
            }
        }
    }
}
```

### 3. Optimize Stash/Unstash

```groovy
// BAD - Stashing everything
stash includes: '**/*', name: 'all'

// GOOD - Stash only what's needed
stash includes: 'target/*.jar', excludes: '**/test*.jar', name: 'artifacts'
```

### 4. Use Shared Libraries

```groovy
@Library('my-shared-library') _

// Reuse optimized functions
standardBuild {
    language = 'java'
    skipTests = false
}
```

## Storage Optimization

### 1. Build History Retention

```groovy
pipeline {
    options {
        buildDiscarder(logRotator(
            numToKeepStr: '30',        // Keep last 30 builds
            daysToKeepStr: '90',       // Keep 90 days
            artifactNumToKeepStr: '10', // Keep artifacts for 10 builds
            artifactDaysToKeepStr: '30' // Keep artifacts for 30 days
        ))
    }
}
```

### 2. Clean Workspace

```groovy
pipeline {
    agent any
    options {
        skipDefaultCheckout()
    }
    stages {
        stage('Build') {
            steps {
                cleanWs()  // Clean before build
                checkout scm
                sh 'make build'
            }
        }
    }
    post {
        always {
            cleanWs()  // Clean after build
        }
    }
}
```

### 3. Workspace Cleanup Script

```groovy
// Script Console - cleanup old workspaces
import hudson.model.*

Jenkins.instance.nodes.each { node ->
    node.getWorkspaceFor(Jenkins.instance.getAllItems(AbstractProject.class).first())?.deleteRecursive()
}

Jenkins.instance.getAllItems(AbstractProject.class).each { project ->
    def workspace = project.someWorkspace
    if (workspace != null) {
        println "Checking: ${project.name}"
        def lastBuild = project.lastBuild
        if (lastBuild != null) {
            def age = System.currentTimeMillis() - lastBuild.getTimeInMillis()
            if (age > 7 * 24 * 60 * 60 * 1000) {  // 7 days
                println "  Deleting old workspace"
                workspace.deleteRecursive()
            }
        }
    }
}
```

### 4. Artifact Storage

**Use External Storage:**
```groovy
pipeline {
    agent any
    stages {
        stage('Archive') {
            steps {
                // Upload to S3 instead of Jenkins
                withAWS(credentials: 'aws-creds') {
                    s3Upload(
                        bucket: 'build-artifacts',
                        path: "${env.JOB_NAME}/${env.BUILD_NUMBER}/",
                        includePathPattern: '**/*.jar'
                    )
                }
            }
        }
    }
}
```

## Plugin Management

### 1. Minimize Plugins

```bash
# List installed plugins
java -jar jenkins-cli.jar -s http://jenkins/ list-plugins

# Disable unnecessary plugins
java -jar jenkins-cli.jar -s http://jenkins/ disable-plugin PLUGIN_NAME
```

### 2. Update Plugins Regularly

```groovy
// Check for updates
import jenkins.model.Jenkins

Jenkins.instance.updateCenter.getSites().each { site ->
    site.updateDirectlyNow(hudson.model.DownloadService.signatureCheck)
}

def updates = Jenkins.instance.pluginManager.plugins.findAll {
    it.hasUpdate()
}

updates.each {
    println "${it.shortName}: ${it.version} → ${it.updateInfo.version}"
}
```

### 3. Monitor Plugin Performance

```groovy
// Find slow plugins
import jenkins.model.Jenkins

Jenkins.instance.pluginManager.plugins.each { plugin ->
    def loadTime = plugin.@loadTime
    if (loadTime > 1000) {  // More than 1 second
        println "${plugin.shortName}: ${loadTime}ms"
    }
}
```

## Database & Storage

### 1. Use External Database

**For build history:**
```xml
<!-- Install PostgreSQL plugin -->
<plugin>
    <groupId>org.jenkins-ci.plugins</groupId>
    <artifactId>database-postgresql</artifactId>
</plugin>
```

### 2. Optimize XML Storage

```bash
# Compress old builds
find $JENKINS_HOME/jobs/*/builds -type f -name "build.xml" -mtime +30 -exec gzip {} \;

# Remove old logs
find $JENKINS_HOME/jobs/*/builds/*/log -mtime +30 -delete
```

### 3. Use SSD for JENKINS_HOME

```bash
# Mount SSD for Jenkins
sudo mkdir -p /var/jenkins_home
sudo mount /dev/nvme0n1 /var/jenkins_home
sudo chown jenkins:jenkins /var/jenkins_home
```

## Network Optimization

### 1. Artifact Registry Cache

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                // Use local artifact cache
                sh '''
                    mvn clean package \
                        -Dmaven.repo.local=/cache/maven \
                        -DskipTests
                '''
            }
        }
    }
}
```

### 2. Mirror Repositories

**Maven settings.xml:**
```xml
<mirrors>
    <mirror>
        <id>internal-mirror</id>
        <name>Internal Mirror</name>
        <url>http://internal-nexus:8081/repository/maven-public/</url>
        <mirrorOf>*</mirrorOf>
    </mirror>
</mirrors>
```

### 3. Optimize Git Clone

```groovy
checkout([
    $class: 'GitSCM',
    branches: [[name: '*/main']],
    extensions: [[
        $class: 'CloneOption',
        depth: 1,
        noTags: true,
        reference: '/var/cache/git-reference',  // Reference repo
        shallow: true,
        timeout: 10
    ]],
    userRemoteConfigs: [[url: 'https://github.com/user/repo.git']]
])
```

## Monitoring & Alerting

### Performance Dashboards

**Grafana Dashboard:**
```json
{
  "dashboard": {
    "title": "Jenkins Performance",
    "panels": [
      {
        "title": "Build Duration",
        "targets": [{
          "expr": "jenkins_builds_duration_milliseconds_summary"
        }]
      },
      {
        "title": "Queue Length",
        "targets": [{
          "expr": "jenkins_queue_size_value"
        }]
      },
      {
        "title": "Executor Utilization",
        "targets": [{
          "expr": "(jenkins_executor_in_use_value / jenkins_executor_count_value) * 100"
        }]
      }
    ]
  }
}
```

### Performance Alerts

```yaml
groups:
  - name: jenkins_performance
    rules:
      - alert: SlowBuilds
        expr: |
          avg(rate(jenkins_builds_duration_milliseconds_summary_sum[1h]) /
              rate(jenkins_builds_duration_milliseconds_summary_count[1h])) > 600000
        annotations:
          description: "Average build time > 10 minutes"
      
      - alert: HighQueueLength
        expr: jenkins_queue_size_value > 20
        annotations:
          description: "Build queue has {{ $value }} items"
      
      - alert: LowExecutorUtilization
        expr: |
          (jenkins_executor_in_use_value / jenkins_executor_count_value) < 0.3
        annotations:
          description: "Only {{ $value }}% executors in use"
```

## Real-World Optimization Case Study

### Before Optimization

**Problems:**
- Average build time: 45 minutes
- Queue wait time: 15 minutes
- 5 concurrent builds max
- Disk space issues

**Metrics:**
```
Build duration: 45min
Queue time: 15min
Success rate: 75%
Disk usage: 95%
```

### After Optimization

**Changes:**
1. Added Kubernetes agents (20 concurrent builds)
2. Implemented parallel stages
3. Added Maven dependency cache
4. Shallow Git clones
5. External artifact storage (S3)
6. Optimized JVM settings

**Results:**
```
Build duration: 12min (73% faster)
Queue time: 2min (87% faster)
Success rate: 92% (17% improvement)
Disk usage: 45% (50% reduction)
```

**Configuration:**
```groovy
pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: maven
    image: maven:3.8-jdk-11
    resources:
      requests:
        memory: "2Gi"
        cpu: "1000m"
      limits:
        memory: "4Gi"
        cpu: "2000m"
    volumeMounts:
    - name: maven-cache
      mountPath: /root/.m2
  volumes:
  - name: maven-cache
    persistentVolumeClaim:
      claimName: maven-cache-pvc
'''
        }
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '5'))
        timeout(time: 20, unit: 'MINUTES')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    extensions: [[
                        $class: 'CloneOption',
                        depth: 1,
                        shallow: true
                    ]]
                ])
            }
        }
        
        stage('Build & Test') {
            parallel {
                stage('Build') {
                    steps {
                        container('maven') {
                            sh 'mvn clean package -DskipTests'
                        }
                    }
                }
                stage('Unit Tests') {
                    steps {
                        container('maven') {
                            sh 'mvn test'
                        }
                    }
                }
            }
        }
        
        stage('Archive to S3') {
            steps {
                withAWS(credentials: 'aws-creds') {
                    s3Upload(
                        bucket: 'artifacts',
                        path: "${env.JOB_NAME}/${env.BUILD_NUMBER}/"
                    )
                }
            }
        }
    }
}
```

## Best Practices Checklist

✅ **JVM Tuning:**
- [ ] Heap size configured appropriately
- [ ] Using G1GC
- [ ] GC logs enabled

✅ **Builds:**
- [ ] Parallel stages where possible
- [ ] Shallow Git clones
- [ ] Dependency caching
- [ ] Incremental builds

✅ **Agents:**
- [ ] Ephemeral agents (Docker/K8s)
- [ ] Proper resource limits
- [ ] Load balancing

✅ **Storage:**
- [ ] Build retention policies
- [ ] Workspace cleanup
- [ ] External artifact storage
- [ ] SSD for JENKINS_HOME

✅ **Plugins:**
- [ ] Only necessary plugins installed
- [ ] Plugins up to date
- [ ] Performance monitored

✅ **Monitoring:**
- [ ] Prometheus metrics enabled
- [ ] Grafana dashboards
- [ ] Performance alerts

## Summary

Key optimization areas:
- JVM configuration and heap tuning
- Parallel execution and incremental builds
- Ephemeral agents and resource limits
- Storage management and cleanup
- Plugin optimization
- Caching and external storage

**Impact:**
- 50-80% faster build times
- 5-10x more concurrent builds
- 60-80% disk space reduction
- Higher success rates

## Next Steps

- **Enterprise Patterns** → Scale Jenkins for teams
- **Monitoring** → Track performance metrics
- **Practice Labs** → Apply optimizations

---

**Previous:** [Configuration as Code](18-configuration-as-code.md)  
**Next:** [Enterprise Patterns](20-enterprise-patterns.md)
