# CI/CD Workflows - Temporarily Disabled

## 🚫 Why CI/CD is Disabled

The CI/CD workflows have been **temporarily disabled** because we've completely changed the deployment architecture from the old FastAPI-based approach to the new **AgentCore SDK integration approach**.

## 🔄 What Changed

- **Old Approach**: Custom FastAPI server with complex deployment scripts
- **New Approach**: Direct AgentCore SDK integration using `bedrock-agentcore` package
- **Deployment**: Now uses `scripts/deployment/deploy_DcisionAI_Manufacturing_Agent_v1.py` instead of the old scripts

## 📁 Disabled Files

- `ci-cd.yml.disabled` - Old CI/CD pipeline for FastAPI deployment
- `test.yml.disabled` - Old test workflow for MCP server

## 🚀 Current Deployment Method

The platform is now deployed using:
```bash
python scripts/deployment/deploy_DcisionAI_Manufacturing_Agent_v1.py
```

## 🔧 Re-enabling CI/CD

To re-enable CI/CD, we need to:
1. Update the workflows to use the new AgentCore SDK approach
2. Update the Docker build process to use `Dockerfile.DcisionAI_Manufacturing_Agent_v1`
3. Update the deployment scripts to use the new architecture
4. Update the test workflows to test the new AgentCore agents

## 📋 Next Steps

1. ✅ **COMPLETED**: Deploy using AgentCore SDK (working)
2. 🔄 **PENDING**: Update CI/CD workflows for new architecture
3. 🔄 **PENDING**: Add automated testing for AgentCore agents

## 📞 Contact

For questions about the new deployment approach, see:
- `HANDOFF_DcisionAI_MCP_Platform_Complete.md`
- `AGENTCORE_DEPLOYMENT_SUCCESS.md`
