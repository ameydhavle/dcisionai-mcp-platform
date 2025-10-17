# DcisionAI Deployment Guide

## 🚀 **Complete Deployment Guide**

This guide covers all deployment options for the DcisionAI platform, from local development to enterprise production deployments.

## 🎯 **Deployment Options**

### **Option 1: AWS AgentCore Runtime** (Recommended for Production)
### **Option 2: PyPI Distribution** (Recommended for Development)
### **Option 3: Docker Containers** (Recommended for Custom Infrastructure)
### **Option 4: Local Development** (Recommended for Testing)

---

## ☁️ **Option 1: AWS AgentCore Runtime**

### **Prerequisites**
- AWS Account with appropriate permissions
- AWS CLI configured
- AgentCore CLI installed
- Python 3.8-3.12 (OR-Tools compatibility)

### **Step 1: Install AgentCore CLI**
```bash
# Install AgentCore starter toolkit
pip install bedrock-agentcore-starter-toolkit

# Verify installation
agentcore --version
```

### **Step 2: Set Up AWS Credentials**
```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"
```

### **Step 3: Create Project Structure**
```bash
# Create project directory
mkdir dcisionai-agentcore-project
cd dcisionai-agentcore-project

# Copy deployment files
cp ../saas-platform/deployment/dcisionai_agentcore_production.py ./mcp_server.py
cp ../saas-platform/deployment/requirements_production.txt ./requirements.txt
touch __init__.py
```

### **Step 4: Configure AgentCore**
```bash
# Configure AgentCore deployment
agentcore configure -e mcp_server.py --protocol MCP --name "dcisionai-mcp-server" --region "us-west-2"
```

**Configuration Options:**
- **Execution Role**: Use existing IAM role or create new one
- **ECR**: Press Enter to auto-create
- **Dependency File**: Press Enter to auto-detect
- **OAuth**: Type 'yes' and provide Cognito details

### **Step 5: Set Up Cognito (OAuth)**
```bash
# Run Cognito setup script
bash ../saas-platform/deployment/setup_cognito.sh
```

**Output:**
```
Pool ID: us-west-2_XXXXXXXXX
Client ID: XXXXXXXXXXXXXXXX
Bearer Token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Discovery URL: https://cognito-idp.us-west-2.amazonaws.com/us-west-2_XXXXXXXXX/.well-known/openid-configuration
```

### **Step 6: Deploy to AWS**
```bash
# Deploy to AgentCore Runtime
agentcore launch --name "dcisionai-mcp-server" --region "us-west-2"
```

### **Step 7: Test Deployment**
```bash
# Test the deployed agent
agentcore invoke '{"prompt": "Hello, can you help me optimize my portfolio?"}'
```

**Expected Output:**
```json
{
  "status": "success",
  "message": "DcisionAI Optimization Server is running on AWS AgentCore Runtime",
  "available_tools": [
    "classify_intent", "analyze_data", "build_model", "solve_optimization",
    "select_solver", "explain_optimization", "get_workflow_templates", "execute_workflow"
  ],
  "features": [
    "Claude 3 Haiku model building",
    "OR-Tools optimization with 8+ solvers",
    "Business explainability",
    "21 industry workflows",
    "AWS AgentCore Runtime hosting"
  ]
}
```

### **Step 8: Monitor Deployment**
```bash
# View logs
aws logs tail /aws/bedrock-agentcore/runtimes/dcisionai-mcp-server-DEFAULT --follow

# Check status
agentcore status --name "dcisionai-mcp-server" --region "us-west-2"
```

---

## 📦 **Option 2: PyPI Distribution**

### **Prerequisites**
- Python 3.8-3.12
- pip or uv package manager

### **Step 1: Install Package**
```bash
# Standard installation
pip install dcisionai-mcp-server

# With all optional solvers
pip install dcisionai-mcp-server[all-solvers]

# With specific solver groups
pip install dcisionai-mcp-server[quadratic,mosek]
```

### **Step 2: Configure Environment**
```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"

# Optional: Set custom configuration
export DcisionAI_LOG_LEVEL="INFO"
export DcisionAI_CACHE_SIZE="1000"
```

### **Step 3: Test Installation**
```python
# Test basic functionality
from dcisionai_mcp_server.tools import DcisionAITools
import asyncio

async def test():
    tools = DcisionAITools()
    result = await tools.classify_intent("Test optimization problem")
    print(f"Status: {result['status']}")

asyncio.run(test())
```

### **Step 4: Run MCP Server**
```bash
# Run MCP server directly
python -m dcisionai_mcp_server.working_mcp_server

# Or use uvx
uvx dcisionai-mcp-server
```

