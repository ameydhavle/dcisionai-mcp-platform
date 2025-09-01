# DcisionAI MCP Server - AWS AgentCore Deployment Guide

## **🎯 Overview**

This guide documents the successful deployment of the DcisionAI MCP Server to AWS Bedrock AgentCore using a custom FastAPI agent approach. The deployment bypasses the AgentCore Starter Toolkit to provide full control over the container and configuration.

## **📋 Prerequisites**

- AWS CLI configured with appropriate permissions
- Docker with buildx support
- Python 3.11+
- AgentCore SDK: `bedrock-agentcore>=0.1.2`

## **🏗️ Architecture**

### **Production Structure**
```
dcisionai-mcp-platform/
├── src/mcp_server/                    # Main production architecture
│   ├── DcisionAI_Manufacturing_Agent.py  # FastAPI agent (REQUIRED endpoints)
│   ├── fastmcp_server.py             # MCP server implementation
│   ├── tools/manufacturing/          # Manufacturing tools
│   ├── config/                       # Configuration management
│   └── utils/                        # Utilities
├── Dockerfile                         # ARM64 container (REQUIRED)
├── requirements.mcp.txt              # Dependencies
├── scripts/deployment/dcisionai_manufacturing_build_and_deploy.py      # Complete deployment pipeline
├── scripts/deployment/dcisionai_manufacturing_deploy_agentcore.py      # AgentCore deployment
├── scripts/deployment/dcisionai_manufacturing_invoke_agentcore.py      # AgentCore testing
└── Tasks.md                          # Task tracking
```

### **Key Components**

1. **DcisionAI Manufacturing Agent** (`src/mcp_server/DcisionAI_Manufacturing_Agent.py`)
   - `/invocations` POST endpoint (REQUIRED by AgentCore)
   - `/ping` GET endpoint (REQUIRED by AgentCore)
   - MCP server integration
   - Proper error handling

2. **ARM64 Docker Container** (`Dockerfile`)
   - ARM64 architecture (REQUIRED by AgentCore)
   - Port 8080 (REQUIRED by AgentCore)
   - All dependencies included

3. **Manufacturing Tools**
   - Intent classification
   - Data analysis
   - Model building
   - Optimization solving
   - Workflow orchestration

## **🚀 Deployment Process**

### **Step 1: Local Testing**

```bash
# Start the DcisionAI Manufacturing Agent locally
nohup python3 src/mcp_server/DcisionAI_Manufacturing_Agent.py > manufacturing_agent.log 2>&1 &

# Test ping endpoint
curl http://localhost:8080/ping

# Test invocations endpoint
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "Hello DcisionAI MCP Server"}}'
```

### **Step 2: Build ARM64 Docker Image**

```bash
# Build ARM64 image
docker buildx build --platform linux/arm64 -f Dockerfile -t dcisionai-mcp-custom:arm64 --load .

# Test container locally
docker run --rm -p 8081:8080 dcisionai-mcp-custom:arm64
```

### **Step 3: Create ECR Repository**

```bash
# Create ECR repository
aws ecr create-repository --repository-name dcisionai-mcp-custom --region us-east-1

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 808953421331.dkr.ecr.us-east-1.amazonaws.com
```

### **Step 4: Push to ECR**

```bash
# Tag image
docker tag dcisionai-mcp-custom:arm64 808953421331.dkr.ecr.us-east-1.amazonaws.com/dcisionai-mcp-custom:latest

# Push to ECR
docker push 808953421331.dkr.ecr.us-east-1.amazonaws.com/dcisionai-mcp-custom:latest
```

### **Step 5: Deploy to AgentCore**

```bash
# Deploy using custom script
python scripts/deployment/dcisionai_manufacturing_deploy_agentcore.py
```

### **Step 6: Test Deployment**

```bash
# Test the deployed agent
python scripts/deployment/dcisionai_manufacturing_invoke_agentcore.py
```

## **🔧 Configuration Details**

### **AgentCore Requirements**

- **Platform**: `linux/arm64` (REQUIRED)
- **Endpoints**: `/invocations` POST and `/ping` GET (REQUIRED)
- **Port**: 8080 (REQUIRED)
- **ECR**: Images must be deployed to ECR
- **Network**: PUBLIC mode for internet access

### **Docker Configuration**

