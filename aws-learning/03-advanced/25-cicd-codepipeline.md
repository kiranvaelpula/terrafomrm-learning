# Chapter 25: AWS CI/CD - CodePipeline, CodeBuild, CodeDeploy, CodeCommit

## Overview

AWS provides a native suite of CI/CD services (the "Code*" family) to build fully-managed pipelines without running your own Jenkins servers. This chapter covers the complete toolchain and how the services fit together.

**What You'll Learn**
- CodeCommit — managed Git repositories
- CodeBuild — managed build service (buildspec)
- CodeDeploy — automated deployments (EC2, ECS, Lambda)
- CodePipeline — orchestrates the whole workflow
- CodeArtifact — package/dependency management
- Deployment strategies (blue/green, canary, rolling)
- Complete end-to-end pipeline example

**Prerequisites**
- Git and CI/CD fundamentals
- IAM roles and policies
- Familiarity with ECS/EC2/Lambda

---

## The AWS CI/CD Toolchain

```
┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐
│ CodeCommit │──▶│ CodeBuild  │──▶│  Tests     │──▶│ CodeDeploy │
│  (Source)  │   │  (Build)   │   │            │   │ (Deploy)   │
└────────────┘   └────────────┘   └────────────┘   └────────────┘
       └──────────────────────────────────────────────────┘
                        CodePipeline (orchestrator)
```

| Service | Equivalent | Purpose |
|---------|-----------|---------|
| **CodeCommit** | GitHub/GitLab | Managed Git repos |
| **CodeBuild** | Jenkins build agent | Compile, test, package |
| **CodeDeploy** | Ansible/Spinnaker deploy | Deploy to compute |
| **CodePipeline** | Jenkins pipeline | Orchestrate stages end-to-end |
| **CodeArtifact** | Nexus/Artifactory | Store packages/dependencies |

**Note:** CodeCommit is being de-emphasized by AWS; many teams use GitHub/GitLab as the source and keep CodePipeline/CodeBuild/CodeDeploy. The pipeline works with GitHub sources too.

---

## Part 1: CodeCommit (Source)

Fully-managed Git repositories, private, integrated with IAM.

```bash
# Create a repository
aws codecommit create-repository \
  --repository-name my-app \
  --repository-description "Application source code"

# Clone (uses IAM credentials via git-remote-codecommit or HTTPS)
git clone https://git-codecommit.us-east-1.amazonaws.com/v1/repos/my-app

# Standard git workflow after that
git add . && git commit -m "changes" && git push
```

**Key features:** IAM-based access control, encryption at rest (KMS), triggers to Lambda/SNS on push, no size limits on repos.

---

## Part 2: CodeBuild (Build)

Fully-managed build service. Define build steps in a `buildspec.yml` file at the repo root.

### buildspec.yml — the core file

```yaml
version: 0.2

env:
  variables:
    IMAGE_REPO_NAME: "my-app"
  parameter-store:
    DB_PASSWORD: "/myapp/prod/db-password"   # Pull secrets from SSM
  secrets-manager:
    API_KEY: "myapp/api:apikey"              # Pull from Secrets Manager

phases:
  install:
    runtime-versions:
      python: 3.11
    commands:
      - echo Installing dependencies...
      - pip install -r requirements.txt

  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
      - IMAGE_TAG=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)

  build:
    commands:
      - echo Running tests...
      - pytest --junitxml=test-results.xml
      - echo Building Docker image...
      - docker build -t $IMAGE_REPO_NAME:$IMAGE_TAG .
      - docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG

  post_build:
    commands:
      - echo Pushing image to ECR...
      - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
      - printf '[{"name":"api","imageUri":"%s"}]' $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG > imagedefinitions.json

reports:
  test-reports:
    files:
      - test-results.xml
    file-format: JUNITXML

artifacts:
  files:
    - imagedefinitions.json      # Passed to next stage (CodeDeploy/ECS)

cache:
  paths:
    - '/root/.cache/pip/**/*'    # Speed up subsequent builds
```

