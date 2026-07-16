# Testing in Jenkins Pipelines

## Overview

Automated testing in Jenkins pipelines ensures code quality and catches bugs early. This guide covers unit testing, integration testing, E2E testing, test reporting, and quality gates.

## Testing Strategy

### Test Pyramid

```
        /\
       /E2E\       <- Few, slow, expensive
      /──────\
     /  Int.  \    <- Some, moderate speed
    /──────────\
   /    Unit    \  <- Many, fast, cheap
  /──────────────\
```

**Guidelines:**
- **Unit Tests**: 70% of tests (fast, isolated)
- **Integration Tests**: 20% of tests (moderate, component interaction)
- **E2E Tests**: 10% of tests (slow, full workflow)

## Unit Testing

### Node.js with Jest

**Pipeline:**
```groovy
pipeline {
    agent {
        docker {
            image 'node:16'
        }
    }
    
    stages {
        stage('Install') {
            steps {
                sh 'npm ci'
            }
        }
        
        stage('Unit Tests') {
            steps {
                sh 'npm test -- --ci --coverage'
            }
        }
        
        stage('Publish Results') {
            steps {
                junit 'test-results/junit.xml'
                
                publishHTML([
                    reportDir: 'coverage',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report'
                ])
            }
        }
    }
}
```

**package.json:**
```json
{
  "scripts": {
    "test": "jest",
    "test:ci": "jest --ci --coverage --reporters=default --reporters=jest-junit"
  },
  "jest": {
    "coverageDirectory": "coverage",
    "coverageReporters": ["html", "text", "lcov"],
    "reporters": [
      "default",
      ["jest-junit", {
        "outputDirectory": "test-results",
        "outputName": "junit.xml"
      }]
    ]
  }
}
```

### Java with JUnit

**Pipeline:**
```groovy
pipeline {
    agent {
        docker {
            image 'maven:3.8-openjdk-11'
            args '-v $HOME/.m2:/root/.m2'
        }
    }
    
    stages {
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
        
        stage('Publish Results') {
            steps {
                junit '**/target/surefire-reports/*.xml'
                
                jacoco(
                    execPattern: '**/target/jacoco.exec',
                    classPattern: '**/target/classes',
                    sourcePattern: '**/src/main/java'
                )
            }
        }
    }
}
```

### Python with pytest

**Pipeline:**
```groovy
pipeline {
    agent {
        docker {
            image 'python:3.9'
        }
    }
    
    stages {
        stage('Install') {
            steps {
                sh '''
                    pip install -r requirements.txt
                    pip install pytest pytest-cov pytest-html
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                sh '''
                    pytest tests/ \\
                        --junit-xml=test-results/junit.xml \\
                        --html=test-results/report.html \\
                        --cov=src \\
                        --cov-report=html \\
                        --cov-report=xml
                '''
            }
        }
        
        stage('Publish Results') {
            steps {
                junit 'test-results/junit.xml'
                
                publishHTML([
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report'
                ])
            }
        }
    }
}
```

### Go with Testing Package

**Pipeline:**
```groovy
pipeline {
    agent {
        docker {
            image 'golang:1.19'
        }
    }
    
    stages {
        stage('Test') {
            steps {
                sh '''
                    go test -v ./... -coverprofile=coverage.out -covermode=atomic
                    go tool cover -html=coverage.out -o coverage.html
                '''
            }
        }
        
        stage('Publish') {
            steps {
                publishHTML([
                    reportDir: '.',
                    reportFiles: 'coverage.html',
                    reportName: 'Coverage Report'
                ])
            }
        }
    }
}
```

## Integration Testing

### Database Integration Tests

```groovy
pipeline {
    agent any
    
    stages {
        stage('Start Services') {
            steps {
                sh '''
                    docker-compose -f docker-compose.test.yml up -d
                    sleep 10  # Wait for services to start
                '''
            }
        }
        
        stage('Run Integration Tests') {
            steps {
                sh '''
                    export DB_HOST=localhost
                    export DB_PORT=5432
                    npm run test:integration
                '''
            }
        }
    }
    
    post {
        always {
            sh 'docker-compose -f docker-compose.test.yml down -v'
            junit 'test-results/integration/*.xml'
        }
    }
}
```

