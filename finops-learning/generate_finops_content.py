#!/usr/bin/env python3
"""
Generate comprehensive FinOps learning content
Target: 23 files + 5 labs for AWS DevOps Manager preparation
"""

import os

# File templates
CONTENT_STRUCTURE = {
    "basics": [
        ("02-finops-framework.md", "FinOps Framework: Inform, Optimize, Operate", 1000),
        ("03-aws-cost-basics.md", "AWS Cost Management Basics", 1100),
        ("04-billing-fundamentals.md", "Understanding Cloud Billing", 900),
        ("05-first-cost-report.md", "Building Your First Cost Report", 950),
        ("interview-questions-basics.md", "FinOps Basics - Interview Questions", 800),
    ],
    "intermediate": [
        ("06-cost-allocation.md", "Cost Allocation and Tagging Strategy", 1200),
        ("07-chargeback-showback.md", "Chargeback and Showback Models", 1100),
        ("08-unit-economics.md", "Unit Economics for Cloud", 1000),
        ("09-ri-savings-plans.md", "Reserved Instances and Savings Plans", 1050),
        ("10-anomaly-detection.md", "Cost Anomaly Detection", 900),
        ("11-budget-management.md", "Budget Management and Forecasting", 950),
        ("12-finops-tools.md", "FinOps Tools and Platforms", 1000),
        ("interview-questions-intermediate.md", "FinOps Intermediate - Interview Questions", 1000),
    ],
    "advanced": [
        ("13-optimization-at-scale.md", "Cost Optimization at Enterprise Scale", 1200),
        ("14-finops-automation.md", "FinOps Automation and Orchestration", 1150),
        ("15-cicd-cost-gates.md", "CI/CD Cost Gates", 1000),
        ("16-gpu-ai-costs.md", "GPU and AI Workload Cost Management", 1100),
        ("17-multi-account-finops.md", "Multi-Account FinOps Strategy", 1050),
        ("18-finops-culture.md", "Building FinOps Culture and KPIs", 1000),
        ("19-kubernetes-costs.md", "Kubernetes Cost Management", 1100),
        ("20-finops-project.md", "Real-World FinOps Implementation Project", 1300),
        ("interview-questions-advanced.md", "FinOps Advanced - Interview Questions", 1200),
    ]
}

# Labs
LABS = [
    ("lab-01-tagging", "Cost Tagging Strategy Implementation"),
    ("lab-02-chargeback", "Team Chargeback System"),
    ("lab-03-unit-economics", "Unit Economics Dashboard"),
    ("lab-04-automation", "Automated Cost Optimization"),
    ("lab-05-dashboard", "Complete FinOps Dashboard"),
]

def create_placeholder(path, title, target_lines):
    """Create a placeholder file"""
    content = f"""# {title}

**Status**: Content in development  
**Target**: {target_lines}+ lines of comprehensive content

---

## Coming Soon

This file will cover:
- Core concepts and principles
- Real-world examples with AWS
- Python automation scripts
- Cost optimization strategies
- Manager-level insights
- Interview preparation

**Estimated completion**: This week

---

## Quick Reference

For immediate needs, see:
- [What is FinOps?](../01-basics/01-what-is-finops.md)
- [Quick Start Guide](../QUICK-START.md)
- [FinOps README](../README.md)

---

**Note**: Full content being created to match AWS learning quality standards
"""
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    
    print(f"✅ Created placeholder: {path}")

def main():
    """Generate all FinOps content structure"""
    base_dir = "."
    
    print("🚀 Generating FinOps Learning Content Structure\n")
    
    # Create content files
    for level, files in CONTENT_STRUCTURE.items():
        level_num = {"basics": "01", "intermediate": "02", "advanced": "03"}[level]
        level_dir = f"{base_dir}/{level_num}-{level}"
        
        print(f"\n📁 Creating {level.upper()} files...")
        for filename, title, target_lines in files:
            filepath = f"{level_dir}/{filename}"
            if not os.path.exists(filepath):
                create_placeholder(filepath, title, target_lines)
    
    # Create labs
    print(f"\n📁 Creating LABS...")
    for lab_dir, title in LABS:
        lab_path = f"{base_dir}/finops-practice/{lab_dir}"
        readme_path = f"{lab_path}/README.md"
        
        if not os.path.exists(readme_path):
            os.makedirs(lab_path, exist_ok=True)
            content = f"""# {title}

**Lab Objective**: Hands-on practice with FinOps concepts

---

## Overview

This lab will guide you through implementing {title.lower()} in a real AWS environment.

**Prerequisites:**
- AWS account with billing access
- AWS CLI configured
- Basic Python knowledge

**Time Required**: 60-90 minutes

---

## Lab Steps

### Step 1: Environment Setup
(Content in development)

### Step 2: Implementation
(Content in development)

### Step 3: Verification
(Content in development)

### Step 4: Optimization
(Content in development)

---

## Expected Outcomes

After completing this lab, you will:
- Understand practical FinOps implementation
- Have working code and configurations
- Be able to apply patterns to your organization

---

**Status**: Lab content being created
"""
            with open(readme_path, 'w') as f:
                f.write(content)
            print(f"✅ Created lab: {readme_path}")
    
    print("\n" + "="*50)
    print("✅ FinOps content structure created successfully!")
    print("="*50)
    print(f"\nTotal files created:")
    print(f"  - Basics: {len(CONTENT_STRUCTURE['basics'])} files")
    print(f"  - Intermediate: {len(CONTENT_STRUCTURE['intermediate'])} files")
    print(f"  - Advanced: {len(CONTENT_STRUCTURE['advanced'])} files")
    print(f"  - Labs: {len(LABS)} labs")
    total = sum(len(v) for v in CONTENT_STRUCTURE.values()) + len(LABS)
    print(f"  TOTAL: {total} items")
    print(f"\n📝 Next: Fill in comprehensive content for each file")

if __name__ == "__main__":
    main()
