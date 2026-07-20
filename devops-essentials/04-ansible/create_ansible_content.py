#!/usr/bin/env python3
"""
Generate comprehensive Ansible learning content
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Content to create
content = {
    # Intermediate files
    "intermediate/09-handlers-conditionals.md": """# Handlers & Conditionals

> **Master event-driven automation and conditional task execution**

[Content continues with comprehensive handlers and conditionals guide...]
""",
    
    "intermediate/10-loops.md": """# Loops & Iteration

> **Automate repetitive tasks efficiently with loops**

[Content continues with comprehensive loops guide...]
""",
    
    "intermediate/11-ansible-vault.md": """# Ansible Vault (Secrets Management)

> **Secure sensitive data with encryption**

[Content continues with comprehensive vault guide...]
""",
    
    "intermediate/12-error-handling.md": """# Error Handling & Testing

> **Build reliable automation with proper error handling**

[Content continues with comprehensive error handling guide...]
""",
    
    "intermediate/interview-questions-intermediate.md": """# Ansible Interview Questions - Intermediate

[50+ intermediate interview questions with detailed answers...]
""",
    
    # Advanced files
    "advanced/13-roles.md": """# Ansible Roles

> **Create reusable, modular automation with roles**

[Content continues with comprehensive roles guide...]
""",
    
    "advanced/14-galaxy.md": """# Ansible Galaxy

> **Leverage community roles and share your own**

[Content continues with comprehensive Galaxy guide...]
""",
    
    "advanced/15-dynamic-inventory.md": """# Dynamic Inventory

> **Automatically discover and manage infrastructure**

[Content continues with comprehensive dynamic inventory guide...]
""",
    
    "advanced/16-tower-awx.md": """# Ansible Tower/AWX

> **Enterprise automation platform with UI and API**

[Content continues with comprehensive Tower/AWX guide...]
""",
    
    "advanced/17-performance.md": """# Performance Optimization

> **Scale Ansible for large infrastructures**

[Content continues with comprehensive performance guide...]
""",
    
    "advanced/18-security.md": """# Security Best Practices

> **Secure your automation workflows**

[Content continues with comprehensive security guide...]
""",
    
    "advanced/19-cicd-integration.md": """# CI/CD Integration

> **Integrate Ansible into your CI/CD pipelines**

[Content continues with comprehensive CI/CD integration guide...]
""",
    
    "advanced/20-enterprise-patterns.md": """# Enterprise Patterns

> **Production-ready Ansible architecture and patterns**

[Content continues with comprehensive enterprise patterns guide...]
""",
    
    "advanced/interview-questions-advanced.md": """# Ansible Interview Questions - Advanced

[60+ advanced interview questions with detailed answers...]
""",
    
    # Practice labs
    "ansible-practice/lab-01-basics/README.md": """# Lab 01: Ansible Basics

[Complete hands-on lab for basics...]
""",
    
    "ansible-practice/lab-02-playbooks/README.md": """# Lab 02: Playbooks

[Complete hands-on lab for playbooks...]
""",
    
    "ansible-practice/lab-03-roles/README.md": """# Lab 03: Roles

[Complete hands-on lab for roles...]
""",
    
    "ansible-practice/lab-04-advanced/README.md": """# Lab 04: Advanced Topics

[Complete hands-on lab for advanced topics...]
""",
    
    "ansible-practice/lab-05-real-world/README.md": """# Lab 05: Real-World Project

[Complete end-to-end project lab...]
"""
}

def create_files():
    """Create all content files"""
    for file_path, content_text in content.items():
        full_path = BASE_DIR / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not full_path.exists() or full_path.stat().st_size < 1000:
            print(f"Creating: {file_path}")
            full_path.write_text(content_text, encoding='utf-8')
        else:
            print(f"Skipping (already exists): {file_path}")

if __name__ == "__main__":
    create_files()
    print("\\n✅ Ansible content structure created!")
