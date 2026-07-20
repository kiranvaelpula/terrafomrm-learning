# Ansible Advanced - Interview Questions

> **Senior-level questions covering architecture, performance, security, and enterprise patterns**

---

## Architecture & Design (20 questions)

### Q1: How would you design an Ansible architecture for managing 10,000+ servers across multiple data centers?

**Answer:**
```yaml
# Multi-tier architecture
Architecture:
  Control Nodes:
    - Multiple control nodes (3-5) behind load balancer
    - Geographic distribution (per region)
    - High availability with shared state
  
  Execution:
    - Ansible Tower/AWX for centralized management
    - Distributed job execution
    - Callback plugins for result aggregation
  
  Inventory:
    - Dynamic inventory from CMDB/Cloud APIs
    - Inventory caching (15-30 min TTL)
    - Smart inventory groups (by region, role, environment)
  
  Performance:
    - Forks: 50-100 per control node
    - Serial execution where needed
    - Strategy: free or mitogen for speed
    - Connection: paramiko for bastion, ssh for direct
  
  Storage:
    - Centralized artifact repository
    - Distributed role storage (Ansible Galaxy)
    - Vault secrets in HashiCorp Vault/AWS Secrets Manager
  
  Network:
    - Bastion hosts per region
    - SSH multiplexing enabled
    - Pipelining enabled
    - Compression enabled for slow links
```

Implementation considerations:
- Use Tower/AWX smart inventory for dynamic grouping
- Implement role-based access control (RBAC)
- Set up monitoring and metrics collection
- Use external callback plugins for centralized logging
- Implement automation hub for role/collection distribution

---

### Q2: Explain the differences between push and pull models. When would you use a pull model with Ansible?

**Answer:**

**Push Model (Default Ansible):**
- Control node initiates connections
- Runs on-demand
- Immediate execution
- Better for: Deployments, configuration changes, on-demand tasks

**Pull Model (ansible-pull):**
- Managed nodes pull configurations
- Runs on schedule (cron)
- Eventually consistent
- Better for: Large scale, bootstrapping, autonomous systems

**When to use pull model:**
```yaml
# Use cases for ansible-pull:
1. Bootstrapping new instances:
   - EC2/VM startup scripts
   - Auto-scaling groups
   - Ephemeral containers

2. Large-scale deployments:
   - 10,000+ nodes
   - Reduce control node load
   - Network bandwidth constraints

3. Autonomous systems:
   - Edge devices
   - IoT deployments
   - Disconnected environments

4. Compliance enforcement:
   - Continuous configuration drift correction
   - Security baseline enforcement
   - Scheduled remediation
```

**Example ansible-pull setup:**
```bash
# On managed node
ansible-pull \
  -U https://github.com/company/ansible-config.git \
  -C production \
  -i localhost, \
  -e "node_role=webserver" \
  playbooks/site.yml

# Cron job
*/30 * * * * /usr/bin/ansible-pull -U https://github.com/company/ansible-config.git -C production
```

---

### Q3: How do you handle secret rotation in a large Ansible deployment?

**Answer:**

**Strategy:**
```yaml
# 1. External secrets management
- HashiCorp Vault integration
- AWS Secrets Manager
- Azure Key Vault
- CyberArk

# 2. Automated rotation workflow
Rotation Process:
  1. Generate new secret
  2. Deploy new secret (dual-write period)
  3. Update applications to use new secret
  4. Verify applications working
  5. Revoke old secret
  6. Audit and log
```

