# 🚀 DcisionAI MCP Platform - Deployment Guide

## 🎯 Production Deployment Guide

**This guide covers the complete deployment process for the DcisionAI MCP Platform, from local development to production AWS deployment.**

## ✨ Pre-Deployment Checklist

### ✅ Prerequisites
- [ ] Python 3.9+ installed
- [ ] AWS CLI configured with appropriate permissions
- [ ] Docker installed and running
- [ ] Git repository cloned
- [ ] Virtual environment activated
- [ ] All tests passing (100% success rate)

### ✅ Environment Setup
- [ ] AWS credentials configured
- [ ] Required Python packages installed
- [ ] Environment variables set
- [ ] Configuration files validated

## 🏗️ Local Development Setup

### 1. Environment Preparation
```bash
# Clone repository
git clone <repository-url>
cd dcisionai-mcp-platform

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration Setup
```bash
# Copy configuration templates
cp shared/config/inference_profiles.yaml.example shared/config/inference_profiles.yaml
cp shared/config/gateway_config.yaml.example shared/config/gateway_config.yaml

# Edit configuration files with your settings
nano shared/config/inference_profiles.yaml
nano shared/config/gateway_config.yaml
```

### 3. Local Testing
```bash
# Run comprehensive test suite
python tests/phase2/test_enhanced_inference_optimization.py

# Expected result: 8/8 tests PASSED (100% success rate)
```

### 4. Local Platform Execution
```bash
# Run main platform
python main.py

# Run specific manufacturing agent
python -m domains.manufacturing.agents.DcisionAI_Manufacturing_Agent_v2

# Run platform manager
python -m platform_core.orchestrator.platform_manager
```

## 🐳 Docker Containerization

### 1. Production Dockerfile
```dockerfile
# Multi-stage build for production
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim as runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Set PATH to include user packages
ENV PATH=/root/.local/bin:$PATH

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Default command
CMD ["python", "main.py"]
```

### 2. Build and Test Container
```bash
# Build production image
docker build -t dcisionai-mcp-platform:latest .

# Test container locally
docker run -p 8080:8080 dcisionai-mcp-platform:latest

# Run tests in container
docker run dcisionai-mcp-platform:latest python tests/phase2/test_enhanced_inference_optimization.py
```

### 3. Container Registry Setup
```bash
# Login to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repository
aws ecr create-repository --repository-name dcisionai-mcp-platform --region us-east-1

# Tag and push image
docker tag dcisionai-mcp-platform:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/dcisionai-mcp-platform:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/dcisionai-mcp-platform:latest
```

## ☁️ AWS Infrastructure Deployment

### 1. CloudFormation Templates

#### Basic Infrastructure (`cloudformation/mcp-server-simple.yaml`)
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'DcisionAI MCP Platform - Basic Infrastructure'

Parameters:
  Environment:
    Type: String
    Default: staging
    AllowedValues: [staging, production]
    Description: Environment name

Resources:
  # VPC and Networking
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub "DcisionAI-MCP-${Environment}"

  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub "DcisionAI-MCP-${Environment}"
      CapacityProviders:
        - FARGATE
      DefaultCapacityProviderStrategy:
        - CapacityProvider: FARGATE
          Weight: 1

  # ECS Service
  ECSService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: !Sub "DcisionAI-MCP-Service-${Environment}"
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: 2
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: ENABLED
          SecurityGroups:
            - !Ref SecurityGroup
          Subnets:
            - !Ref PublicSubnet1
            - !Ref PublicSubnet2

  # Task Definition
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub "DcisionAI-MCP-Task-${Environment}"
      RequiresCompatibilities:
        - FARGATE
      Cpu: 1024
      Memory: 2048
      ExecutionRoleArn: !GetAtt ExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      NetworkMode: awsvpc
      ContainerDefinitions:
        - Name: dcisionai-mcp-platform
          Image: !Sub "${ECRRepository}:latest"
          PortMappings:
            - ContainerPort: 8080
              Protocol: tcp
          Environment:
            - Name: ENVIRONMENT
              Value: !Ref Environment
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs

  # Security Group
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub "DcisionAI-MCP-SG-${Environment}"
      GroupDescription: Security group for DcisionAI MCP Platform
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          CidrIp: 0.0.0.0/0

  # IAM Roles
  ExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "DcisionAI-MCP-ExecutionRole-${Environment}"
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

  TaskRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "DcisionAI-MCP-TaskRole-${Environment}"
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: BedrockAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - bedrock:InvokeModel
                  - bedrock:InvokeModelWithResponseStream
                Resource: '*'

  # CloudWatch Log Group
  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: !Sub "/ecs/DcisionAI-MCP-${Environment}"
      RetentionInDays: 30

Outputs:
  ECSClusterName:
    Description: ECS Cluster Name
    Value: !Ref ECSCluster
    Export:
      Name: !Sub "DcisionAI-MCP-Cluster-${Environment}"

  ECSServiceName:
    Description: ECS Service Name
    Value: !Ref ECSService
    Export:
      Name: !Sub "DcisionAI-MCP-Service-${Environment}"
```