### buildspec phases explained

| Phase | Purpose |
|-------|---------|
| `install` | Install runtime + tools |
| `pre_build` | Login to registries, set up env |
| `build` | Compile, test, build artifacts |
| `post_build` | Push images, generate output artifacts |
| `reports` | Test/coverage reports (shown in console) |
| `artifacts` | Files passed to the next pipeline stage |
| `cache` | Cache dependencies for faster builds |

```bash
# Create a CodeBuild project
aws codebuild create-project \
  --name my-app-build \
  --source type=CODEPIPELINE \
  --artifacts type=CODEPIPELINE \
  --environment type=LINUX_CONTAINER,image=aws/codebuild/standard:7.0,computeType=BUILD_GENERAL1_MEDIUM,privilegedMode=true \
  --service-role arn:aws:iam::123456789012:role/CodeBuildServiceRole
```

---

## Part 3: CodeDeploy (Deploy)

Automates deployments to EC2, ECS, and Lambda with built-in deployment strategies and rollback.

### Deployment Types

| Compute | Strategies |
|---------|-----------|
| **EC2/On-prem** | In-place, Blue/Green |
| **ECS** | Blue/Green, Canary, Linear |
| **Lambda** | Canary, Linear, All-at-once |

### appspec.yml — deployment instructions

**For ECS:**
```yaml
version: 0.0
Resources:
  - TargetService:
      Type: AWS::ECS::Service
      Properties:
        TaskDefinition: <TASK_DEFINITION>
        LoadBalancerInfo:
          ContainerName: "api"
          ContainerPort: 8080
```

**For EC2 (with lifecycle hooks):**
```yaml
version: 0.0
os: linux
files:
  - source: /
    destination: /var/www/app
hooks:
  BeforeInstall:
    - location: scripts/stop_server.sh
      timeout: 300
  AfterInstall:
    - location: scripts/install_deps.sh
  ApplicationStart:
    - location: scripts/start_server.sh
  ValidateService:
    - location: scripts/health_check.sh
      timeout: 60
```

### Deployment Strategies (Lambda/ECS examples)

```
Canary:   Shift 10% traffic, wait, then 90%
   CodeDeployDefault.LambdaCanary10Percent5Minutes

Linear:   Shift 10% every N minutes until 100%
   CodeDeployDefault.LambdaLinear10PercentEvery1Minute

All-at-once: Shift 100% immediately (fastest, riskiest)
   CodeDeployDefault.LambdaAllAtOnce
```

**Automatic rollback:** CodeDeploy monitors CloudWatch alarms during deployment. If an alarm fires (error rate spikes), it automatically rolls back to the previous version.

---

## Part 4: CodePipeline (Orchestration)

Ties everything together into stages that run automatically on code changes.

### Pipeline Structure

```
┌─────────────────────────────────────────────────────────┐
│                    CodePipeline                            │
│                                                           │
│  Source ──▶ Build ──▶ Test ──▶ Approval ──▶ Deploy        │
│  (Commit)  (Build)   (Build)  (Manual)     (Deploy)       │
│    │          │         │         │            │          │
│  CodeCommit CodeBuild CodeBuild  Manual    CodeDeploy     │
│  or GitHub                       gate                     │
└─────────────────────────────────────────────────────────┘
```

### Pipeline Definition (JSON)