**Implementation:**
```yaml
# playbooks/rotate_secrets.yml
---
- name: Rotate database password
  hosts: databases
  serial: 1  # One at a time to prevent outage
  
  vars:
    rotation_wait_time: 300  # 5 minutes dual-write period
  
  tasks:
    - name: Generate new password
      set_fact:
        new_db_password: "{{ lookup('password', '/dev/null length=32 chars=ascii_letters,digits') }}"
      run_once: true
      no_log: true
    
    - name: Store new password in Vault
      hashivault_write:
        secret: "database/{{ inventory_hostname }}"
        data:
          password: "{{ new_db_password }}"
          rotated_at: "{{ ansible_date_time.iso8601 }}"
          rotated_by: "{{ ansible_user_id }}"
      delegate_to: localhost
      no_log: true
    
    - name: Update database user (allow both passwords)
      mysql_user:
        name: appuser
        password: "{{ new_db_password }}"
        host: "%"
        state: present
      no_log: true
    
    - name: Notify applications of new password
      uri:
        url: "http://{{ item }}:8080/admin/reload-config"
        method: POST
        headers:
          X-Admin-Token: "{{ admin_token }}"
      loop: "{{ groups['webservers'] }}"
    
    - name: Wait for applications to pick up new password
      pause:
        seconds: "{{ rotation_wait_time }}"
    
    - name: Verify applications using new password
      shell: |
        mysql -h localhost -u appuser -p'{{ new_db_password }}' -e "SELECT 1" > /dev/null 2>&1
      register: verify
      failed_when: verify.rc != 0
      no_log: true
    
    - name: Revoke old password from Vault history
      hashivault_delete:
        secret: "database/{{ inventory_hostname }}"
        version: "{{ lookup('hashivault', 'database/' + inventory_hostname, 'version') | int - 1 }}"
      delegate_to: localhost
    
    - name: Log rotation event
      lineinfile:
        path: /var/log/ansible/secret_rotations.log
        line: "{{ ansible_date_time.iso8601 }} - {{ inventory_hostname }} - database password rotated"
        create: true
      delegate_to: localhost
```

**Best practices:**
- Rotate secrets on schedule (e.g., every 90 days)
- Use external secret management (never store in Git)
- Implement dual-write periods to prevent outages
- Audit all secret access
- Automate rotation testing
- Have rollback procedures

---

### Q4: Describe your strategy for managing Ansible roles across hundreds of playbooks and multiple teams.

**Answer:**

**Strategy:**
```yaml
# 1. Role Organization
Structure:
  Public Roles:
    - Ansible Galaxy for community roles
    - Versioned dependencies (requirements.yml)
    - Automated security scanning
  
  Private Roles:
    - Internal Galaxy/Automation Hub
    - Semantic versioning (MAJOR.MINOR.PATCH)
    - CI/CD for role testing
  
  Organization:
    roles/
      common/           # Shared across all teams
      platform/         # Platform engineering
      application/      # Application teams
      security/         # Security team roles

# 2. Versioning Strategy
Version Pinning:
  # requirements.yml
  - name: geerlingguy.nginx
    version: "3.1.4"  # Pin exact version
  
  - name: company.monitoring
    version: ">=2.0.0,<3.0.0"  # Semver range
  
  - name: team-app.deployment
    src: git+https://github.com/company/ansible-app-role.git
    version: v1.2.3

# 3. Governance
Process:
  - Role development in feature branches
  - Molecule testing required
  - Code review by 2+ team members
  - Security scan (ansible-lint --profile=safety)
  - Automated publishing to Galaxy/Hub
  - Changelog maintenance (CHANGELOG.md)
```

**Implementation:**
```yaml
# Role CI/CD pipeline (.gitlab-ci.yml)
stages:
  - lint
  - test
  - security
  - publish

lint:
  stage: lint
  script:
    - ansible-lint .
    - yamllint .

test:
  stage: test
  script:
    - molecule test --all

security:
  stage: security
  script:
    - ansible-lint --profile=safety .
    - trivy config .

publish:
  stage: publish
  script:
    - ansible-galaxy role import company ansible-role-name --api-key=$GALAXY_API_KEY
  only:
    - tags

# Team role catalog (roles/catalog.yml)
roles:
  common/base:
    owner: platform-team
    description: "Base system configuration"
    version: "2.1.0"
    compatibility: ["Ubuntu 20.04", "RHEL 8"]
    dependencies: []
  
  platform/monitoring:
    owner: platform-team
    description: "Prometheus and Grafana setup"
    version: "1.5.2"
    dependencies:
      - common/base
  
  application/webapp:
    owner: app-team-alpha
    description: "Web application deployment"
    version: "3.2.1"
    dependencies:
      - common/base
      - platform/monitoring
```

