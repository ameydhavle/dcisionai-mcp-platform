# 🏭 DcisionAI Manufacturing Optimizer - AWS Deployment

## 🚀 **Complete AWS Production Deployment Package**

This directory contains everything needed to deploy the DcisionAI Manufacturing Optimizer to AWS with a production-ready architecture. Transform your manufacturing operations with AI-powered mathematical optimization.

## 📁 **Directory Structure**

```
aws-deployment/
├── backend/                    # MCP Server Backend
│   ├── mcp_server.py          # Core MCP server with real optimization
│   ├── simple_http_server.py  # HTTP server wrapper
│   ├── requirements.txt       # Python dependencies
│   ├── config/                # Configuration files
│   └── Dockerfile             # Backend container
├── frontend/                   # Web Application
│   ├── simple-index.html      # Static HTML frontend
│   ├── Dockerfile.simple      # Simple frontend container
│   └── nginx.conf             # Nginx configuration
├── infrastructure/             # AWS Infrastructure
│   └── cloudformation-template.yaml  # Complete AWS stack
├── deploy.sh                   # Automated deployment script
├── simple-deploy.sh            # Simplified deployment script
├── test-deployment.sh          # Deployment validation script
├── README.md                   # This file
├── QUICK_START_GUIDE.md        # 15-minute quick start
├── CUSTOMER_DOCUMENTATION.md   # Complete documentation
└── CUSTOMER_EXAMPLES.md        # Real-world examples
```

## 🏗️ **AWS Architecture**

### **Infrastructure Components:**

- **VPC**: Isolated network environment
- **Application Load Balancer**: Routes traffic to services
- **ECS Fargate**: Serverless container hosting
- **ECR**: Container image registry
- **CloudWatch**: Logging and monitoring
- **IAM**: Secure access management

### **Service Architecture:**

```
Internet → ALB → ECS Fargate Services
                ├── Frontend (React + Nginx)
                └── Backend (MCP Server + Flask)
```

## 🛠️ **Prerequisites**

### **Required Tools:**
- AWS CLI v2
- Docker
- AWS Account with appropriate permissions

### **AWS Permissions:**
- ECS (Fargate)
- ECR (Elastic Container Registry)
- CloudFormation
- VPC
- IAM
- CloudWatch Logs
- Application Load Balancer

### **Setup AWS CLI:**
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter your default output format (json)
```

## 🚀 **Deployment Steps**

### **Option 1: Automated Deployment (Recommended)**

```bash
# Navigate to deployment directory
cd aws-deployment

# Run the deployment script
./deploy.sh
```

The script will:
1. ✅ Check prerequisites
2. ✅ Create ECR repository
3. ✅ Build and push Docker images
4. ✅ Deploy CloudFormation stack
5. ✅ Provide application URLs

### **Option 2: Manual Deployment**

#### **Step 1: Create ECR Repository**
```bash
aws ecr create-repository --repository-name dcisionai-manufacturing-dcisionai --region us-east-1
```

#### **Step 2: Login to ECR**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
```

#### **Step 3: Build and Push Images**
```bash
# Backend
cd backend
docker build -t dcisionai-backend .
docker tag dcisionai-backend:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-dcisionai:backend-latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-dcisionai:backend-latest

# Frontend
cd ../frontend
docker build -t dcisionai-frontend .
docker tag dcisionai-frontend:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-dcisionai:frontend-latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-dcisionai:frontend-latest
```

#### **Step 4: Deploy Infrastructure**
```bash
aws cloudformation deploy \
  --template-file infrastructure/cloudformation-template.yaml \
  --stack-name dcisionai-manufacturing \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

## 🌐 **Access Your Application**

After deployment, you'll get:

- **Application URL**: `http://<ALB-DNS-NAME>`
- **Backend API**: `http://<ALB-DNS-NAME>/api`
- **Health Check**: `http://<ALB-DNS-NAME>/health`

## 📊 **Monitoring and Logs**

### **CloudWatch Logs:**
- Backend logs: `/ecs/dcisionai-manufacturing-backend`
- Frontend logs: `/ecs/dcisionai-manufacturing-frontend`

### **ECS Console:**
- View running services
- Monitor task health
- Scale services

### **Application Load Balancer:**
- Monitor request metrics
- View target health
- Configure SSL certificates

## 🔧 **Configuration**

### **Environment Variables:**
- `AWS_DEFAULT_REGION`: AWS region
- `ENVIRONMENT`: prod/staging/dev
- `REACT_APP_API_URL`: Backend API URL

### **Scaling:**
- **Backend**: 2 tasks (512 CPU, 1024 MB memory)
- **Frontend**: 2 tasks (256 CPU, 512 MB memory)
- **Auto-scaling**: Configure in ECS service

## 🔒 **Security Features**

- **VPC Isolation**: Private network environment
- **Security Groups**: Restrictive firewall rules
- **IAM Roles**: Least privilege access
- **HTTPS Ready**: SSL certificate support
- **Container Security**: Non-root user execution

## 💰 **Cost Optimization**

- **Fargate Spot**: 70% cost savings for non-critical workloads
- **Auto-scaling**: Scale down during low usage
- **CloudWatch Logs**: 30-day retention
- **ECR**: Automatic image cleanup

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **Deployment Fails:**
   ```bash
   # Check CloudFormation events
   aws cloudformation describe-stack-events --stack-name dcisionai-manufacturing
   ```

2. **Services Not Starting:**
   ```bash
   # Check ECS service events
   aws ecs describe-services --cluster dcisionai-manufacturing-cluster --services dcisionai-manufacturing-backend-service
   ```

3. **Health Check Failures:**
   ```bash
   # Check application logs
   aws logs tail /ecs/dcisionai-manufacturing-backend --follow
   ```

### **Useful Commands:**

```bash
# Get stack outputs
aws cloudformation describe-stacks --stack-name dcisionai-manufacturing --query 'Stacks[0].Outputs'

# List ECS services
aws ecs list-services --cluster dcisionai-manufacturing-cluster

# View application logs
aws logs tail /ecs/dcisionai-manufacturing-backend --follow
```

## 🔄 **Updates and Maintenance**

### **Update Application:**
```bash
# Rebuild and push images
./deploy.sh

# Update ECS services
aws ecs update-service --cluster dcisionai-manufacturing-cluster --service dcisionai-manufacturing-backend-service --force-new-deployment
```

### **Scale Services:**
```bash
# Scale backend to 4 tasks
aws ecs update-service --cluster dcisionai-manufacturing-cluster --service dcisionai-manufacturing-backend-service --desired-count 4
```

## 🎯 **Production Checklist**

- ✅ **SSL Certificate**: Configure HTTPS
- ✅ **Custom Domain**: Set up Route 53
- ✅ **Monitoring**: Configure CloudWatch alarms
- ✅ **Backup**: Set up automated backups
- ✅ **Security**: Review IAM permissions
- ✅ **Scaling**: Configure auto-scaling policies
- ✅ **Logging**: Set up log aggregation
- ✅ **Testing**: Run load tests

## 🎉 **Success!**

Your DcisionAI Manufacturing Optimizer is now running on AWS with:

- ✅ **High Availability**: Multi-AZ deployment
- ✅ **Auto-scaling**: Handles traffic spikes
- ✅ **Security**: Production-grade security
- ✅ **Monitoring**: Complete observability
- ✅ **Cost Optimization**: Efficient resource usage

**Ready for production traffic!** 🚀
