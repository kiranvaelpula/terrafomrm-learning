# Ansible Vault (Secrets Management)

> **Secure sensitive data with encryption in your Ansible automation**

---

## 📖 What You'll Learn

- Ansible Vault fundamentals
- Encrypting and decrypting files
- Using vault in playbooks
- Multiple vault passwords
- Vault IDs and best practices
- Integration with CI/CD

---

## 🔐 What is Ansible Vault?

Ansible Vault encrypts sensitive data such as:
- Passwords
- API keys
- Private keys
- Certificates
- SSH keys
- Database credentials
- Any confidential configuration

**Key features:**
- AES256 encryption
- Password or file-based authentication
- Seamless integration with playbooks
- Multiple vault IDs support
- Version control safe

---

## 🚀 Basic Usage

### Creating Encrypted Files

```bash
# Create new encrypted file
ansible-vault create secrets.yml

# Opens editor, add content:
db_password: supersecret123
api_key: abc123xyz789
ssh_private_key: |
  -----BEGIN RSA PRIVATE KEY-----
  MIIEpAIBAAKCAQEA...
  -----END RSA PRIVATE KEY-----
```

### Encrypting Existing Files

```bash
# Encrypt existing file
ansible-vault encrypt vars/passwords.yml

# Encrypt multiple files
ansible-vault encrypt vars/*.yml
```

### Viewing Encrypted Files

```bash
# View without decrypting
ansible-vault view secrets.yml

# Edit encrypted file
ansible-vault edit secrets.yml
```

### Decrypting Files

```bash
# Decrypt file (removes encryption)
ansible-vault decrypt secrets.yml

# Decrypt to different file
ansible-vault decrypt secrets.yml --output=plain_secrets.yml
```

---

## 📝 Using Vault in Playbooks

### Basic Playbook Usage

```yaml
# playbook.yml
---
- name: Deploy application
  hosts: webservers
  vars_files:
    - vars/secrets.yml  # Encrypted file
  
  tasks:
    - name: Configure database
      template:
        src: db_config.j2
        dest: /etc/app/db.conf
      no_log: yes  # Don't log sensitive data
```

**Running with vault:**
```bash
# Prompt for password
ansible-playbook site.yml --ask-vault-pass

# Use password file
ansible-playbook site.yml --vault-password-file .vault_pass

# Use script
ansible-playbook site.yml --vault-password-file vault-pass.sh
```

### Inline Encrypted Variables

```yaml
# vars/main.yml
---
db_host: db.example.com
db_port: 5432
db_name: myapp

# Encrypt specific variable
db_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          66386439653963636537643035383037613632383464633165373663653634383133373230333566
          6134333330316630313735303232373434613432363565360a626134623534646335633862313264
          35646663373831616137363864366539613832383230336630383164663262633739653237316539
          6236653337653466630a373364373338616465363963343739383832636561373765626364636636
          3364
```

**Encrypting a string:**
```bash
ansible-vault encrypt_string 'supersecret' --name 'db_password'
```

---

## 🎯 Vault Password Management

### Password File

```bash
# Create password file
echo "MyVaultPassword123" > .vault_pass
chmod 600 .vault_pass

# Add to .gitignore
echo ".vault_pass" >> .gitignore

# Use in playbook
ansible-playbook site.yml --vault-password-file .vault_pass
```

### Password Script

```bash
#!/bin/bash
# vault-pass.sh - Retrieve password from secure location

# From environment variable
echo "$ANSIBLE_VAULT_PASSWORD"

# Or from AWS Secrets Manager
# aws secretsmanager get-secret-value --secret-id ansible-vault --query SecretString --output text

# Or from password manager
# pass show ansible/vault
```

```bash
chmod +x vault-pass.sh
ansible-playbook site.yml --vault-password-file ./vault-pass.sh
```

### Environment Variable

```bash
# Set vault password in environment
export ANSIBLE_VAULT_PASSWORD="MySecurePassword"

# Configure ansible to use it
# ansible.cfg
[defaults]
vault_password_file = /path/to/vault-pass.sh
```

---

## 🔑 Multiple Vault IDs

### Why Multiple Vaults?

- Different passwords for different environments
- Separate team access
- Different security levels
- Third-party secrets

### Using Vault IDs

```bash
# Create with vault ID
ansible-vault create --vault-id dev@prompt secrets_dev.yml
ansible-vault create --vault-id prod@prompt secrets_prod.yml

# View with vault ID
ansible-vault view --vault-id dev@prompt secrets_dev.yml

# Encrypt string with ID
ansible-vault encrypt_string --vault-id dev@prompt 'secret' --name 'api_key'
```

