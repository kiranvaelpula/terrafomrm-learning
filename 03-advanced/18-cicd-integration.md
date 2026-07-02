# Module 18: CI/CD Integration

## 📚 What You'll Learn
- CI/CD fundamentals for Terraform
- GitHub Actions workflows
- GitLab CI/CD pipelines
- Jenkins integration
- Terraform Cloud workflows
- Best practices for automation

---

## 🎯 CI/CD for Terraform

### CI/CD Goals
- ✅ Automated testing
- ✅ Consistent deployments
- ✅ Code review integration
- ✅ Environment promotion
- ✅ Rollback capabilities
- ✅ Audit trail

### Typical Workflow

```
Developer
    ↓
  Git Push
    ↓
  CI Pipeline
    ├── Format Check
    ├── Validation
    ├── Security Scan
    ├── Plan
    └── PR Comment with Plan
    ↓
Code Review & Approval
    ↓
  CD Pipeline
    ├── Terraform Apply
    ├── Integration Tests
    └── Notification
```

---

## 1️⃣ GitHub Actions

### Basic Workflow

```.github/workflows/terraform.yml
name: 'Terraform'

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main

env:
  TF_VERSION: '1.6.0'
  AWS_REGION: 'us-east-1'

jobs:
  terraform:
    name: 'Terraform'
    runs-on: ubuntu-latest
    
    # Use environment for secrets
    environment: production
    
    # Required permissions
    permissions:
      contents: read
      pull-requests: write
      id-token: write
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}
      
      - name: Terraform Format
        id: fmt
        run: terraform fmt -check
        continue-on-error: true
      
      - name: Terraform Init
        id: init
        run: terraform init
      
      - name: Terraform Validate
        id: validate
        run: terraform validate -no-color
      
      - name: Terraform Plan
        id: plan
        if: github.event_name == 'pull_request'
        run: terraform plan -no-color -input=false
        continue-on-error: true
      
      - name: Update Pull Request
        uses: actions/github-script@v6
        if: github.event_name == 'pull_request'
        env:
          PLAN: ${{ steps.plan.outputs.stdout }}
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const output = `#### Terraform Format and Style 🖌\`${{ steps.fmt.outcome }}\`
            #### Terraform Initialization ⚙️\`${{ steps.init.outcome }}\`
            #### Terraform Validation 🤖\`${{ steps.validate.outcome }}\`
            #### Terraform Plan 📖\`${{ steps.plan.outcome }}\`
            
            <details><summary>Show Plan</summary>
            
            \`\`\`terraform
            ${process.env.PLAN}
            \`\`\`
            
            </details>
            
            *Pushed by: @${{ github.actor }}, Action: \`${{ github.event_name }}\`*`;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            })
      
      - name: Terraform Plan Status
        if: steps.plan.outcome == 'failure'
        run: exit 1
      
      - name: Terraform Apply
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: terraform apply -auto-approve -input=false
```

---

## 🎪 Lab 1: Complete GitHub Actions Workflow

### Multi-Environment Setup

```.github/workflows/terraform-multi-env.yml
name: 'Terraform Multi-Environment'

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main
      - develop

env:
  TF_VERSION: '1.6.0'

