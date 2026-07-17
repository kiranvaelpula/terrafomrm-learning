# Chapter 13: CloudFormation Basics - Infrastructure as Code

## Overview

AWS CloudFormation is a service that helps you model and provision AWS resources using infrastructure as code (IaC). Instead of manually creating resources through the console or CLI, you define them in templates that can be version-controlled, reused, and automated.

**What You'll Learn**
- CloudFormation fundamentals and concepts
- Template structure and syntax (JSON/YAML)
- Resource provisioning and management
- Stack operations and lifecycle
- Best practices for IaC on AWS

**Prerequisites**
- Understanding of VPC, EC2, S3 basics
- Familiarity with JSON or YAML
- AWS CLI configured
- Basic IAM permissions

---

## Why CloudFormation?

### Manual Provisioning Problems

**Without IaC:**
```bash
# Manual steps - error-prone, not reproducible
aws ec2 create-vpc --cidr-block 10.0.0.0/16
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --vpc-id vpc-xxx --igw-id igw-xxx
# ... many more manual steps
```


**Problems:**
- Time-consuming and repetitive
- Human error prone
- Hard to replicate across environments
- No version control
- Difficult to track changes
- Manual rollback on failures

**With CloudFormation:**
```yaml
# Template defines desired state
Resources:
  MyVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
  
  MySubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: 10.0.1.0/24
```

**Benefits:**
- Declarative and reproducible
- Version-controlled infrastructure
- Automatic dependency resolution
- Consistent deployments
- Easy rollback capabilities
- Documentation as code

---

## CloudFormation Core Concepts

### 1. Templates

Templates are JSON or YAML files that describe your AWS resources.

**Template Structure:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'My first CloudFormation template'

Parameters:
  # Input values for template

Resources:
  # AWS resources to create (required)

Outputs:
  # Values to export or display
```

### 2. Stacks

A stack is a collection of AWS resources managed as a single unit.

**Stack Lifecycle:**
```
Create → Update → Delete
   ↓        ↓        ↓
CREATE_COMPLETE → UPDATE_COMPLETE → DELETE_COMPLETE
```


### 3. Change Sets

Preview changes before applying them to your stack.

```bash
# Create change set to preview changes
aws cloudformation create-change-set \
  --stack-name my-stack \
  --change-set-name my-changes \
  --template-body file://template.yaml

# Review changes
aws cloudformation describe-change-set \
  --stack-name my-stack \
  --change-set-name my-changes

# Execute if satisfied
aws cloudformation execute-change-set \
  --stack-name my-stack \
  --change-set-name my-changes
```

---

## Your First CloudFormation Template

### Example 1: Simple S3 Bucket

**template-s3-basic.yaml:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Simple S3 bucket with versioning'

Resources:
  MyS3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-cfn-bucket-12345
      VersioningConfiguration:
        Status: Enabled
      Tags:
        - Key: Environment
          Value: Development
        - Key: ManagedBy
          Value: CloudFormation

Outputs:
  BucketName:
    Description: 'Name of the S3 bucket'
    Value: !Ref MyS3Bucket
  BucketArn:
    Description: 'ARN of the S3 bucket'
    Value: !GetAtt MyS3Bucket.Arn
```

**Deploy the stack:**
```bash
# Create stack
aws cloudformation create-stack \
  --stack-name my-s3-stack \
  --template-body file://template-s3-basic.yaml

# Check status
aws cloudformation describe-stacks \
  --stack-name my-s3-stack \
  --query 'Stacks[0].StackStatus'

# Get outputs
aws cloudformation describe-stacks \
  --stack-name my-s3-stack \
  --query 'Stacks[0].Outputs'
```


### Example 2: EC2 Instance with Security Group

**template-ec2-basic.yaml:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'EC2 instance with security group'

Parameters:
  InstanceType:
    Type: String
    Default: t2.micro
    AllowedValues:
      - t2.micro
      - t2.small
      - t2.medium
    Description: 'EC2 instance type'
  
  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: 'SSH key pair for EC2 access'
  
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2
    Description: 'Latest Amazon Linux 2 AMI ID'

