#!/bin/bash
# Deploy DcisionAI MCP Server to AWS Bedrock AgentCore
# Based on AWS AgentCore MCP documentation

set -e

echo "🚀 Deploying DcisionAI MCP Server to AWS AgentCore..."
echo "=================================================="

# Check if required tools are installed
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI is required but not installed. Aborting." >&2; exit 1; }
command -v agentcore >/dev/null 2>&1 || { echo "❌ AgentCore CLI is required but not installed. Aborting." >&2; exit 1; }

# Set environment variables
export PROJECT_NAME="dcisionai-mcp-server"
export REGION="us-west-2"
export ENVIRONMENT="production"

echo "📋 Project Configuration:"
echo "  Project Name: $PROJECT_NAME"
echo "  Region: $REGION"
echo "  Environment: $ENVIRONMENT"

# Step 1: Install AgentCore starter toolkit
echo ""
echo "📦 Installing AgentCore starter toolkit..."
pip install bedrock-agentcore-starter-toolkit

# Step 2: Create project structure
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

# Step 3: Configure deployment
echo ""
echo "⚙️  Configuring AgentCore deployment..."
echo "This will start a guided configuration process."
echo "Please follow the prompts:"
echo "  - Execution role: Use existing IAM role or create new one"
echo "  - ECR: Press Enter to auto-create"
echo "  - Dependency file: Press Enter to auto-detect"
echo "  - OAuth: Type 'yes' and provide Cognito details"

agentcore configure -e mcp_server.py --protocol MCP

# Step 4: Deploy to AWS
echo ""
echo "🚀 Deploying to AWS AgentCore..."
echo "This will:"
echo "  1. Build Docker container with MCP server"
echo "  2. Push to Amazon ECR"
echo "  3. Create AgentCore runtime"
echo "  4. Deploy to AWS"

agentcore launch

# Step 5: Get deployment information
echo ""
echo "✅ Deployment completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Note the Agent Runtime ARN from the output above"
echo "2. Set up Cognito authentication (if not already done)"
echo "3. Test the deployed MCP server"
echo "4. Update SaaS platform to use the AgentCore endpoint"
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