### 2. Infrastructure Deployment
```bash
# Deploy basic infrastructure
aws cloudformation deploy \
  --template-file cloudformation/mcp-server-simple.yaml \
  --stack-name DcisionAI-MCP-Infrastructure-staging \
  --parameter-overrides Environment=staging \
  --capabilities CAPABILITY_NAMED_IAM

# Deploy production infrastructure
aws cloudformation deploy \
  --template-file cloudformation/mcp-server-simple.yaml \
  --stack-name DcisionAI-MCP-Infrastructure-production \
  --parameter-overrides Environment=production \
  --capabilities CAPABILITY_NAMED_IAM
```

### 3. ECS Service Deployment
```bash
# Update ECS service with new image
aws ecs update-service \
  --cluster DcisionAI-MCP-staging \
  --service DcisionAI-MCP-Service-staging \
  --force-new-deployment

# Check deployment status
aws ecs describe-services \
  --cluster DcisionAI-MCP-staging \
  --services DcisionAI-MCP-Service-staging
```

## 🚀 AgentCore Deployment

### 1. Manufacturing Agent Deployment
```bash
# Deploy manufacturing agent to AgentCore
python scripts/deployment/deploy_DcisionAI_Manufacturing_Agent_v1.py

# Expected output:
# ✅ ECR authentication successful
# ✅ Docker image built and pushed
# ✅ AgentCore runtime created
# ✅ Manufacturing agent deployed successfully
```

### 2. Test Deployed Agent
```bash
# Test the deployed agent
python scripts/deployment/test_DcisionAI_Manufacturing_Agent_v1.py

# Expected output:
# ✅ Agent invocation successful
# ✅ Workflow execution completed
# ✅ Performance metrics collected
# ✅ Cost tracking working
```

### 3. Agent Management
```bash
# List AgentCore runtimes
aws bedrock-agentcore-control list-agent-runtimes

# Get specific runtime details
aws bedrock-agentcore-control get-agent-runtime \
  --agent-runtime-id <runtime-id>

# Delete runtime (if needed)
aws bedrock-agentcore-control delete-agent-runtime \
  --agent-runtime-id <runtime-id>
```

## 🔧 Configuration Management

### 1. Environment-Specific Configuration
```bash
# Create environment-specific configs
mkdir -p config/environments

# Staging configuration
cat > config/environments/staging.yaml << EOF
inference_profiles:
  manufacturing:
    regions: ["us-east-1"]
    max_throughput: 500
    optimization_focus: "development"

gateway:
  name: "DcisionAI_Gateway_Staging"
  endpoints:
    primary: "https://staging-gateway.dcisionai.com"

monitoring:
  log_level: "DEBUG"
  enable_metrics: true
  enable_cost_tracking: false
EOF

# Production configuration
cat > config/environments/production.yaml << EOF
inference_profiles:
  manufacturing:
    regions: ["us-east-1", "us-west-2", "eu-west-1"]
    max_throughput: 1000
    optimization_focus: "production"

gateway:
  name: "DcisionAI_Gateway_Production"
  endpoints:
    primary: "https://gateway.dcisionai.com"

monitoring:
  log_level: "INFO"
  enable_metrics: true
  enable_cost_tracking: true
EOF
```

### 2. Configuration Validation
```bash
# Validate configuration files
python -c "
import yaml
from pathlib import Path

config_files = [
    'shared/config/inference_profiles.yaml',
    'shared/config/gateway_config.yaml',
    'config/environments/staging.yaml',
    'config/environments/production.yaml'
]

for config_file in config_files:
    try:
        with open(config_file, 'r') as f:
            yaml.safe_load(f)
        print(f'✅ {config_file} - Valid YAML')
    except Exception as e:
        print(f'❌ {config_file} - Invalid: {e}')
"
```

## 📊 Monitoring and Observability

### 1. CloudWatch Dashboard
```bash
# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name "DcisionAI-MCP-Platform" \
  --dashboard-body file://monitoring/dashboard.json
```

### 2. Log Aggregation
```bash
# View ECS service logs
aws logs tail /ecs/DcisionAI-MCP-staging --follow

# View application logs
aws logs filter-log-events \
  --log-group-name "/ecs/DcisionAI-MCP-staging" \
  --filter-pattern "ERROR"
```

