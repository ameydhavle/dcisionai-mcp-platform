# DcisionAI Deployment Guide

## 🚀 **Overview**

This guide covers deploying the DcisionAI platform across different environments, from local development to production on AWS Bedrock AgentCore Runtime.

---

## 📋 **Prerequisites**

### **System Requirements**
- **Python**: 3.10 or higher
- **Node.js**: 18 or higher (for frontend)
- **AWS CLI**: Latest version
- **Docker**: 20.10 or higher (optional)

### **AWS Requirements**
- **AWS Account**: Active account with billing enabled
- **IAM Permissions**: BedrockAgentCoreFullAccess policy
- **Region**: us-east-1 (recommended)
- **Service Quotas**: Bedrock AgentCore runtime limits

### **Development Tools**
- **Git**: For version control
- **pip/uv**: Python package management
- **npm/yarn**: Node.js package management

---

## 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                        │
│              platform.dcisionai.com                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Backend (Flask)                             │
│              MCP Client & API Gateway                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│            AWS Bedrock AgentCore Runtime                   │
│              (Hosted MCP Server)                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ **Deployment Options**

### **Option 1: SaaS Platform (Recommended)**
Deploy the complete web application with AgentCore Runtime integration.

### **Option 2: MCP Server Only**
Deploy just the MCP server for integration with existing applications.

### **Option 3: Local Development**
Set up local development environment for testing and development.

---

## 🌐 **Option 1: SaaS Platform Deployment**

### **Step 1: Prepare AWS Environment**

#### **1.1 Configure AWS CLI**
```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key  
# Enter default region: us-east-1
# Enter default output format: json
```

#### **1.2 Set Up IAM Permissions**
```bash
# Create IAM policy for AgentCore
cat > agentcore-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:*",
                "iam:PassRole",
                "iam:CreateRole",
                "iam:AttachRolePolicy"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Attach policy to your user/role
aws iam attach-user-policy \
    --user-name your-username \
    --policy-arn arn:aws:iam::aws:policy/BedrockAgentCoreFullAccess
```

### **Step 2: Deploy MCP Server to AgentCore**

#### **2.1 Install AgentCore CLI**
```bash
# Install AgentCore starter toolkit
pip install bedrock-agentcore-starter-toolkit

# Verify installation
agentcore --version
```

#### **2.2 Deploy Standalone Agent**
```bash
# Navigate to deployment directory
cd saas-platform/deployment

# Deploy to AgentCore (non-interactive)
./deploy_to_agentcore_noninteractive.sh

# Verify deployment
agentcore list
```

#### **2.3 Test AgentCore Deployment**
```bash
# Test the deployed agent
agentcore invoke '{"prompt": "Test optimization problem"}'

# Check agent status
agentcore status
```

### **Step 3: Deploy Backend Server**

#### **3.1 Set Up Backend Environment**
```bash
# Navigate to backend directory
cd saas-platform/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### **3.2 Configure Environment Variables**
```bash
# Create .env file
cat > .env << EOF
FLASK_ENV=production
FLASK_DEBUG=False
MCP_SERVER_URL=https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/mcp_server-IkOAiK3aOz/invocations
AWS_DEFAULT_REGION=us-east-1
EOF
```

#### **3.3 Start Backend Server**
```bash
# Start Flask server
python app.py

# Or use gunicorn for production
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### **Step 4: Deploy Frontend**

#### **4.1 Set Up Frontend Environment**
```bash
# Navigate to frontend directory
cd saas-platform/frontend

# Install dependencies
npm install

# Build for production
npm run build
```

#### **4.2 Deploy to Web Server**
```bash
# Copy build files to web server
cp -r build/* /var/www/html/

# Configure web server (nginx example)
sudo nano /etc/nginx/sites-available/dcisionai
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name platform.dcisionai.com;
    
    root /var/www/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **Step 5: Configure Domain and SSL**

#### **5.1 Set Up Domain**
```bash
# Point domain to your server
# A record: platform.dcisionai.com -> YOUR_SERVER_IP
```

#### **5.2 Configure SSL with Let's Encrypt**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d platform.dcisionai.com

# Test auto-renewal
sudo certbot renew --dry-run
```