jobs:
  changes:
    name: Detect Changes
    runs-on: ubuntu-latest
    outputs:
      environments: ${{ steps.filter.outputs.changes }}
    steps:
      - uses: actions/checkout@v3
      - uses: dorny/paths-filter@v2
        id: filter
        with:
          filters: |
            dev:
              - 'environments/dev/**'
            staging:
              - 'environments/staging/**'
            prod:
              - 'environments/prod/**'
  
  plan:
    name: Plan - ${{ matrix.environment }}
    runs-on: ubuntu-latest
    needs: changes
    if: needs.changes.outputs.environments != '[]'
    strategy:
      matrix:
        environment: ${{ fromJSON(needs.changes.outputs.environments) }}
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets[format('AWS_ROLE_ARN_{0}', matrix.environment)] }}
          aws-region: us-east-1
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}
      
      - name: Terraform Init
        working-directory: environments/${{ matrix.environment }}
        run: terraform init
      
      - name: Terraform Plan
        working-directory: environments/${{ matrix.environment }}
        run: |
          terraform plan -out=tfplan
          terraform show -no-color tfplan > plan.txt
      
      - name: Upload Plan
        uses: actions/upload-artifact@v3
        with:
          name: tfplan-${{ matrix.environment }}
          path: environments/${{ matrix.environment }}/tfplan
  
  apply:
    name: Apply - ${{ matrix.environment }}
    runs-on: ubuntu-latest
    needs: [changes, plan]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    strategy:
      matrix:
        environment: ${{ fromJSON(needs.changes.outputs.environments) }}
      max-parallel: 1  # Apply one environment at a time
    
    environment:
      name: ${{ matrix.environment }}
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets[format('AWS_ROLE_ARN_{0}', matrix.environment)] }}
          aws-region: us-east-1
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}
      
      - name: Download Plan
        uses: actions/download-artifact@v3
        with:
          name: tfplan-${{ matrix.environment }}
          path: environments/${{ matrix.environment }}
      
      - name: Terraform Apply
        working-directory: environments/${{ matrix.environment }}
        run: terraform apply -auto-approve tfplan
      
      - name: Notify Success
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: success
          text: 'Terraform applied successfully to ${{ matrix.environment }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
      
      - name: Notify Failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          text: 'Terraform apply failed for ${{ matrix.environment }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 2️⃣ GitLab CI/CD

### Complete Pipeline

```.gitlab-ci.yml
stages:
  - validate
  - plan
  - apply
  - destroy

variables:
  TF_ROOT: ${CI_PROJECT_DIR}
  TF_VERSION: "1.6.0"
  AWS_DEFAULT_REGION: "us-east-1"

cache:
  paths:
    - ${TF_ROOT}/.terraform

before_script:
  - cd ${TF_ROOT}
  - terraform --version

validate:
  stage: validate
  image:
    name: hashicorp/terraform:${TF_VERSION}
    entrypoint: [""]
  script:
    - terraform fmt -check
    - terraform init -backend=false
    - terraform validate
  only:
    - merge_requests
    - main

plan:dev:
  stage: plan
  image:
    name: hashicorp/terraform:${TF_VERSION}
    entrypoint: [""]
  script:
    - cd environments/dev
    - terraform init
    - terraform plan -out=tfplan
    - terraform show -no-color tfplan > plan.txt
  artifacts:
    paths:
      - environments/dev/tfplan
      - environments/dev/plan.txt
    expire_in: 1 week
  only:
    - merge_requests
    - main

plan:staging:
  stage: plan
  image:
    name: hashicorp/terraform:${TF_VERSION}
    entrypoint: [""]
  script:
    - cd environments/staging
    - terraform init
    - terraform plan -out=tfplan
  artifacts:
    paths:
      - environments/staging/tfplan
    expire_in: 1 week
  only:
    - main

plan:prod:
  stage: plan
  image:
    name: hashicorp/terraform:${TF_VERSION}
    entrypoint: [""]
  script:
    - cd environments/prod
    - terraform init
    - terraform plan -out=tfplan
  artifacts:
    paths:
      - environments/prod/tfplan
    expire_in: 1 week
  only:
    - main

apply:dev:
  stage: apply
  image:
    name: hashicorp/terraform:${TF_VERSION}
    entrypoint: [""]
  script:
    - cd environments/dev
    - terraform init
    - terraform apply -auto-approve tfplan
  dependencies:
    - plan:dev
  only:
    - main
  when: on_success

apply:staging:
  stage: apply
  image:
    name: hashicorp/terraform:${TF_VERSION}
    entrypoint: [""]
  script:
    - cd environments/staging
    - terraform init
    - terraform apply -auto-approve tfplan
  dependencies:
    - plan:staging
  only:
    - main
  when: manual

apply:prod:
  stage: apply
  image:
    name: hashicorp/terraform:${TF_VERSION}
    entrypoint: [""]
  script:
    - cd environments/prod
    - terraform init
    - terraform apply -auto-approve tfplan
  dependencies:
    - plan:prod
  environment:
    name: production
  only:
    - main
  when: manual

destroy:
  stage: destroy
  image:
    name: hashicorp/terraform:${TF_VERSION}
    entrypoint: [""]
  script:
    - cd environments/${ENVIRONMENT}
    - terraform init
    - terraform destroy -auto-approve
  when: manual
  only:
    - main
```

