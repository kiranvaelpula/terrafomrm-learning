# Ansible Learning Path

> **Master configuration management and automation with Ansible**

---

## 📖 Overview

This comprehensive Ansible learning path takes you from basics to advanced automation, covering everything you need to become an Ansible expert.

### What You'll Learn:
- ✅ Ansible fundamentals and architecture
- ✅ Writing and executing playbooks
- ✅ Managing inventory and variables
- ✅ Creating reusable roles
- ✅ Advanced automation patterns
- ✅ Production-ready deployments
- ✅ Interview preparation

---

## 🎯 Learning Path Structure

### **Basics** (5 files)
Foundation concepts and getting started with Ansible.

1. [What is Ansible?](basics/01-what-is-ansible.md)
2. [Installation & Setup](basics/02-installation-setup.md)
3. [Inventory & Ad-hoc Commands](basics/03-inventory-adhoc.md)
4. [First Playbook](basics/04-first-playbook.md)
5. [Basic Modules](basics/05-basic-modules.md)
6. [Interview Questions - Basics](basics/interview-questions-basics.md)

### **Intermediate** (7 files)
Advanced playbook features and best practices.

7. [Playbook Structure & Best Practices](intermediate/06-playbook-structure.md)
8. [Variables & Facts](intermediate/07-variables-facts.md)
9. [Templates (Jinja2)](intermediate/08-templates.md)
10. [Handlers & Conditionals](intermediate/09-handlers-conditionals.md)
11. [Loops & Iteration](intermediate/10-loops.md)
12. [Ansible Vault (Secrets)](intermediate/11-ansible-vault.md)
13. [Error Handling & Testing](intermediate/12-error-handling.md)
14. [Interview Questions - Intermediate](intermediate/interview-questions-intermediate.md)

### **Advanced** (8 files)
Production patterns and enterprise automation.

15. [Ansible Roles](advanced/13-roles.md)
16. [Ansible Galaxy](advanced/14-galaxy.md)
17. [Dynamic Inventory](advanced/15-dynamic-inventory.md)
18. [Ansible Tower/AWX](advanced/16-tower-awx.md)
19. [Performance Optimization](advanced/17-performance.md)
20. [Security Best Practices](advanced/18-security.md)
21. [CI/CD Integration](advanced/19-cicd-integration.md)
22. [Enterprise Patterns](advanced/20-enterprise-patterns.md)
23. [Interview Questions - Advanced](advanced/interview-questions-advanced.md)

---

## 🚀 Quick Start

### Prerequisites:
- Linux/Unix basics
- SSH understanding
- Basic YAML knowledge
- Python installed

### Installation (5 minutes):
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ansible -y

# RHEL/CentOS
sudo yum install ansible -y

# macOS
brew install ansible

# Verify
ansible --version
```

### First Command (2 minutes):
```bash
# Test connection to localhost
ansible localhost -m ping

# Run ad-hoc command
ansible localhost -m command -a "uptime"
```

### First Playbook (5 minutes):
```yaml
# hello.yml
---
- name: My first playbook
  hosts: localhost
  tasks:
    - name: Print message
      debug:
        msg: "Hello, Ansible!"
