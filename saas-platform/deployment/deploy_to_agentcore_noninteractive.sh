#!/bin/bash
# Deploy DcisionAI MCP Server to AWS Bedrock AgentCore (Non-Interactive)
# Based on AWS AgentCore MCP documentation

set -e

echo "🚀 Deploying DcisionAI MCP Server to AWS AgentCore (Non-Interactive)..."
echo "======================================================================"

# Configuration
export PROJECT_NAME="dcisionai-mcp-server"
export REGION="us-west-2"
export ENVIRONMENT="production"

# Cognito Configuration (from setup_cognito.sh output)
export POOL_ID="us-west-2_pEQfTkscK"
export CLIENT_ID="5h4o4dpu7r7qreusrjhu54umqo"
export BEARER_TOKEN="eyJraWQiOiJsM1FpRWI1T01JVWhnNnpQRmNsM1R1SVRBRHh5MmxyTkh2bis2T2ljY3dnPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJhODExNjM0MC0wMDUxLTcwNTQtMmU4ZC1jMzBkNjhlYjQ1MjEiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtd2VzdC0yLmFtYXpvbmF3cy5jb21cL3VzLXdlc3QtMl9wRVFmVGtzY0siLCJjbGllbnRfaWQiOiI1aDRvNGRwdTdyN3FyZXVzcmpodTU0dW1xbyIsIm9yaWdpbl9qdGkiOiIzYWYzZmE3Yy1lNWQxLTQ2OTktYWU0Ny02OTBjY2Y0YWJmMTEiLCJldmVudF9pZCI6IjkzMmEwZWE3LWRiNzktNDQ4OC1iMTZiLWM2ZWJkODRhYTIzZSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NjA2NDEyNzEsImV4cCI6MTc2MDY0NDg3MSwiaWF0IjoxNzYwNjQxMjcyLCJqdGkiOiJmODY2Y2ZkMy05MTU1LTQwMTYtODBhZS1mZTBlNDA4ODYzODgiLCJ1c2VybmFtZSI6ImRjaXNpb25haS11c2VyIn0.S0CL8NDvfsw42AJ_yIn1hSFNixjQnAENPwg7phIyo9Xr2CyvoTuxXg8bdfnESroUNAd0b1yHafW9YSveXD06zjXKld5jLh9mGwTOFp8mpVDQBaJPSRHiq4Ov0Ej_11MX28pKOS-R5jlHeAxDmBbq-qk67CSLRgg215XYC9yVjVyZZue0ha-RHolOKyfg2SZqjVmumJaYswAJ6jX07MhQnRT-m2gB5DI_uawR-GyHmHiCijRXYan0Fo-OPnuSRxyxhWbOTsFctWgaayvLekLBJTMyTjoySaMeu_dVQ9WlVNHcKx1PuMq4-_fOcYFbGvYdSi0Yqxgcr9iSl9P0P9oZFA"
export DISCOVERY_URL="https://cognito-idp.us-west-2.amazonaws.com/us-west-2_pEQfTkscK/.well-known/openid-configuration"

echo "📋 Project Configuration:"
echo "  Project Name: $PROJECT_NAME"
echo "  Region: $REGION"
echo "  Environment: $ENVIRONMENT"
echo "  Pool ID: $POOL_ID"
echo "  Client ID: $CLIENT_ID"

# Check if required tools are installed
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI is required but not installed. Aborting." >&2; exit 1; }
command -v agentcore >/dev/null 2>&1 || { echo "❌ AgentCore CLI is required but not installed. Aborting." >&2; exit 1; }

# Step 1: Create project structure
echo ""
echo "📁 Setting up project structure..."
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

# Copy MCP server and requirements
cp ../agentcore_mcp_server.py ./mcp_server.py
cp ../requirements.txt ./requirements.txt
touch __init__.py

echo "✅ Project structure created:"
echo "  ├── mcp_server.py"
echo "  ├── requirements.txt"
echo "  └── __init__.py"

# Step 2: Configure deployment (non-interactive)
echo ""
echo "⚙️  Configuring AgentCore deployment (non-interactive)..."

# Create a configuration file to avoid interactive prompts
cat > agentcore_config.yaml << EOF
agent:
  name: $PROJECT_NAME
  entrypoint: mcp_server.py
  protocol: MCP
  region: $REGION

aws:
  execution_role: ""  # Auto-create
  ecr_repository: ""  # Auto-create

dependencies:
  requirements_file: requirements.txt

oauth:
  enabled: true
  discovery_url: "$DISCOVERY_URL"
  client_id: "$CLIENT_ID"
EOF

echo "✅ Configuration file created: agentcore_config.yaml"

# Step 3: Deploy to AWS (non-interactive)
echo ""
echo "🚀 Deploying to AWS AgentCore..."
echo "This will:"
echo "  1. Build Docker container with MCP server"
echo "  2. Push to Amazon ECR"
echo "  3. Create AgentCore runtime"
echo "  4. Deploy to AWS"

# Use the configuration file for non-interactive deployment
agentcore configure --config agentcore_config.yaml --non-interactive

# Deploy the agent
agentcore launch

# Step 4: Get deployment information
echo ""
echo "✅ Deployment completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Note the Agent Runtime ARN from the output above"
echo "2. Test the deployed MCP server"
echo "3. Update SaaS platform to use the AgentCore endpoint"
echo ""
echo "🔗 Useful Commands:"
echo "  - Test locally: python mcp_server.py"
echo "  - Check deployment: agentcore status"
echo "  - View logs: agentcore logs"
echo ""
echo "📚 Documentation:"
echo "  - AWS AgentCore MCP: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html"
echo "  - MCP Inspector: npx @modelcontextprotocol/inspector"
echo ""
echo "🎯 Your DcisionAI MCP Server is now hosted on AWS AgentCore!"
