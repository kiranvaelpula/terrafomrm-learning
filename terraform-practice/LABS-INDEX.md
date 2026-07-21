# Terraform Practice Labs - Complete Index

## 📚 All Available Labs

### **BASICS** (5 Labs)

#### Lab 01: Create Your First S3 Bucket ✅ CREATED
**Path**: `basics/lab-01-s3-bucket/`  
**Time**: 15 min | **Difficulty**: ⭐  
**Topics**: Resources, Providers, Outputs, Tags  
**Status**: README created - Ready to practice!

#### Lab 02: Launch an EC2 Instance ✅ CREATED
**Path**: `basics/lab-02-ec2-instance/`  
**Time**: 20 min | **Difficulty**: ⭐  
**Topics**: EC2, Security Groups, Data Sources, User Data  
**Status**: README created - Ready to practice!

#### Lab 03: Security Groups Deep Dive
**Path**: `basics/lab-03-security-groups/`  
**Time**: 20 min | **Difficulty**: ⭐  
**Topics**: Ingress/Egress Rules, Dynamic Blocks  
**What You'll Learn**:
- Create security groups with multiple rules
- Use dynamic blocks for repetitive configuration
- Security group dependencies
- Best practices for firewall rules

#### Lab 04: Variables and Outputs ✅ CREATED
**Path**: `basics/lab-04-variables-outputs/`  
**Time**: 25 min | **Difficulty**: ⭐⭐  
**Topics**: Variables, Locals, Outputs, Validation  
**Status**: README created - Ready to practice!

#### Lab 05: Data Sources and Dependencies
**Path**: `basics/lab-05-data-sources/`  
**Time**: 20 min | **Difficulty**: ⭐  
**Topics**: Data Sources, Resource Dependencies, depends_on  
**What You'll Learn**:
- Query existing AWS resources
- Create dependencies between resources
- Use data sources for dynamic configuration
- Combine multiple data sources

---

### **INTERMEDIATE** (5 Labs)

#### Lab 06: VPC with Public and Private Subnets
**Path**: `intermediate/lab-06-vpc-networking/`  
**Time**: 45 min | **Difficulty**: ⭐⭐  
**Topics**: VPC, Subnets, Route Tables, Internet Gateway, NAT  
**What You'll Learn**:
- Create a custom VPC
- Configure public and private subnets
- Set up routing
- Configure Internet Gateway and NAT Gateway

#### Lab 07: Creating and Using Modules
**Path**: `intermediate/lab-07-modules/`  
**Time**: 40 min | **Difficulty**: ⭐⭐⭐  
**Topics**: Modules, Module Sources, Versioning  
**What You'll Learn**:
- Create reusable modules
- Module inputs and outputs
- Module composition
- Version pinning

#### Lab 08: State Management and Remote Backend
**Path**: `intermediate/lab-08-state-management/`  
**Time**: 35 min | **Difficulty**: ⭐⭐  
**Topics**: State Files, Remote Backend, State Locking  
**What You'll Learn**:
- Understand Terraform state
- Configure S3 backend
- Enable state locking with DynamoDB
- State operations (list, show, mv, rm)

#### Lab 09: RDS Database with Multi-AZ
**Path**: `intermediate/lab-09-rds-database/`  
**Time**: 35 min | **Difficulty**: ⭐⭐  
**Topics**: RDS, Database Subnets, Parameter Groups, Secrets  
**What You'll Learn**:
- Create RDS instances
- Configure subnet groups
- Set up security for databases
- Use sensitive variables

#### Lab 10: Terraform Workspaces
**Path**: `intermediate/lab-10-workspaces/`  
**Time**: 30 min | **Difficulty**: ⭐⭐  
**Topics**: Workspaces, Environment Management  
**What You'll Learn**:
- Create and switch workspaces
- Environment-specific configurations
- Workspace-aware resource naming
- When to use workspaces vs. separate states

---

### **ADVANCED** (5 Labs)

#### Lab 11: Load Balancer + Auto Scaling
**Path**: `advanced/lab-11-load-balancer-asg/`  
**Time**: 60 min | **Difficulty**: ⭐⭐⭐  
**Topics**: ALB, Target Groups, Launch Templates, Auto Scaling  
**What You'll Learn**:
- Create Application Load Balancer
- Configure target groups and health checks
- Set up launch templates
- Configure Auto Scaling Groups
- Scaling policies

