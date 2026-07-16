#!/usr/bin/env python3
"""
DevOps Essentials Content Generator

Generates all topics, labs, and interview questions for Git, Docker, and Jenkins curriculum.
Following the same structure and quality as AIOps, DevSecOps, and MLOps curricula.

Usage:
    python generate_devops_content.py
"""

import os
from pathlib import Path

def create_directory_structure():
    """Create the complete directory structure"""
    
    base_dirs = [
        "01-git/basics",
        "01-git/intermediate",
        "01-git/advanced",
        "01-git/git-practice/lab-01-basics",
        "01-git/git-practice/lab-02-branching",
        "01-git/git-practice/lab-03-collaboration",
        "01-git/git-practice/lab-04-advanced",
        "01-git/git-practice/lab-05-gitflow",
        "02-docker/basics",
        "02-docker/intermediate",
        "02-docker/advanced",
        "02-docker/docker-practice/lab-01-basics",
        "02-docker/docker-practice/lab-02-dockerfile",
        "02-docker/docker-practice/lab-03-compose",
        "02-docker/docker-practice/lab-04-networking",
        "02-docker/docker-practice/lab-05-production",
        "03-jenkins/basics",
        "03-jenkins/intermediate",
        "03-jenkins/advanced",
        "03-jenkins/jenkins-practice/lab-01-setup",
        "03-jenkins/jenkins-practice/lab-02-first-pipeline",
        "03-jenkins/jenkins-practice/lab-03-git-integration",
        "03-jenkins/jenkins-practice/lab-04-docker-integration",
        "03-jenkins/jenkins-practice/lab-05-complete-cicd",
        "04-integration/project-01-simple-cicd",
        "04-integration/project-02-microservices",
        "04-integration/project-03-multi-env",
        "04-integration/project-04-blue-green",
        "04-integration/project-05-gitops",
    ]
    
    for dir_path in base_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {dir_path}")

# Topic definitions for all three tools
GIT_TOPICS = {
    "basics": [
        ("01-what-is-git.md", "What is Git and Version Control"),
        ("02-installation-configuration.md", "Git Installation and Configuration"),
        ("03-basic-commands.md", "Basic Git Commands"),
        ("04-git-workflow.md", "Understanding Git Workflow"),
        ("05-remote-repositories.md", "Working with Remote Repositories"),
    ],
    "intermediate": [
        ("06-branching-merging.md", "Branching and Merging"),
        ("07-branching-strategies.md", "Git Branching Strategies"),
        ("08-resolving-conflicts.md", "Resolving Merge Conflicts"),
        ("09-rebase-vs-merge.md", "Git Rebase vs Merge"),
        ("10-stash-cherry-pick.md", "Git Stash and Cherry-pick"),
        ("11-tags-releases.md", "Git Tags and Releases"),
        ("12-pull-requests.md", "Collaborating with Pull Requests"),
    ],
    "advanced": [
        ("13-git-internals.md", "Git Internals"),
        ("14-advanced-operations.md", "Advanced Git Operations"),
        ("15-git-hooks.md", "Git Hooks and Automation"),
        ("16-performance.md", "Git Performance Optimization"),
        ("17-monorepo-strategies.md", "Monorepo vs Multi-repo"),
        ("18-security.md", "Git Security Best Practices"),
        ("19-enterprise-git.md", "Git in Enterprise"),
        ("20-troubleshooting.md", "Troubleshooting and Recovery"),
    ]
}

