# 🎯 Complete Terraform Interview Guide

**Master Terraform interviews from basics to advanced!**

This guide contains 150+ interview questions covering everything from fundamental concepts to real-world production scenarios.

---

## 📚 Interview Question Sets

### 🟢 Beginner Level (50 Questions)
**Topics:** Terraform basics, IaC concepts, basic commands, workflow

[**→ View Beginner Questions**](./01-basics/interview-questions-basics.md)

**Key areas:**
- What is Terraform and IaC?
- Installation and setup
- Basic resource creation
- Terraform workflow (init, plan, apply)
- Basic commands and their usage
- Understanding state files

**Study time:** 3-5 days of practice

---

### 🟡 Intermediate Level (50 Questions)
**Topics:** Variables, modules, state management, loops, conditionals

[**→ View Intermediate Questions**](./02-intermediate/interview-questions-intermediate.md)

**Key areas:**
- Variables and outputs
- Input methods and precedence
- Local vs remote state
- State locking
- Module creation and usage
- Count vs for_each
- Dynamic blocks
- For expressions

**Study time:** 1-2 weeks of practice

---

### 🔴 Advanced Level (50 Questions)
**Topics:** Best practices, CI/CD, security, production scenarios

[**→ View Advanced Questions**](./03-advanced/interview-questions-advanced.md)

**Key areas:**
- Production best practices
- State management strategies
- Module versioning
- CI/CD integration
- Security and compliance
- Troubleshooting
- Performance optimization
- Real-world scenarios

**Study time:** 2-3 weeks of practice

---

## 🎓 Study Plan

### Week 1: Foundations
- [ ] Complete Modules 01-05
- [ ] Practice all beginner questions
- [ ] Create 5 simple resources (S3, EC2, VPC)
- [ ] Master basic commands

### Week 2: Intermediate Concepts
- [ ] Complete Modules 06-09
- [ ] Practice intermediate questions
- [ ] Build a reusable module
- [ ] Implement variables and outputs
- [ ] Practice count and for_each

### Week 3: Advanced Topics
- [ ] Complete Module 10
- [ ] Practice advanced questions
- [ ] Set up remote state
- [ ] Create CI/CD pipeline
- [ ] Build production-ready infrastructure

### Week 4: Interview Prep
- [ ] Review all questions
- [ ] Practice explaining concepts out loud
- [ ] Build a portfolio project
- [ ] Take practice exams
- [ ] Review real-world scenarios

---

## 💡 Interview Tips

### Before the Interview

1. **Know the company's cloud platform**
   - AWS, Azure, GCP?
   - Review provider-specific resources

2. **Understand their scale**
   - Small team (simpler questions)
   - Large enterprise (focus on state management, modules, CI/CD)

3. **Review your own experience**
   - Be ready to discuss projects you've worked on
   - Explain challenges and solutions

### During the Interview

1. **Think out loud**
   - Explain your reasoning
   - Show problem-solving process

2. **Ask clarifying questions**
   - "What scale are we talking about?"
   - "Is this for a team or solo work?"
   - "What's the current infrastructure setup?"

3. **Be honest**
   - Say "I don't know, but here's how I'd find out"
   - Don't pretend to know something you don't

4. **Use examples**
   - Reference real projects
   - Draw diagrams if helpful

---

## 🔥 Most Common Interview Questions

### Top 10 Must-Know Questions

1. **What is Terraform and how does it differ from other IaC tools?**
2. **Explain the Terraform workflow**
3. **What is Terraform state and why is it important?**
4. **What's the difference between count and for_each?**
5. **How do you manage state for team collaboration?**
6. **What are modules and when should you use them?**
7. **How do you handle secrets in Terraform?**
8. **Explain the difference between terraform plan and terraform apply**
9. **How do you import existing resources into Terraform?**
10. **What are best practices for structuring Terraform code?**

### Top 5 Scenario Questions