```json
{
  "pipeline": {
    "name": "my-app-pipeline",
    "roleArn": "arn:aws:iam::123456789012:role/CodePipelineServiceRole",
    "artifactStore": {
      "type": "S3",
      "location": "my-pipeline-artifacts-bucket"
    },
    "stages": [
      {
        "name": "Source",
        "actions": [{
          "name": "SourceAction",
          "actionTypeId": {
            "category": "Source", "owner": "AWS",
            "provider": "CodeCommit", "version": "1"
          },
          "configuration": {
            "RepositoryName": "my-app",
            "BranchName": "main"
          },
          "outputArtifacts": [{"name": "SourceOutput"}]
        }]
      },
      {
        "name": "Build",
        "actions": [{
          "name": "BuildAction",
          "actionTypeId": {
            "category": "Build", "owner": "AWS",
            "provider": "CodeBuild", "version": "1"
          },
          "configuration": {"ProjectName": "my-app-build"},
          "inputArtifacts": [{"name": "SourceOutput"}],
          "outputArtifacts": [{"name": "BuildOutput"}]
        }]
      },
      {
        "name": "Approval",
        "actions": [{
          "name": "ManualApproval",
          "actionTypeId": {
            "category": "Approval", "owner": "AWS",
            "provider": "Manual", "version": "1"
          }
        }]
      },
      {
        "name": "Deploy",
        "actions": [{
          "name": "DeployAction",
          "actionTypeId": {
            "category": "Deploy", "owner": "AWS",
            "provider": "ECS", "version": "1"
          },
          "configuration": {
            "ClusterName": "production",
            "ServiceName": "my-app"
          },
          "inputArtifacts": [{"name": "BuildOutput"}]
        }]
      }
    ]
  }
}
```

```bash
# Create the pipeline
aws codepipeline create-pipeline --cli-input-json file://pipeline.json
```

### Stage Types

| Category | Providers |
|----------|-----------|
| Source | CodeCommit, GitHub, S3, ECR, Bitbucket |
| Build | CodeBuild, Jenkins |
| Test | CodeBuild, third-party |
| Approval | Manual (human gate) |
| Deploy | CodeDeploy, ECS, CloudFormation, S3, Elastic Beanstalk, Lambda |
| Invoke | Lambda (custom actions) |

---

## Part 5: CodeArtifact (Packages)

Managed artifact repository for dependencies (npm, pip, Maven, NuGet).

```bash
# Create a domain and repository
aws codeartifact create-domain --domain my-company
aws codeartifact create-repository \
  --domain my-company \
  --repository my-repo

# Configure pip to use it
aws codeartifact login --tool pip --domain my-company --repository my-repo
pip install my-internal-package    # Now pulls from CodeArtifact
```

**Use case:** Store private internal packages, proxy public registries (npm, PyPI) for caching and security scanning.

---

## Complete End-to-End Example (IaC with Terraform)

```hcl
# CodeBuild project
resource "aws_codebuild_project" "app" {
  name         = "my-app-build"
  service_role = aws_iam_role.codebuild.arn

  artifacts { type = "CODEPIPELINE" }

  environment {
    compute_type    = "BUILD_GENERAL1_MEDIUM"
    image           = "aws/codebuild/standard:7.0"
    type            = "LINUX_CONTAINER"
    privileged_mode = true    # Needed for Docker builds
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec.yml"
  }
}

# CodePipeline
resource "aws_codepipeline" "app" {
  name     = "my-app-pipeline"
  role_arn = aws_iam_role.codepipeline.arn

  artifact_store {
    location = aws_s3_bucket.artifacts.bucket
    type     = "S3"
  }

  stage {
    name = "Source"
    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeCommit"
      version          = "1"
      output_artifacts = ["source_output"]
      configuration = {
        RepositoryName = "my-app"
        BranchName     = "main"
      }
    }
  }

  stage {
    name = "Build"
    action {
      name             = "Build"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_output"]
      configuration = {
        ProjectName = aws_codebuild_project.app.name
      }
    }
  }

  stage {
    name = "Deploy"
    action {
      name            = "Deploy"
      category        = "Deploy"
      owner           = "AWS"
      provider        = "ECS"
      version         = "1"
      input_artifacts = ["build_output"]
      configuration = {
        ClusterName = "production"
        ServiceName = "my-app"
      }
    }
  }
}
```

---