DOCKER_TOPICS = {
    "basics": [
        ("01-what-is-docker.md", "What is Docker and Containerization"),
        ("02-installation-setup.md", "Docker Installation and Setup"),
        ("03-images-containers.md", "Docker Images and Containers"),
        ("04-dockerfile-basics.md", "Dockerfile Basics"),
        ("05-basic-commands.md", "Essential Docker Commands"),
    ],
    "intermediate": [
        ("06-multistage-builds.md", "Multi-stage Docker Builds"),
        ("07-volumes.md", "Docker Volumes and Data Persistence"),
        ("08-networking.md", "Docker Networking"),
        ("09-docker-compose.md", "Docker Compose"),
        ("10-environment-config.md", "Environment Variables and Configuration"),
        ("11-registry.md", "Docker Registry and Image Management"),
        ("12-logging-debugging.md", "Container Logging and Debugging"),
    ],
    "advanced": [
        ("13-optimization.md", "Docker Image Optimization"),
        ("14-security.md", "Docker Security Best Practices"),
        ("15-production.md", "Docker in Production"),
        ("16-orchestration-intro.md", "Container Orchestration Introduction"),
        ("17-docker-swarm.md", "Docker Swarm Basics"),
        ("18-performance.md", "Docker Performance Tuning"),
        ("19-multi-arch.md", "Building for Multiple Architectures"),
        ("20-enterprise-patterns.md", "Docker Enterprise Patterns"),
    ]
}

JENKINS_TOPICS = {
    "basics": [
        ("01-what-is-jenkins.md", "What is Jenkins and CI/CD"),
        ("02-installation.md", "Jenkins Installation and Configuration"),
        ("03-first-job.md", "Creating Your First Jenkins Job"),
        ("04-ui-navigation.md", "Jenkins UI and Navigation"),
        ("05-build-triggers.md", "Basic Build Triggers"),
    ],
    "intermediate": [
        ("06-pipeline-as-code.md", "Jenkins Pipeline as Code"),
        ("07-declarative-scripted.md", "Declarative vs Scripted Pipelines"),
        ("08-git-integration.md", "Integrating Jenkins with Git"),
        ("09-docker-integration.md", "Jenkins and Docker Integration"),
        ("10-testing.md", "Automated Testing in Jenkins"),
        ("11-plugins.md", "Jenkins Plugins Ecosystem"),
        ("12-parameters-artifacts.md", "Build Parameters and Artifacts"),
    ],
    "advanced": [
        ("13-distributed-builds.md", "Distributed Jenkins (Master-Agent)"),
        ("14-pipeline-libraries.md", "Jenkins Pipeline Libraries"),
        ("15-security.md", "Jenkins Security and Access Control"),
        ("16-monitoring.md", "Jenkins Monitoring and Observability"),
        ("17-blue-ocean.md", "Blue Ocean and Modern UI"),
        ("18-configuration-as-code.md", "Jenkins Configuration as Code"),
        ("19-performance.md", "Jenkins Performance Optimization"),
        ("20-enterprise-patterns.md", "Enterprise Jenkins Patterns"),
    ]
}

def generate_topic_file(tool, level, filename, title):
    """Generate a single topic markdown file"""
    
    content = f"""# {title}

Understanding {title.lower()} and practical implementation.

---

## Overview

[Brief introduction to the topic]

---

## Key Concepts

### Concept 1

[Explanation]

### Concept 2

[Explanation]

---

## Practical Examples

```bash
# Example code here
```

---

## Best Practices

1. **Practice 1**: Description
2. **Practice 2**: Description
3. **Practice 3**: Description

---

## Common Pitfalls

- **Pitfall 1**: How to avoid
- **Pitfall 2**: How to avoid

---

## Real-World Use Cases

### Use Case 1
[Description and example]

### Use Case 2
[Description and example]

---

## Hands-On Exercise

Try this yourself:

```bash
# Step-by-step commands
```

---

## Interview Tips

Common questions:
1. Question about this topic
2. Another question
3. Third question

---

## Next Steps

Continue to the next topic or practice in the labs.

---

**Next:** [Next Topic →](next-topic.md)

*This is a placeholder. Full content to be developed.*
"""
    
    filepath = f"{tool}/{level}/{filename}"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Generated: {filepath}")

