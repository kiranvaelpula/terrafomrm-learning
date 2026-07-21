# Terraform Practice Labs

Complete hands-on labs organized by difficulty level. Each lab includes objectives, tasks, and solutions.

## 📚 Lab Structure

### **Basics Labs** (terraform-practice/basics/)
- Lab 01: First S3 Bucket
- Lab 02: EC2 Instance with Tags
- Lab 03: Security Groups
- Lab 04: Variables and Outputs
- Lab 05: Data Sources

### **Intermediate Labs** (terraform-practice/intermediate/)
- Lab 06: VPC with Subnets
- Lab 07: Modules - Creating and Using
- Lab 08: State Management
- Lab 09: RDS Database
- Lab 10: Workspaces

### **Advanced Labs** (terraform-practice/advanced/)
- Lab 11: Load Balancer + Auto Scaling
- Lab 12: Remote State with S3
- Lab 13: Dynamic Blocks
- Lab 14: Import Existing Resources
- Lab 15: Complete 3-Tier Architecture

## 🚀 Getting Started

1. **Prerequisites**:
   - Terraform installed (`terraform version`)
   - AWS CLI configured (`aws configure --profile terraform_practice`)
   - Valid AWS credentials

2. **Start with Basics**:
   ```bash
   cd terraform-practice/basics/lab-01-s3-bucket
   cat README.md  # Read the lab instructions
   ```

3. **Lab Workflow**:
   ```bash
   terraform init       # Initialize
   terraform fmt        # Format code
   terraform validate   # Check syntax
   terraform plan       # Preview
   terraform apply      # Create resources
   terraform destroy    # Clean up (ALWAYS!)
   ```

## 💡 Best Practices

- Always use unique resource names
- Tag all resources with your name/project
- Destroy resources after each lab to avoid charges
- Read the README before starting each lab
- Try writing code yourself before looking at solutions

## 📖 Learning Path

1. Complete basics labs 01-05
2. Move to intermediate labs 06-10
3. Finish with advanced labs 11-15

## 🎯 Lab Completion Tracking

Track your progress:
- [ ] Basics: Lab 01 - S3 Bucket
- [ ] Basics: Lab 02 - EC2 Instance
- [ ] Basics: Lab 03 - Security Groups
- [ ] Basics: Lab 04 - Variables
- [ ] Basics: Lab 05 - Data Sources
- [ ] Intermediate: Lab 06 - VPC
- [ ] Intermediate: Lab 07 - Modules
- [ ] Intermediate: Lab 08 - State
- [ ] Intermediate: Lab 09 - RDS
- [ ] Intermediate: Lab 10 - Workspaces
- [ ] Advanced: Lab 11 - Load Balancer
- [ ] Advanced: Lab 12 - Remote State
- [ ] Advanced: Lab 13 - Dynamic Blocks
- [ ] Advanced: Lab 14 - Import Resources
- [ ] Advanced: Lab 15 - 3-Tier App

Good luck with your Terraform learning journey!