Resources:
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: 'Allow HTTP and SSH'
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
          Description: 'Allow HTTP from anywhere'
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
          Description: 'Allow SSH from anywhere'
      Tags:
        - Key: Name
          Value: WebServerSG

  WebServerInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      ImageId: !Ref LatestAmiId
      KeyName: !Ref KeyPairName
      SecurityGroupIds:
        - !Ref WebServerSecurityGroup
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          systemctl start httpd
          systemctl enable httpd
          echo "<h1>Hello from CloudFormation!</h1>" > /var/www/html/index.html
      Tags:
        - Key: Name
          Value: WebServer

Outputs:
  InstanceId:
    Description: 'EC2 Instance ID'
    Value: !Ref WebServerInstance
  
  PublicIP:
    Description: 'Public IP address'
    Value: !GetAtt WebServerInstance.PublicIp
  
  PublicDNS:
    Description: 'Public DNS name'
    Value: !GetAtt WebServerInstance.PublicDnsName
  
  WebsiteURL:
    Description: 'Website URL'
    Value: !Sub 'http://${WebServerInstance.PublicDnsName}'
```


**Deploy with parameters:**
```bash
# Create stack with parameters
aws cloudformation create-stack \
  --stack-name web-server-stack \
  --template-body file://template-ec2-basic.yaml \
  --parameters \
    ParameterKey=InstanceType,ParameterValue=t2.micro \
    ParameterKey=KeyPairName,ParameterValue=my-key-pair

# Monitor creation
aws cloudformation wait stack-create-complete \
  --stack-name web-server-stack

# Get the website URL
aws cloudformation describe-stacks \
  --stack-name web-server-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' \
  --output text
```

---

## Template Anatomy

### 1. Parameters

Accept input values to customize stacks.

```yaml
Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod
    Description: 'Deployment environment'
  
  BucketPrefix:
    Type: String
    MinLength: 3
    MaxLength: 20
    Description: 'S3 bucket name prefix'
  
  EnableBackup:
    Type: String
    Default: 'true'
    AllowedValues:
      - 'true'
      - 'false'
    Description: 'Enable automated backups'
```

### 2. Mappings

Define conditional values based on keys.

```yaml
Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-0c55b159cbfafe1f0
    us-west-2:
      AMI: ami-0d1cd67c26f5fca19
    eu-west-1:
      AMI: ami-0bbc25e23a7640b9b
  
  EnvironmentMap:
    dev:
      InstanceType: t2.micro
      MinSize: 1
      MaxSize: 2
    prod:
      InstanceType: t3.medium
      MinSize: 2
      MaxSize: 10

Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionMap, !Ref 'AWS::Region', AMI]
      InstanceType: !FindInMap [EnvironmentMap, !Ref Environment, InstanceType]
```


### 3. Conditions

Create resources conditionally.

```yaml
Parameters:
  CreateProdResources:
    Type: String
    Default: 'false'
    AllowedValues:
      - 'true'
      - 'false'

Conditions:
  IsProd: !Equals [!Ref CreateProdResources, 'true']
  IsNotProd: !Not [!Condition IsProd]

Resources:
  DevBucket:
    Type: AWS::S3::Bucket
    Condition: IsNotProd
    Properties:
      BucketName: my-dev-bucket
  
  ProdBucket:
    Type: AWS::S3::Bucket
    Condition: IsProd
    Properties:
      BucketName: my-prod-bucket
      VersioningConfiguration:
        Status: Enabled
      LifecycleConfiguration:
        Rules:
          - Status: Enabled
            Transitions:
              - StorageClass: GLACIER
                TransitionInDays: 90
```

### 4. Intrinsic Functions

Built-in functions for dynamic values.

**Common Functions:**
```yaml
Resources:
  # Ref - Reference a parameter or resource
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceTypeParameter
      SecurityGroupIds:
        - !Ref MySecurityGroup
  
  # GetAtt - Get resource attributes
  MyOutput:
    Value: !GetAtt MyInstance.PublicIp
  
  # Sub - String substitution
  UserData:
    Fn::Base64: !Sub |
      #!/bin/bash
      echo "Region: ${AWS::Region}"
      echo "Stack: ${AWS::StackName}"
  
  # Join - Concatenate strings
  MyString:
    !Join
      - '-'
      - - !Ref Environment
        - !Ref 'AWS::Region'
        - 'bucket'
  
  # Select - Get item from list
  MyAZ:
    !Select
      - 0
      - !GetAZs ''
  
  # If - Conditional value
  InstanceType:
    !If [IsProd, 't3.large', 't2.micro']