---

## 🔧 **Option 2: MCP Server Only**

### **Step 1: Install MCP Server**
```bash
# Install from PyPI
pip install dcisionai-mcp-server

# Or install from source
git clone https://github.com/dcisionai/dcisionai-mcp-platform.git
cd dcisionai-mcp-platform/mcp-server
pip install -e .
```

### **Step 2: Configure MCP Client**

#### **2.1 Cursor IDE Configuration**
```json
// .cursor/mcp.json
{
    "mcpServers": {
        "dcisionai-mcp-server": {
            "command": "uvx",
            "args": ["dcisionai-mcp-server"],
            "env": {
                "AWS_DEFAULT_REGION": "us-east-1"
            }
        }
    }
}
```

#### **2.2 Claude Desktop Configuration**
```json
// claude_desktop_config.json
{
    "mcpServers": {
        "dcisionai-mcp-server": {
            "command": "uvx",
            "args": ["dcisionai-mcp-server"]
        }
    }
}
```

### **Step 3: Test MCP Integration**
```bash
# Test MCP server
uvx dcisionai-mcp-server

# In Cursor IDE, try:
# "Classify this optimization problem: I need to optimize my production schedule..."
```

---

## 💻 **Option 3: Local Development**

### **Step 1: Clone Repository**
```bash
# Clone the repository
git clone https://github.com/dcisionai/dcisionai-mcp-platform.git
cd dcisionai-mcp-platform
```

### **Step 2: Set Up Backend**
```bash
# Navigate to backend
cd saas-platform/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
python app.py
```

### **Step 3: Set Up Frontend**
```bash
# Navigate to frontend (new terminal)
cd saas-platform/frontend

# Install dependencies
npm install

# Start development server
npm start
```

### **Step 4: Configure Local MCP**
```bash
# Install MCP server locally
cd mcp-server
pip install -e .

# Test local MCP server
python -m dcisionai_mcp_server
```

---

## 🐳 **Docker Deployment**

### **Step 1: Create Dockerfile**
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5001

# Start application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
```

### **Step 2: Build and Run**
```bash
# Build Docker image
docker build -t dcisionai-backend .

# Run container
docker run -p 5001:5001 \
    -e AWS_ACCESS_KEY_ID=your_key \
    -e AWS_SECRET_ACCESS_KEY=your_secret \
    -e AWS_DEFAULT_REGION=us-east-1 \
    dcisionai-backend
```

### **Step 3: Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./saas-platform/backend
    ports:
      - "5001:5001"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=us-east-1
    depends_on:
      - frontend

  frontend:
    build: ./saas-platform/frontend
    ports:
      - "3000:3000"
    volumes:
      - ./saas-platform/frontend:/app
      - /app/node_modules
```

```bash
# Start with Docker Compose
docker-compose up -d
```

---

## 🔍 **Monitoring and Logging**

### **Step 1: Set Up CloudWatch**
```bash
# Create CloudWatch log group
aws logs create-log-group \
    --log-group-name /aws/bedrock-agentcore/dcisionai

# Set retention policy
aws logs put-retention-policy \
    --log-group-name /aws/bedrock-agentcore/dcisionai \
    --retention-in-days 30
```

### **Step 2: Configure Application Logging**
```python
# In app.py
import logging
import boto3

# Set up CloudWatch logging
cloudwatch = boto3.client('logs')
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### **Step 3: Set Up Health Checks**
```bash
# Create health check script
cat > health_check.sh << EOF
#!/bin/bash
curl -f http://localhost:5001/api/health || exit 1
EOF

chmod +x health_check.sh

# Add to crontab
echo "*/5 * * * * /path/to/health_check.sh" | crontab -
```

---

## 🔒 **Security Configuration**

### **Step 1: Set Up IAM Roles**
```bash
# Create IAM role for AgentCore
aws iam create-role \
    --role-name DcisionAIAgentCoreRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock-agentcore.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }'

