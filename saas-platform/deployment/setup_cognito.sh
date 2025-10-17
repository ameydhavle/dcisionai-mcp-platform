#!/bin/bash
# Setup Cognito User Pool for AWS AgentCore MCP Server Authentication
# Based on AWS AgentCore MCP documentation

set -e

echo "🔐 Setting up Cognito User Pool for DcisionAI MCP Server..."
echo "========================================================="

# Configuration
export REGION="us-west-2"
export POOL_NAME="DcisionAIMCPUserPool"
export CLIENT_NAME="DcisionAIMCPClient"
export USERNAME="dcisionai-user"
export TEMP_PASSWORD="TempPass123!"
export PERMANENT_PASSWORD="DcisionAI2025!"

echo "📋 Configuration:"
echo "  Region: $REGION"
echo "  Pool Name: $POOL_NAME"
echo "  Client Name: $CLIENT_NAME"
echo "  Username: $USERNAME"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Check if jq is installed
if ! command -v jq >/dev/null 2>&1; then
    echo "❌ jq is required but not installed. Please install jq first."
    exit 1
fi

echo ""
echo "🏗️  Creating User Pool..."

# Create User Pool and capture Pool ID
export POOL_ID=$(aws cognito-idp create-user-pool \
  --pool-name "$POOL_NAME" \
  --policies '{"PasswordPolicy":{"MinimumLength":8}}' \
  --region $REGION | jq -r '.UserPool.Id')

echo "✅ User Pool created with ID: $POOL_ID"

echo ""
echo "🔧 Creating App Client..."

# Create App Client and capture Client ID
export CLIENT_ID=$(aws cognito-idp create-user-pool-client \
  --user-pool-id $POOL_ID \
  --client-name "$CLIENT_NAME" \
  --no-generate-secret \
  --explicit-auth-flows "ALLOW_USER_PASSWORD_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" \
  --region $REGION | jq -r '.UserPoolClient.ClientId')

echo "✅ App Client created with ID: $CLIENT_ID"

echo ""
echo "👤 Creating User..."

# Create User
aws cognito-idp admin-create-user \
  --user-pool-id $POOL_ID \
  --username "$USERNAME" \
  --temporary-password "$TEMP_PASSWORD" \
  --region $REGION \
  --message-action SUPPRESS > /dev/null

echo "✅ User created with temporary password"

echo ""
echo "🔑 Setting Permanent Password..."

# Set Permanent Password
aws cognito-idp admin-set-user-password \
  --user-pool-id $POOL_ID \
  --username "$USERNAME" \
  --password "$PERMANENT_PASSWORD" \
  --region $REGION \
  --permanent > /dev/null

echo "✅ Permanent password set"

echo ""
echo "🎫 Getting Access Token..."

# Authenticate User and capture Access Token
export BEARER_TOKEN=$(aws cognito-idp initiate-auth \
  --client-id "$CLIENT_ID" \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME="$USERNAME",PASSWORD="$PERMANENT_PASSWORD" \
  --region $REGION | jq -r '.AuthenticationResult.AccessToken')

echo "✅ Access token obtained"

echo ""
echo "🎉 Cognito Setup Complete!"
echo "=========================="
echo ""
echo "📋 Required Values for AgentCore Deployment:"
echo "  Pool ID: $POOL_ID"
echo "  Discovery URL: https://cognito-idp.$REGION.amazonaws.com/$POOL_ID/.well-known/openid-configuration"
echo "  Client ID: $CLIENT_ID"
echo "  Bearer Token: $BEARER_TOKEN"
echo ""
echo "🔧 Environment Variables:"
echo "  export POOL_ID=\"$POOL_ID\""
echo "  export CLIENT_ID=\"$CLIENT_ID\""
echo "  export BEARER_TOKEN=\"$BEARER_TOKEN\""
echo "  export DISCOVERY_URL=\"https://cognito-idp.$REGION.amazonaws.com/$POOL_ID/.well-known/openid-configuration\""
echo ""
echo "📝 Next Steps:"
echo "1. Save these values securely"
echo "2. Use them during 'agentcore configure' step"
echo "3. Use the Bearer Token for testing the deployed MCP server"
echo ""
echo "⚠️  Security Notes:"
echo "  - Change the default passwords in production"
echo "  - Store credentials securely (AWS Secrets Manager recommended)"
echo "  - Rotate tokens regularly"
echo ""
echo "🔗 Documentation:"
echo "  - AWS Cognito: https://docs.aws.amazon.com/cognito/"
echo "  - AgentCore MCP: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html"