**docker-compose.test.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    ports:
      - "5432:5432"
    
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
```

### API Integration Tests

```groovy
pipeline {
    agent any
    
    stages {
        stage('Start Application') {
            steps {
                sh '''
                    docker build -t myapp:test .
                    docker run -d --name myapp-test -p 3000:3000 myapp:test
                    sleep 5  # Wait for app to start
                '''
            }
        }
        
        stage('Integration Tests') {
            steps {
                sh '''
                    npm run test:api -- \\
                        --baseUrl=http://localhost:3000 \\
                        --reporter=junit \\
                        --reporter-options=output=test-results/api-tests.xml
                '''
            }
        }
    }
    
    post {
        always {
            sh 'docker rm -f myapp-test || true'
            junit 'test-results/api-tests.xml'
        }
    }
}
```

## End-to-End (E2E) Testing

### Selenium Tests

```groovy
pipeline {
    agent any
    
    stages {
        stage('Start Selenium Grid') {
            steps {
                sh '''
                    docker run -d --name selenium-hub \\
                        -p 4444:4444 \\
                        selenium/hub:4.8.0
                    
                    docker run -d --name chrome-node \\
                        --link selenium-hub:hub \\
                        selenium/node-chrome:4.8.0
                    
                    sleep 10
                '''
            }
        }
        
        stage('Run E2E Tests') {
            steps {
                sh '''
                    npm run test:e2e -- \\
                        --selenium-hub=http://localhost:4444 \\
                        --baseUrl=http://staging.example.com
                '''
            }
        }
    }
    
    post {
        always {
            sh '''
                docker rm -f selenium-hub chrome-node || true
            '''
            junit 'test-results/e2e/*.xml'
            
            publishHTML([
                reportDir: 'test-results/screenshots',
                reportFiles: 'index.html',
                reportName: 'Test Screenshots'
            ])
        }
    }
}
```

### Cypress Tests

```groovy
pipeline {
    agent {
        docker {
            image 'cypress/included:12.0.0'
            args '--entrypoint='
        }
    }
    
    stages {
        stage('E2E Tests') {
            steps {
                sh '''
                    cypress run \\
                        --browser chrome \\
                        --headless \\
                        --reporter junit \\
                        --reporter-options "mochaFile=test-results/cypress-[hash].xml"
                '''
            }
        }
    }
    
    post {
        always {
            junit 'test-results/*.xml'
            
            publishHTML([
                reportDir: 'cypress/videos',
                reportFiles: '*.mp4',
                reportName: 'Test Videos'
            ])
            
            publishHTML([
                reportDir: 'cypress/screenshots',
                reportFiles: '**/*.png',
                reportName: 'Test Screenshots'
            ])
        }
    }
}
```

### Playwright Tests

```groovy
pipeline {
    agent {
        docker {
            image 'mcr.microsoft.com/playwright:v1.30.0'
        }
    }
    
    stages {
        stage('Install') {
            steps {
                sh 'npm ci'
            }
        }
        
        stage('E2E Tests') {
            steps {
                sh '''
                    npx playwright test \\
                        --reporter=junit \\
                        --reporter=html
                '''
            }
        }
    }
    
    post {
        always {
            junit 'test-results/junit.xml'
            
            publishHTML([
                reportDir: 'playwright-report',
                reportFiles: 'index.html',
                reportName: 'Playwright Report'
            ])
        }
    }
}
```

## Test Reporting

### JUnit Test Results

```groovy
stage('Publish Test Results') {
    steps {
        // Basic usage
        junit 'test-results/**/*.xml'
        
        // Advanced configuration
        junit(
            testResults: 'test-results/**/*.xml',
            allowEmptyResults: false,
            keepLongStdio: true,
            testDataPublishers: [
                [$class: 'AttachmentPublisher']
            ]
        )
    }
}
```

### TestNG Results

```groovy
stage('Publish TestNG Results') {
    steps {
        step([
            $class: 'Publisher',
            testResults: '**/testng-results.xml',
            allowEmptyResults: false
        ])
    }
}
```

### HTML Reports

```groovy
stage('Publish HTML Report') {
    steps {
        publishHTML([
            reportDir: 'target/site/jacoco',
            reportFiles: 'index.html',
            reportName: 'JaCoCo Coverage',
            allowMissing: false,
            alwaysLinkToLastBuild: true,
            keepAll: true
        ])
    }
}
```

### Allure Reports

**Install Plugin:**
```
Allure Plugin
```

**Pipeline:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Test') {
            steps {
                sh 'mvn clean test'
            }
        }
    }
    
    post {
        always {
            allure([
                includeProperties: false,
                jdk: '',
                results: [[path: 'target/allure-results']]
            ])
        }
    }
}
```