```


---

## Real-World Example: VPC with Public Subnet

**template-vpc-complete.yaml:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'VPC with public subnet and Internet Gateway'

Parameters:
  ProjectName:
    Type: String
    Default: MyProject
    Description: 'Project name for resource tagging'
  
  VpcCidr:
    Type: String
    Default: 10.0.0.0/16
    Description: 'CIDR block for VPC'
  
  PublicSubnetCidr:
    Type: String
    Default: 10.0.1.0/24
    Description: 'CIDR block for public subnet'

Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-VPC'
  
  # Internet Gateway
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-IGW'
  
  # Attach IGW to VPC
  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway
  
  # Public Subnet
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Ref PublicSubnetCidr
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-PublicSubnet'
  
  # Route Table
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${ProjectName}-PublicRT'
  
  # Route to Internet
  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway
  
  # Associate subnet with route table
  SubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet
      RouteTableId: !Ref PublicRouteTable

Outputs:
  VpcId:
    Description: 'VPC ID'
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VpcId'
  
  PublicSubnetId:
    Description: 'Public Subnet ID'
    Value: !Ref PublicSubnet
    Export:
      Name: !Sub '${AWS::StackName}-PublicSubnetId'
  
  VpcCidr:
    Description: 'VPC CIDR block'
    Value: !GetAtt VPC.CidrBlock
```


**Deploy the VPC stack:**
```bash
# Create VPC stack
aws cloudformation create-stack \
  --stack-name my-vpc-stack \
  --template-body file://template-vpc-complete.yaml \
  --parameters \
    ParameterKey=ProjectName,ParameterValue=MyApp \
    ParameterKey=VpcCidr,ParameterValue=10.0.0.0/16

# Wait for completion
aws cloudformation wait stack-create-complete \
  --stack-name my-vpc-stack

# Get VPC ID from exports
aws cloudformation list-exports \
  --query 'Exports[?Name==`my-vpc-stack-VpcId`].Value' \
  --output text
```

---

## Stack Operations

### Create Stack

```bash
# From file
aws cloudformation create-stack \
  --stack-name my-stack \
  --template-body file://template.yaml \
  --parameters file://parameters.json

# From S3
aws cloudformation create-stack \
  --stack-name my-stack \
  --template-url https://s3.amazonaws.com/bucket/template.yaml

# With tags
aws cloudformation create-stack \
  --stack-name my-stack \
  --template-body file://template.yaml \
  --tags Key=Environment,Value=Production Key=Owner,Value=DevOps
```

### Update Stack

```bash
# Update with new template
aws cloudformation update-stack \
  --stack-name my-stack \
  --template-body file://template-updated.yaml

# Update parameters only
aws cloudformation update-stack \
  --stack-name my-stack \
  --use-previous-template \
  --parameters \
    ParameterKey=InstanceType,ParameterValue=t2.small

# Preview changes first
aws cloudformation create-change-set \
  --stack-name my-stack \
  --change-set-name my-update \
  --template-body file://template-updated.yaml

aws cloudformation describe-change-set \
  --stack-name my-stack \
  --change-set-name my-update
```


### Delete Stack

```bash
# Delete stack and all resources
aws cloudformation delete-stack \
  --stack-name my-stack

# Wait for deletion
aws cloudformation wait stack-delete-complete \
  --stack-name my-stack

# Delete with retain policy (keep some resources)
# Define DeletionPolicy in template:
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain  # Don't delete on stack deletion
```

### Monitor Stack Events

```bash
# Get stack events
aws cloudformation describe-stack-events \
  --stack-name my-stack \
  --query 'StackEvents[*].[Timestamp,ResourceStatus,ResourceType,LogicalResourceId]' \
  --output table

# Tail events in real-time
aws cloudformation describe-stack-events \
  --stack-name my-stack \
  --max-items 10
```

