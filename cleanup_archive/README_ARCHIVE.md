# AgentCore Redundant Files Archive

## 📁 What Was Archived

This folder contains infrastructure files that are no longer needed after switching to the AgentCore deployment strategy.

## 🚫 Why These Files Are Redundant

### **Phase 3 Deployment Files (No Longer Needed)**
- **`PHASE3_DEPLOYMENT_STRATEGY.md`** - Old strategy using Lambda + API Gateway
- **`PHASE3_RESOLUTION_SUMMARY.md`** - Conflict resolution for old approach
- **`deploy-phase3*.sh`** - Deployment scripts for Lambda infrastructure
- **`phase3-*.yaml`** - CloudFormation templates for Lambda services

### **Lambda + API Gateway Files (Replaced by AgentCore)**
- **`deploy-lambda-functions.sh`** - Lambda function deployment
- **`lambda-dynamodb-policy.json`** - Lambda IAM policies
- **`api-gateway-*.yaml`** - API Gateway CloudFormation templates
- **`deploy-api-gateway*.sh`** - API Gateway deployment scripts

### **MCP Distribution Files (Old Approach)**
- **`mcp-dist-config*.json`** - CloudFront distribution configs for MCP
- **`mcp-bucket-policy*.json`** - S3 bucket policies for MCP hosting

## ✅ What We're Using Instead

### **AgentCore Direct Deployment**
- **Deployment**: `domains/manufacturing/deployment/deploy_DcisionAI_Manufacturing_Agent_v1.py`
- **Docker**: `domains/manufacturing/Dockerfile.DcisionAI_Manufacturing_Agent_v1`
- **Agent**: `domains/manufacturing/agents/DcisionAI_Manufacturing_Agent_v3.py`

### **Phase 2 Infrastructure (Still Active)**
- **CloudFront**: Content delivery and SSL
- **S3 Buckets**: Documentation, SDK, status pages
- **DNS**: Professional subdomains

## 🔄 Migration Summary

| **Old Approach** | **New Approach** |
|------------------|------------------|
| Lambda + API Gateway | AgentCore Runtime |
| CloudFormation Phase 3 | AgentCore SDK |
| Complex deployment scripts | Simple Python deployment |
| Multiple AWS services | Single AgentCore service |

## 💡 Lessons Learned

1. **AgentCore is simpler** than Lambda + API Gateway for MCP servers
2. **Built-in capabilities** eliminate need for custom utilities
3. **Direct deployment** reduces infrastructure complexity
4. **Phase 2 infrastructure** is still valuable for content delivery

## 🗓️ Archived Date

**September 3, 2025** - After successful AgentCore deployment and testing.

## 🔍 If You Need These Files

These files are archived, not deleted. If you need to reference the old approach:
1. Check this README for context
2. Review the archived files for implementation details
3. Consider if the old approach might be useful for other use cases

## 🚀 Current Status

- ✅ **AgentCore deployment working**
- ✅ **All manufacturing tools functional**
- ✅ **Phase 2 infrastructure active**
- ✅ **Codebase consolidated and clean**