## Code Coverage

### JaCoCo (Java)

**pom.xml:**
```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.8</version>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

**Pipeline:**
```groovy
stage('Coverage') {
    steps {
        jacoco(
            execPattern: '**/target/jacoco.exec',
            classPattern: '**/target/classes',
            sourcePattern: '**/src/main/java',
            exclusionPattern: '**/test/**',
            changeBuildStatus: true,
            minimumInstructionCoverage: '80',
            maximumInstructionCoverage: '90'
        )
    }
}
```

### Istanbul/NYC (JavaScript)

```groovy
stage('Coverage') {
    steps {
        sh 'npm run test:coverage'
        
        publishHTML([
            reportDir: 'coverage',
            reportFiles: 'index.html',
            reportName: 'Coverage Report'
        ])
        
        // Cobertura format
        cobertura(
            coberturaReportFile: 'coverage/cobertura-coverage.xml',
            onlyStable: false,
            failUnhealthy: true,
            failUnstable: true,
            autoUpdateHealth: true,
            autoUpdateStability: true,
            zoomCoverageChart: true,
            maxNumberOfBuilds: 10,
            lineCoverageTargets: '80, 70, 60',
            conditionalCoverageTargets: '80, 70, 60',
            methodCoverageTargets: '80, 70, 60'
        )
    }
}
```

### Coverage.py (Python)

```groovy
stage('Coverage') {
    steps {
        sh '''
            pytest --cov=src --cov-report=xml --cov-report=html
        '''
        
        cobertura(
            coberturaReportFile: 'coverage.xml',
            failNoReports: false
        )
    }
}
```

## Quality Gates

### SonarQube Integration

**Install Plugin:**
```
SonarQube Scanner Plugin
```

**Configure:**
```
Manage Jenkins → Configure System → SonarQube servers

