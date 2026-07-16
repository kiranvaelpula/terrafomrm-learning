# Jenkins Security and Access Control

## Overview

Security is critical for Jenkins deployments. This guide covers authentication, authorization, credential management, security hardening, and compliance best practices.

## Security Fundamentals

### The CIA Triad for Jenkins

**Confidentiality:**
- Protect credentials and secrets
- Secure build artifacts
- Control access to sensitive data

**Integrity:**
- Prevent unauthorized modifications
- Audit trail for changes
- Validate pipeline code

**Availability:**
- Backup Jenkins data
- High availability setup
- Disaster recovery plan

## Authentication

### Enable Security

```
Manage Jenkins → Configure Global Security
✓ Enable security
```

### Authentication Methods

#### 1. Jenkins' Own User Database

**Best for:** Small teams, development

```
Security Realm: Jenkins' own user database
✓ Allow users to sign up (disable after creating users!)
```

**Create Admin User:**
```
Manage Jenkins → Manage Users → Create User
Username: admin
Password: [Strong password]
Full name: Administrator
Email: admin@company.com
```

#### 2. LDAP Integration

**Best for:** Enterprise environments

```
Security Realm: LDAP

Server: ldap://ldap.company.com
root DN: dc=company,dc=com
User search base: ou=users
User search filter: uid={0}
Group search base: ou=groups
```

**Test LDAP:**
```
Test LDAP settings
Username: testuser
Password: [password]
```

#### 3. Active Directory

**Best for:** Windows environments

```
Security Realm: Active Directory

Domain: company.com
Domain Controllers: dc1.company.com:3268,dc2.company.com:3268
Site: Default
Bind DN: cn=jenkins,cn=Users,dc=company,dc=com
Bind Password: [password]
```

#### 4. OAuth (GitHub/GitLab/Google)

**GitHub Example:**

**Install Plugin:**
```
GitHub Authentication Plugin
```

**Configure:**
```
Security Realm: GitHub Authentication Plugin

GitHub Web URI: https://github.com
GitHub API URI: https://api.github.com
Client ID: [from GitHub OAuth App]
Client Secret: [from GitHub OAuth App]

Authorized Organizations: yourorg
Admin User Names: admin1,admin2
```

**Create GitHub OAuth App:**
```
GitHub → Settings → Developer settings → OAuth Apps
Application name: Jenkins CI
Homepage URL: https://jenkins.company.com
Authorization callback URL: https://jenkins.company.com/securityRealm/finishLogin
```

#### 5. SAML 2.0

**Best for:** Enterprise SSO

**Install Plugin:**
```
SAML Plugin
```

**Configure:**
```
Security Realm: SAML 2.0

IdP Metadata: [URL or XML]
SP Entity ID: https://jenkins.company.com
```

## Authorization

### Authorization Strategies

#### 1. Matrix-Based Security

**Simple permissions matrix:**

```
Authorization: Matrix-based security

User/Group         Overall  Agent  Job    View   SCM
admin              ✓ All    ✓ All  ✓ All  ✓ All  ✓ All
developers         ✓ Read   ✓ Read ✓ All  ✓ All  ✓ Read
viewers            ✓ Read   -      ✓ Read ✓ Read -
Anonymous          ✓ Read   -      -      ✓ Read -
```

**Permissions:**
- **Overall**: Jenkins-wide permissions
- **Agent**: Build agent management
- **Job**: Job creation and configuration
- **View**: View access
- **SCM**: Source control operations

#### 2. Project-Based Matrix

**Job-specific permissions:**

```
Authorization: Project-based Matrix Authorization Strategy

Global permissions (same as matrix-based)

Per-project permissions (in job config):
  developers: Build, Read, Configure
  testers: Build, Read
```

**Enable in Job:**
```
Job Configuration → Enable project-based security
Add users/groups with specific permissions
```

#### 3. Role-Based Access Control (RBAC)

