# 🚀 Phase 2: SaaS Platform MCP Client Deployment Guide

## 🎯 **Objective**
Deploy the DcisionAI MCP server to AWS Bedrock AgentCore and update the SaaS platform to act as an MCP client.

## 📋 **Prerequisites**

### **Required Tools**
- AWS CLI configured with appropriate permissions
- Python 3.10+ 
- Node.js 18+ (for frontend)
- Docker (optional, for containerization)

### **AWS Permissions**
- Bedrock AgentCore access
- ECR (Elastic Container Registry) access
- Cognito User Pool management
- IAM role creation

## 🛠️ **Step-by-Step Deployment**

### **Step 1: Setup Cognito Authentication**

```bash
cd saas-platform/deployment
./setup_cognito.sh
```

**Save the output values:**
- Pool ID
- Discovery URL
- Client ID  
- Bearer Token

### **Step 2: Deploy MCP Server to AgentCore**

```bash
cd saas-platform/deployment
./deploy_to_agentcore.sh
```

**During configuration, provide:**
- Execution role: Create new or use existing IAM role
- ECR: Press Enter to auto-create
- Dependency file: Press Enter to auto-detect
- OAuth: Type 'yes' and provide Cognito details from Step 1

**Save the Agent Runtime ARN from the output.**

### **Step 3: Test Deployed MCP Server**

```bash
# Set environment variables
export AGENT_ARN="your_agent_runtime_arn"
export BEARER_TOKEN="your_bearer_token"

# Test the deployed server
python test_agentcore_mcp.py
```

### **Step 4: Update SaaS Platform Configuration**

```bash
# Set environment variables for SaaS platform
export MCP_SERVER_URL="https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/your-encoded-arn/invocations?qualifier=DEFAULT"
export BEARER_TOKEN="your_bearer_token"
```

### **Step 5: Update SaaS Backend**

The backend has been updated to use the MCP client. Key changes:

```python
# saas-platform/backend/app.py
from mcp_client import get_mcp_client

# All endpoints now use MCP client instead of direct imports
mcp_client = get_mcp_client()
result = await mcp_client.classify_intent(problem_description, context)
```

### **Step 6: Test SaaS Platform Integration**

```bash
cd saas-platform/backend
python app.py
```

Test the health check:
```bash
curl http://localhost:5001/api/mcp/health-check
```

### **Step 7: Update Frontend (if needed)**

The frontend should work without changes as it calls the same API endpoints. However, you can enhance it to show MCP server status:

```javascript
// saas-platform/frontend/src/App.js
const checkMCPServerStatus = async () => {
  const response = await axios.get('/api/mcp/health-check');
  setMCPServerStatus(response.data.status);
};
```

## 🔧 **Configuration Files**

### **Environment Variables**

Create `.env` file in `saas-platform/backend/`:

```bash
# MCP Server Configuration
MCP_SERVER_URL=https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/your-encoded-arn/invocations?qualifier=DEFAULT
BEARER_TOKEN=your_bearer_token

# AWS Configuration
AWS_DEFAULT_REGION=us-west-2
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# SaaS Platform Configuration
FLASK_ENV=production
FLASK_DEBUG=False
```

### **Docker Configuration (Optional)**

Update `saas-platform/backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5001

CMD ["python", "app.py"]
```

## 🧪 **Testing**

### **Local Testing**

```bash
# Test MCP server locally
cd saas-platform/deployment
python agentcore_mcp_server.py

# In another terminal, test locally
python test_agentcore_mcp.py local
```

### **Remote Testing**

```bash
# Test deployed MCP server
python test_agentcore_mcp.py
```

### **SaaS Platform Testing**

```bash
# Test backend
curl -X POST http://localhost:5001/api/mcp/classify-intent \
  -H "Content-Type: application/json" \
  -d '{"problem_description": "Optimize my portfolio allocation"}'

# Test frontend
cd saas-platform/frontend
npm start
# Open http://localhost:3000
```

## 📊 **Monitoring**

### **AWS CloudWatch**

Monitor the deployed MCP server:
- Logs: `/aws/bedrock-agentcore/runtime/dcisionai-mcp-server`
- Metrics: Invocation count, duration, errors

### **Health Checks**

```bash
# MCP Server Health
curl -X GET http://localhost:5001/api/mcp/health-check

# SaaS Platform Health  
curl -X GET http://localhost:5001/health
```

## 🔒 **Security**

### **Authentication**

- OAuth tokens for MCP server access
- CORS configuration for frontend
- Environment variable security

### **Network Security**

- VPC isolation (if using ECS)
- Security groups
- HTTPS endpoints

## 🚀 **Production Deployment**

### **AWS ECS Deployment**

Update `saas-platform/deployment/cloudformation-template.yaml` to include:

```yaml
# Add MCP server environment variables
Environment:
  - Name: MCP_SERVER_URL
    Value: !Ref MCPServerURL
  - Name: BEARER_TOKEN
    Value: !Ref BearerToken
```

### **Load Balancer Configuration**

```yaml
# Application Load Balancer
ALB:
  Type: AWS::ElasticLoadBalancingV2::LoadBalancer
  Properties:
    Scheme: internet-facing
    Type: application
    SecurityGroups:
      - !Ref ALBSecurityGroup
```

## 📈 **Scaling**

### **Auto Scaling**

```yaml
# ECS Service Auto Scaling
AutoScalingTarget:
  Type: AWS::ApplicationAutoScaling::ScalableTarget
  Properties:
    ServiceNamespace: ecs
    ScalableDimension: ecs:service:DesiredCount
    ResourceId: !Sub "service/${ECSCluster}/${ECSService}"
    MinCapacity: 1
    MaxCapacity: 10
```

### **MCP Server Scaling**

The AgentCore Runtime automatically handles MCP server scaling based on demand.

## 🔍 **Troubleshooting**

### **Common Issues**

1. **MCP Server Connection Failed**
   - Check AGENT_ARN format
   - Verify BEARER_TOKEN validity
   - Ensure AWS credentials are configured

2. **Cognito Authentication Issues**
   - Verify user pool configuration
   - Check client settings
   - Ensure proper OAuth flow

3. **SaaS Platform Errors**
   - Check MCP client configuration
   - Verify environment variables
   - Review backend logs

### **Debug Commands**

```bash
# Check AWS credentials
aws sts get-caller-identity

# Test MCP server directly
python test_agentcore_mcp.py

# Check SaaS platform logs
tail -f saas-platform/backend/app.log
```

## 📚 **Documentation References**

- [AWS Bedrock AgentCore MCP](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [AWS Cognito Documentation](https://docs.aws.amazon.com/cognito/)

## 🎯 **Success Criteria**

- [ ] MCP server deployed to AWS AgentCore
- [ ] Cognito authentication working
- [ ] SaaS platform connecting to hosted MCP server
- [ ] All 8 MCP tools accessible via SaaS platform
- [ ] Frontend displaying optimization results
- [ ] Health checks passing
- [ ] End-to-end optimization workflow working

## 🚀 **Next Steps**

1. **Deploy**: Run the deployment scripts
2. **Test**: Validate all components
3. **Monitor**: Set up CloudWatch alarms
4. **Scale**: Configure auto-scaling
5. **Optimize**: Fine-tune performance

---

**Your SaaS platform is now a true MCP client connecting to a hosted optimization server!** 🎯
