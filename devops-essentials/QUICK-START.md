# DevOps Essentials - Quick Start Guide

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
