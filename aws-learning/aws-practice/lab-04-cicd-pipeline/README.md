# Lab 04: CI/CD Pipeline with CodePipeline

## Objective

Build a complete CI/CD pipeline using AWS native services (CodeCommit, CodeBuild, CodeDeploy, CodePipeline) to automatically deploy applications.

**Duration:** 90-120 minutes

**Skills:**
- CodeCommit for source control
- CodeBuild for building applications
- CodeDeploy for deployments
- CodePipeline for orchestration
- S3 for artifact storage
- SNS for notifications

---

## Architecture

```
CodeCommit (Git Push)
       ↓
CodePipeline (Orchestration)
       ↓
CodeBuild (Build & Test)
       ↓
S3 (Artifacts)
       ↓
CodeDeploy → EC2 Instances
       ↓
SNS Notifications
```

---

## Prerequisites

- AWS Account with Admin access
- AWS CLI configured
- Git installed
- Basic understanding of CI/CD concepts
- SSH key pair created

---

## Step 1: Create CodeCommit Repository

```bash
# Create repository
aws codecommit create-repository \
  --repository-name demo-app \
  --repository-description "Demo application for CI/CD"

# Get clone URL
CLONE_URL=$(aws codecommit get-repository \
  --repository-name demo-app \
  --query 'repositoryMetadata.cloneUrlHttp' \
  --output text)

echo "Clone URL: $CLONE_URL"

# Configure Git credentials
aws configure set credential.helper '!aws codecommit credential-helper $@'
aws configure set credential.UseHttpPath true

# Clone repository
git clone $CLONE_URL
cd demo-app
```

---

## Step 2: Create Sample Application