1. **A team member manually created resources. How do you manage them with Terraform?**
   ```bash
   terraform import aws_instance.server i-1234567890
   ```

2. **Two people run terraform apply simultaneously. What happens?**
   - Without locking: Conflicts
   - With locking: Second person waits

3. **You lost the state file. How do you recover?**
   - Remote state: Re-init
   - Local: Restore from backup or import resources

4. **How do you manage dev, staging, and prod environments?**
   - Separate directories with separate state files

5. **State is locked and person is offline. What do you do?**
   ```bash
   terraform force-unlock <lock-id>
   ```

---

## 📊 Question Difficulty Matrix

### Easy (Entry Level)
- What is Terraform?
- Basic commands (init, plan, apply)
- Resource syntax
- Variable basics
- Simple troubleshooting

### Medium (Mid Level)
- State management
- Module creation
- Count vs for_each
- Remote state setup
- Variable precedence
- Output values
- For expressions

### Hard (Senior Level)
- Production architecture
- CI/CD integration
- State locking strategies
- Security best practices
- Performance optimization
- Module versioning
- Complex troubleshooting
- Policy as code

---

## 🎯 Role-Specific Focus Areas

### DevOps Engineer
**Focus on:**
- CI/CD integration
- State management for teams
- Module creation
- Best practices
- Security

### Cloud Architect
**Focus on:**
- Multi-cloud strategies
- Module design patterns
- Infrastructure organization
- Cost optimization
- Scalability

### Platform Engineer
**Focus on:**
- Module registry
- Self-service patterns
- Policy enforcement
- Standards and compliance
- Team enablement

### Site Reliability Engineer (SRE)
**Focus on:**
- Reliability patterns
- Monitoring infrastructure
- Disaster recovery
- Performance tuning
- Troubleshooting

---

## 🏆 Certification Preparation

### HashiCorp Certified: Terraform Associate

**Exam Details:**
- **Duration:** 60 minutes
- **Questions:** 57 (multiple choice)
- **Passing Score:** Not disclosed
- **Cost:** $70.50 USD
- **Valid:** 2 years

**Exam Objectives:**

1. **Understand IaC concepts** (15%)
2. **Understand Terraform purpose** (20%)
3. **Understand Terraform basics** (25%)
4. **Use Terraform CLI** (15%)
5. **Interact with modules** (10%)
6. **Navigate Terraform workflow** (10%)
7. **Implement and maintain state** (15%)
8. **Read, generate, modify configuration** (20%)
9. **Understand Terraform Cloud** (10%)

**Study Resources:**
- HashiCorp Learn: https://learn.hashicorp.com/terraform
- Official study guide
- Practice exams
- This learning path!

---

## 📝 Practice Questions by Category

### Infrastructure as Code
- [ ] Explain declarative vs imperative
- [ ] Benefits of IaC
- [ ] When NOT to use Terraform

### Terraform Basics
- [ ] Terraform workflow
- [ ] Provider configuration
- [ ] Resource syntax
- [ ] State file purpose

### Variables & Outputs
- [ ] Variable types
- [ ] Precedence order
- [ ] Output usage
- [ ] Locals vs variables

### State Management
- [ ] Local vs remote state
- [ ] State locking
- [ ] State commands
- [ ] Drift detection

### Modules
- [ ] Module structure
- [ ] Module sources
- [ ] Versioning
- [ ] Best practices

### Advanced Topics
- [ ] Count vs for_each
- [ ] Dynamic blocks
- [ ] For expressions
- [ ] Conditionals

### Production
- [ ] CI/CD integration
- [ ] Security practices
- [ ] Team collaboration
- [ ] Troubleshooting

---

## 🛠️ Hands-On Challenges

### Challenge 1: Basic Setup
**Time: 30 minutes**
1. Install Terraform
2. Configure AWS credentials
3. Create an S3 bucket
4. Add versioning
5. Output bucket ARN

### Challenge 2: Multi-Environment
**Time: 1 hour**
1. Create variables for dev/prod
2. Use tfvars files
3. Deploy to both environments
4. Use different instance sizes per environment