Name: SonarQube
Server URL: http://sonarqube.company.com
Server authentication token: [SonarQube token]
```

**Pipeline:**
```groovy
pipeline {
    agent any
    
    environment {
        SCANNER_HOME = tool 'SonarQube Scanner'
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }
        
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        ${SCANNER_HOME}/bin/sonar-scanner \\
                            -Dsonar.projectKey=myproject \\
                            -Dsonar.sources=src \\
                            -Dsonar.java.binaries=target/classes \\
                            -Dsonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml
                    '''
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }
}
```

### Custom Quality Gates

```groovy
stage('Quality Checks') {
    steps {
        script {
            // Check test coverage
            def coverage = readFile('coverage/coverage-summary.json')
            def coverageJson = readJSON text: coverage
            def lineCoverage = coverageJson.total.lines.pct
            
            if (lineCoverage < 80) {
                error("Coverage ${lineCoverage}% is below threshold 80%")
            }
            
            // Check test pass rate
            def testResults = junit 'test-results/**/*.xml'
            def passRate = (testResults.totalCount - testResults.failCount) / testResults.totalCount * 100
            
            if (passRate < 95) {
                error("Test pass rate ${passRate}% is below threshold 95%")
            }
        }
    }
}
```

## Parallel Test Execution

### Split Tests Across Agents

```groovy
pipeline {
    agent none
    
    stages {
        stage('Parallel Tests') {
            parallel {
                stage('Unit Tests - Set 1') {
                    agent { label 'test-runner' }
                    steps {
                        sh 'npm test -- tests/unit/set1/**'
                    }
                }
                
                stage('Unit Tests - Set 2') {
                    agent { label 'test-runner' }
                    steps {
                        sh 'npm test -- tests/unit/set2/**'
                    }
                }
                
                stage('Integration Tests') {
                    agent { label 'test-runner' }
                    steps {
                        sh 'npm run test:integration'
                    }
                }
                
                stage('E2E Tests') {
                    agent { label 'test-runner' }
                    steps {
                        sh 'npm run test:e2e'
                    }
                }
            }
        }
    }
    
    post {
        always {
            node('master') {
                junit '**/test-results/**/*.xml'
            }
        }
    }
}
```

### Matrix Testing

```groovy
pipeline {
    agent none
    
    stages {
        stage('Test Matrix') {
            matrix {
                agent any
                axes {
                    axis {
                        name 'PLATFORM'
                        values 'linux', 'mac', 'windows'
                    }
                    axis {
                        name 'BROWSER'
                        values 'chrome', 'firefox', 'safari'
                    }
                }
                stages {
                    stage('Test') {
                        steps {
                            echo "Testing on ${PLATFORM} with ${BROWSER}"
                            sh "npm run test:e2e -- --platform=${PLATFORM} --browser=${BROWSER}"
                        }
                    }
                }
            }
        }
    }
}
```

## Test Performance Monitoring

### Track Test Duration

```groovy
pipeline {
    agent any
    
    stages {
        stage('Test') {
            steps {
                script {
                    def startTime = System.currentTimeMillis()
                    
                    sh 'npm test'
                    
                    def duration = System.currentTimeMillis() - startTime
                    echo "Tests completed in ${duration}ms"
                    
                    if (duration > 300000) {  // 5 minutes
                        unstable('Tests took longer than expected')
                    }
                }
            }
        }
    }
}
```

### Performance Tests

```groovy
stage('Performance Tests') {
    steps {
        sh '''
            artillery run performance-test.yml \\
                --output test-results/artillery.json
        '''
        
        performanceReport(
            sourceDataFiles: 'test-results/artillery.json',
            errorUnstableThreshold: 5,
            errorFailedThreshold: 10,
            errorUnstableResponseTimeThreshold: 2000
        )
    }
}
```

## Best Practices

### 1. Fail Fast

```groovy
pipeline {
    agent any
    
    options {
        timeout(time: 30, unit: 'MINUTES')
    }
    
    stages {
        stage('Quick Tests') {
            steps {
                sh 'npm run test:quick'
            }
        }
        
        stage('Full Test Suite') {
            steps {
                sh 'npm test'
            }
        }
    }
}
```

### 2. Test Isolation

```groovy
stage('Test') {
    steps {
        sh '''
            # Clean state before tests
            docker-compose down -v
            docker-compose up -d
            sleep 5
            
            # Run tests
            npm test
            
            # Cleanup
            docker-compose down -v
        '''
    }
}
```

### 3. Retry Flaky Tests

```groovy
stage('Test') {
    steps {
        retry(3) {
            sh 'npm test'
        }
    }
}
```

### 4. Store Test Artifacts

```groovy
post {
    always {
        archiveArtifacts(
            artifacts: 'test-results/**/*',
            allowEmptyArchive: true
        )
        
        junit 'test-results/**/*.xml'
    }
}
```

## Summary

Comprehensive testing in Jenkins includes:
- Unit tests (fast, isolated)
- Integration tests (components)
- E2E tests (full workflow)
- Coverage reporting
- Quality gates
- Parallel execution

**Key Points:**
- Follow test pyramid
- Fail fast with quick tests
- Report all test results
- Set coverage thresholds
- Use quality gates
- Monitor test performance

---

**Previous:** [← Docker Integration](09-docker-integration.md) | **Next:** [Plugins →](11-plugins.md)