**Role Standards:**
```yaml
# roles/STANDARDS.md
Required Structure:
  my_role/
    ├── README.md (must include examples)
    ├── meta/main.yml (dependencies, galaxy_info)
    ├── defaults/main.yml (default variables)
    ├── vars/main.yml (internal variables)
    ├── tasks/main.yml (task entry point)
    ├── handlers/main.yml (if needed)
    ├── templates/ (Jinja2 templates)
    ├── files/ (static files)
    ├── molecule/ (test scenarios)
    └── CHANGELOG.md (version history)

Required Documentation:
  - Purpose and scope
  - Requirements (OS, dependencies)
  - Variables (name, type, required/optional, default, description)
  - Examples (basic and advanced)
  - License
  - Author/Maintainer

Testing Requirements:
  - Molecule scenarios for supported OS
  - Idempotency tests
  - Integration tests
  - CI passing

Versioning Rules:
  - Semantic versioning (MAJOR.MINOR.PATCH)
  - MAJOR: Breaking changes
  - MINOR: New features, backward compatible
  - PATCH: Bug fixes

Code Quality:
  - ansible-lint score > 4.5/5
  - YAML lint passing
  - No hardcoded secrets
  - Parameterized and reusable
```

---

### Q5: How would you implement a multi-tenant Ansible Tower/AWX setup?

**Answer:**

**Architecture:**
```yaml
Multi-Tenant Structure:
  Organizations:
    - One per tenant/business unit
    - Isolated resources
    - Independent RBAC
  
  Teams:
    - Admin team (full access)
    - Developer team (deploy only)
    - ReadOnly team (auditors)
  
  Inventories:
    - Tenant-specific
    - No cross-tenant visibility
    - Dynamic sources per tenant
  
  Credentials:
    - Scoped to organizations
    - Encrypted at rest
    - Role-based access
  
  Projects:
    - Separate Git repos per tenant
    - Branch-based environments
    - Automated sync
```

**Implementation:**
```python
# Tower API configuration script
import tower_cli

# Create organization
tower_cli.get_resource('organization').create(
    name='TenantA',
    description='Tenant A Organization'
)

# Create teams
tower_cli.get_resource('team').create(
    name='TenantA-Admins',
    organization='TenantA'
)

tower_cli.get_resource('team').create(
    name='TenantA-Developers',
    organization='TenantA'
)

# Create inventory
tower_cli.get_resource('inventory').create(
    name='TenantA-Production',
    organization='TenantA',
    variables='{"tenant_id": "tenant-a", "environment": "production"}'
)

# Create project
tower_cli.get_resource('project').create(
    name='TenantA-Playbooks',
    organization='TenantA',
    scm_type='git',
    scm_url='https://github.com/company/tenant-a-ansible.git',
    scm_branch='main',
    scm_update_on_launch=True
)

# Create job template
tower_cli.get_resource('job_template').create(
    name='TenantA-Deploy-App',
    job_type='run',
    inventory='TenantA-Production',
    project='TenantA-Playbooks',
    playbook='deploy.yml',
    credentials=['TenantA-SSH', 'TenantA-Vault']
)

# Set RBAC
tower_cli.get_resource('role').grant(
    type='team',
    team='TenantA-Admins',
    target_team='TenantA-Developers',
    role='admin'
)

tower_cli.get_resource('role').grant(
    type='team',
    team='TenantA-Developers',
    job_template='TenantA-Deploy-App',
    role='execute'
)
```