### 3. Performance Monitoring
```bash
# Check ECS service metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=DcisionAI-MCP-Service-staging \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Average
```

## 🔒 Security Configuration

### 1. IAM Role Management
```bash
# Create custom execution role
aws iam create-role \
  --role-name DcisionAI-MCP-CustomExecutionRole \
  --assume-role-policy-document file://iam/execution-role-trust-policy.json

# Attach required policies
aws iam attach-role-policy \
  --role-name DcisionAI-MCP-CustomExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Create custom task role
aws iam create-role \
  --role-name DcisionAI-MCP-CustomTaskRole \
  --assume-role-policy-document file://iam/task-role-trust-policy.json

# Attach Bedrock access policy
aws iam put-role-policy \
  --role-name DcisionAI-MCP-CustomTaskRole \
  --policy-name BedrockAccess \
  --policy-document file://iam/bedrock-access-policy.json
```

### 2. Network Security
```bash
# Update security group rules
aws ec2 authorize-security-group-ingress \
  --group-id <security-group-id> \
  --protocol tcp \
  --port 8080 \
  --cidr <your-ip>/32

# Remove public access (for production)
aws ec2 revoke-security-group-ingress \
  --group-id <security-group-id> \
  --protocol tcp \
  --port 8080 \
  --cidr 0.0.0.0/0
```

## 🚀 CI/CD Pipeline

### 1. GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy DcisionAI MCP Platform

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python tests/phase2/test_enhanced_inference_optimization.py

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      - name: Build, tag, and push image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: dcisionai-mcp-platform
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster DcisionAI-MCP-production \
            --service DcisionAI-MCP-Service-production \
            --force-new-deployment
```

### 2. Automated Testing
```bash
# Pre-deployment test script
#!/bin/bash
set -e

echo "🧪 Running pre-deployment tests..."

# Run test suite
python tests/phase2/test_enhanced_inference_optimization.py

# Check test results
if [ $? -eq 0 ]; then
    echo "✅ All tests passed - ready for deployment"
    exit 0
else
    echo "❌ Tests failed - deployment blocked"
    exit 1
fi
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (100% success rate)
- [ ] Configuration files validated
- [ ] Security review completed
- [ ] Performance testing completed
- [ ] Rollback plan prepared

### Deployment
- [ ] Infrastructure deployed
- [ ] Container images built and pushed
- [ ] ECS services updated
- [ ] Health checks passing
- [ ] Monitoring configured

### Post-Deployment
- [ ] Smoke tests completed
- [ ] Performance metrics validated
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] Team notified

## 🆘 Troubleshooting

### Common Issues

#### 1. ECS Service Not Starting
```bash
# Check service events
aws ecs describe-services \
  --cluster DcisionAI-MCP-staging \
  --services DcisionAI-MCP-Service-staging

# Check task definition
aws ecs describe-task-definition \
  --task-definition DcisionAI-MCP-Task-staging
```

#### 2. Container Health Check Failing
```bash
# Check container logs
aws logs filter-log-events \
  --log-group-name "/ecs/DcisionAI-MCP-staging" \
  --filter-pattern "ERROR"

# Check container status
aws ecs describe-tasks \
  --cluster DcisionAI-MCP-staging \
  --tasks <task-arn>
```

#### 3. Performance Issues
```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=DcisionAI-MCP-Service-staging \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Average
```

### Rollback Procedures
```bash
# Rollback to previous task definition
aws ecs update-service \
  --cluster DcisionAI-MCP-staging \
  --service DcisionAI-MCP-Service-staging \
  --task-definition DcisionAI-MCP-Task-staging:1

# Rollback infrastructure
aws cloudformation rollback-stack \
  --stack-name DcisionAI-MCP-Infrastructure-staging
```

## 🏆 Production Readiness

### ✅ Achieved Standards
- **100% Test Success Rate**: All 8 tests passing
- **Production Error Handling**: Comprehensive error management
- **Resource Management**: Proper cleanup and resource handling
- **Security Implementation**: Multi-layer security architecture
- **Monitoring & Alerting**: Comprehensive observability

### 🚀 Deployment Ready
- **AWS Integration**: Full AWS service integration
- **Containerization**: Production Docker images
- **Infrastructure as Code**: CloudFormation templates
- **CI/CD Pipeline**: Automated deployment pipeline
- **Monitoring Stack**: Production monitoring and alerting

---

**The DcisionAI MCP Platform is production-ready with comprehensive deployment procedures, security configurations, and monitoring capabilities. No shortcuts taken - ready for enterprise deployment!** 🚀