### Vault ID Files

```bash
# Directory structure
.vault/
├── dev_password
├── staging_password
└── prod_password

# Encrypt with ID
ansible-vault encrypt --vault-id dev@.vault/dev_password vars/dev.yml
ansible-vault encrypt --vault-id prod@.vault/prod_password vars/prod.yml
```

### Running with Multiple IDs

```yaml
# playbook.yml
---
- name: Multi-environment deployment
  hosts: all
  vars_files:
    - vars/common.yml
    - vars/{{ environment }}_secrets.yml  # dev_secrets.yml or prod_secrets.yml
  
  tasks:
    - name: Deploy config
      template:
        src: app.conf.j2
        dest: /etc/app/app.conf
```

```bash
# Run with multiple vault IDs
ansible-playbook site.yml \
  --vault-id dev@.vault/dev_password \
  --vault-id prod@.vault/prod_password \
  -e environment=dev
```

---

## 🏗️ Project Structure

### Recommended Layout

```
ansible-project/
├── .gitignore
├── ansible.cfg
├── .vault/
│   ├── dev_password       # Not in git
│   ├── staging_password   # Not in git
│   └── prod_password      # Not in git
├── inventory/
│   ├── dev/
│   │   └── hosts
│   ├── staging/
│   │   └── hosts
│   └── prod/
│       └── hosts
├── group_vars/
│   ├── all/
│   │   ├── vars.yml       # Plain text vars
│   │   └── vault.yml      # Encrypted vars
│   ├── webservers/
│   │   ├── vars.yml
│   │   └── vault.yml
│   └── databases/
│       ├── vars.yml
│       └── vault.yml
├── playbooks/
│   └── site.yml
└── README.md
```

### .gitignore

```gitignore
# Vault passwords
.vault/*_password
.vault_pass
vault_password.txt

# Decrypted files
*_decrypted.yml
*.dec

# Backup files
*.bak
*~
```

### ansible.cfg

```ini
[defaults]
# Vault settings
vault_password_file = ./.vault/dev_password
vault_identity_list = dev@./.vault/dev_password, prod@./.vault/prod_password

# Don't create .retry files
retry_files_enabled = False
```

---

## 📚 Complete Examples

### Example 1: Database Credentials

```yaml
# group_vars/databases/vars.yml (plain text)
---
db_engine: postgresql
db_port: 5432
db_max_connections: 100

# group_vars/databases/vault.yml (encrypted)
---
db_master_user: admin
db_master_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          ...encrypted...
db_replication_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          ...encrypted...

# playbook
---
- name: Configure database
  hosts: databases
  become: yes
  
  tasks:
    - name: Create master user
      postgresql_user:
        name: "{{ db_master_user }}"
        password: "{{ db_master_password }}"
        role_attr_flags: SUPERUSER
      no_log: yes
```

### Example 2: API Keys

```yaml
# vars/api_keys.yml (encrypted)
---
aws_access_key: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          ...encrypted...

aws_secret_key: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          ...encrypted...

github_token: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          ...encrypted...

# playbook
---
- name: Deploy with API access
  hosts: localhost
  vars_files:
    - vars/api_keys.yml
  
  tasks:
    - name: Upload to S3
      aws_s3:
        aws_access_key: "{{ aws_access_key }}"
        aws_secret_key: "{{ aws_secret_key }}"
        bucket: my-bucket
        src: /local/file
        object: remote/file
      no_log: yes
```

### Example 3: SSL Certificates

```yaml
# vars/ssl_certs.yml (encrypted)
---
ssl_certificate: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          ...encrypted certificate...

ssl_private_key: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          ...encrypted private key...

# playbook
---
- name: Deploy SSL certificates
  hosts: webservers
  become: yes
  vars_files:
    - vars/ssl_certs.yml
  
  tasks:
    - name: Deploy certificate
      copy:
        content: "{{ ssl_certificate }}"
        dest: /etc/ssl/certs/server.crt
        mode: '0644'
      no_log: yes
    
    - name: Deploy private key
      copy:
        content: "{{ ssl_private_key }}"
        dest: /etc/ssl/private/server.key
        mode: '0600'
      no_log: yes
      notify: restart nginx
```

### Example 4: Environment-Specific Secrets

```yaml
# group_vars/all/vault_dev.yml (encrypted with dev@)
---
environment: development
app_secret_key: dev_secret_123
db_password: dev_password

# group_vars/all/vault_prod.yml (encrypted with prod@)
---
environment: production
app_secret_key: !vault |
          $ANSIBLE_VAULT;1.2;AES256;prod
          ...encrypted...
db_password: !vault |
          $ANSIBLE_VAULT;1.2;AES256;prod
          ...encrypted...
```

