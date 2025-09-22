#!/bin/bash
"""
DcisionAI Manufacturing MCP Server - Proper Deployment Script
============================================================

This script implements the proper MCP server deployment strategy using:
- FastMCP framework
- AgentCore CLI toolkit
- Cognito authentication setup
- Standard MCP protocol compliance

Based on: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html

Usage:
    bash scripts/deployment/deploy_mcp_server_proper.sh

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

set -e

# Configuration
REGION="us-east-1"
PROJECT_DIR="domains/manufacturing/mcp_server"
TEMP_PASSWORD="TempPass123!"
PERMANENT_PASSWORD="PermPass123!"

echo "🚀 DEPLOYING DcisionAI Manufacturing MCP Server (Proper Strategy)"
echo "=================================================================="
echo ""

# Step 1: Install required packages
echo "📦 Installing required packages..."
pip install bedrock-agentcore-starter-toolkit
pip install mcp

# Step 2: Navigate to MCP server directory
echo "📁 Navigating to MCP server directory..."
cd $PROJECT_DIR

# Step 3: Set up Cognito user pool for authentication
echo "🔐 Setting up Cognito user pool for authentication..."

# Create User Pool and capture Pool ID directly
export POOL_ID=$(aws cognito-idp create-user-pool \
  --pool-name "DcisionAIMCPUserPool" \
  --policies '{"PasswordPolicy":{"MinimumLength":8}}' \
  --region $REGION | jq -r '.UserPool.Id')

echo "✅ User Pool created: $POOL_ID"

# Create App Client and capture Client ID directly
export CLIENT_ID=$(aws cognito-idp create-user-pool-client \
  --user-pool-id $POOL_ID \
  --client-name "DcisionAIMCPClient" \
  --no-generate-secret \
  --explicit-auth-flows "ALLOW_USER_PASSWORD_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" \
  --region $REGION | jq -r '.UserPoolClient.ClientId')

echo "✅ App Client created: $CLIENT_ID"

# Create User
aws cognito-idp admin-create-user \
  --user-pool-id $POOL_ID \
  --username "mcpuser" \
  --temporary-password "$TEMP_PASSWORD" \
  --region $REGION \
  --message-action SUPPRESS > /dev/null

echo "✅ User created: mcpuser"

# Set Permanent Password
aws cognito-idp admin-set-user-password \
  --user-pool-id $POOL_ID \
  --username "mcpuser" \
  --password "$PERMANENT_PASSWORD" \
  --region $REGION \
  --permanent > /dev/null

echo "✅ Permanent password set"

# Authenticate User and capture Access Token
export BEARER_TOKEN=$(aws cognito-idp initiate-auth \
  --client-id "$CLIENT_ID" \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME='mcpuser',PASSWORD="$PERMANENT_PASSWORD" \
  --region $REGION | jq -r '.AuthenticationResult.AccessToken')

echo "✅ Authentication successful"

# Output the required values
echo ""
echo "📋 Authentication Configuration:"
echo "   Pool ID: $POOL_ID"
echo "   Discovery URL: https://cognito-idp.$REGION.amazonaws.com/$POOL_ID/.well-known/openid-configuration"
echo "   Client ID: $CLIENT_ID"
echo "   Bearer Token: $BEARER_TOKEN"
echo ""

# Step 4: Configure AgentCore deployment
echo "⚙️ Configuring AgentCore deployment..."
echo "   This will start an interactive configuration process."
echo "   Use the values above when prompted."
echo ""

# Configure deployment (interactive)
agentcore configure -e mcp_server.py --protocol MCP

# Step 5: Deploy to AWS
echo "🚀 Deploying MCP server to AWS AgentCore..."
agentcore launch

echo ""
echo "✅ DEPLOYMENT COMPLETED!"
echo "========================"
echo ""
echo "📋 Next Steps:"
echo "1. Test your deployed MCP server using the MCP Inspector"
echo "2. Use the Bearer Token for authentication"
echo "3. The agent runtime ARN will be displayed above"
echo ""
echo "🧪 Testing Commands:"
echo "   export AGENT_ARN=\"<agent_runtime_arn>\""
echo "   export BEARER_TOKEN=\"$BEARER_TOKEN\""
echo "   python test_mcp_client_remote.py"
echo ""
echo "🔍 MCP Inspector:"
echo "   npx @modelcontextprotocol/inspector"
echo "   Use the agent endpoint URL with Bearer token authentication"
echo ""
