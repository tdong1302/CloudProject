# AWS Django Blog Application - Deployment Guide

## Project Overview

This document provides a complete guide for deploying a Django blog application on AWS with the following architecture:

### Architecture Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      AWS Infrastructure                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ CloudFront CDN (Content Delivery)                      │   │
│  └────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Application Load Balancer (ALB) + SSL/TLS Certificate │   │
│  └────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Auto Scaling Group (EC2 Instances)                    │   │
│  │ - Min: 2 instances                                    │   │
│  │ - Max: 4 instances                                    │   │
│  │ - Target CPU: 70%                                     │   │
│  └────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  ┌──────────────────┐    ┌──────────────────┐                 │
│  │ RDS MySQL        │    │ S3 Bucket        │                 │
│  │ (database1)      │    │ (Media Storage)  │                 │
│  └──────────────────┘    └──────────────────┘                 │
│                               ↓                                 │
│                    ┌──────────────────────┐                    │
│                    │ Lambda Function      │                    │
│                    │ (S3 → DynamoDB)      │                    │
│                    │ Event Trigger        │                    │
│                    └──────────────────────┘                    │
│                               ↓                                 │
│                    ┌──────────────────────┐                    │
│                    │ DynamoDB Table       │                    │
│                    │ (Metadata Storage)   │                    │
│                    └──────────────────────┘                    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Route 53 (DNS + Failover) → S3 Static Website         │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Key AWS Services Used

1. **VPC** - Isolated network with custom CIDR blocks
2. **EC2** - Compute instances running Django application
3. **RDS** - MySQL database for user and blog data
4. **S3** - Object storage for media files
5. **ALB** - Application Load Balancer for traffic distribution
6. **Auto Scaling** - Automatic instance scaling based on CPU load
7. **CloudFront** - CDN for static content delivery
8. **Route 53** - DNS management with failover routing
9. **DynamoDB** - NoSQL database for S3 metadata
10. **Lambda** - Serverless function for S3 → DynamoDB sync
11. **Certificate Manager** - SSL/TLS certificates
12. **IAM** - Identity and Access Management

## Pre-Deployment Configuration

### 1. Environment Variables (.env)

```env
SECRET_KEY=your-django-secret-key
USE_AWS=True
AWS_STORAGE_BUCKET_NAME=awscapstoneXXXblog
AWS_S3_REGION_NAME=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
DB_ENGINE=django.db.backends.mysql
DB_NAME=database1
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=TechMust1234
```

### 2. Django Settings (settings.py)

- Supports both SQLite (local) and MySQL (AWS RDS)
- S3 storage integration for static and media files
- CloudFront CDN configuration
- Security settings optimized for AWS

### 3. Installation Requirements

All Python packages are listed in `requirements.txt`:
```
Django==4.2.11
boto3==1.28.85
mysqlclient==2.2.7
Pillow==11.1.0
django-storages==1.14.2
```

## AWS Deployment Steps

### Step 1: Create VPC and Network Infrastructure

**VPC Configuration:**
- Name: aws_capstone-VPC
- CIDR: 90.90.0.0/16
- Subnets:
  - Public 1A: 90.90.10.0/24
  - Private 1A: 90.90.11.0/24
  - Public 1B: 90.90.20.0/24
  - Private 1B: 90.90.21.0/24

**Internet Gateway:** aws_capstone-IGW
**NAT Instance:** For private subnet internet access
**VPC Endpoints:** S3 endpoint in private subnets

### Step 2: Create Security Groups

**ALB Security Group:**
- Inbound: HTTP (80) and HTTPS (443) from 0.0.0.0/0

**EC2 Security Group:**
- Inbound: HTTP/HTTPS from ALB, SSH (22) from 0.0.0.0/0

**RDS Security Group:**
- Inbound: MySQL 3306 from EC2 security group

**Lambda Security Group:**
- Inbound: All traffic (for VPC communication)

### Step 3: Create RDS MySQL Database

```
Engine: MySQL 8.0.20
Instance Class: db.t2.micro
Storage: 20 GB (auto-scale to 40 GB)
DB Name: database1
Master Username: admin
Master Password: TechMust1234
Backup: 7 days retention
Multi-AZ: Yes (for high availability)
```

### Step 4: Create S3 Buckets

**Bucket 1 (Application Storage):**
- Name: awscapstoneXXXblog
- Region: us-east-1
- Public access: Disabled
- Purpose: Store media files (images, videos)

**Bucket 2 (Failover Website):**
- Name: www.yourdomain.com
- Region: us-east-1
- Public access: Enable static website hosting
- Purpose: Failover static website

### Step 5: Create SSL/TLS Certificate

- Use AWS Certificate Manager
- Domain: *.yourdomain.com
- Validation: DNS
- Used for: ALB and CloudFront

### Step 6: Create IAM Roles

**EC2 Role:**
- Permissions: S3FullAccess
- Attached to EC2 instances
- Allows access to S3 buckets