---

## 🐳 **Option 3: Docker Containers**

### **Prerequisites**
- Docker installed
- Docker Compose (optional)

### **Step 1: Create Dockerfile**
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run MCP server
CMD ["python", "-m", "dcisionai_mcp_server.working_mcp_server"]
```

### **Step 2: Create docker-compose.yml**
```yaml
version: '3.8'

services:
  dcisionai-mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - dcisionai-mcp-server
    restart: unless-stopped
```

### **Step 3: Build and Deploy**
```bash
# Build Docker image
docker build -t dcisionai-mcp-server .

# Run container
docker run -d \
  --name dcisionai-mcp-server \
  -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID="your-key" \
  -e AWS_SECRET_ACCESS_KEY="your-secret" \
  -e AWS_DEFAULT_REGION="us-west-2" \
  dcisionai-mcp-server

# Or use Docker Compose
docker-compose up -d
```

### **Step 4: Test Deployment**
```bash
# Check container status
docker ps

# View logs
docker logs dcisionai-mcp-server

# Test MCP server
curl http://localhost:8000/health
```

---

## 🏠 **Option 4: Local Development**

### **Prerequisites**
- Python 3.8-3.12
- Git
- Virtual environment (recommended)

### **Step 1: Clone Repository**
```bash
git clone https://github.com/dcisionai/dcisionai-mcp-platform.git
cd dcisionai-mcp-platform
```

### **Step 2: Set Up Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### **Step 3: Install Dependencies**
```bash
# Install development dependencies
pip install -r mcp-server/requirements.txt

# Install package in development mode
cd mcp-server
pip install -e .
```

### **Step 4: Configure Environment**
```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"

# Set development environment
export DcisionAI_ENV="development"
export DcisionAI_LOG_LEVEL="DEBUG"
```

### **Step 5: Run Tests**
```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration/

# Run end-to-end tests
python -m pytest tests/e2e/
```

### **Step 6: Start Development Server**
```bash
# Run MCP server
python -m dcisionai_mcp_server.working_mcp_server

# Or run with debug mode
python -m dcisionai_mcp_server.working_mcp_server --debug
```

---

## 🔧 **Configuration**

### **Environment Variables**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AWS_ACCESS_KEY_ID` | AWS access key | - | Yes |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - | Yes |
| `AWS_DEFAULT_REGION` | AWS region | us-west-2 | No |
| `DcisionAI_LOG_LEVEL` | Logging level | INFO | No |
| `DcisionAI_CACHE_SIZE` | Cache size | 1000 | No |
| `DcisionAI_ENV` | Environment | production | No |

### **Configuration Files**

#### **MCP Configuration** (`~/.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "dcisionai-mcp-server": {
      "command": "uvx",
      "args": ["dcisionai-mcp-server@latest"],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "AWS_ACCESS_KEY_ID": "your-key",
        "AWS_SECRET_ACCESS_KEY": "your-secret"
      }
    }
  }
}
```

#### **Docker Configuration** (`docker-compose.yml`)
```yaml
version: '3.8'
services:
  dcisionai-mcp-server:
    image: dcisionai-mcp-server:latest
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
    ports:
      - "8000:8000"
```

---

## 📊 **Monitoring & Observability**

### **Health Checks**

#### **MCP Server Health**
```bash
# Check MCP server status
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "version": "1.4.3",
  "tools_available": 8,
  "uptime": "2h 15m 30s"
}
```

#### **AWS AgentCore Health**
```bash
# Check AgentCore status
agentcore status --name "dcisionai-mcp-server"

# View logs
aws logs tail /aws/bedrock-agentcore/runtimes/dcisionai-mcp-server-DEFAULT --follow
```

### **Metrics & Logging**

#### **Application Metrics**
- Request count and latency
- Optimization solve times
- Error rates and types
- Solver performance metrics

#### **Infrastructure Metrics**
- CPU and memory usage
- Network I/O
- Disk usage
- Container health

#### **Business Metrics**
- Optimization success rate
- User satisfaction scores
- Cost savings achieved
- Time to solution

### **Alerting**

#### **Critical Alerts**
- Service downtime
- High error rates (>5%)
- Long solve times (>30s)
- Resource exhaustion

#### **Warning Alerts**
- High memory usage (>80%)
- Slow response times (>5s)
- Failed optimizations
- Authentication failures

---

## 🔒 **Security**

### **Authentication & Authorization**

#### **AWS IAM Roles**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
    }
  ]
}
```