**index.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>CI/CD Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        h1 { font-size: 3em; margin-bottom: 20px; }
        p { font-size: 1.5em; }
        .version { 
            background: rgba(255,255,255,0.2); 
            padding: 10px 20px;
            border-radius: 5px;
            display: inline-block;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Welcome to CI/CD Pipeline Demo!</h1>
    <p>This application is automatically deployed via AWS CodePipeline</p>
    <div class="version">Version: 1.0.0</div>
</body>
</html>
```

**app.py:**
```python
from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML = open('index.html').read()

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/health')
def health():
    return {'status': 'healthy', 'version': '1.0.0'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
```

**requirements.txt:**
```
flask==2.3.2
gunicorn==21.2.0
```

**buildspec.yml:** (for CodeBuild)
```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.9
    commands:
      - echo "Installing dependencies..."
      - pip install -r requirements.txt

  pre_build:
    commands:
      - echo "Running tests..."
      - python -m pytest tests/ || true
      - echo "Build started on `date`"

  build:
    commands:
      - echo "Building application..."
      - echo "Nothing to compile for Python Flask app"

  post_build:
    commands:
      - echo "Build completed on `date`"

artifacts:
  files:
    - '**/*'
  name: demo-app-$(date +%Y%m%d-%H%M%S)
```

**appspec.yml:** (for CodeDeploy)
```yaml
version: 0.0
os: linux

files:
  - source: /
    destination: /var/www/html

hooks:
  BeforeInstall:
    - location: scripts/install_dependencies.sh
      timeout: 300
      runas: root

  ApplicationStart:
    - location: scripts/start_server.sh
      timeout: 300
      runas: root

  ApplicationStop:
    - location: scripts/stop_server.sh
      timeout: 300
      runas: root

  ValidateService:
    - location: scripts/validate_service.sh
      timeout: 300
      runas: root
```

**scripts/install_dependencies.sh:**
```bash
#!/bin/bash
yum update -y
yum install -y python3 python3-pip
pip3 install -r /var/www/html/requirements.txt
```

**scripts/start_server.sh:**
```bash
#!/bin/bash
cd /var/www/html
nohup gunicorn --bind 0.0.0.0:80 --workers 2 app:app > /var/log/app.log 2>&1 &
echo $! > /var/run/app.pid
```

**scripts/stop_server.sh:**
```bash
#!/bin/bash
if [ -f /var/run/app.pid ]; then
    kill $(cat /var/run/app.pid) || true
    rm /var/run/app.pid
fi
```

**scripts/validate_service.sh:**
```bash
#!/bin/bash
for i in {1..10}; do
    if curl -s http://localhost/health | grep -q "healthy"; then
        echo "Service is healthy"
        exit 0
    fi
    sleep 5
done
echo "Service validation failed"
exit 1
```

**tests/test_app.py:**
```python
import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'CI/CD' in response.data

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
```

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Commit and push to CodeCommit
git add .
git commit -m "Initial commit: Flask app with CI/CD configuration"
git push origin main
```

---

## Step 3: Create S3 Bucket for Artifacts

```bash
# Create bucket
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="codepipeline-artifacts-$ACCOUNT_ID"

aws s3 mb s3://$BUCKET_NAME

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket $BUCKET_NAME \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

---

## Step 4: Create IAM Roles

**CodeBuild Role:**
```bash
cat > codebuild-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "codebuild.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name CodeBuildServiceRole \
  --assume-role-policy-document file://codebuild-trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name CodeBuildServiceRole \
  --policy-arn arn:aws:iam::aws:policy/AWSCodeBuildDeveloperAccess

# Custom policy for S3 and logs
cat > codebuild-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "codecommit:GitPull"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name CodeBuildServiceRole \
  --policy-name CodeBuildPolicy \
  --policy-document file://codebuild-policy.json
```

**CodeDeploy Role:**
```bash
cat > codedeploy-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "codedeploy.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name CodeDeployServiceRole \
  --assume-role-policy-document file://codedeploy-trust-policy.json

aws iam attach-role-policy \
  --role-name CodeDeployServiceRole \
  --policy-arn arn:aws:iam::aws:policy/AWSCodeDeployRole
```

**CodePipeline Role:**
```bash
cat > codepipeline-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "codepipeline.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name CodePipelineServiceRole \
  --assume-role-policy-document file://codepipeline-trust-policy.json

cat > codepipeline-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::$BUCKET_NAME",
        "arn:aws:s3:::$BUCKET_NAME/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "codecommit:GetBranch",
        "codecommit:GetCommit",
        "codecommit:UploadArchive",
        "codecommit:GetUploadArchiveStatus"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "codebuild:BatchGetBuilds",
        "codebuild:StartBuild"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "codedeploy:CreateDeployment",
        "codedeploy:GetApplication",
        "codedeploy:GetApplicationRevision",
        "codedeploy:GetDeployment",
        "codedeploy:GetDeploymentConfig",
        "codedeploy:RegisterApplicationRevision"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name CodePipelineServiceRole \
  --policy-name CodePipelinePolicy \
  --policy-document file://codepipeline-policy.json
```

**EC2 Instance Role:**
```bash
cat > ec2-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ec2.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name EC2CodeDeployRole \
  --assume-role-policy-document file://ec2-trust-policy.json

aws iam attach-role-policy \
  --role-name EC2CodeDeployRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

aws iam attach-role-policy \
  --role-name EC2CodeDeployRole \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy

# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name EC2CodeDeployInstanceProfile

aws iam add-role-to-instance-profile \
  --instance-profile-name EC2CodeDeployInstanceProfile \
  --role-name EC2CodeDeployRole
```

---

## Step 5: Create EC2 Instances for Deployment

```bash
# Create security group
aws ec2 create-security-group \
  --group-name WebServer-SG \
  --description "Security group for web servers"

SG_ID=$(aws ec2 describe-security-groups \
  --group-names WebServer-SG \
  --query 'SecurityGroups[0].GroupId' \
  --output text)

# Allow HTTP and SSH
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# User data script to install CodeDeploy agent
cat > user-data.sh <<'EOF'
#!/bin/bash
yum update -y
yum install -y ruby wget

# Install CodeDeploy agent
cd /home/ec2-user
wget https://aws-codedeploy-us-east-1.s3.us-east-1.amazonaws.com/latest/install
chmod +x ./install
./install auto

# Start the agent
service codedeploy-agent start
EOF

# Launch instances
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --count 2 \
  --security-group-ids $SG_ID \
  --iam-instance-profile Name=EC2CodeDeployInstanceProfile \
  --user-data file://user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[
    {Key=Name,Value=WebServer},
    {Key=Environment,Value=Production}
  ]'

# Wait for instances
aws ec2 wait instance-running \
  --filters "Name=tag:Name,Values=WebServer"
```

---

## Step 6: Create CodeBuild Project

```bash
# Get role ARN
CODEBUILD_ROLE_ARN=$(aws iam get-role \
  --role-name CodeBuildServiceRole \
  --query 'Role.Arn' \
  --output text)

# Create build project
aws codebuild create-project \
  --name demo-app-build \
  --source type=CODECOMMIT,location=$CLONE_URL \
  --artifacts type=S3,location=$BUCKET_NAME \
  --environment type=LINUX_CONTAINER,image=aws/codebuild/standard:5.0,computeType=BUILD_GENERAL1_SMALL \
  --service-role $CODEBUILD_ROLE_ARN

# Test build manually
aws codebuild start-build --project-name demo-app-build
```

---

## Step 7: Create CodeDeploy Application

```bash
# Get role ARN
CODEDEPLOY_ROLE_ARN=$(aws iam get-role \
  --role-name CodeDeployServiceRole \
  --query 'Role.Arn' \
  --output text)

# Create application
aws deploy create-application \
  --application-name demo-app \
  --compute-platform Server

# Create deployment group
aws deploy create-deployment-group \
  --application-name demo-app \
  --deployment-group-name production \
  --service-role-arn $CODEDEPLOY_ROLE_ARN \
  --deployment-config-name CodeDeployDefault.OneAtATime \
  --ec2-tag-filters Key=Environment,Value=Production,Type=KEY_AND_VALUE \
  --auto-rollback-configuration enabled=true,events=DEPLOYMENT_FAILURE
```

---

## Step 8: Create SNS Topic for Notifications

```bash
# Create SNS topic
aws sns create-topic --name codepipeline-notifications

SNS_TOPIC_ARN=$(aws sns list-topics \
  --query "Topics[?contains(TopicArn, 'codepipeline-notifications')].TopicArn" \
  --output text)

# Subscribe email
aws sns subscribe \
  --topic-arn $SNS_TOPIC_ARN \
  --protocol email \
  --notification-endpoint your-email@example.com

# Confirm subscription in email
```

---

## Step 9: Create CodePipeline

```bash
# Get role ARN
PIPELINE_ROLE_ARN=$(aws iam get-role \
  --role-name CodePipelineServiceRole \
  --query 'Role.Arn' \
  --output text)

# Create pipeline configuration
cat > pipeline.json <<EOF
{
  "pipeline": {
    "name": "demo-app-pipeline",
    "roleArn": "$PIPELINE_ROLE_ARN",
    "artifactStore": {
      "type": "S3",
      "location": "$BUCKET_NAME"
    },
    "stages": [
      {
        "name": "Source",
        "actions": [{
          "name": "SourceAction",
          "actionTypeId": {
            "category": "Source",
            "owner": "AWS",
            "provider": "CodeCommit",
            "version": "1"
          },
          "configuration": {
            "RepositoryName": "demo-app",
            "BranchName": "main",
            "PollForSourceChanges": "false"
          },
          "outputArtifacts": [{
            "name": "SourceOutput"
          }]
        }]
      },
      {
        "name": "Build",
        "actions": [{
          "name": "BuildAction",
          "actionTypeId": {
            "category": "Build",
            "owner": "AWS",
            "provider": "CodeBuild",
            "version": "1"
          },
          "configuration": {
            "ProjectName": "demo-app-build"
          },
          "inputArtifacts": [{
            "name": "SourceOutput"
          }],
          "outputArtifacts": [{
            "name": "BuildOutput"
          }]
        }]
      },
      {
        "name": "Deploy",
        "actions": [{
          "name": "DeployAction",
          "actionTypeId": {
            "category": "Deploy",
            "owner": "AWS",
            "provider": "CodeDeploy",
            "version": "1"
          },
          "configuration": {
            "ApplicationName": "demo-app",
            "DeploymentGroupName": "production"
          },
          "inputArtifacts": [{
            "name": "BuildOutput"
          }]
        }]
      }
    ]
  }
}
EOF

# Create pipeline
aws codepipeline create-pipeline --cli-input-json file://pipeline.json

# Create EventBridge rule to trigger pipeline on commits
aws events put-rule \
  --name codecommit-demo-app-trigger \
  --event-pattern '{
    "source": ["aws.codecommit"],
    "detail-type": ["CodeCommit Repository State Change"],
    "detail": {
      "event": ["referenceCreated", "referenceUpdated"],
      "referenceType": ["branch"],
      "referenceName": ["main"]
    }
  }'

