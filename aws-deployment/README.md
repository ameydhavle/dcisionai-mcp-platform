# 🚀 DcisionAI Platform - AWS Deployment

## 🌟 **Complete AWS Production Deployment Package**

This directory contains everything needed to deploy the DcisionAI Platform to AWS with a production-ready architecture. Transform your business operations with AI-powered mathematical optimization across 7 industries with 21 predefined workflows.

## 📁 **Directory Structure**

```
aws-deployment/
├── backend/                           # Enhanced Lambda Backend
│   ├── enhanced_lambda_with_workflows.py  # Main Lambda function
│   ├── workflow_templates.py          # 21 industry workflows
│   ├── workflow_api.py               # Workflow API endpoints
│   ├── requirements.txt              # Python dependencies
│   └── config/                       # Configuration files
├── frontend/                          # React Web Application
│   ├── src/                          # React source code
│   │   ├── components/               # React components
│   │   ├── App.js                    # Main application
│   │   └── App.css                   # Styling
│   └── package.json                  # Frontend dependencies
├── agentcore/                         # AgentCore Gateway (Future)
│   ├── setup_agentcore_gateway.py    # Gateway setup script
│   ├── convert_workflows_to_mcp.py   # MCP tool conversion
│   ├── test_agentcore_gateway.py     # Gateway testing
│   └── async_optimization_solution.py # Async processing
├── infrastructure/                    # AWS Infrastructure
│   └── cloudformation-template.yaml  # Complete AWS stack
├── deploy_workflows.py               # Workflow deployment script
├── fix_api_gateway_routing.py        # API Gateway configuration
├── enhanced_optimization_system.py   # Enhanced system setup
├── README.md                         # This file
├── QUICK_START_GUIDE.md              # 15-minute quick start
├── CUSTOMER_DOCUMENTATION.md         # Complete documentation
└── CUSTOMER_EXAMPLES.md              # Real-world examples
```

## 🏗️ **AWS Architecture**

### **Current Architecture (Enhanced Lambda + API Gateway)**

#### **Infrastructure Components:**
- **API Gateway**: RESTful API endpoints with CORS support
- **AWS Lambda**: Serverless optimization functions (2GB memory, 5-minute timeout)
- **Amazon Bedrock**: AI-powered optimization with Claude models
- **DynamoDB**: Async optimization status tracking
- **CloudWatch**: Comprehensive logging and monitoring
- **IAM**: Secure access management and permissions

#### **Service Architecture:**
```
Internet → CloudFront → API Gateway → Lambda Functions
                                    ├── Enhanced Optimization Engine
                                    ├── Workflow API (21 workflows)
                                    ├── Async Processing
                                    └── Bedrock Integration
```

### **Future Architecture (AgentCore Gateway)**

#### **Enhanced Components:**
- **AgentCore Gateway**: Next-generation agent platform
- **Amazon Cognito**: JWT-based authentication
- **MCP Tools**: Model Context Protocol for agent communication
- **Semantic Search**: Natural language tool discovery
- **Persistent Memory**: Context retention across sessions

#### **Advanced Service Architecture:**
```
Internet → CloudFront → AgentCore Gateway → MCP Tools
                                    ├── Semantic Search Engine
                                    ├── Persistent Memory Store
                                    ├── Enhanced Observability
                                    └── Extended Execution Time
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

## 🏭 **Industry-Specific Workflows**

### **21 Predefined Optimization Templates**

DcisionAI now includes comprehensive workflow templates across 7 major industries:

#### **Manufacturing (3 Workflows)**
- **Advanced Production Planning**: Multi-product production optimization with capacity, labor, and material constraints
- **Supply Chain Optimization**: Network design and inventory management optimization  
- **Quality Control Optimization**: Process optimization and defect detection

#### **Marketing (3 Workflows)**
- **Comprehensive Marketing Spend Optimization**: Budget allocation across channels, campaigns, and customer segments
- **Multi-Campaign Performance Optimization**: Cross-channel campaign coordination and budget allocation
- **Customer Acquisition Cost Optimization**: CAC optimization across acquisition channels

#### **Healthcare (3 Workflows)**
- **Resource Allocation Optimization**: Staff scheduling and resource allocation for healthcare facilities
- **Patient Flow Optimization**: Emergency department and patient flow optimization
- **Pharmaceutical Supply Chain**: Drug distribution and inventory optimization

#### **Retail (3 Workflows)**
- **Inventory Optimization**: Multi-location inventory management and demand forecasting
- **Pricing Strategy Optimization**: Dynamic pricing across product categories and locations
- **Store Layout Optimization**: Space allocation and product placement optimization

#### **Financial (3 Workflows)**
- **Portfolio Optimization**: Investment portfolio allocation and risk management
- **Credit Risk Assessment**: Loan approval and risk scoring optimization
- **Fraud Detection Optimization**: Transaction monitoring and fraud prevention

#### **Logistics (3 Workflows)**
- **Route Optimization**: Delivery route planning and vehicle scheduling
- **Warehouse Operations**: Storage allocation and picking optimization
- **Fleet Management**: Vehicle utilization and maintenance scheduling

#### **Energy (3 Workflows)**
- **Grid Optimization**: Power grid load balancing and distribution
- **Renewable Energy Integration**: Solar and wind energy optimization
- **Energy Storage Management**: Battery storage and demand response optimization

### **Workflow Features**
- **Realistic Problem Descriptions**: Detailed, industry-specific optimization problems
- **Expected Outcomes**: Clear success metrics and optimization objectives
- **Difficulty Levels**: Beginner, intermediate, and advanced workflows
- **Time Estimates**: Realistic completion time expectations (3-6 minutes)
- **Async Processing**: Background execution with progress tracking

## 🚀 **Deployment Steps**

### **Option 1: Enhanced Workflow Deployment (Recommended)**

```bash
# Navigate to deployment directory
cd aws-deployment

# Deploy enhanced optimization system with workflows
python3 deploy_workflows.py
```

The script will:
1. ✅ Deploy enhanced Lambda function with 2GB memory
2. ✅ Configure API Gateway with workflow endpoints
3. ✅ Set up DynamoDB for async optimization tracking
4. ✅ Deploy 21 industry-specific workflows
5. ✅ Configure CORS and authentication
6. ✅ Provide API endpoints and testing instructions

### **Option 2: AgentCore Gateway Setup (Future)**

```bash
# Set up AgentCore Gateway infrastructure
python3 setup_agentcore_gateway.py

# Convert workflows to MCP tools
python3 convert_workflows_to_mcp.py

# Test Gateway integration
python3 test_agentcore_gateway.py
```

### **Option 3: Legacy Container Deployment**

```bash
# Navigate to deployment directory
cd aws-deployment

# Run the legacy deployment script
./deploy.sh
```

The script will:
1. ✅ Check prerequisites
2. ✅ Create ECR repository
3. ✅ Build and push Docker images
4. ✅ Deploy CloudFormation stack
5. ✅ Provide application URLs

### **Option 4: Manual Deployment**

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
