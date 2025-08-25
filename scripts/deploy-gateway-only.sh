#!/bin/bash

# DcisionAI Gateway Infrastructure Deployment (Gateway Only)
# This script deploys just the gateway infrastructure without MCP server dependencies

set -e

# Configuration
ENVIRONMENT=${1:-staging}
REGION=${2:-us-east-1}
STACK_NAME="DcisionAI-Gateway-${ENVIRONMENT}"

echo "🏗️ Deploying DcisionAI Gateway Infrastructure (Gateway Only)"
echo "============================================================="
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "Stack Name: $STACK_NAME"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI."
    exit 1
fi

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ AWS Account ID: $AWS_ACCOUNT_ID"

# Step 1: Deploy Gateway Infrastructure
echo ""
echo "🚀 Step 1: Deploying Gateway Infrastructure"
echo "-------------------------------------------"

# Deploy CloudFormation stack for gateway
aws cloudformation deploy \
    --template-file cloudformation/gateway-infrastructure.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        Environment=$ENVIRONMENT \
        DomainName=api.dcisionai.com \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --region $REGION

# Get stack outputs
echo "📊 Getting gateway outputs..."
GATEWAY_OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs' \
    --output json)

USER_POOL_ID=$(echo $GATEWAY_OUTPUTS | jq -r '.[] | select(.OutputKey=="UserPoolId").OutputValue')
USER_POOL_CLIENT_ID=$(echo $GATEWAY_OUTPUTS | jq -r '.[] | select(.OutputKey=="UserPoolClientId").OutputValue')
GATEWAY_URL=$(echo $GATEWAY_OUTPUTS | jq -r '.[] | select(.OutputKey=="GatewayUrl").OutputValue')
TENANTS_TABLE=$(echo $GATEWAY_OUTPUTS | jq -r '.[] | select(.OutputKey=="TenantsTableName").OutputValue')
API_KEYS_TABLE=$(echo $GATEWAY_OUTPUTS | jq -r '.[] | select(.OutputKey=="APIKeysTableName").OutputValue')

echo "✅ Gateway infrastructure deployed"
echo "   User Pool ID: $USER_POOL_ID"
echo "   Client ID: $USER_POOL_CLIENT_ID"
echo "   Gateway URL: $GATEWAY_URL"

# Step 2: Create Test User
echo ""
echo "🚀 Step 2: Creating Test User"
echo "-----------------------------"

# Create test user in Cognito
aws cognito-idp admin-create-user \
    --user-pool-id $USER_POOL_ID \
    --username "test@dcisionai.com" \
    --temporary-password "TempPass123!" \
    --user-attributes Name=email,Value="test@dcisionai.com" \
    --region $REGION

# Set permanent password
aws cognito-idp admin-set-user-password \
    --user-pool-id $USER_POOL_ID \
    --username "test@dcisionai.com" \
    --password "TestPass123!" \
    --permanent \
    --region $REGION

echo "✅ Test user created"
echo "   Username: test@dcisionai.com"
echo "   Password: TestPass123!"

# Step 3: Create Environment Configuration
echo ""
echo "🚀 Step 3: Creating Environment Configuration"
echo "---------------------------------------------"

# Create environment file for local testing
cat > .env.${ENVIRONMENT} << EOF
# DcisionAI Gateway Configuration
ENVIRONMENT=$ENVIRONMENT
AWS_REGION=$REGION

# Gateway Configuration
USER_POOL_ID=$USER_POOL_ID
USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID
TENANTS_TABLE=$TENANTS_TABLE
API_KEYS_TABLE=$API_KEYS_TABLE
MCP_SERVER_URL=http://localhost:8000

# Gateway URL
GATEWAY_URL=$GATEWAY_URL

# Test User
TEST_USERNAME=test@dcisionai.com
TEST_PASSWORD=TestPass123!
EOF

echo "✅ Environment configuration saved to .env.${ENVIRONMENT}"

# Final Summary
echo ""
echo "🎉 DcisionAI Gateway Infrastructure Deployed Successfully!"
echo "=========================================================="
echo ""
echo "📋 Deployment Summary:"
echo "   Environment: $ENVIRONMENT"
echo "   Region: $REGION"
echo "   Gateway URL: $GATEWAY_URL"
echo ""
echo "🔐 Authentication:"
echo "   User Pool ID: $USER_POOL_ID"
echo "   Client ID: $USER_POOL_CLIENT_ID"
echo "   Test User: test@dcisionai.com"
echo ""
echo "🚀 Next Steps:"
echo "   1. Deploy MCP server separately"
echo "   2. Update gateway to point to MCP server"
echo "   3. Test the complete architecture"
echo ""
echo "✅ Gateway infrastructure is ready!"