**Install Plugin:**
```
Role-based Authorization Strategy Plugin
```

**Configure Roles:**
```
Manage Jenkins → Manage and Assign Roles → Manage Roles

Global Roles:
  admin: Overall Administer
  developer: Overall Read, Job Build/Cancel/Read/Workspace
  viewer: Overall Read, Job Read

Project Roles:
  frontend-dev: Pattern: frontend-.*
    Permissions: Job Build/Configure/Read
  backend-dev: Pattern: backend-.*
    Permissions: Job Build/Configure/Read
```

**Assign Roles:**
```
Manage and Assign Roles → Assign Roles

Global roles:
  admin: user-admin
  developer: dev-team
  viewer: all-users

Project roles:
  frontend-dev: frontend-team
  backend-dev: backend-team
```

## Credential Management

### Types of Credentials

#### 1. Username with Password

```
Manage Jenkins → Manage Credentials → Global → Add Credentials

Kind: Username with password
Scope: Global
Username: myuser
Password: [secure password]
ID: github-credentials
Description: GitHub access
```

#### 2. SSH Username with Private Key

```
Kind: SSH Username with private key
Scope: Global
ID: ssh-deploy-key
Username: git
Private Key: Enter directly
[Paste private key]
Passphrase: [if key is encrypted]
Description: Deployment SSH key
```

#### 3. Secret Text

```
Kind: Secret text
Scope: Global
Secret: [API token or password]
ID: api-token
Description: API authentication token
```

#### 4. Secret File

```
Kind: Secret file
Scope: Global
File: [Upload .kube/config, certificate, etc.]
ID: kubeconfig
Description: Kubernetes config
```

#### 5. Certificate

```
Kind: Certificate
Scope: Global
Certificate: Upload PKCS#12 file
Password: [certificate password]
ID: ssl-cert
Description: SSL Certificate
```

### Using Credentials in Pipelines

#### Username/Password

```groovy
pipeline {
    agent any
    
    stages {
        stage('Deploy') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-credentials',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_PASS'
                )]) {
                    sh '''
                        git clone https://${GIT_USER}:${GIT_PASS}@github.com/repo.git
                    '''
                }
            }
        }
    }
}
```

#### SSH Key

```groovy
stage('Deploy') {
    steps {
        sshagent(credentials: ['ssh-deploy-key']) {
            sh '''
                ssh user@server 'deploy-script.sh'
                scp artifact.jar user@server:/opt/app/
            '''
        }
    }
}
```

#### Secret Text

```groovy
stage('API Call') {
    steps {
        withCredentials([string(
            credentialsId: 'api-token',
            variable: 'API_TOKEN'
        )]) {
            sh '''
                curl -H "Authorization: Bearer ${API_TOKEN}" \\
                     https://api.example.com/deploy
            '''
        }
    }
}
```

#### Secret File

```groovy
stage('Kubernetes Deploy') {
    steps {
        withCredentials([file(
            credentialsId: 'kubeconfig',
            variable: 'KUBECONFIG'
        )]) {
            sh '''
                kubectl --kubeconfig=${KUBECONFIG} apply -f deployment.yaml
            '''
        }
    }
}
```

#### Multiple Credentials

```groovy
stage('Deploy') {
    steps {
        withCredentials([
            usernamePassword(
                credentialsId: 'docker-hub',
                usernameVariable: 'DOCKER_USER',
                passwordVariable: 'DOCKER_PASS'
            ),
            string(
                credentialsId: 'deploy-token',
                variable: 'DEPLOY_TOKEN'
            ),
            file(
                credentialsId: 'kubeconfig',
                variable: 'KUBECONFIG'
            )
        ]) {
            sh '''
                echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
                kubectl --kubeconfig=${KUBECONFIG} set image deployment/app app=myapp:latest
            '''
        }
    }
}
```

### Credential Scopes