## AWS CI/CD vs Jenkins/GitHub Actions

| Aspect | AWS Code* Suite | Jenkins | GitHub Actions |
|--------|----------------|---------|----------------|
| Management | Fully managed | Self-hosted | Managed (GitHub) |
| AWS integration | Native, deep | Plugin-based | Via actions/OIDC |
| Cost | Pay per use | Server costs | Free tier + minutes |
| Flexibility | AWS-focused | Very flexible | Very flexible |
| Best for | AWS-heavy shops | Complex/hybrid | GitHub-hosted code |

**Interview point:** "AWS CodePipeline is ideal when you're all-in on AWS and want no CI/CD servers to manage. But many teams keep GitHub/GitHub Actions for source and CI, and use CodeDeploy/CodePipeline only for the AWS deployment part. The tools aren't mutually exclusive."

---

## Best Practices

1. **Store secrets in SSM Parameter Store or Secrets Manager** — reference them in buildspec, never hardcode.
2. **Use least-privilege IAM roles** for each service (CodeBuild role, CodeDeploy role, Pipeline role).
3. **Add a manual approval stage** before production deploys.
4. **Enable automatic rollback** in CodeDeploy tied to CloudWatch alarms.
5. **Use blue/green or canary** for production, not all-at-once.
6. **Cache dependencies** in CodeBuild to speed up builds.
7. **Encrypt the artifact S3 bucket** and pipeline artifacts (KMS).
8. **Use separate pipelines per environment** or stages with approvals.

---

## Interview Q&A

**Q: Walk me through a CI/CD pipeline on AWS.**
> Source in CodeCommit or GitHub triggers CodePipeline. The Source stage pulls code, the Build stage runs CodeBuild using a buildspec.yml to test and build a Docker image pushed to ECR. Then a manual approval gate for production, and a Deploy stage using CodeDeploy or ECS to roll out — ideally blue/green with automatic rollback tied to CloudWatch alarms. Secrets come from SSM/Secrets Manager, and each stage uses a least-privilege IAM role.

**Q: How do you do zero-downtime deployments with CodeDeploy?**
> Blue/green deployment. CodeDeploy provisions a new (green) environment alongside the old (blue), shifts traffic gradually via the load balancer — canary or linear — while monitoring CloudWatch alarms. If metrics are healthy, it completes the shift and tears down blue. If an alarm fires, it automatically rolls back to blue. No downtime because both run during the transition.

**Q: CodePipeline vs Jenkins — when would you choose which?**
> CodePipeline when you're AWS-native and want zero infrastructure to manage — it's fully managed and integrates deeply with AWS services. Jenkins when you need maximum flexibility, complex custom workflows, hybrid/multi-cloud, or you already have Jenkins expertise. Many teams blend them — Jenkins/GitHub Actions for CI, CodeDeploy for the AWS deployment.

**Q: How do you manage secrets in a CodeBuild pipeline?**
> Never hardcode. Use `parameter-store` or `secrets-manager` blocks in the buildspec env section to pull secrets at build time from SSM Parameter Store or Secrets Manager. The CodeBuild role needs read access to those specific parameters, following least privilege.

---

## Summary

**Key Takeaways:**
- **CodeCommit** — managed Git (being de-emphasized; GitHub works too)
- **CodeBuild** — managed builds via buildspec.yml
- **CodeDeploy** — deployments with blue/green, canary, auto-rollback
- **CodePipeline** — orchestrates source → build → approve → deploy
- **CodeArtifact** — private package management
- Use manual approvals + automatic rollback for safe production deploys
- Secrets via SSM/Secrets Manager, least-privilege IAM per service

**Related Chapters:**
- [16-ecs-eks.md](./16-ecs-eks.md) — Container deployment targets
- [19-security-best-practices.md](./19-security-best-practices.md) — IAM, secrets
- [23-real-world-project.md](./23-real-world-project.md) — End-to-end project
