# DcisionAI Manufacturing MCP Server - Deployment Scripts

## **🏭 Overview**

This directory contains deployment scripts for the DcisionAI Manufacturing MCP Server on AWS Bedrock AgentCore. These scripts provide a complete deployment pipeline for the manufacturing optimization platform.

## **📁 Scripts**

### **1. Complete Deployment Pipeline**
```bash
python scripts/deployment/dcisionai_manufacturing_build_and_deploy.py
```
**Purpose**: Complete end-to-end deployment pipeline
- Builds ARM64 Docker image
- Sets up ECR repository
- Pushes image to ECR
- Deploys to AgentCore
- Tests deployment

### **2. AgentCore Deployment**
```bash
python scripts/deployment/dcisionai_manufacturing_deploy_agentcore.py
```
**Purpose**: Deploy to AWS AgentCore
- Creates agent runtime
- Configures network settings
- Sets up IAM roles

### **3. AgentCore Invocation**
```bash
python scripts/deployment/dcisionai_manufacturing_invoke_agentcore.py
```
**Purpose**: Test deployed agent
- Invokes manufacturing agent
- Tests optimization workflows
- Validates tool availability

## **🚀 Quick Start**

### **Complete Deployment**
```bash
# Run complete deployment pipeline
python scripts/deployment/dcisionai_manufacturing_build_and_deploy.py
```

### **Manual Deployment**
```bash
# Step 1: Build and push image
docker buildx build --platform linux/arm64 -f Dockerfile -t dcisionai-manufacturing-mcp:arm64 --load .
docker tag dcisionai-manufacturing-mcp:arm64 808953421331.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-mcp:latest
docker push 808953421331.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-mcp:latest

# Step 2: Deploy to AgentCore
python scripts/deployment/dcisionai_manufacturing_deploy_agentcore.py

# Step 3: Test deployment
python scripts/deployment/dcisionai_manufacturing_invoke_agentcore.py
```

## **🏭 Manufacturing Tools**

The deployment includes the following manufacturing optimization tools:

- **Intent Classification**: Analyze manufacturing intent and requirements
- **Data Analysis**: Process manufacturing data requirements
- **Model Building**: Create optimization models for production
- **Solver Swarm**: Multi-solver optimization (8 solvers available)
- **Workflow Orchestration**: Coordinate manufacturing processes
- **Critique Tools**: Evaluate and critique optimization solutions
- **Explanation Tools**: Explain results and decision rationale

## **🔧 Configuration**

### **Agent Runtime Configuration**
- **Name**: `dcisionai_manufacturing_mcp_server`
- **Container**: `808953421331.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-mcp:latest`
- **Region**: `us-east-1`
- **Network**: `PUBLIC`

### **Docker Configuration**
- **Platform**: `linux/arm64` (AgentCore requirement)
- **Port**: `8080` (AgentCore requirement)
- **Base Image**: `python:3.11-slim`

## **📊 Monitoring**

### **CloudWatch Logs**
```bash
# Monitor deployment logs
aws logs tail /aws/bedrock-agentcore/runtimes/dcisionai_manufacturing_mcp_server-* --follow
```

### **Agent Status**
```bash
# Check agent status
aws bedrock-agentcore-control list-agent-runtimes --region us-east-1
```

## **🔍 Troubleshooting**

### **Common Issues**

1. **Build Failures**
   - Ensure Docker buildx is available
   - Check ARM64 platform support

2. **ECR Issues**
   - Verify AWS credentials
   - Check ECR repository permissions

3. **AgentCore Deployment**
   - Verify IAM role permissions
   - Check network configuration

### **Debug Commands**
```bash
# Test local container
docker run --rm -p 8081:8080 dcisionai-manufacturing-mcp:arm64

# Check ECR repository
aws ecr describe-images --repository-name dcisionai-manufacturing-mcp --region us-east-1

# Verify agent runtime
aws bedrock-agentcore-control get-agent-runtime --agent-runtime-id dcisionai_manufacturing_mcp_server-* --region us-east-1
```

## **📚 References**

- [AWS AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [DcisionAI Manufacturing Platform](../README.md)
- [Deployment Guide](../../AGENTCORE_DEPLOYMENT_GUIDE.md)

---

**Domain**: Manufacturing Optimization & Decision Intelligence  
**Brand**: DcisionAI  
**Platform**: AWS Bedrock AgentCore  
**Version**: 1.0.0