```dockerfile
# ARM64 base image (REQUIRED)
FROM --platform=linux/arm64 python:3.11-slim

# Expose port 8080 (REQUIRED)
EXPOSE 8080

# Run custom agent
CMD ["python", "src/mcp_server/DcisionAI_Manufacturing_Agent.py"]
```

### **FastAPI Agent Structure**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: InvocationRequest):
    # Agent logic here
    pass

@app.get("/ping")
async def ping():
    # Health check
    pass
```

## **📊 Deployment Results**

### **Successful Deployment**
- **Agent Runtime**: `dcisionai_mcp_custom-1j8icgDxrY`
- **Status**: READY
- **ARN**: `arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/dcisionai_mcp_custom-1j8icgDxrY`
- **ECR URI**: `808953421331.dkr.ecr.us-east-1.amazonaws.com/dcisionai-mcp-custom`

### **Available Tools**
- `classify_manufacturing_intent`
- `analyze_data_requirements`
- `build_optimization_model`
- `solve_optimization_problem`
- `manufacturing_optimization_workflow`
- `manufacturing_tools_status`

## **🔍 Troubleshooting**

### **Common Issues**

1. **Entry Point Errors**
   - **Problem**: AgentCore Starter Toolkit overriding configuration
   - **Solution**: Use custom agent approach (this guide)

2. **Credential Issues**
   - **Problem**: AWS credentials not available locally
   - **Solution**: Expected in local environment, works in AgentCore

3. **Port Conflicts**
   - **Problem**: Wrong port configuration
   - **Solution**: Use port 8080 (AgentCore requirement)

4. **Architecture Issues**
   - **Problem**: Wrong Docker architecture
   - **Solution**: Use ARM64 (AgentCore requirement)

### **Debugging Commands**

```bash
# Check agent status
aws bedrock-agentcore-control list-agent-runtimes --region us-east-1

# Get agent details
aws bedrock-agentcore-control get-agent-runtime \
  --agent-runtime-id dcisionai_mcp_custom-1j8icgDxrY \
  --region us-east-1

# Test local container
docker run --rm -p 8081:8080 dcisionai-mcp-custom:arm64
```

## **📈 Monitoring and Logs**

### **CloudWatch Logs**
- **Log Group**: `/aws/bedrock-agentcore/runtimes/dcisionai_mcp_custom-1j8icgDxrY-DEFAULT`
- **Command**: `aws logs tail /aws/bedrock-agentcore/runtimes/dcisionai_mcp_custom-1j8icgDxrY-DEFAULT --follow`

### **Health Monitoring**
- **Endpoint**: `GET /ping`
- **Expected Response**: JSON with status and tool information

## **🔄 Updates and Maintenance**

### **Updating the Agent**

1. **Rebuild Image**
   ```bash
   docker buildx build --platform linux/arm64 -f Dockerfile -t dcisionai-mcp-custom:arm64 --load .
   ```

2. **Push to ECR**
   ```bash
   docker tag dcisionai-mcp-custom:arm64 808953421331.dkr.ecr.us-east-1.amazonaws.com/dcisionai-mcp-custom:latest
   docker push 808953421331.dkr.ecr.us-east-1.amazonaws.com/dcisionai-mcp-custom:latest
   ```

3. **Update Agent Runtime**
   ```bash
   aws bedrock-agentcore-control update-agent-runtime \
     --agent-runtime-id dcisionai_mcp_custom-1j8icgDxrY \
     --agent-runtime-artifact containerConfiguration.containerUri=808953421331.dkr.ecr.us-east-1.amazonaws.com/dcisionai-mcp-custom:latest \
     --region us-east-1
   ```

## **📚 References**

- [AWS AgentCore Custom Agent Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-custom.html)
- [AWS AgentCore Blog Post](https://aws.amazon.com/blogs/aws/introducing-amazon-bedrock-agentcore-securely-deploy-and-operate-ai-agents-at-any-scale/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Multi-Platform Builds](https://docs.docker.com/build/building/multi-platform/)

## **✅ Success Criteria**

- [x] Custom FastAPI agent with required endpoints
- [x] ARM64 Docker container
- [x] Successful ECR deployment
- [x] AgentCore runtime creation
- [x] Working invocations
- [x] All manufacturing tools available
- [x] Proper error handling
- [x] Health monitoring

---

**Last Updated**: August 26, 2025  
**Status**: ✅ Production Ready  
**Version**: 1.0.0
