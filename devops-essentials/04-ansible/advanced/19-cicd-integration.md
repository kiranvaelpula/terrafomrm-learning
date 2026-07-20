# CI/CD Integration

> **Integrate Ansible into your continuous delivery pipelines**

---

## 📖 What You'll Learn

- CI/CD pipeline concepts
- GitLab CI integration
- GitHub Actions
- Jenkins integration
- Azure DevOps
- Best practices

---

## 🔄 CI/CD Fundamentals

### Why Integrate Ansible?

**Benefits:**
- Automated deployments
- Consistent environments
- Version-controlled infrastructure
- Rollback capabilities
- Audit trail

**Common workflows:**
1. Code commit → Test → Deploy
2. PR merge → Staging deploy → Production deploy
3. Tag release → Build → Deploy

---

## 🦊 GitLab CI

### Basic Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - test
  - deploy

variables:
  ANSIBLE_FORCE_COLOR: "true"
  ANSIBLE_HOST_KEY_CHECKING: "false"

before_script:
  - apt-get update -qq
  - apt-get install -y ansible

validate:
  stage: validate
  script:
    - ansible-playbook --syntax-check site.yml
    - ansible-lint site.yml
  only:
    - merge_requests

test:
  stage: test
  script:
    - ansible-playbook site.yml --check --diff
  environment:
    name: staging
  only:
    - develop

deploy_staging:
  stage: deploy
  script:
    - echo "$ANSIBLE_VAULT_PASSWORD" > .vault_pass
    - ansible-playbook -i inventory/staging site.yml --vault-password-file .vault_pass
  after_script:
    - rm -f .vault_pass
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop

deploy_production:
  stage: deploy
  script:
    - echo "$ANSIBLE_VAULT_PASSWORD" > .vault_pass
    - ansible-playbook -i inventory/production site.yml --vault-password-file .vault_pass
  after_script:
    - rm -f .vault_pass
  environment:
    name: production
    url: https://example.com
  when: manual
  only:
    - main
```

### With Docker

```yaml
# .gitlab-ci.yml
image: williamyeh/ansible:ubuntu20.04

stages:
  - deploy

deploy:
  stage: deploy
  before_script:
    - mkdir -p ~/.ssh
    - echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
    - chmod 600 ~/.ssh/id_rsa
    - ssh-keyscan -H $DEPLOY_HOST >> ~/.ssh/known_hosts
  script:
    - ansible-playbook -i $DEPLOY_HOST, deploy.yml
  environment:
    name: production
```

---

## 🐙 GitHub Actions

### Basic Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy with Ansible

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Ansible
        run: |
          pip install ansible ansible-lint
      
      - name: Syntax check
        run: ansible-playbook --syntax-check site.yml
      
      - name: Lint playbooks
        run: ansible-lint site.yml

  test:
    runs-on: ubuntu-latest
    needs: validate
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Ansible
        run: pip install ansible
      
      - name: Check mode
        run: ansible-playbook site.yml --check

  deploy-staging:
    runs-on: ubuntu-latest
    needs: validate
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging.example.com
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.DEPLOY_HOST }} >> ~/.ssh/known_hosts
      
      - name: Setup Ansible
        run: pip install ansible
      
      - name: Deploy to staging
        env:
          ANSIBLE_VAULT_PASSWORD: ${{ secrets.ANSIBLE_VAULT_PASSWORD }}
        run: |
          echo "$ANSIBLE_VAULT_PASSWORD" > .vault_pass
          ansible-playbook -i inventory/staging site.yml --vault-password-file .vault_pass
          rm -f .vault_pass

  deploy-production:
    runs-on: ubuntu-latest
    needs: validate
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://example.com
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        uses: dawidd6/action-ansible-playbook@v2
        with:
          playbook: site.yml
          directory: ./
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          inventory: inventory/production
          vault_password: ${{ secrets.ANSIBLE_VAULT_PASSWORD }}
          options: |
            --verbose
```

### Matrix Strategy

```yaml
# .github/workflows/test.yml
name: Test Multiple Environments

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [dev, staging, prod]
        ansible_version: ['2.9', '2.10', '2.11']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Ansible ${{ matrix.ansible_version }}
        run: pip install ansible==${{ matrix.ansible_version }}.*
      
      - name: Test ${{ matrix.environment }}
        run: ansible-playbook -i inventory/${{ matrix.environment }} site.yml --check
```

---

## 🔨 Jenkins