```

```bash
ansible-playbook hello.yml
```

---

## 🎓 Learning Approach

### Beginner (Weeks 1-2):
- Complete Basics section
- Practice ad-hoc commands
- Write simple playbooks
- Lab 01-02

### Intermediate (Weeks 3-4):
- Study Intermediate section
- Learn variables and templates
- Master handlers and loops
- Lab 03

### Advanced (Weeks 5-6):
- Deep dive into Roles
- Explore dynamic inventory
- Learn performance tuning
- Lab 04-05

### Expert (Ongoing):
- Build production playbooks
- Contribute to Galaxy
- Automate complex workflows
- Real-world projects

---

## 💼 Practice Labs

### Lab 01: Basics
**Time:** 2 hours  
**Focus:** Installation, inventory, ad-hoc commands  
[Start Lab 01 →](ansible-practice/lab-01-basics/README.md)

### Lab 02: Playbooks
**Time:** 3 hours  
**Focus:** Writing playbooks, modules, debugging  
[Start Lab 02 →](ansible-practice/lab-02-playbooks/README.md)

### Lab 03: Roles
**Time:** 3 hours  
**Focus:** Creating and using roles  
[Start Lab 03 →](ansible-practice/lab-03-roles/README.md)

### Lab 04: Advanced
**Time:** 4 hours  
**Focus:** Dynamic inventory, vault, optimization  
[Start Lab 04 →](ansible-practice/lab-04-advanced/README.md)

### Lab 05: Real-World Project
**Time:** 5 hours  
**Focus:** Complete LAMP stack automation  
[Start Lab 05 →](ansible-practice/lab-05-real-world/README.md)

---

## 🎯 Use Cases Covered

### Infrastructure Automation:
- Server provisioning
- Package management
- Service configuration
- File management

### Application Deployment:
- Web servers (Apache, Nginx)
- Databases (MySQL, PostgreSQL)
- Application stacks (LAMP, MEAN)
- Container deployments

### Configuration Management:
- System configuration
- User management
- Security hardening
- Compliance enforcement

### Cloud Automation:
- AWS provisioning
- Azure resources
- GCP deployment
- Multi-cloud management

---

## 📊 Skills You'll Gain

### Technical Skills:
- ✅ Write production playbooks
- ✅ Create reusable roles
- ✅ Manage secrets with Vault
- ✅ Optimize for performance
- ✅ Integrate with CI/CD
- ✅ Troubleshoot automation

### Soft Skills:
- ✅ Infrastructure as Code mindset
- ✅ Documentation practices
- ✅ Collaboration patterns
- ✅ Problem-solving approaches

---

## 🎤 Interview Preparation

### Question Coverage:
- **Basics:** 30+ questions
- **Intermediate:** 40+ questions
- **Advanced:** 50+ questions
- **Total:** 120+ interview questions

### Topics Covered:
- Ansible architecture
- Playbook best practices
- Role design
- Performance tuning
- Security considerations
- Real-world scenarios

---

## 📚 Additional Resources

### Official Documentation:
- [Ansible Docs](https://docs.ansible.com/)
- [Ansible Galaxy](https://galaxy.ansible.com/)
- [Ansible Community](https://www.ansible.com/community)

### Tools & Integrations:
- **Ansible Lint:** Playbook linting
- **Molecule:** Role testing
- **AWX/Tower:** Web UI & API
- **Ansible Navigator:** TUI for playbooks

---

## 🏆 Certification Path

### Red Hat Certified Specialist:
This content prepares you for:
- Red Hat Certified Specialist in Ansible Automation (EX407)
- Red Hat Certified Architect in Automation (EX467)

### Skills Alignment:
- ✅ All exam objectives covered
- ✅ Hands-on labs included
- ✅ Real-world scenarios
- ✅ Best practices emphasized

---

## 🎯 Learning Outcomes

After completing this path, you will:

1. **Automate Infrastructure:**
   - Configure 100+ servers in minutes
   - Ensure consistency across environments
   - Reduce manual errors to near-zero

2. **Build Career:**
   - Qualify for DevOps Engineer roles
   - Command $90K-$150K salary
   - Pass technical interviews

3. **Deliver Value:**
   - Reduce deployment time by 80%
   - Improve system reliability
   - Enable rapid scaling

---

## 🔗 Related Topics

### Complement with:
- [Git](../01-git/README.md) - Version control
- [Docker](../02-docker/README.md) - Containerization
- [Jenkins](../03-jenkins/README.md) - CI/CD
- [Terraform](../../01-basics/01-what-is-terraform.md) - Infrastructure provisioning

### Integration:
Ansible works seamlessly with:
- Git (version control)
- Docker (container management)
- Kubernetes (orchestration)
- Jenkins (CI/CD pipelines)
- Terraform (infrastructure)

---

## ⏱️ Time Commitment

### Minimum (Basics Only):
- **Study:** 10 hours
- **Labs:** 5 hours
- **Total:** 15 hours
- **Result:** Entry-level knowledge

### Recommended (All Levels):
- **Study:** 30 hours
- **Labs:** 15 hours
- **Practice:** 10 hours
- **Total:** 55 hours
- **Result:** Job-ready skills

### Expert (Complete Mastery):
- **All Content:** 55 hours
- **Projects:** 20 hours
- **Certification Prep:** 15 hours
- **Total:** 90 hours
- **Result:** Senior-level expertise

---

## 💡 Pro Tips

### Best Practices:
1. **Start Simple:** Master basics before advancing
2. **Practice Daily:** Run playbooks regularly
3. **Read Others' Code:** Study Galaxy roles
4. **Build Projects:** Create real automation
5. **Test Everything:** Use check mode extensively

### Common Pitfalls to Avoid:
- ❌ Ignoring idempotency
- ❌ Hardcoding values
- ❌ Skipping error handling
- ❌ Poor documentation
- ❌ Not using roles

---

## 🎉 Get Started

**Ready to begin?**

👉 [Start with: What is Ansible?](basics/01-what-is-ansible.md)

**Questions?**
- Check interview questions in each section
- Review practice labs
- Study real-world examples

---

## 📈 Progress Tracking

Track your learning:

```
Basics:      [ ] [ ] [ ] [ ] [ ]  0%
Intermediate: [ ] [ ] [ ] [ ] [ ] [ ] [ ]  0%
Advanced:    [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]  0%
Labs:        [ ] [ ] [ ] [ ] [ ]  0%

Overall: 0% Complete
```

---

**Last Updated:** July 20, 2026  
**Status:** Complete Learning Path  
**Level:** Beginner → Expert  
**Time:** 15-90 hours (based on depth)

**🚀 Start learning Ansible today!**