# Add pipeline as target
aws events put-targets \
  --rule codecommit-demo-app-trigger \
  --targets Id=1,Arn=arn:aws:codepipeline:us-east-1:$ACCOUNT_ID:demo-app-pipeline,RoleArn=$PIPELINE_ROLE_ARN
```

---

## Step 10: Test the Pipeline

```bash
# Make a change
cd demo-app
sed -i 's/Version: 1.0.0/Version: 2.0.0/' index.html

git add index.html
git commit -m "Update version to 2.0.0"
git push origin main

# Watch pipeline execution
watch -n 5 'aws codepipeline get-pipeline-state \
  --name demo-app-pipeline \
  --query "stageStates[*].[stageName,latestExecution.status]" \
  --output table'

# Get EC2 instance IP
INSTANCE_IP=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=WebServer" "Name=instance-state-name,Values=running" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "Visit: http://$INSTANCE_IP"

# Test application
curl http://$INSTANCE_IP
```

---

## Verification Checklist

- [ ] CodeCommit repository created and accessible
- [ ] Code pushed successfully
- [ ] S3 bucket for artifacts created
- [ ] IAM roles configured correctly
- [ ] EC2 instances running with CodeDeploy agent
- [ ] CodeBuild project builds successfully
- [ ] CodeDeploy application and deployment group created
- [ ] Pipeline created with all stages
- [ ] Pipeline executes on code commit
- [ ] Application deployed to EC2 instances
- [ ] Application accessible via browser
- [ ] SNS notifications received

---

## Cleanup

```bash
# Delete pipeline
aws codepipeline delete-pipeline --name demo-app-pipeline

