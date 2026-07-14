#!/usr/bin/env python3
"""
Generate all missing DevSecOps content
This script creates all missing chapters, labs, and projects
"""

import os
from pathlib import Path

# Define all content to be created
CONTENT_MAP = {
    "01-basics/05-first-security-pipeline.md": """# Building Your First Security Pipeline

[Complete chapter with CI/CD integration, GitHub Actions examples, practical exercises]
""",
    
    "02-intermediate/08-kubernetes-security.md": """# Kubernetes Security

[Pod security, RBAC, network policies, admission controllers, secrets management in K8s]
""",
    
    "02-intermediate/09-infrastructure-as-code-security.md": """# Infrastructure as Code Security

[Terraform/CloudFormation security, tfsec, Checkov, policy as code, secure IaC patterns]
""",
    
    "02-intermediate/10-secrets-management-advanced.md": """# Advanced Secrets Management

[HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, secret rotation, dynamic secrets]
""",
    
    "02-intermediate/11-api-security.md": """# API Security

[OAuth/OIDC, JWT, API gateways, rate limiting, API scanning, GraphQL security]
""",
    
    "02-intermediate/12-security-monitoring.md": """# Security Monitoring

[SIEM, security logging, alerting, threat detection, incident response automation]
""",
    
    "02-intermediate/13-compliance-basics.md": """# Compliance Basics

[SOC 2, PCI-DSS, HIPAA, GDPR basics, compliance as code, audit logging]
""",
    
    "03-advanced/14-zero-trust-architecture.md": """# Zero-Trust Architecture

[Zero trust principles, service mesh security, mTLS, workload identity, microsegmentation]
""",
    
    "03-advanced/15-threat-modeling.md": """# Threat Modeling

[STRIDE, DREAD, attack trees, security design reviews, threat intelligence]
""",
    
    "03-advanced/16-supply-chain-security.md": """# Supply Chain Security

[SBOM, Sigstore, image signing, provenance, dependency security, software attestation]
""",
    
    "03-advanced/17-cloud-native-security.md": """# Cloud-Native Security Patterns

[Service mesh, eBPF, Falco, runtime security, container breakout prevention]
""",
    
    "03-advanced/18-security-automation-at-scale.md": """# Security Automation at Scale

[Scaling security testing, distributed scanning, auto-remediation, security orchestration]
""",
    
    "03-advanced/19-incident-response-devsecops.md": """# Incident Response in DevSecOps

[Incident detection, response playbooks, forensics, post-mortems, security chaos engineering]
""",
    
    "03-advanced/20-real-world-devsecops-project.md": """# Real-World DevSecOps Project

[20-page capstone project: End-to-end DevSecOps for FinTech application]
"""
}

LAB_MAP = {
    "devsecops-practice/lab-02-sast-dast/README.md": """# Lab 2: SAST and DAST Integration""",
    "devsecops-practice/lab-03-container-hardening/README.md": """# Lab 3: Container Security Hardening""",
    "devsecops-practice/lab-04-secrets-vault/README.md": """# Lab 4: Secrets Management with Vault""",
    "devsecops-practice/lab-05-kubernetes-security/README.md": """# Lab 5: Kubernetes Security""",
    "devsecops-practice/lab-06-iac-security/README.md": """# Lab 6: Infrastructure as Code Security""",
    "devsecops-practice/lab-07-cicd-hardening/README.md": """# Lab 7: CI/CD Pipeline Hardening""",
    "devsecops-practice/lab-08-complete-platform/README.md": """# Lab 8: Complete DevSecOps Platform"""
}

def create_file(path, content):
    """Create file with content"""
    full_path = Path("devsecops-learning") / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(full_path, 'w') as f:
        f.write(content)
    
    print(f"Created: {path}")

def main():
    print("Generating all missing DevSecOps content...")
    print("=" * 60)
    
    # Create chapters
    print("\nCreating chapters...")
    for path, content in CONTENT_MAP.items():
        create_file(path, content)
    
    # Create labs
    print("\nCreating labs...")
    for path, content in LAB_MAP.items():
        create_file(path, content)
    
    print("\n" + "=" * 60)
    print(f"✅ Created {len(CONTENT_MAP)} chapters")
    print(f"✅ Created {len(LAB_MAP)} labs")
    print("\n🎉 All DevSecOps content structure generated!")
    print("\nNote: Content contains placeholders. Full content will be added next.")

if __name__ == "__main__":
    main()