def generate_all_topics():
    """Generate all topic files"""
    
    print("\n=== Generating Git Topics ===")
    for level, topics in GIT_TOPICS.items():
        for filename, title in topics:
            generate_topic_file("01-git", level, filename, title)
    
    print("\n=== Generating Docker Topics ===")
    for level, topics in DOCKER_TOPICS.items():
        for filename, title in topics:
            generate_topic_file("02-docker", level, filename, title)
    
    print("\n=== Generating Jenkins Topics ===")
    for level, topics in JENKINS_TOPICS.items():
        for filename, title in topics:
            generate_topic_file("03-jenkins", level, filename, title)

def generate_lab_file(tool, lab_num, lab_name):
    """Generate a lab README file"""
    
    content = f"""# Lab {lab_num:02d}: {lab_name}

Hands-on practice with {lab_name.lower()}.

---

## Objectives

By completing this lab, you will:
- [ ] Objective 1
- [ ] Objective 2
- [ ] Objective 3

---

## Prerequisites

- Tool installed
- Basic understanding of concepts
- Terminal/command line access

---

## Lab Duration

**Estimated Time:** 1-2 hours

---

## Step-by-Step Guide

### Step 1: Setup

```bash
# Setup commands
```

### Step 2: Core Exercise

```bash
# Main lab commands
```

### Step 3: Verification

```bash
# Verification commands
```

---

## Exercises

### Exercise 1: Basic Task
[Description and commands]

### Exercise 2: Intermediate Task
[Description and commands]

### Exercise 3: Advanced Task
[Description and commands]

---

## Validation

Check your work:

```bash
# Validation commands
```

Expected output:
```
[Expected results]
```

---

## Troubleshooting

**Issue 1:** Problem description  
**Solution:** How to fix

**Issue 2:** Problem description  
**Solution:** How to fix

---

## Clean Up

```bash
# Cleanup commands
```

---

## Additional Challenges

1. **Challenge 1**: Description
2. **Challenge 2**: Description
3. **Challenge 3**: Description

---

## Summary

What you learned:
- Key takeaway 1
- Key takeaway 2
- Key takeaway 3

---

## Next Steps

- [ ] Review the concepts
- [ ] Complete additional exercises
- [ ] Move to next lab

---

*This is a placeholder. Full lab content to be developed.*
"""
    
    lab_dir = f"{tool}/{tool.split('-')[1]}-practice/lab-{lab_num:02d}-{lab_name.lower().replace(' ', '-')}"
    filepath = f"{lab_dir}/README.md"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Generated: {filepath}")

def generate_interview_questions(tool, level):
    """Generate interview questions file"""
    
    content = f"""# {tool.split('-')[1].title()} Interview Questions - {level.title()} Level

Comprehensive interview questions for {tool.split('-')[1]} at {level} level.

---

## Conceptual Questions

### Q1: [Question about fundamental concept]

**Answer:**

[Detailed answer]

---

### Q2: [Another fundamental question]

**Answer:**

[Detailed answer]

---

## Practical Questions

### Q3: [Hands-on scenario question]

**Answer:**

```bash
# Code example
```

[Explanation]

---

### Q4: [Implementation question]

**Answer:**

[Step-by-step answer]

---

## Troubleshooting Questions

### Q5: [Debug scenario]

**Answer:**

[How to troubleshoot]

---

## Best Practices Questions

### Q6: [Best practice question]

**Answer:**

[Best practice explanation]

---

## Scenario-Based Questions

### Q7: [Real-world scenario]

**Answer:**

[Detailed solution]

---

## Quick Answer Questions

### Q8-Q20: [Rapid-fire questions]

**Q8:** Question  
**A:** Answer

**Q9:** Question  
**A:** Answer

[... continue to Q20]

---

## Interview Tips

- Tip 1
- Tip 2
- Tip 3

---

*This is a placeholder. Full interview content to be developed.*
"""
    
    filepath = f"{tool}/{level}/interview-questions-{level}.md"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Generated: {filepath}")