# Attach policy
aws iam attach-role-policy \
    --role-name DcisionAIAgentCoreRole \
    --policy-arn arn:aws:iam::aws:policy/BedrockAgentCoreFullAccess
```

### **Step 2: Configure VPC (Optional)**
```bash
# Create VPC for private deployment
aws ec2 create-vpc \
    --cidr-block 10.0.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=dcisionai-vpc}]'
```

### **Step 3: Set Up Secrets Management**
```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
    --name dcisionai/api-keys \
    --description "API keys for DcisionAI platform" \
    --secret-string '{"api_key": "your-api-key"}'
```

---

## 📊 **Performance Optimization**

### **Step 1: Configure Caching**
```python
# In app.py
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})

@app.route('/api/mcp/classify-intent', methods=['POST'])
@cache.memoize(timeout=300)  # Cache for 5 minutes
def mcp_classify_intent():
    # ... existing code
```

### **Step 2: Set Up Load Balancing**
```nginx
# nginx.conf
upstream backend {
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}

server {
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **Step 3: Configure Auto-scaling**
```bash
# Set up systemd service
cat > /etc/systemd/system/dcisionai-backend.service << EOF
[Unit]
Description=DcisionAI Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/dcisionai/backend
ExecStart=/opt/dcisionai/backend/venv/bin/gunicorn -w 4 -b 0.0.0.0:5001 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable dcisionai-backend
sudo systemctl start dcisionai-backend
```

---

## 🧪 **Testing and Validation**

### **Step 1: Run Integration Tests**
```bash
# Test AgentCore integration
cd saas-platform/backend
python -m pytest tests/test_agentcore_integration.py -v

# Test API endpoints
python -m pytest tests/test_api_endpoints.py -v
```

### **Step 2: Load Testing**
```bash
# Install locust
pip install locust

# Create load test
cat > load_test.py << EOF
from locust import HttpUser, task, between

class DcisionAIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def classify_intent(self):
        self.client.post("/api/mcp/classify-intent", json={
            "problem_description": "Test optimization problem"
        })
EOF

# Run load test
locust -f load_test.py --host=http://localhost:5001
```

### **Step 3: Health Monitoring**
```bash
# Create monitoring script
cat > monitor.sh << EOF
#!/bin/bash
echo "Checking DcisionAI platform health..."

# Check backend
curl -f http://localhost:5001/api/health || echo "Backend DOWN"

# Check AgentCore
agentcore status || echo "AgentCore DOWN"

# Check disk space
df -h | grep -E "(Filesystem|/dev/)"

# Check memory usage
free -h
EOF

chmod +x monitor.sh
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **AgentCore Deployment Fails**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check AgentCore CLI
agentcore --version

# Check deployment logs
agentcore logs --tail
```

#### **Backend Connection Issues**
```bash
# Check if backend is running
ps aux | grep python

# Check port availability
netstat -tlnp | grep 5001

# Check logs
tail -f /var/log/dcisionai/backend.log
```

#### **Frontend Build Issues**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version
```

### **Debug Commands**
```bash
# Test AgentCore connection
agentcore invoke '{"prompt": "test"}'

# Test backend API
curl -X GET http://localhost:5001/api/health

# Test frontend
curl -X GET http://localhost:3000

# Check system resources
htop
df -h
free -h
```

---

## 📚 **Additional Resources**

### **Documentation**
- [AWS Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://reactjs.org/docs/)

### **Support**
- **GitHub Issues**: [Report bugs and request features](https://github.com/dcisionai/dcisionai-mcp-platform/issues)
- **Discord Community**: [Join our developer community](https://discord.gg/dcisionai)
- **Email Support**: support@dcisionai.com

### **Training**
- **Workshops**: Monthly optimization workshops
- **Certification**: DcisionAI Platform Certification
- **Consulting**: Enterprise deployment consulting

---

*For additional deployment scenarios or custom configurations, please contact our support team or refer to our [GitHub repository](https://github.com/dcisionai/dcisionai-mcp-platform).*