---

## Stack Policies

Protect critical resources from accidental updates or deletions.

**stack-policy.json:**
```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "Update:*",
      "Resource": "*"
    },
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": ["Update:Replace", "Update:Delete"],
      "Resource": "LogicalResourceId/ProductionDatabase"
    }
  ]
}
```

**Apply policy:**
```bash
# Set stack policy during creation
aws cloudformation create-stack \
  --stack-name my-stack \
  --template-body file://template.yaml \
  --stack-policy-body file://stack-policy.json

# Update stack policy
aws cloudformation set-stack-policy \
  --stack-name my-stack \
  --stack-policy-body file://stack-policy.json
```

---

## Cross-Stack References

Share resources between stacks using exports and imports.

**Stack 1: Network Stack (exports VPC)**
```yaml
Outputs:
  VpcId:
    Value: !Ref VPC
    Export:
      Name: NetworkStack-VpcId
  
  PublicSubnetId:
    Value: !Ref PublicSubnet
    Export:
      Name: NetworkStack-PublicSubnetId
```


**Stack 2: Application Stack (imports VPC)**
```yaml
Resources:
  AppInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-12345678
      SubnetId: !ImportValue NetworkStack-PublicSubnetId
      SecurityGroupIds:
        - !Ref AppSecurityGroup
  
  AppSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      VpcId: !ImportValue NetworkStack-VpcId
      GroupDescription: 'Application security group'
```

**Deploy in order:**
```bash
# 1. Deploy network stack first
aws cloudformation create-stack \
  --stack-name network-stack \
  --template-body file://network-template.yaml

# 2. Deploy app stack (references network)
aws cloudformation create-stack \
  --stack-name app-stack \
  --template-body file://app-template.yaml
```

---

## Nested Stacks

Organize complex infrastructure into reusable components.

**Master Template:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Master stack with nested stacks'

Resources:
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/mybucket/network-template.yaml
      Parameters:
        VpcCidr: 10.0.0.0/16
      Tags:
        - Key: Name
          Value: Network
  
  DatabaseStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: NetworkStack
    Properties:
      TemplateURL: https://s3.amazonaws.com/mybucket/database-template.yaml
      Parameters:
        VpcId: !GetAtt NetworkStack.Outputs.VpcId
        SubnetId: !GetAtt NetworkStack.Outputs.PrivateSubnetId
  
  ApplicationStack:
    Type: AWS::CloudFormation::Stack
    DependsOn:
      - NetworkStack
      - DatabaseStack
    Properties:
      TemplateURL: https://s3.amazonaws.com/mybucket/app-template.yaml
      Parameters:
        VpcId: !GetAtt NetworkStack.Outputs.VpcId
        DbEndpoint: !GetAtt DatabaseStack.Outputs.DbEndpoint
```

---

## Error Handling and Rollback

### Rollback Configuration

```yaml
# In template - set DeletionPolicy
Resources:
  MyDatabase:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot  # Create snapshot before deleting
    Properties:
      # ... properties

  MyBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain  # Keep bucket on stack deletion
```


### Disable Rollback

```bash
# Create without rollback (for debugging)
aws cloudformation create-stack \
  --stack-name my-stack \
  --template-body file://template.yaml \
  --on-failure DO_NOTHING

# Continue update rollback if stuck
aws cloudformation continue-update-rollback \
  --stack-name my-stack
```

### Common Errors and Solutions

**Error: Parameter validation failed**
```
Solution: Check parameter constraints
- MinLength, MaxLength for strings
- MinValue, MaxValue for numbers
- AllowedValues list
- AllowedPattern regex
```

**Error: Resource already exists**
```
Solution: 
- Use unique names or add randomness
- Check for orphaned resources
- Use DeletionPolicy: Delete
```

**Error: Circular dependency detected**
```
Solution:
- Review !Ref and !GetAtt relationships
- Break cycles using separate stacks
- Use DependsOn carefully
```

---

## Best Practices

### 1. Template Organization

```yaml
# Use clear naming conventions
Resources:
  # Networking
  VPC:
    Type: AWS::EC2::VPC
  PublicSubnet:
    Type: AWS::EC2::Subnet
  
  # Security
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
  
  # Compute
  WebServerInstance:
    Type: AWS::EC2::Instance
