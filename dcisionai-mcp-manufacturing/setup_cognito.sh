#!/bin/bash

# Setup Cognito User Pool for AWS Bedrock AgentCore Authentication
# Based on AWS Bedrock AgentCore documentation

echo "🔐 Setting up Cognito User Pool for Bedrock AgentCore authentication..."

# Set secure passwords (change these in production!)
TEMP_PASSWORD="TempPass123!"
PERMANENT_PASSWORD="SecurePass123!"

# Create User Pool and capture Pool ID directly
echo "📝 Creating Cognito User Pool..."
export POOL_ID=$(aws cognito-idp create-user-pool \
  --pool-name "DcisionAI-AgentCore-UserPool" \
  --policies '{"PasswordPolicy":{"MinimumLength":8}}' \
  --region us-east-1 | jq -r '.UserPool.Id')

if [ -z "$POOL_ID" ] || [ "$POOL_ID" = "null" ]; then
    echo "❌ Failed to create User Pool"
    exit 1
fi

echo "✅ User Pool created: $POOL_ID"

# Create App Client and capture Client ID directly
echo "📱 Creating App Client..."
export CLIENT_ID=$(aws cognito-idp create-user-pool-client \
  --user-pool-id $POOL_ID \
  --client-name "DcisionAI-AgentCore-Client" \
  --no-generate-secret \
  --explicit-auth-flows "ALLOW_USER_PASSWORD_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" \
  --region us-east-1 | jq -r '.UserPoolClient.ClientId')

if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" = "null" ]; then
    echo "❌ Failed to create App Client"
    exit 1
fi

echo "✅ App Client created: $CLIENT_ID"

# Create User
echo "👤 Creating test user..."
aws cognito-idp admin-create-user \
  --user-pool-id $POOL_ID \
  --username "dcisionai-user" \
  --temporary-password "$TEMP_PASSWORD" \
  --region us-east-1 \
  --message-action SUPPRESS > /dev/null

if [ $? -ne 0 ]; then
    echo "❌ Failed to create user"
    exit 1
fi

echo "✅ Test user created"

# Set Permanent Password
echo "🔑 Setting permanent password..."
aws cognito-idp admin-set-user-password \
  --user-pool-id $POOL_ID \
  --username "dcisionai-user" \
  --password "$PERMANENT_PASSWORD" \
  --region us-east-1 \
  --permanent > /dev/null

if [ $? -ne 0 ]; then
    echo "❌ Failed to set permanent password"
    exit 1
fi

echo "✅ Permanent password set"

# Authenticate User and capture Access Token
echo "🔐 Authenticating user and getting access token..."
export BEARER_TOKEN=$(aws cognito-idp initiate-auth \
  --client-id "$CLIENT_ID" \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME='dcisionai-user',PASSWORD="$PERMANENT_PASSWORD" \
  --region us-east-1 | jq -r '.AuthenticationResult.AccessToken')

if [ -z "$BEARER_TOKEN" ] || [ "$BEARER_TOKEN" = "null" ]; then
    echo "❌ Failed to get access token"
    exit 1
fi

echo "✅ Access token obtained"

# Output the required values
echo ""
echo "🎉 Cognito setup completed successfully!"
echo ""
echo "📋 Required values for Bedrock AgentCore deployment:"
echo "=================================================="
echo "Pool ID: $POOL_ID"
echo "Discovery URL: https://cognito-idp.us-east-1.amazonaws.com/$POOL_ID/.well-known/openid-configuration"
echo "Client ID: $CLIENT_ID"
echo "Bearer Token: $BEARER_TOKEN"
echo ""
echo "💾 Save these values - you'll need them for the agentcore configure step!"
echo ""
echo "🚀 Next steps:"
echo "1. Run: agentcore configure -e bedrock_agentcore_mcp_server.py --protocol MCP"
echo "2. Use the Discovery URL and Client ID when prompted"
echo "3. Run: agentcore launch"
echo ""
