#!/bin/bash

# DcisionAI MCP Server Deployment to AWS AgentCore
# This script deploys the MCP server to AWS AgentCore using the official CLI
# Based on AWS AgentCore MCP documentation

set -e

# Configuration
PROJECT_NAME="dcisionai-mcp-server"
ENVIRONMENT=${1:-staging}

echo "🚀 Deploying DcisionAI MCP Server to AWS AgentCore ($ENVIRONMENT)"
echo "================================================================"

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+."
    exit 1
fi

# Check if bedrock-agentcore-starter-toolkit is installed
if ! python3 -c "import bedrock_agentcore_starter_toolkit" 2>/dev/null; then
    echo "📦 Installing AWS AgentCore CLI..."
    pip install bedrock-agentcore-starter-toolkit
fi

# Create project structure for AgentCore
echo "📁 Setting up AgentCore project structure..."
mkdir -p agentcore_deployment
cd agentcore_deployment

# Create the main MCP server file
cat > mcp_server.py << 'EOF'
#!/usr/bin/env python3
"""
DcisionAI MCP Server for AWS AgentCore
=====================================

Main entry point for AWS AgentCore deployment.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to Python path to access our modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import our FastMCP server
from src.mcp_server.fastmcp_server import create_fastmcp_server

if __name__ == "__main__":
    # Create and run the FastMCP server
    server = create_fastmcp_server()
    server.run()
EOF

# Create requirements.txt for AgentCore
cat > requirements.txt << 'EOF'
# AWS AgentCore MCP Server Requirements
mcp>=1.0.0
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
structlog>=23.2.0
boto3>=1.39.7
aiohttp>=3.9.0
EOF

# Create __init__.py
touch __init__.py

# Copy our source code
echo "📦 Copying source code..."
cp -r ../src .

# Configure AgentCore deployment
echo "⚙️ Configuring AgentCore deployment..."
echo "Note: You will be prompted for configuration details."
echo "For execution role, you need an IAM role with appropriate permissions."
echo "For ECR, press Enter to auto-create."
echo "For OAuth, type 'yes' and provide your Cognito details."

agentcore configure -e mcp_server.py --protocol MCP

# Deploy to AWS
echo "🚀 Deploying to AWS AgentCore..."
agentcore launch

# Get deployment outputs
echo "📊 Getting deployment information..."
AGENT_ARN=$(agentcore describe | grep "Agent Runtime ARN" | awk '{print $4}')

if [ -n "$AGENT_ARN" ]; then
    echo "✅ Deployment successful!"
    echo "📋 Deployment Details:"
    echo "   Environment: $ENVIRONMENT"
    echo "   Agent Runtime ARN: $AGENT_ARN"
    echo ""
    echo "🔗 To test your deployed server:"
    echo "1. Set environment variables:"
    echo "   export AGENT_ARN=\"$AGENT_ARN\""
    echo "   export BEARER_TOKEN=\"your_bearer_token\""
    echo ""
    echo "2. Run the test client:"
    echo "   python test_agentcore_client.py"
    echo ""
    echo "3. Or use MCP Inspector:"
    echo "   npx @modelcontextprotocol/inspector"
    echo "   URL: https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/$(echo $AGENT_ARN | sed 's/:/%3A/g' | sed 's/\//%2F/g')/invocations?qualifier=DEFAULT"
else
    echo "❌ Deployment failed or ARN not found"
    exit 1
fi

echo "🎉 MCP Server successfully deployed to AWS AgentCore!"