**Lambda Role:**
- Permissions: S3FullAccess, DynamoDBFullAccess, VPCAccessExecutionRole, NetworkAdministrator
- Attached to Lambda function

### Step 7: Create Launch Template

```
Name: aws_capstone_launch_template
AMI: Ubuntu 18.04 LTS
Instance Type: t2.micro
Key Pair: your-key-pair.pem
Security Group: aws_capstone_EC2_Sec_Group
IAM Instance Profile: aws_capstone_EC2_S3_Full_Access
User Data: userdata_final.sh
```

### Step 8: Create ALB and Target Group

```
Name: awscapstoneALB
Scheme: Internet-facing
Protocol: HTTPS (443)
Certificate: *.yourdomain.com
Target Group: awscapstoneTargetGroup
Health Check Path: /
```

### Step 9: Create Auto Scaling Group

```
Name: aws_capstone_ASG
Min Capacity: 2
Desired Capacity: 2
Max Capacity: 4
Launch Template: aws_capstone_launch_template
Scaling Policy: Target tracking (70% CPU)
Target Group: awscapstoneTargetGroup
```

### Step 10: Create CloudFront Distribution

```
Origin: ALB DNS name
Protocol: HTTPS
Cache Behavior: All HTTP methods
Headers: Include all (for Django)
Cookies: Forward all
Query Strings: Forward all
CNAME: www.yourdomain.com
Certificate: *.yourdomain.com
```

### Step 11: Create DynamoDB Table

```
Name: awscapstoneDynamo
Primary Key: id (String)
Billing Mode: On-demand
```

### Step 12: Create Lambda Function

```
Name: awscapsitonelambdafunction
Runtime: Python 3.8
Role: aws_capstone_lambda_Role
Code: lambda_function_final.py
Timeout: 60 seconds
Memory: 256 MB
VPC: aws_capstone_VPC (all subnets and security group)
Trigger: S3 (Put and Delete events)
```

### Step 13: Create Route 53 with Failover

**Health Check:** Monitor CloudFront endpoint

**Primary Record:**
- Type: Failover
- Value: CloudFront distribution
- Health Check: Enabled

**Secondary Record:**
- Type: Failover
- Value: S3 static website

## Local Testing

### 1. Run locally:
```bash
python manage.py runserver
```

### 2. Test with SQLite database (local)
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3. Upload test media files via admin panel

## Testing Checklist

- [ ] Django application runs on localhost:8000
- [ ] Admin panel accessible and working
- [ ] User registration and login functional
- [ ] Blog post creation working
- [ ] Image/video upload working
- [ ] S3 bucket contains uploaded files
- [ ] DynamoDB table contains file metadata
- [ ] Lambda function triggered successfully
- [ ] CloudFront caching working
- [ ] Route 53 DNS resolution working
- [ ] Auto-scaling triggered on high CPU load
- [ ] Failover to S3 static website working

## Troubleshooting

### EC2 Instance Health Check Failed
- Check security group rules
- Verify Django application running on port 80
- Check CloudWatch logs for errors
- Verify RDS connectivity

### DynamoDB Not Syncing
- Check Lambda function logs
- Verify S3 bucket has Lambda trigger configured
- Check Lambda IAM role permissions
- Verify DynamoDB table name in Lambda code

### S3 Upload Failures
- Verify EC2 IAM role has S3 permissions
- Check S3 bucket public access settings
- Verify Django DEBUG settings
- Check CORS configuration

## Performance Optimization

- CloudFront caching for static files
- RDS read replicas for database scaling
- S3 transfer acceleration for faster uploads
- Lambda function optimization for faster processing

## Security Best Practices

- SSL/TLS for all communications
- Security groups restrict traffic
- IAM roles follow least privilege principle
- Database encryption enabled
- S3 bucket versioning for data protection
- VPC isolated network

## Cost Estimation

- **EC2**: 2-4 instances × t2.micro = $10-20/month
- **RDS**: db.t2.micro = $15/month
- **S3**: Depends on storage usage
- **Data Transfer**: First 1GB free, then $0.09/GB
- **Lambda**: First 1M invocations free
- **DynamoDB**: On-demand pricing
- **CloudFront**: $0.085/GB (varies by region)

**Total Estimated Cost**: $50-100/month for basic setup

## Cleanup

When finished testing, delete all AWS resources to avoid charges:

1. Delete Auto Scaling Group
2. Delete Load Balancer
3. Terminate EC2 instances
4. Delete RDS instance
5. Empty and delete S3 buckets
6. Delete CloudFront distribution
7. Delete DynamoDB table
8. Delete Lambda function
9. Delete CloudWatch logs
10. Delete VPC

---

## Support and Documentation

- AWS Documentation: https://docs.aws.amazon.com
- Django Documentation: https://docs.djangoproject.com
- Django-Storages: https://django-storages.readthedocs.io
- Boto3: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