### Challenge 3: Module Creation
**Time: 2 hours**
1. Create a VPC module
2. Add subnets, route tables, gateways
3. Use the module in root config
4. Add comprehensive outputs

### Challenge 4: Remote State
**Time: 1 hour**
1. Set up S3 backend
2. Configure DynamoDB for locking
3. Migrate local state to remote
4. Test with team member

### Challenge 5: CI/CD Pipeline
**Time: 3 hours**
1. Set up GitHub Actions
2. Add terraform fmt check
3. Add terraform plan on PR
4. Add terraform apply on merge

---

## 📚 Additional Resources

### Official Documentation
- [Terraform Documentation](https://www.terraform.io/docs)
- [AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws)
- [Terraform Registry](https://registry.terraform.io/)

### Learning Platforms
- HashiCorp Learn
- A Cloud Guru
- Linux Academy
- Udemy courses

### Community
- [HashiCorp Discuss](https://discuss.hashicorp.com/)
- [r/Terraform](https://reddit.com/r/terraform)
- Stack Overflow (tag: terraform)
- HashiCorp Community Forum

### Books
- "Terraform: Up & Running" by Yevgeniy Brikman
- "Terraform in Action" by Scott Winkler

### Tools
- **tfsec** - Security scanning
- **Checkov** - Policy as code
- **Terragrunt** - Terraform wrapper
- **Atlantis** - Terraform PR automation

---

## ✅ Pre-Interview Checklist

**Night Before:**
- [ ] Review top 10 questions
- [ ] Review your resume/projects
- [ ] Set up test environment
- [ ] Get good sleep

**Day Of:**
- [ ] Test your internet/mic/camera
- [ ] Have documentation open
- [ ] Paper and pen ready
- [ ] Water nearby
- [ ] Join 5 minutes early

**During Interview:**
- [ ] Think out loud
- [ ] Ask clarifying questions
- [ ] Use examples from experience
- [ ] Be honest about what you don't know
- [ ] Show problem-solving skills

**After Interview:**
- [ ] Send thank you email
- [ ] Note questions you struggled with
- [ ] Study those areas
- [ ] Follow up as promised

---

## 🎓 Common Mistakes to Avoid

### Technical Mistakes
❌ Committing state files to Git
❌ Hardcoding secrets
❌ Not using modules for reusability
❌ Applying without planning first
❌ Editing state files manually
❌ Using count when for_each is better
❌ No state locking for teams

### Interview Mistakes
❌ Not asking clarifying questions
❌ Pretending to know something you don't
❌ Not providing examples
❌ Speaking too technically (or not technical enough)
❌ Not explaining thought process
❌ Giving up on questions too quickly

---

## 💪 Confidence Boosters

**Remember:**
- Everyone starts as a beginner
- Interviews are conversations, not interrogations
- It's okay to say "I don't know, but here's how I'd figure it out"
- Real experience is more valuable than memorized answers
- Companies want to see how you think, not just what you know

**You've got this!** 🚀

---

## 📞 Quick Reference

### Essential Commands
```bash
terraform init          # Initialize
terraform fmt           # Format code
terraform validate      # Validate syntax
terraform plan          # Preview changes
terraform apply         # Apply changes
terraform destroy       # Destroy all
terraform state list    # List resources
terraform output        # Show outputs
```

### File Structure
```
project/
├── main.tf           # Resources
├── variables.tf      # Variables
├── outputs.tf        # Outputs
├── provider.tf       # Providers
├── backend.tf        # Backend config
└── terraform.tfvars  # Variable values
```

### Must-Know Concepts
- Declarative language
- State management
- Provider plugins
- Resource dependencies
- Idempotency
- Drift detection

---

**Ready to ace your Terraform interview?**

Start with the [Beginner Questions](./01-basics/interview-questions-basics.md) and work your way up!

Good luck! 🎉
