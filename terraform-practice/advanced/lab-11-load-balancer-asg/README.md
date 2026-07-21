# Lab 11: Application Load Balancer + Auto Scaling

**Difficulty**: Advanced  
**Time**: 60 minutes  
**Cost**: ~$0.30/hour (ALB ~$0.0225/hour + EC2 instances)

## 🎯 Objectives

- Create Application Load Balancer (ALB)
- Configure target groups and health checks
- Create launch templates for EC2 instances
- Set up Auto Scaling Groups (ASG)
- Implement scaling policies
- Configure listener rules

## 📋 Prerequisites

- Completed Lab 06 (VPC) or have existing VPC
- Understanding of load balancing concepts
- Knowledge of auto scaling principles

## 🏗️ Architecture

```
                    Internet
                       │
                       ▼
               [Internet Gateway]
                       │
         ┌─────────────┴─────────────┐
         │   Application Load        │
         │   Balancer (ALB)          │
         │   Port 80                 │
         └──────────┬─────────┬──────┘
                    │         │
         ┌──────────┘         └──────────┐
         │                               │
    ┌────▼────┐                     ┌────▼────┐
    │ Public  │                     │ Public  │
    │ Subnet1 │                     │ Subnet2 │
    │         │                     │         │
    │  ASG    │                     │  ASG    │
    │  2-4    │                     │  2-4    │
    │  EC2    │                     │  EC2    │
    └─────────┘                     └─────────┘
    us-east-1a                      us-east-1b
```

## 🔨 Tasks

### Task 1: Create Variables

**variables.tf**:

```hcl
variable "min_size" {
  description = "Minimum number of instances"
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Maximum number of instances"
  type        = number
  default     = 4
}

variable "desired_capacity" {
  description = "Desired number of instances"
  type        = number
  default     = 2
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

# TODO: Add variables for:
# - health_check_grace_period
# - target_group_health_check_interval
# - scale_up_threshold
# - scale_down_threshold
```

### Task 2: Create Security Groups

**security-groups.tf**:

```hcl
# Security group for ALB
resource "aws_security_group" "alb" {
  name        = "alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = data.aws_vpc.selected.id
  
  # Allow HTTP from internet
  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Allow HTTPS from internet
  ingress {
    description = "HTTPS from anywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "ALB Security Group"
  }
}

# Security group for EC2 instances
resource "aws_security_group" "ec2" {
  name        = "ec2-asg-sg"
  description = "Security group for Auto Scaling Group instances"
  vpc_id      = data.aws_vpc.selected.id
  
  # Allow HTTP from ALB only
  ingress {
    description     = "HTTP from ALB"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  
  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "EC2 ASG Security Group"
  }
}
```

### Task 3: Create Launch Template

**launch-template.tf**:

```hcl
# Get latest Amazon Linux AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# User data script to install and start web server
data "template_file" "user_data" {
  template = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y httpd
    systemctl start httpd
    systemctl enable httpd
    
    # Create simple web page
    INSTANCE_ID=$(ec2-metadata --instance-id | cut -d " " -f 2)
    AVAILABILITY_ZONE=$(ec2-metadata --availability-zone | cut -d " " -f 2)
    
    cat > /var/www/html/index.html <<HTML
    <!DOCTYPE html>
    <html>
    <head>
        <title>Auto Scaling Demo</title>
        <style>
            body { font-family: Arial; text-align: center; margin-top: 50px; }
            h1 { color: #232F3E; }
            .info { background: #f0f0f0; padding: 20px; margin: 20px auto; width: 500px; }
        </style>
    </head>
    <body>
        <h1>🚀 Auto Scaling Group Demo</h1>
        <div class="info">
            <h2>Instance Information</h2>
            <p><strong>Instance ID:</strong> $INSTANCE_ID</p>
            <p><strong>Availability Zone:</strong> $AVAILABILITY_ZONE</p>
            <p><strong>Hostname:</strong> $(hostname)</p>
        </div>
        <p>Refresh to see load balancing in action!</p>
    </body>
    </html>
HTML
  EOF
}

# Launch template
resource "aws_launch_template" "app" {
  name_prefix   = "app-launch-template-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  
  vpc_security_group_ids = [aws_security_group.ec2.id]
  
  user_data = base64encode(data.template_file.user_data.rendered)
  
  monitoring {
    enabled = true
  }
  
  tag_specifications {
    resource_type = "instance"
    
    tags = {
      Name = "ASG Instance"
    }
  }
  
  lifecycle {
    create_before_destroy = true
  }
}
```

### Task 4: Create Target Group

**target-group.tf**:

```hcl
resource "aws_lb_target_group" "app" {
  name     = "app-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.selected.id
  
  # Health check configuration
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"
    matcher             = "200"
    protocol            = "HTTP"
  }
  
  # Deregistration delay
  deregistration_delay = 30
  
  tags = {
    Name = "App Target Group"
  }
}
```

### Task 5: Create Application Load Balancer

**load-balancer.tf**:

```hcl
# Get subnets for ALB
data "aws_vpc" "selected" {
  default = true
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }
}

# Application Load Balancer
resource "aws_lb" "app" {
  name               = "app-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = data.aws_subnets.public.ids
  
  enable_deletion_protection = false  # For practice only!
  
  tags = {
    Name = "Application Load Balancer"
  }
}

# Listener for HTTP
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}
```

### Task 6: Create Auto Scaling Group

**auto-scaling.tf**:

```hcl
resource "aws_autoscaling_group" "app" {
  name = "app-asg"
  
  min_size         = var.min_size
  max_size         = var.max_size
  desired_capacity = var.desired_capacity
  
  vpc_zone_identifier = data.aws_subnets.public.ids
  target_group_arns   = [aws_lb_target_group.app.arn]
  
  health_check_type         = "ELB"
  health_check_grace_period = 300
  
  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }
  
  enabled_metrics = [
    "GroupDesiredCapacity",
    "GroupInServiceInstances",
    "GroupMinSize",
    "GroupMaxSize",
  ]
  
  tag {
    key                 = "Name"
    value               = "ASG Instance"
    propagate_at_launch = true
  }
  
  tag {
    key                 = "ManagedBy"
    value               = "Terraform"
    propagate_at_launch = true
  }
  
  lifecycle {
    create_before_destroy = true
  }
}
```

### Task 7: Create Scaling Policies

**scaling-policies.tf**:

```hcl
# Scale up policy
resource "aws_autoscaling_policy" "scale_up" {
  name                   = "scale-up"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.app.name
}

# CloudWatch alarm to trigger scale up
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "cpu-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "70"
  alarm_description   = "This metric monitors high CPU utilization"
  alarm_actions       = [aws_autoscaling_policy.scale_up.arn]
  
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }
}

# Scale down policy
resource "aws_autoscaling_policy" "scale_down" {
  name                   = "scale-down"
  scaling_adjustment     = -1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.app.name
}

# CloudWatch alarm to trigger scale down
resource "aws_cloudwatch_metric_alarm" "cpu_low" {
  alarm_name          = "cpu-utilization-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "20"
  alarm_description   = "This metric monitors low CPU utilization"
  alarm_actions       = [aws_autoscaling_policy.scale_down.arn]
  
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app.name
  }
}
```

### Task 8: Create Outputs

**outputs.tf**:

```hcl
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.app.dns_name
}

output "alb_url" {
  description = "URL of the load balancer"
  value       = "http://${aws_lb.app.dns_name}"
}

output "asg_name" {
  description = "Name of the Auto Scaling Group"
  value       = aws_autoscaling_group.app.name
}

output "target_group_arn" {
  description = "ARN of the target group"
  value       = aws_lb_target_group.app.arn
}
```

## ✅ Validation Steps

1. **Apply configuration**:
   ```bash
   terraform init
   terraform apply
   ```
   
   Wait 5-10 minutes for instances to launch and health checks to pass.

2. **Get ALB URL**:
   ```bash
   terraform output alb_url
   ```

3. **Test load balancer**:
   ```bash
   # Open in browser or curl
   curl $(terraform output -raw alb_url)
   
   # Refresh multiple times - you should see different instance IDs
   ```

4. **Verify in AWS Console**:
   - EC2 → Load Balancers → Your ALB
   - Check target group health (should show 2 healthy targets)
   - EC2 → Auto Scaling Groups → Your ASG
   - Check activity history
   - View CloudWatch metrics

5. **Test auto scaling**:
   ```bash
   # SSH into instance and generate CPU load
   # (This requires adding SSH access to security group)
   
   # Or use AWS CLI to set desired capacity
   aws autoscaling set-desired-capacity \
     --auto-scaling-group-name app-asg \
     --desired-capacity 4 \
     --profile terraform_practice
   
   # Watch instances launch
   watch -n 5 'aws autoscaling describe-auto-scaling-groups \
     --auto-scaling-group-names app-asg \
     --query "AutoScalingGroups[0].Instances[*].[InstanceId,LifecycleState]" \
     --output table \
     --profile terraform_practice'
   ```

## 🧹 Cleanup

```bash
terraform destroy
```

Verify ALB and instances are deleted.

## 📚 Key Concepts Learned

- Application Load Balancer configuration
- Target groups and health checks
- Launch templates for EC2
- Auto Scaling Groups
- Scaling policies (scale up/down)
- CloudWatch alarms for auto scaling
- Load balancer listeners and rules
- Multi-AZ deployment

## 🎓 Challenge

1. **Add HTTPS Support**:
   - Request ACM certificate
   - Add HTTPS listener (port 443)
   - Redirect HTTP to HTTPS

2. **Target Tracking Scaling**:
   ```hcl
   resource "aws_autoscaling_policy" "target_tracking" {
     name                   = "target-tracking-policy"
     autoscaling_group_name = aws_autoscaling_group.app.name
     policy_type            = "TargetTrackingScaling"
     
     target_tracking_configuration {
       predefined_metric_specification {
         predefined_metric_type = "ASGAverageCPUUtilization"
       }
       target_value = 50.0
     }
   }
   ```

3. **Add Custom Health Check Page**:
   - Create `/health` endpoint
   - Configure target group to use it

4. **Implement Blue-Green Deployment**:
   - Two target groups
   - Weighted routing
   - Gradual traffic shift

5. **Add Application Metrics**:
   - Custom CloudWatch metrics
   - Dashboard for monitoring
   - Alarms for request count and latency

## 💡 Tips

- Health check grace period should be long enough for instance startup
- Set appropriate cooldown periods to prevent flapping
- Use target tracking scaling for simpler configuration
- Monitor target group health in console
- ALB health checks are more reliable than EC2 health checks
- Always deploy across multiple AZs
- Use connection draining (deregistration delay)
- Test scaling policies thoroughly

## 💰 Cost Breakdown

- ALB: ~$0.0225/hour (~$16/month)
- LCU (Load Balancer Capacity Units): ~$0.008/hour per LCU
- EC2 instances (2 × t3.micro): ~$0.0208/hour (~$15/month)
- CloudWatch alarms: First 10 free
- **Total**: ~$0.30/hour (~$31-35/month)

**Destroy after practice!**

## 📖 Reference

- [AWS ALB Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb)
- [Auto Scaling Group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/autoscaling_group)
- [Launch Template](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/launch_template)
- [Target Group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_target_group)

## ✨ Solution

Solution files are in the `solution/` directory. Try completing the lab yourself first!