```

### 2. Parameterization

```yaml
# Make templates reusable
Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]
  
  InstanceType:
    Type: String
    Default: t2.micro
    Description: 'EC2 instance type'

Mappings:
  EnvironmentSettings:
    dev:
      InstanceCount: 1
    prod:
      InstanceCount: 3
```

### 3. Use Outputs and Exports

```yaml
Outputs:
  # Export for other stacks
  VpcId:
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VpcId'
  
  # Display important info
  ApplicationURL:
    Description: 'Application endpoint'
    Value: !Sub 'https://${LoadBalancer.DNSName}'
```


### 4. Version Control

```bash
# Store templates in Git
git add templates/
git commit -m "Add VPC CloudFormation template"

# Use semantic versioning
templates/
  v1.0/
    vpc-template.yaml
  v1.1/
    vpc-template.yaml
  v2.0/
    vpc-template.yaml
```

### 5. Validation

```bash
# Validate syntax before deployment
aws cloudformation validate-template \
  --template-body file://template.yaml

# Use linters
cfn-lint template.yaml

# Test with cfn-nag for security
cfn_nag_scan --input-path template.yaml
```

### 6. Stack Tags

```bash
# Tag all resources in stack
aws cloudformation create-stack \
  --stack-name my-stack \
  --template-body file://template.yaml \
  --tags \
    Key=Environment,Value=Production \
    Key=Owner,Value=TeamA \
    Key=CostCenter,Value=Engineering \
    Key=ManagedBy,Value=CloudFormation
```

---

## Hands-On Exercise

### Task: Deploy a Complete Web Application Stack

Create a CloudFormation template that provisions:
1. VPC with public and private subnets
2. Internet Gateway and NAT Gateway
3. EC2 instance in public subnet running web server
4. RDS database in private subnet
5. Security groups for web and database tiers

**Step 1: Create VPC template**
```yaml
# Save as web-app-infrastructure.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Complete web application infrastructure'

Parameters:
  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: 'EC2 Key Pair for SSH access'
  
  DBPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    Description: 'Database master password'

Resources:
  # VPC and Networking
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: WebAppVPC
  
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: PublicSubnet
  
  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      Tags:
        - Key: Name
          Value: PrivateSubnet
```


**Step 2: Add Internet and NAT Gateways**
```yaml
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: WebAppIGW
  
  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway
  
  NATGatewayEIP:
    Type: AWS::EC2::EIP
    DependsOn: AttachGateway
    Properties:
      Domain: vpc
  
  NATGateway:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NATGatewayEIP.AllocationId
      SubnetId: !Ref PublicSubnet
  
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: PublicRouteTable
  
  PublicRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway
  
  PublicSubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet
      RouteTableId: !Ref PublicRouteTable
  
  PrivateRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: PrivateRouteTable
  
  PrivateRoute:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NATGateway
  
  PrivateSubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PrivateSubnet
      RouteTableId: !Ref PrivateRouteTable
```


**Step 3: Add Security Groups and EC2**
```yaml
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: 'Security group for web server'
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: WebServerSG
  
  DBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: 'Security group for database'
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref WebServerSecurityGroup
      Tags:
        - Key: Name
          Value: DatabaseSG
  
  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t2.micro
      ImageId: !Sub '{{resolve:ssm:/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2}}'
      KeyName: !Ref KeyPairName
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref WebServerSecurityGroup
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y httpd mysql
          systemctl start httpd
          systemctl enable httpd
          echo "<h1>Web Server from CloudFormation</h1>" > /var/www/html/index.html
          echo "<p>Database: ${DBInstance.Endpoint.Address}</p>" >> /var/www/html/index.html
      Tags:
        - Key: Name
          Value: WebServer

  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: 'Subnet group for RDS'
      SubnetIds:
        - !Ref PrivateSubnet
        - !Ref PublicSubnet
      Tags:
        - Key: Name
          Value: DBSubnetGroup
  
  DBInstance:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    Properties:
      DBInstanceIdentifier: webapp-db
      DBInstanceClass: db.t3.micro
      Engine: mysql
      EngineVersion: '8.0'
      MasterUsername: admin
      MasterUserPassword: !Ref DBPassword
      AllocatedStorage: 20
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      BackupRetentionPeriod: 7
      Tags:
        - Key: Name
          Value: WebAppDatabase