#### **API Authentication**
```python
# JWT token validation
import jwt
from datetime import datetime, timedelta

def validate_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

### **Data Protection**

#### **Encryption**
- **In Transit**: TLS 1.3 for all communications
- **At Rest**: AES-256 encryption for stored data
- **Key Management**: AWS KMS for key rotation

#### **Data Anonymization**
```python
# Anonymize sensitive data
def anonymize_data(data):
    # Remove PII
    data = remove_pii(data)
    # Hash identifiers
    data = hash_identifiers(data)
    # Aggregate values
    data = aggregate_values(data)
    return data
```

### **Network Security**

#### **Firewall Rules**
```bash
# Allow only necessary ports
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw deny 8000/tcp  # Block direct MCP access
```

#### **VPC Configuration**
```yaml
# VPC with private subnets
VPC:
  CIDR: 10.0.0.0/16
  Subnets:
    - Private: 10.0.1.0/24
    - Private: 10.0.2.0/24
    - Public: 10.0.3.0/24
```

---

## 🚀 **Scaling**

### **Horizontal Scaling**

#### **Load Balancing**
```yaml
# Nginx load balancer configuration
upstream dcisionai_backend {
    server dcisionai-1:8000;
    server dcisionai-2:8000;
    server dcisionai-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://dcisionai_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### **Auto Scaling**
```yaml
# Kubernetes HPA configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: dcisionai-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: dcisionai-mcp-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### **Vertical Scaling**

#### **Resource Limits**
```yaml
# Kubernetes resource limits
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

#### **Performance Tuning**
```python
# Optimize solver performance
solver_params = {
    'time_limit': 30000,  # 30 seconds
    'threads': 4,         # Use 4 CPU cores
    'memory_limit': 2048  # 2GB memory limit
}
```

---

## 🔄 **CI/CD Pipeline**

### **GitHub Actions**

#### **Build and Test**
```yaml
name: Build and Test
on: [push, pull_request]

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
        pip install -r requirements.txt
        pip install pytest
    - name: Run tests
      run: pytest tests/
    - name: Build package
      run: python -m build
```

#### **Deploy to AWS**
```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2
    - name: Deploy to AgentCore
      run: |
        agentcore launch --name "dcisionai-mcp-server" --region "us-west-2"
```

### **Docker Registry**

#### **Build and Push**
```yaml
name: Build and Push Docker Image
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build Docker image
      run: docker build -t dcisionai-mcp-server .
    - name: Push to registry
      run: |
        docker tag dcisionai-mcp-server:latest ${{ secrets.REGISTRY_URL }}/dcisionai-mcp-server:latest
        docker push ${{ secrets.REGISTRY_URL }}/dcisionai-mcp-server:latest
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. AWS Credentials Error**
```bash
# Check AWS configuration
aws sts get-caller-identity

# Reconfigure if needed
aws configure
```

#### **2. OR-Tools Installation Issues**
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y gcc g++

# Reinstall OR-Tools
pip uninstall ortools
pip install ortools
```

#### **3. MCP Server Not Starting**
```bash
# Check Python version
python --version

# Check dependencies
pip list | grep dcisionai-mcp-server

# Check logs
tail -f logs/mcp_server.log
```

#### **4. AgentCore Deployment Issues**
```bash
# Check AgentCore status
agentcore status --name "dcisionai-mcp-server"

# View deployment logs
aws logs tail /aws/bedrock-agentcore/runtimes/dcisionai-mcp-server-DEFAULT --follow
```

### **Debug Mode**

#### **Enable Debug Logging**
```bash
export DcisionAI_LOG_LEVEL="DEBUG"
export PYTHONUNBUFFERED=1
python -m dcisionai_mcp_server.working_mcp_server
```

#### **Verbose Output**
```bash
# Run with verbose output
python -m dcisionai_mcp_server.working_mcp_server --verbose

# Or use debug mode
python -m dcisionai_mcp_server.working_mcp_server --debug
```

---

## 📞 **Support**

### **Getting Help**

1. **Documentation**: [docs.dcisionai.com](https://docs.dcisionai.com)
2. **Support Email**: [support@dcisionai.com](mailto:support@dcisionai.com)
3. **GitHub Issues**: [github.com/dcisionai/issues](https://github.com/dcisionai/issues)
4. **Community Discord**: [discord.gg/dcisionai](https://discord.gg/dcisionai)

### **Enterprise Support**

- **24/7 Support**: Available for Enterprise customers
- **Dedicated Support**: Assigned support engineer
- **SLA**: 99.9% uptime guarantee
- **Custom Deployments**: On-premise and hybrid options

---

**DcisionAI Deployment Guide**: *From Development to Production*