#### Lab 12: Remote State with Team Collaboration
**Path**: `advanced/lab-12-remote-state-collab/`  
**Time**: 40 min | **Difficulty**: ⭐⭐⭐  
**Topics**: Remote State, State Locking, Backend Configuration  
**What You'll Learn**:
- Configure S3 + DynamoDB backend
- State encryption
- State locking mechanisms
- Team collaboration best practices

#### Lab 13: Dynamic Blocks and For Expressions
**Path**: `advanced/lab-13-dynamic-blocks/`  
**Time**: 35 min | **Difficulty**: ⭐⭐⭐  
**Topics**: Dynamic Blocks, For Expressions, Conditionals  
**What You'll Learn**:
- Use dynamic blocks for repetitive config
- For expressions and transformations
- Conditional resource creation
- Complex variable structures

#### Lab 14: Import Existing AWS Resources
**Path**: `advanced/lab-14-import-resources/`  
**Time**: 30 min | **Difficulty**: ⭐⭐⭐  
**Topics**: Import, State Operations, Resource Migration  
**What You'll Learn**:
- Import existing AWS resources
- Generate configuration from imports
- Migrate resources between states
- Handle import conflicts

#### Lab 15: Complete 3-Tier Web Application
**Path**: `advanced/lab-15-three-tier-app/`  
**Time**: 90 min | **Difficulty**: ⭐⭐⭐⭐  
**Topics**: Multi-tier Architecture, All Previous Concepts  
**What You'll Build**:
- VPC with public/private subnets
- Web tier (ALB + EC2 in ASG)
- Application tier (EC2 in private subnet)
- Database tier (RDS Multi-AZ)
- Complete with modules, remote state, monitoring

---

## 🚀 Quick Start

```bash
# Start with basics
cd terraform-practice/basics/lab-01-s3-bucket
cat README.md

# Follow the standard workflow
terraform init
terraform plan
terraform apply
terraform destroy
```

## 📈 Suggested Learning Path

### Week 1: Basics
- Days 1-2: Labs 01-02 (S3, EC2)
- Days 3-4: Labs 03-04 (Security Groups, Variables)
- Day 5: Lab 05 (Data Sources)

### Week 2: Intermediate
- Days 1-2: Lab 06 (VPC Networking)
- Days 3-4: Labs 07-08 (Modules, State)
- Day 5: Labs 09-10 (RDS, Workspaces)

### Week 3: Advanced
- Days 1-2: Lab 11 (Load Balancer + ASG)
- Day 3: Labs 12-13 (Remote State, Dynamic Blocks)
- Day 4: Lab 14 (Import Resources)
- Day 5: Lab 15 (Complete 3-Tier App)

## 💰 Cost Estimates

- **Basics Labs**: ~$0-0.05/hour (mostly free tier)
- **Intermediate Labs**: ~$0.10-0.20/hour
- **Advanced Labs**: ~$0.30-0.50/hour

**ALWAYS destroy resources after each lab!**

## 📋 Lab Completion Checklist

```markdown
### Basics (Foundational)
- [ ] Lab 01: S3 Bucket
- [ ] Lab 02: EC2 Instance
- [ ] Lab 03: Security Groups
- [ ] Lab 04: Variables & Outputs
- [ ] Lab 05: Data Sources

### Intermediate (Building Blocks)
- [ ] Lab 06: VPC Networking
- [ ] Lab 07: Modules
- [ ] Lab 08: State Management
- [ ] Lab 09: RDS Database
- [ ] Lab 10: Workspaces

### Advanced (Real-World)
- [ ] Lab 11: Load Balancer + ASG
- [ ] Lab 12: Remote State Collaboration
- [ ] Lab 13: Dynamic Blocks
- [ ] Lab 14: Import Resources
- [ ] Lab 15: 3-Tier Application
```

## 🎯 What You'll Master

After completing all labs, you'll be able to:
- ✅ Write production-ready Terraform code
- ✅ Manage infrastructure for real applications
- ✅ Use modules for code reusability
- ✅ Handle state management properly
- ✅ Implement security best practices
- ✅ Build multi-tier architectures
- ✅ Collaborate with teams using remote state
- ✅ Import and manage existing resources
- ✅ Use advanced Terraform features

## 📚 Additional Resources

- Terraform Official Docs: https://developer.hashicorp.com/terraform
- AWS Provider Docs: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- Your Learning Content: `01-basics/`, `02-intermediate/`, `03-advanced/`

## 🆘 Need Help?

- Review the concept in the corresponding learning module
- Check AWS provider documentation
- Use `terraform console` to test expressions
- Review solution files (when provided)
- Ask for help!

Happy Learning! 🚀