Outputs:
  WebServerPublicIP:
    Description: 'Web server public IP'
    Value: !GetAtt WebServer.PublicIp
  
  WebServerURL:
    Description: 'Web application URL'
    Value: !Sub 'http://${WebServer.PublicDnsName}'
  
  DatabaseEndpoint:
    Description: 'Database endpoint'
    Value: !GetAtt DBInstance.Endpoint.Address
```


**Step 4: Deploy the complete stack**
```bash
# Validate template
aws cloudformation validate-template \
  --template-body file://web-app-infrastructure.yaml

# Create stack
aws cloudformation create-stack \
  --stack-name web-app-stack \
  --template-body file://web-app-infrastructure.yaml \
  --parameters \
    ParameterKey=KeyPairName,ParameterValue=my-key \
    ParameterKey=DBPassword,ParameterValue=MySecurePassword123

# Monitor progress
watch -n 5 aws cloudformation describe-stacks \
  --stack-name web-app-stack \
  --query 'Stacks[0].StackStatus'

# Get outputs
aws cloudformation describe-stacks \
  --stack-name web-app-stack \
  --query 'Stacks[0].Outputs'

# Test the web application
curl $(aws cloudformation describe-stacks \
  --stack-name web-app-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`WebServerURL`].OutputValue' \
  --output text)
```

---

## Troubleshooting

### Common Issues

**Issue 1: Stack stuck in CREATE_IN_PROGRESS**
```bash
# Check events for errors
aws cloudformation describe-stack-events \
  --stack-name my-stack \
  --max-items 20

# Look for FAILED statuses
aws cloudformation describe-stack-events \
  --stack-name my-stack \
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]'
```

**Issue 2: Resource dependency errors**
```
Error: Resource X depends on Y but Y doesn't exist

Solution:
- Use DependsOn for explicit dependencies
- Check !Ref and !GetAtt references
- Ensure resources are created in correct order
```

**Issue 3: Parameter validation errors**
```bash
# Check parameter constraints
aws cloudformation describe-stack-parameters \
  --stack-name my-stack

# Review template parameters section
# Verify AllowedValues, MinLength, MaxLength, etc.
```

**Issue 4: Insufficient permissions**
```
Error: User is not authorized to perform...

Solution:
# Add required IAM permissions
{
  "Effect": "Allow",
  "Action": [
    "cloudformation:*",
    "ec2:*",
    "s3:*",
    "rds:*"
  ],
  "Resource": "*"
}
```


### Debugging Tips

**Enable termination protection:**
```bash
aws cloudformation update-termination-protection \
  --stack-name my-stack \
  --enable-termination-protection
```

**Export stack template:**
```bash
# Get current stack template
aws cloudformation get-template \
  --stack-name my-stack \
  --query 'TemplateBody' > current-template.yaml
```

**Detect drift:**
```bash
# Check if resources were modified outside CloudFormation
aws cloudformation detect-stack-drift \
  --stack-name my-stack

# Get drift results
aws cloudformation describe-stack-resource-drifts \
  --stack-name my-stack
```

---

## CloudFormation vs Terraform

| Feature | CloudFormation | Terraform |
|---------|---------------|-----------|
| **Provider** | AWS native | Multi-cloud |
| **Language** | JSON/YAML | HCL |
| **State** | AWS managed | Manual/remote |
| **Cost** | Free | Free (OSS) |
| **Learning Curve** | Moderate | Moderate |
| **AWS Integration** | Excellent | Good |
| **Multi-cloud** | No | Yes |

**When to use CloudFormation:**
- AWS-only infrastructure
- Deep AWS service integration needed
- Want AWS-managed state
- Team comfortable with YAML/JSON

**When to use Terraform:**
- Multi-cloud deployments
- Prefer HCL syntax
- Need extensive module ecosystem
- Already using Terraform

---

## Cost Considerations

**CloudFormation Service:**
- ✅ **Free** - No charge for CloudFormation itself
- 💰 **Resources** - Pay for AWS resources created
- 💰 **API Calls** - Standard AWS API charges apply

**Cost Optimization Tips:**
```yaml
# Use condition to control expensive resources
Conditions:
  CreateNATGateway: !Equals [!Ref Environment, 'prod']