---

## 3️⃣ Jenkins Pipeline

### Jenkinsfile

```groovy
pipeline {
    agent any
    
    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'], description: 'Environment to deploy')
        choice(name: 'ACTION', choices: ['plan', 'apply', 'destroy'], description: 'Terraform action')
        booleanParam(name: 'AUTO_APPROVE', defaultValue: false, description: 'Auto-approve apply/destroy')
    }
    
    environment {
        TF_VERSION = '1.6.0'
        AWS_DEFAULT_REGION = 'us-east-1'
        TF_IN_AUTOMATION = 'true'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup') {
            steps {
                script {
                    // Install Terraform
                    sh '''
                        if ! command -v terraform &> /dev/null; then
                            wget https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip
                            unzip terraform_${TF_VERSION}_linux_amd64.zip
                            sudo mv terraform /usr/local/bin/
                        fi
                        terraform --version
                    '''
                }
            }
        }
        
        stage('Validate') {
            steps {
                dir("environments/${params.ENVIRONMENT}") {
                    sh '''
                        terraform fmt -check
                        terraform init -backend=false
                        terraform validate
                    '''
                }
            }
        }
        
        stage('Plan') {
            when {
                expression { params.ACTION == 'plan' || params.ACTION == 'apply' }
            }
            steps {
                dir("environments/${params.ENVIRONMENT}") {
                    withCredentials([
                        [
                            $class: 'AmazonWebServicesCredentialsBinding',
                            credentialsId: "aws-${params.ENVIRONMENT}",
                            accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                            secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                        ]
                    ]) {
                        sh '''
                            terraform init
                            terraform plan -out=tfplan
                            terraform show -no-color tfplan > plan.txt
                        '''
                    }
                    
                    // Archive plan
                    archiveArtifacts artifacts: 'tfplan,plan.txt'
                    
                    // Show plan in console
                    sh 'cat plan.txt'
                }
            }
        }
        
        stage('Approval') {
            when {
                expression { 
                    (params.ACTION == 'apply' || params.ACTION == 'destroy') && 
                    !params.AUTO_APPROVE 
                }
            }
            steps {
                script {
                    def userInput = input(
                        id: 'Proceed',
                        message: "Apply Terraform changes to ${params.ENVIRONMENT}?",
                        parameters: [
                            booleanParam(defaultValue: false, description: 'Confirm apply', name: 'confirm')
                        ]
                    )
                    
                    if (!userInput) {
                        error('User declined to proceed')
                    }
                }
            }
        }
        
        stage('Apply') {
            when {
                expression { params.ACTION == 'apply' }
            }
            steps {
                dir("environments/${params.ENVIRONMENT}") {
                    withCredentials([
                        [
                            $class: 'AmazonWebServicesCredentialsBinding',
                            credentialsId: "aws-${params.ENVIRONMENT}",
                            accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                            secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                        ]
                    ]) {
                        sh 'terraform apply -auto-approve tfplan'
                    }
                }
            }
        }
        
        stage('Destroy') {
            when {
                expression { params.ACTION == 'destroy' }
            }
            steps {
                dir("environments/${params.ENVIRONMENT}") {
                    withCredentials([
                        [
                            $class: 'AmazonWebServicesCredentialsBinding',
                            credentialsId: "aws-${params.ENVIRONMENT}",
                            accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                            secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                        ]
                    ]) {
                        sh 'terraform init'
                        sh 'terraform destroy -auto-approve'
                    }
                }
            }
        }
    }
    
    post {
        success {
            slackSend(
                color: 'good',
                message: "Terraform ${params.ACTION} succeeded for ${params.ENVIRONMENT}: ${env.BUILD_URL}"
            )
        }
        failure {
            slackSend(
                color: 'danger',
                message: "Terraform ${params.ACTION} failed for ${params.ENVIRONMENT}: ${env.BUILD_URL}"
            )
        }
        always {
            cleanWs()
        }
    }
}
```