# Delete CodeDeploy
aws deploy delete-deployment-group \
  --application-name demo-app \
  --deployment-group-name production
aws deploy delete-application --application-name demo-app

# Delete CodeBuild project
aws codebuild delete-project --name demo-app-build

# Terminate EC2 instances
aws ec2 terminate-instances \
  --instance-ids $(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=WebServer" \
    --query 'Reservations[*].Instances[*].InstanceId' \
    --output text)

# Delete security group (after instances terminated)
sleep 60
aws ec2 delete-security-group --group-id $SG_ID

# Delete S3 bucket
aws s3 rb s3://$BUCKET_NAME --force

# Delete CodeCommit repository
aws codecommit delete-repository --repository-name demo-app

# Delete IAM roles and policies
aws iam remove-role-from-instance-profile \
  --instance-profile-name EC2CodeDeployInstanceProfile \
  --role-name EC2CodeDeployRole
aws iam delete-instance-profile --instance-profile-name EC2CodeDeployInstanceProfile

for ROLE in CodeBuildServiceRole CodeDeployServiceRole CodePipelineServiceRole EC2CodeDeployRole; do
  aws iam list-attached-role-policies --role-name $ROLE \
    --query 'AttachedPolicies[*].PolicyArn' --output text | \
    xargs -n 1 aws iam detach-role-policy --role-name $ROLE --policy-arn
  aws iam list-role-policies --role-name $ROLE \
    --query 'PolicyNames[*]' --output text | \
    xargs -n 1 aws iam delete-role-policy --role-name $ROLE --policy-name
  aws iam delete-role --role-name $ROLE
done

# Delete SNS topic
aws sns delete-topic --topic-arn $SNS_TOPIC_ARN

# Delete EventBridge rule
aws events remove-targets --rule codecommit-demo-app-trigger --ids 1
aws events delete-rule --name codecommit-demo-app-trigger
```

---

## Troubleshooting

**Pipeline fails at Source stage:**
- Verify CodeCommit repository exists
- Check IAM permissions for CodePipeline
- Ensure EventBridge rule is configured

**Build fails:**
- Check CodeBuild logs in CloudWatch
- Verify buildspec.yml syntax
- Ensure IAM role has S3 permissions

**Deployment fails:**
- Check CodeDeploy agent is running: `sudo service codedeploy-agent status`
- Review deployment logs: `/var/log/aws/codedeploy-agent/codedeploy-agent.log`
- Verify EC2 instance has proper IAM role
- Check appspec.yml and script permissions

---

## Bonus Challenges

1. **Manual Approval**: Add manual approval stage before production
2. **Multi-Environment**: Deploy to dev, staging, then production
3. **Docker Build**: Build Docker images instead of direct deployment
4. **ECS Deployment**: Deploy to ECS instead of EC2
5. **Testing Stage**: Add automated testing with Selenium
6. **Slack Notifications**: Integrate with Slack for notifications
7. **Rollback**: Implement automatic rollback on errors

---

## Cost Estimate

**Monthly costs for basic usage:**
- **CodeCommit**: $1/active user
- **CodeBuild**: $0.005/build minute (first 100 minutes free)
- **CodeDeploy**: Free for EC2
- **CodePipeline**: $1/active pipeline/month
- **EC2 (t2.micro × 2)**: ~$16
- **S3**: $0.023/GB storage
- **SNS**: $0.50 for first 1M requests
- **CloudWatch Logs**: $0.50/GB

**Total**: ~$20-25/month

---

## Learning Outcomes

✅ Created complete CI/CD pipeline  
✅ Configured AWS native DevOps services  
✅ Automated build and deployment  
✅ Implemented notification system  
✅ Practiced infrastructure as code  
✅ Learned deployment best practices

**Next Lab:** [lab-05-production-architecture](../lab-05-production-architecture/) - Build complete production system