def generate_quick_start():
    """Generate quick start guide"""
    
    content = """# DevOps Essentials - Quick Start Guide

Get up and running with Git, Docker, and Jenkins in 30 minutes.

---

## Prerequisites Check

Before starting, ensure you have:
- [ ] Computer with admin access
- [ ] Internet connection
- [ ] Terminal/command line access
- [ ] Text editor (VS Code recommended)

---

## 30-Minute Quick Start

### Minute 0-10: Git Setup

```bash
# Install Git
# Windows: Download from https://git-scm.com
# Mac: brew install git
# Linux: sudo apt-get install git

# Verify installation
git --version

# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Create first repository
mkdir my-first-repo
cd my-first-repo
git init
echo "# My First Repo" > README.md
git add README.md
git commit -m "Initial commit"
```

### Minute 10-20: Docker Setup

```bash
# Install Docker
# Download from https://docs.docker.com/get-docker/

# Verify installation
docker --version

# Run first container
docker run hello-world

# Run interactive container
docker run -it ubuntu bash
```

### Minute 20-30: Jenkins Setup

```bash
# Run Jenkins in Docker (easiest way)
docker run -p 8080:8080 jenkins/jenkins:lts

# Open browser to http://localhost:8080
# Follow setup wizard
# Install suggested plugins
# Create admin user
```

---

## What's Next?

Choose your learning path:

1. **Complete Beginner**: Start with Git basics
2. **Some Experience**: Jump to Docker intermediate
3. **Ready to Build**: Go straight to Jenkins pipelines

---

## Recommended Learning Order

```
Week 1: Git Basics + Lab 01
Week 2: Docker Basics + Lab 01
Week 3: Jenkins Basics + Lab 01
Week 4: Integration Project
```

---

## Get Help

- Check the topic READMEs
- Complete the hands-on labs
- Practice with interview questions
- Build integration projects

---

**Ready to Start?** → [Begin with Git](01-git/basics/01-what-is-git.md)
"""
    
    with open("QUICK-START.md", 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Generated: QUICK-START.md")

def main():
    """Main function to generate all content"""
    
    print("=" * 60)
    print("DevOps Essentials Content Generator")
    print("=" * 60)
    
    print("\n1. Creating directory structure...")
    create_directory_structure()
    
    print("\n2. Generating topic files...")
    generate_all_topics()
    
    print("\n3. Generating lab files...")
    # Git labs
    git_labs = [
        (1, "Basics"),
        (2, "Branching"),
        (3, "Collaboration"),
        (4, "Advanced"),
        (5, "GitFlow")
    ]
    for num, name in git_labs:
        generate_lab_file("01-git", num, name)
    
    # Docker labs
    docker_labs = [
        (1, "Basics"),
        (2, "Dockerfile"),
        (3, "Compose"),
        (4, "Networking"),
        (5, "Production")
    ]
    for num, name in docker_labs:
        generate_lab_file("02-docker", num, name)
    
    # Jenkins labs
    jenkins_labs = [
        (1, "Setup"),
        (2, "First Pipeline"),
        (3, "Git Integration"),
        (4, "Docker Integration"),
        (5, "Complete CICD")
    ]
    for num, name in jenkins_labs:
        generate_lab_file("03-jenkins", num, name)
    
    print("\n4. Generating interview questions...")
    for tool in ["01-git", "02-docker", "03-jenkins"]:
        for level in ["basics", "intermediate", "advanced"]:
            generate_interview_questions(tool, level)
    
    print("\n5. Generating quick start guide...")
    generate_quick_start()
    
    print("\n" + "=" * 60)
    print("✅ Content Generation Complete!")
    print("=" * 60)
    print("\nGenerated:")
    print("  - 60 topic files")
    print("  - 15 lab files")
    print("  - 9 interview question files")
    print("  - 1 quick start guide")
    print("\nTotal: 85+ files created")
    print("\nNote: Files contain placeholders. Full content development needed.")
    print("=" * 60)

if __name__ == "__main__":
    main()