Resources:
  NATGateway:
    Type: AWS::EC2::NatGateway
    Condition: CreateNATGateway  # Skip in dev/test
```

---

## Security Best Practices

### 1. Never Hardcode Credentials

```yaml
# ❌ BAD - Hardcoded password
Resources:
  Database:
    Properties:
      MasterUserPassword: 'MyPassword123'

# ✅ GOOD - Use parameter with NoEcho
Parameters:
  DBPassword:
    Type: String
    NoEcho: true
    MinLength: 8

Resources:
  Database:
    Properties:
      MasterUserPassword: !Ref DBPassword
```

### 2. Use IAM Roles, Not Access Keys

```yaml
# ✅ Attach IAM role to EC2
Resources:
  InstanceRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
  
  InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref InstanceRole
  
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      IamInstanceProfile: !Ref InstanceProfile
```


### 3. Encrypt Sensitive Data

```yaml
Resources:
  EncryptedBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
  
  EncryptedDatabase:
    Type: AWS::RDS::DBInstance
    Properties:
      StorageEncrypted: true
      KmsKeyId: !Ref DBEncryptionKey
  
  DBEncryptionKey:
    Type: AWS::KMS::Key
    Properties:
      Description: 'KMS key for database encryption'
      KeyPolicy:
        Statement:
          - Effect: Allow
            Principal:
              Service: rds.amazonaws.com
            Action:
              - kms:Decrypt
              - kms:CreateGrant
            Resource: '*'
```

### 4. Restrict Security Group Access

```yaml
# ❌ BAD - Open to internet
SecurityGroupIngress:
  - IpProtocol: tcp
    FromPort: 22
    ToPort: 22
    CidrIp: 0.0.0.0/0

# ✅ GOOD - Restricted access
SecurityGroupIngress:
  - IpProtocol: tcp
    FromPort: 22
    ToPort: 22
    CidrIp: 10.0.0.0/8  # Internal only
```

---

## Next Steps

Now that you understand CloudFormation basics:

1. **Practice**: Deploy the complete web app stack
2. **Explore**: Try nested stacks for complex architectures
3. **Learn**: Study AWS CloudFormation Designer (visual editor)
4. **Compare**: Try the same infrastructure in Terraform
5. **Advanced**: Look into AWS CDK for programmatic templates

**Recommended Practice:**
- Build a 3-tier application with CloudFormation
- Implement CI/CD for template deployments
- Create reusable template library
- Set up automated testing with cfn-lint

---

## Summary

**Key Takeaways:**
- CloudFormation enables infrastructure as code on AWS
- Templates define resources declaratively
- Stacks manage resources as a single unit
- Parameters make templates reusable
- Intrinsic functions enable dynamic configurations
- Cross-stack references allow modular architectures
- Change sets preview updates before applying
- Stack policies protect critical resources

**CloudFormation Benefits:**
- ✅ Repeatable deployments
- ✅ Version-controlled infrastructure
- ✅ Automated provisioning
- ✅ Consistent environments
- ✅ Simplified management
- ✅ Free service (pay for resources only)

**Common Use Cases:**
- Environment provisioning (dev/staging/prod)
- Disaster recovery
- Application deployment
- Multi-region replication
- Compliance and governance

---

## Additional Resources

**Official Documentation:**
- [AWS CloudFormation User Guide](https://docs.aws.amazon.com/cloudformation/)
- [Template Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-reference.html)
- [Intrinsic Functions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference.html)

**Tools:**
- [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) - Template linter
- [cfn-nag](https://github.com/stelligent/cfn_nag) - Security scanner
- [CloudFormation Designer](https://console.aws.amazon.com/cloudformation/designer) - Visual editor

**Next Chapter:** [14-advanced-vpc.md](../../03-advanced/14-advanced-vpc.md) - Advanced VPC architectures