**Isolation:**
```yaml
# Instance groups for tenant isolation
- name: Configure instance groups
  hosts: localhost
  tasks:
    - name: Create tenant-specific instance group
      awx.awx.instance_group:
        name: "tenanta-workers"
        policy_instance_percentage: 0
        policy_instance_minimum: 2
        instances:
          - tower-worker-tenanta-1
          - tower-worker-tenanta-2
    
    - name: Associate with organization
      awx.awx.organization:
        name: "TenantA"
        instance_groups:
          - "tenanta-workers"
```

**Resource Limits:**
```yaml
# Capacity planning per tenant
Limits:
  TenantA:
    max_concurrent_jobs: 10
    max_forks: 50
    job_timeout: 3600
    instance_group: tenanta-workers
  
  TenantB:
    max_concurrent_jobs: 5
    max_forks: 25
    job_timeout: 1800
    instance_group: tenantb-workers
```

---

## Performance & Scalability (15 questions)

### Q6: What are the performance implications of using `serial` vs `free` strategy? When would you use each?

**Answer:**

**Serial Strategy:**
```yaml
- name: Rolling deployment
  hosts: webservers
  serial: 3  # Or "25%", "10%"
  
  # Behavior:
  # - Processes hosts in batches
  # - Waits for all tasks in batch to complete before next batch
  # - Predictable, ordered execution
  # - Slower but safer
```

**Performance characteristics:**
- **Duration:** O(n/batch_size * tasks)
- **Memory:** Lower (fewer concurrent connections)
- **Control:** High (can stop between batches)
- **Failure handling:** Isolates failures to batches

**Use cases:**
- Rolling deployments (prevent full outage)
- Database updates (master-replica order)
- Load balancer updates (maintain capacity)
- When order matters

**Free Strategy:**
```yaml
- name: Parallel execution
  hosts: all
  strategy: free
  
  # Behavior:
  # - Each host runs independently
  # - Doesn't wait for others
  # - Maximum parallelism
  # - Fastest execution
```

**Performance characteristics:**
- **Duration:** O(max(task_times))
- **Memory:** Higher (all connections active)
- **Control:** Lower (can't easily stop mid-flight)
- **Failure handling:** Independent per host

**Use cases:**
- Information gathering
- Independent host configurations
- Package installations
- When speed is critical and order doesn't matter

**Comparison:**
```yaml
# Example: 100 hosts, 10 tasks, 2 seconds per task

Serial (batch=10):
  Duration: (100/10) * 10 * 2 = 200 seconds
  Peak connections: 10
  
Free:
  Duration: 10 * 2 = 20 seconds
  Peak connections: 100 (limited by forks)
  
Linear (default):
  Duration: 10 * 2 = 20 seconds (waits for slowest host per task)
  Peak connections: 100 (limited by forks)
```

**Hybrid approach:**
```yaml
- name: Fast parallel setup
  hosts: all
  strategy: free
  tasks:
    - name: Install packages
      package:
        name: nginx
        state: present

- name: Coordinated deployment
  hosts: all
  serial: "20%"
  tasks:
    - name: Deploy application
      copy:
        src: app.jar
        dest: /opt/app/
    
    - name: Restart service
      systemd:
        name: app
        state: restarted
```

---

### Q7: How do you optimize Ansible for managing 5,000 hosts? What configuration changes would you make?

**Answer:**

**Configuration optimizations:**
```ini
# ansible.cfg
[defaults]
# Connection optimization
forks = 100  # Increase from default 5
host_key_checking = False
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400  # 24 hours

# SSH optimization
[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s -o Compression=yes
pipelining = True  # Reduce SSH operations
control_path_dir = /tmp/ansible-ssh-%%h-%%p-%%r

# Performance
[inventory]
cache = True
cache_plugin = jsonfile
cache_timeout = 3600
cache_connection = /tmp/ansible_inventory
```

**Playbook optimization:**