### Declarative Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        ANSIBLE_FORCE_COLOR = 'true'
        ANSIBLE_HOST_KEY_CHECKING = 'false'
    }
    
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['staging', 'production'],
            description: 'Deployment environment'
        )
        booleanParam(
            name: 'DRY_RUN',
            defaultValue: false,
            description: 'Run in check mode'
        )
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Validate') {
            steps {
                sh 'ansible-playbook --syntax-check site.yml'
                sh 'ansible-lint site.yml || true'
            }
        }
        
        stage('Test') {
            when {
                branch 'develop'
            }
            steps {
                sh 'ansible-playbook site.yml --check --diff'
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    def checkMode = params.DRY_RUN ? '--check' : ''
                    
                    withCredentials([
                        string(credentialsId: 'ansible-vault-password', variable: 'VAULT_PASS'),
                        sshUserPrivateKey(credentialsId: 'ssh-key', keyFileVariable: 'SSH_KEY')
                    ]) {
                        sh """
                            echo \$VAULT_PASS > .vault_pass
                            ansible-playbook \\
                                -i inventory/${params.ENVIRONMENT} \\
                                site.yml \\
                                --vault-password-file .vault_pass \\
                                --private-key \$SSH_KEY \\
                                ${checkMode}
                            rm -f .vault_pass
                        """
                    }
                }
            }
        }
        
        stage('Verify') {
            steps {
                sh """
                    ansible-playbook \\
                        -i inventory/${params.ENVIRONMENT} \\
                        verify.yml
                """
            }
        }
    }
    
    post {
        success {
            slackSend(
                color: 'good',
                message: "Deployment to ${params.ENVIRONMENT} succeeded"
            )
        }
        failure {
            slackSend(
                color: 'danger',
                message: "Deployment to ${params.ENVIRONMENT} failed"
            )
        }
        always {
            cleanWs()
        }
    }
}
```

### Multi-Branch Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Deploy') {
            when {
                anyOf {
                    branch 'develop'
                    branch 'main'
                }
            }
            steps {
                script {
                    def environment = env.BRANCH_NAME == 'main' ? 'production' : 'staging'
                    
                    sh """
                        ansible-playbook \\
                            -i inventory/${environment} \\
                            site.yml
                    """
                }
            }
        }
    }
}
```

---

## ☁️ Azure DevOps

### YAML Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: ansible-secrets

stages:
  - stage: Validate
    jobs:
      - job: Syntax
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.10'
          
          - script: |
              pip install ansible ansible-lint
              ansible-playbook --syntax-check site.yml
              ansible-lint site.yml
            displayName: 'Validate playbooks'

  - stage: Deploy_Staging
    condition: eq(variables['Build.SourceBranch'], 'refs/heads/develop')
    jobs:
      - deployment: DeployStaging
        environment: staging
        strategy:
          runOnce:
            deploy:
              steps:
                - checkout: self
                
                - task: InstallSSHKey@0
                  inputs:
                    knownHostsEntry: '$(KNOWN_HOSTS)'
                    sshPublicKey: '$(SSH_PUBLIC_KEY)'
                    sshKeySecureFile: 'ansible_ssh_key'
                
                - script: |
                    pip install ansible
                    echo "$(VAULT_PASSWORD)" > .vault_pass
                    ansible-playbook -i inventory/staging site.yml --vault-password-file .vault_pass
                    rm -f .vault_pass
                  displayName: 'Deploy to staging'

  - stage: Deploy_Production
    condition: eq(variables['Build.SourceBranch'], 'refs/heads/main')
    jobs:
      - deployment: DeployProduction
        environment: production
        strategy:
          runOnce:
            deploy:
              steps:
                - checkout: self
                
                - task: InstallSSHKey@0
                  inputs:
                    knownHostsEntry: '$(KNOWN_HOSTS)'
                    sshPublicKey: '$(SSH_PUBLIC_KEY)'
                    sshKeySecureFile: 'ansible_ssh_key'
                
                - script: |
                    pip install ansible
                    echo "$(VAULT_PASSWORD)" > .vault_pass
                    ansible-playbook -i inventory/production site.yml --vault-password-file .vault_pass
                    rm -f .vault_pass
                  displayName: 'Deploy to production'
```

---

## 🎨 Best Practices

### 1. Separate Environments

```yaml
# .gitlab-ci.yml
deploy_dev:
  script: ansible-playbook -i inventory/dev site.yml
  environment: dev
  only: [develop]

deploy_prod:
  script: ansible-playbook -i inventory/prod site.yml
  environment: production
  when: manual
  only: [main]
```

### 2. Use Check Mode First

```yaml
steps:
  - name: Dry run
    run: ansible-playbook site.yml --check --diff
  
  - name: Actual deployment
    if: github.event_name != 'pull_request'
    run: ansible-playbook site.yml