---

## 🔄 Vault Operations

### Rekeying (Changing Password)

```bash
# Change vault password
ansible-vault rekey secrets.yml

# Rekey with new vault ID
ansible-vault rekey --vault-id old@prompt --new-vault-id new@prompt secrets.yml

# Rekey multiple files
ansible-vault rekey vars/*.yml
```

### Encrypting Strings

```bash
# Interactive
ansible-vault encrypt_string

# With prompt
ansible-vault encrypt_string 'secret_value' --name 'variable_name'

# With vault ID
ansible-vault encrypt_string --vault-id prod@prompt 'secret' --name 'api_key'

# From stdin
echo -n 'secret_password' | ansible-vault encrypt_string --stdin-name 'db_password'
```

### Bulk Operations

```bash
# Encrypt all yml files in directory
for file in vars/*.yml; do
    ansible-vault encrypt "$file"
done

# Decrypt all for editing
ansible-vault decrypt vars/*.yml
# ... make changes ...
ansible-vault encrypt vars/*.yml
```

---

## 🔧 CI/CD Integration

### GitLab CI

```yaml
# .gitlab-ci.yml
variables:
  ANSIBLE_VAULT_PASSWORD: $CI_VAULT_PASSWORD

deploy:
  stage: deploy
  script:
    - echo "$ANSIBLE_VAULT_PASSWORD" > .vault_pass
    - chmod 600 .vault_pass
    - ansible-playbook -i inventory/prod site.yml --vault-password-file .vault_pass
  after_script:
    - rm -f .vault_pass
  only:
    - master
```

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup vault password
        run: |
          echo "${{ secrets.ANSIBLE_VAULT_PASSWORD }}" > .vault_pass
          chmod 600 .vault_pass
      
      - name: Run playbook
        run: |
          ansible-playbook site.yml --vault-password-file .vault_pass
      
      - name: Cleanup
        if: always()
        run: rm -f .vault_pass
```

### Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        VAULT_PASS = credentials('ansible-vault-password')
    }
    
    stages {
        stage('Deploy') {
            steps {
                sh '''
                    echo "$VAULT_PASS" > .vault_pass
                    chmod 600 .vault_pass
                    ansible-playbook site.yml --vault-password-file .vault_pass
                    rm -f .vault_pass
                '''
            }
        }
    }
}
```

---

## ✅ Best Practices

1. **Never commit passwords** - Use .gitignore
2. **Use vault IDs** - Separate environments
3. **Rotate passwords** - Regular rekey operations
4. **Minimal encryption** - Only encrypt secrets
5. **Use no_log** - Hide sensitive output
6. **Secure password files** - chmod 600
7. **Password managers** - Use scripts to fetch
8. **Separate files** - vault.yml separate from vars.yml
9. **Document vault IDs** - README for team
10. **Audit access** - Track who has passwords

---

## 🔒 Security Tips

### Do's
✅ Encrypt only sensitive data  
✅ Use strong passwords  
✅ Rotate vault passwords regularly  
✅ Use vault IDs for different teams  
✅ Store password files securely  
✅ Use password managers  
✅ Enable no_log for sensitive tasks  
✅ Review vault files in code review  

### Don'ts
❌ Commit vault passwords to git  
❌ Use weak passwords  
❌ Share production passwords  
❌ Decrypt files in public  
❌ Log sensitive data  
❌ Store passwords in plain text  
❌ Reuse passwords across environments  
❌ Skip password file permissions  

---

## ❌ Common Pitfalls

### Wrong Vault Password

```bash
# Error: Vault password incorrect
ERROR! Decryption failed

# Solution: Check password file
cat .vault_pass
# Or try manual password
ansible-playbook site.yml --ask-vault-pass
```

### Missing no_log

```yaml
# Bad - logs password
- name: Set password
  user:
    name: admin
    password: "{{ admin_password }}"

# Good - hides password
- name: Set password
  user:
    name: admin
    password: "{{ admin_password }}"
  no_log: yes
```

### Encrypted Files in Wrong Format

```bash
# Bad - encrypts whole playbook
ansible-vault encrypt site.yml

# Good - encrypt only vars
ansible-vault encrypt vars/secrets.yml
```

---

## 🔗 What's Next?

- **Next:** [Error Handling & Testing](12-error-handling.md)
- **Previous:** [Loops](10-loops.md)
- **Related:** [Variables & Facts](07-variables-facts.md)

---

**Pro Tip:** Use `ansible-vault encrypt_string` to encrypt individual values within files instead of entire files for better version control diffs!