| Scope | Description | Use Case |
|-------|-------------|----------|
| **Global** | Available everywhere | Shared credentials |
| **System** | Only for Jenkins system | Agent connections |
| **Project** | Specific folder/job | Team-specific creds |

**Example: Folder-Scoped Credentials**

```
Create folder: frontend-team
Folder Credentials: frontend-github-token (scoped to this folder)
Jobs in folder: Can use frontend-github-token
Jobs outside folder: Cannot access
```

## Security Hardening

### 1. Enable CSRF Protection

```
Configure Global Security
✓ Prevent Cross Site Request Forgery exploits
  Default Crumb Issuer
```

### 2. Disable CLI Over Remoting

```
Configure Global Security
Agent Protocols:
  ✗ Uncheck all deprecated protocols
  ✓ Only enable: Inbound TCP Agent Protocol/4 (TLS encryption)
```

### 3. Configure Agent Security

```
Configure Global Security
Agents:
  TCP port for inbound agents: Fixed (50000)
  ✗ Disable deprecated agent protocols
  Agent → Controller Security: ✓ Enable
```

### 4. Set Content Security Policy

**In Groovy Console:**
```groovy
System.setProperty("hudson.model.DirectoryBrowserSupport.CSP", 
    "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';")
```

### 5. Limit Build History

```
Job Configuration
✓ Discard old builds
  Days to keep builds: 30
  Max # of builds to keep: 100
```

### 6. Secure Jenkins URL

```
Manage Jenkins → Configure System
Jenkins Location:
  Jenkins URL: https://jenkins.company.com (HTTPS!)
  System Admin e-mail address: admin@company.com
```

### 7. Enable Audit Logging

**Install Plugin:**
```
Audit Trail Plugin
```

**Configure:**
```
Manage Jenkins → Configure System → Audit Trail

Log file: /var/log/jenkins/audit.log
Log Rotation: 
  Max Size: 100 MB
  Max Files: 10
```

### 8. Script Security

```
Manage Jenkins → Configure Global Security
  ✓ Enable script security for Job DSL scripts
  ✓ Sandbox groovy scripts
```

**Approve Scripts:**
```
Manage Jenkins → In-process Script Approval
Review and approve pending scripts
```

## Secrets Management

### 1. HashiCorp Vault Integration

**Install Plugin:**
```
HashiCorp Vault Plugin
```

**Configure:**
```
Manage Jenkins → Configure System → Vault

Vault URL: https://vault.company.com
Vault Credential: vault-token
```

**Use in Pipeline:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Deploy') {
            steps {
                script {
                    def secrets = [
                        [
                            path: 'secret/data/app',
                            secretValues: [
                                [envVar: 'DB_PASSWORD', vaultKey: 'password'],
                                [envVar: 'API_KEY', vaultKey: 'api_key']
                            ]
                        ]
                    ]
                    
                    withVault([vaultSecrets: secrets]) {
                        sh 'deploy.sh'
                    }
                }
            }
        }
    }
}
```

### 2. AWS Secrets Manager

```groovy
pipeline {
    agent any
    
    stages {
        stage('Get Secrets') {
            steps {
                script {
                    withAWS(credentials: 'aws-credentials', region: 'us-east-1') {
                        def secret = awsSecretsManager(
                            secretId: 'prod/app/credentials'
                        )
                        env.DB_PASSWORD = secret.password
                        env.API_KEY = secret.api_key
                    }
                }
            }
        }
    }
}
```

### 3. Azure Key Vault

**Install Plugin:**
```
Azure Key Vault Plugin
```

**Use in Pipeline:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Deploy') {
            steps {
                azureKeyVault([
                    [
                        envVariable: 'DB_PASSWORD',
                        name: 'dbpassword',
                        secretType: 'Secret'
                    ],
                    [
                        envVariable: 'API_KEY',
                        name: 'apikey',
                        secretType: 'Secret'
                    ]
                ]) {
                    sh 'deploy.sh'
                }
            }
        }
    }
}
```