---

## 4️⃣ Terraform Cloud

### Workspace Configuration

```hcl
# backend.tf
terraform {
  cloud {
    organization = "my-org"
    
    workspaces {
      name = "production"
    }
  }
}
```

### VCS-Driven Workflow

```hcl
# terraform.tf
terraform {
  cloud {
    organization = "my-org"
    
    workspaces {
      tags = ["app:myapp", "env:prod"]
    }
  }
}
```

### Trigger via API

```bash
# Create a run
curl \
  --header "Authorization: Bearer $TFC_TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request POST \
  --data @payload.json \
  https://app.terraform.io/api/v2/runs

# payload.json
{
  "data": {
    "attributes": {
      "message": "Triggered via API"
    },
    "type":"runs",
    "relationships": {
      "workspace": {
        "data": {
          "type": "workspaces",
          "id": "ws-xxxxxxxxxxxxx"
        }
      }
    }
  }
}
```

---

## 🔒 Security Best Practices

### 1. Use OIDC Instead of Long-Lived Credentials

```yaml
# GitHub Actions with OIDC
- name: Configure AWS Credentials
  uses: aws-actions/configure-aws-credentials@v2
  with:
    role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
    aws-region: us-east-1
```

### 2. Scan for Secrets

```yaml
- name: TruffleHog Scan
  uses: trufflesecurity/trufflehog@main
  with:
    path: ./
    base: main
    head: HEAD
```

### 3. Enforce Branch Protection

```yaml
# Only allow applies from main branch
- name: Terraform Apply
  if: github.ref == 'refs/heads/main'
  run: terraform apply -auto-approve
```

### 4. Use Environment Secrets

```yaml
jobs:
  deploy:
    environment: production
    steps:
      - uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
```

---

## 💡 Best Practices

### 1. Separate Plan and Apply

```yaml
# Two separate jobs
plan:
  runs-on: ubuntu-latest
  steps:
    - run: terraform plan -out=tfplan

apply:
  needs: plan
  runs-on: ubuntu-latest
  steps:
    - run: terraform apply tfplan
```

### 2. Add Manual Approval for Production

```yaml
deploy-prod:
  environment:
    name: production
  steps:
    - run: terraform apply
```

### 3. Notify on Failures

```yaml
- name: Slack Notification
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 4. Store Plans as Artifacts

```yaml
- name: Upload Plan
  uses: actions/upload-artifact@v3
  with:
    name: tfplan
    path: tfplan
```

### 5. Use Matrix for Multiple Environments

```yaml
strategy:
  matrix:
    environment: [dev, staging, prod]
steps:
  - run: terraform apply
    working-directory: environments/${{ matrix.environment }}
```

---

## 📝 Quiz

1. What's the difference between CI and CD in Terraform?
2. Why should you separate plan and apply stages?
3. What is OIDC and why use it?
4. How do you prevent accidental production deployments?
5. What should be stored as artifacts?

---

## 🎓 Challenge Exercise

Create a complete CI/CD pipeline with:
1. Multi-environment support (dev, staging, prod)
2. Automated testing
3. Security scanning
4. Manual approval for production
5. Slack notifications
6. Plan artifacts
7. Rollback capability

---

## ⏭️ Next Steps

Continue to [Module 19: Real-World Project](./19-real-world-project.md)

---

**🎉 Congratulations!** You can now automate Terraform deployments with CI/CD!