```

### 3. Version Pin Ansible

```yaml
# requirements.txt
ansible==2.10.7
ansible-lint==5.4.0

# In CI
pip install -r requirements.txt
```

### 4. Validate Before Deploy

```yaml
stages:
  - validate:
      - syntax-check
      - lint
      - dry-run
  - deploy:
      - staging (auto)
      - production (manual)
```

### 5. Store Secrets Securely

```yaml
# Use CI/CD secrets, not hardcoded
env:
  ANSIBLE_VAULT_PASSWORD: ${{ secrets.VAULT_PASSWORD }}
  SSH_PRIVATE_KEY: ${{ secrets.SSH_KEY }}
  AWS_ACCESS_KEY: ${{ secrets.AWS_ACCESS_KEY }}
```

### 6. Add Rollback Capability

```groovy
stage('Rollback') {
    when {
        expression { currentBuild.result == 'FAILURE' }
    }
    steps {
        sh 'ansible-playbook rollback.yml'
    }
}
```

---

## 📚 Complete Example

### GitOps Workflow

```
Repository Structure:
├── .gitlab-ci.yml
├── ansible.cfg
├── requirements.yml
├── inventory/
│   ├── dev/
│   ├── staging/
│   └── production/
├── group_vars/
├── playbooks/
│   ├── site.yml
│   ├── rollback.yml
│   └── verify.yml
└── roles/
```

**.gitlab-ci.yml:**
```yaml
stages:
  - validate
  - test
  - deploy
  - verify
  - rollback

variables:
  ANSIBLE_FORCE_COLOR: "true"

.ansible_base:
  image: williamyeh/ansible:ubuntu20.04
  before_script:
    - ansible-galaxy install -r requirements.yml
    - mkdir -p ~/.ssh
    - echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
    - chmod 600 ~/.ssh/id_rsa

validate:
  extends: .ansible_base
  stage: validate
  script:
    - ansible-playbook --syntax-check playbooks/site.yml
    - ansible-lint playbooks/site.yml

test_staging:
  extends: .ansible_base
  stage: test
  script:
    - ansible-playbook -i inventory/staging playbooks/site.yml --check --diff
  only:
    - develop

deploy_staging:
  extends: .ansible_base
  stage: deploy
  script:
    - echo "$ANSIBLE_VAULT_PASSWORD" > .vault_pass
    - ansible-playbook -i inventory/staging playbooks/site.yml --vault-password-file .vault_pass
  after_script:
    - rm -f .vault_pass
  environment:
    name: staging
    on_stop: rollback_staging
  only:
    - develop

verify_staging:
  extends: .ansible_base
  stage: verify
  script:
    - ansible-playbook -i inventory/staging playbooks/verify.yml
  only:
    - develop

deploy_production:
  extends: .ansible_base
  stage: deploy
  script:
    - echo "$ANSIBLE_VAULT_PASSWORD" > .vault_pass
    - ansible-playbook -i inventory/production playbooks/site.yml --vault-password-file .vault_pass
  after_script:
    - rm -f .vault_pass
  environment:
    name: production
    on_stop: rollback_production
  when: manual
  only:
    - main

verify_production:
  extends: .ansible_base
  stage: verify
  script:
    - ansible-playbook -i inventory/production playbooks/verify.yml
  only:
    - main

rollback_staging:
  extends: .ansible_base
  stage: rollback
  script:
    - ansible-playbook -i inventory/staging playbooks/rollback.yml
  when: manual
  environment:
    name: staging
    action: stop

rollback_production:
  extends: .ansible_base
  stage: rollback
  script:
    - ansible-playbook -i inventory/production playbooks/rollback.yml
  when: manual
  environment:
    name: production
    action: stop
```

---

## ✅ Checklist

- [ ] Validate syntax in CI
- [ ] Run lint checks
- [ ] Test with --check mode
- [ ] Use environment branches (develop → staging, main → production)
- [ ] Store secrets in CI/CD variables
- [ ] Pin Ansible version
- [ ] Add manual approval for production
- [ ] Implement verification stage
- [ ] Enable rollback capability
- [ ] Send notifications on success/failure
- [ ] Clean up temporary files (vault passwords, SSH keys)
- [ ] Use caching for dependencies
- [ ] Add timeout limits
- [ ] Log deployments
- [ ] Monitor deployment metrics

---

## 🔗 What's Next?

- **Next:** [Enterprise Patterns](20-enterprise-patterns.md)
- **Previous:** [Security](18-security.md)
- **Related:** [Ansible Vault](../intermediate/11-ansible-vault.md)

---

**Pro Tip:** Always run `--check` mode in CI for pull requests to catch issues before merging!