## Security Best Practices

### 1. Regular Updates

```bash
# Check for updates
Manage Jenkins → Manage Plugins → Updates

# Enable auto-update for security patches
Install Security Advisory Plugin
```

### 2. Principle of Least Privilege

```
✅ Grant minimum permissions needed
✅ Use project-based permissions
✅ Regular permission audits
❌ Don't give everyone admin access
```

### 3. Secure Build Agents

```groovy
// Use labeled agents
agent {
    label 'secure-build'
}

// Use Docker agents for isolation
agent {
    docker {
        image 'maven:3.8'
        args '--read-only --tmpfs /tmp'
    }
}
```

### 4. Pipeline Security

```groovy
pipeline {
    agent any
    
    options {
        // Prevent secrets in logs
        disableConcurrentBuilds()
        // Timeout to prevent resource exhaustion
        timeout(time: 1, unit: 'HOURS')
        // Build retention
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    
    stages {
        stage('Secure Build') {
            steps {
                // Use credentials properly
                withCredentials([...]) {
                    sh 'command'
                }
                
                // Never echo secrets!
                // ❌ sh 'echo ${PASSWORD}'
                // ✅ sh 'command-using-password'
            }
        }
    }
}
```

### 5. Code Signing

```groovy
stage('Sign Artifacts') {
    steps {
        withCredentials([file(
            credentialsId: 'signing-key',
            variable: 'SIGNING_KEY'
        )]) {
            sh '''
                gpg --import ${SIGNING_KEY}
                gpg --sign artifact.jar
            '''
        }
    }
}
```

### 6. Network Security

```
# Firewall rules
Allow: 8080 (HTTPS only)
Allow: 50000 (agent port, internal only)
Deny: All other ports

# Use HTTPS
Configure reverse proxy (nginx/Apache)
Redirect HTTP → HTTPS
```

## Compliance and Audit

### 1. Audit Logging

```
Audit Trail Plugin logs:
- User logins/logouts
- Job creation/deletion
- Configuration changes
- Build triggers
- Permission changes
```

### 2. Job Configuration History

**Install Plugin:**
```
Job Configuration History Plugin
```

**View History:**
```
Job → Job Config History
See all configuration changes
Compare versions
Restore previous versions
```

### 3. Build User Tracking

**Install Plugin:**
```
Build User Vars Plugin
```

**Use in Pipeline:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Track User') {
            steps {
                script {
                    echo "Build triggered by: ${env.BUILD_USER}"
                    echo "User email: ${env.BUILD_USER_EMAIL}"
                }
            }
        }
    }
}
```

## Troubleshooting Security Issues

### Issue: Locked Out of Jenkins

**Solution:**
```bash
# Edit config.xml
sudo systemctl stop jenkins
sudo vi /var/lib/jenkins/config.xml

# Disable security temporarily
<useSecurity>false</useSecurity>

sudo systemctl start jenkins

# Login, fix permissions, re-enable security
```

### Issue: Credentials Not Working

**Check:**
1. Credential scope (Global vs Project)
2. Credential ID spelling
3. User has permission to use credentials
4. Credentials not expired

### Issue: Permission Denied

**Check:**
```
1. User authentication successful?
2. User has required permissions?
3. Project-based security enabled?
4. Check authorization strategy
```

## Summary

Jenkins security requires:
- Proper authentication setup
- Fine-grained authorization
- Secure credential management
- Regular security updates
- Audit logging
- Network security
- Compliance monitoring

**Critical Actions:**
- Enable CSRF protection
- Use HTTPS
- Implement RBAC
- Secure credentials properly
- Regular security audits
- Keep Jenkins updated

---

**Previous:** [← Pipeline Libraries](14-pipeline-libraries.md) | **Next:** [Monitoring →](16-monitoring.md)
