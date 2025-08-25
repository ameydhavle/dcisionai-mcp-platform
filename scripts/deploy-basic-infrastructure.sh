#!/bin/bash

# DcisionAI Basic Infrastructure Deployment
# This script deploys the basic infrastructure components (Cognito, DynamoDB, etc.)

set -e

# Configuration
ENVIRONMENT=${1:-staging}
REGION=${2:-us-east-1}
STACK_NAME="DcisionAI-Basic-${ENVIRONMENT}"

echo "🏗️ Deploying DcisionAI Basic Infrastructure"
echo "============================================"
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

# Step 1: Deploy Basic Infrastructure
echo ""
echo "🚀 Step 1: Deploying Basic Infrastructure"
echo "----------------------------------------"

# Deploy CloudFormation stack for basic infrastructure
aws cloudformation deploy \
    --template-file cloudformation/gateway-basic.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        Environment=$ENVIRONMENT \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --region $REGION

# Get stack outputs
echo "📊 Getting infrastructure outputs..."
INFRASTRUCTURE_OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs' \
    --output json)

USER_POOL_ID=$(echo $INFRASTRUCTURE_OUTPUTS | jq -r '.[] | select(.OutputKey=="UserPoolId").OutputValue')
USER_POOL_CLIENT_ID=$(echo $INFRASTRUCTURE_OUTPUTS | jq -r '.[] | select(.OutputKey=="UserPoolClientId").OutputValue')
TENANTS_TABLE=$(echo $INFRASTRUCTURE_OUTPUTS | jq -r '.[] | select(.OutputKey=="TenantsTableName").OutputValue')
API_KEYS_TABLE=$(echo $INFRASTRUCTURE_OUTPUTS | jq -r '.[] | select(.OutputKey=="APIKeysTableName").OutputValue')
RATE_LIMIT_TABLE=$(echo $INFRASTRUCTURE_OUTPUTS | jq -r '.[] | select(.OutputKey=="RateLimitTableName").OutputValue')
ALERTS_TOPIC_ARN=$(echo $INFRASTRUCTURE_OUTPUTS | jq -r '.[] | select(.OutputKey=="AlertsTopicArn").OutputValue')

echo "✅ Basic infrastructure deployed"
echo "   User Pool ID: $USER_POOL_ID"
echo "   Client ID: $USER_POOL_CLIENT_ID"
echo "   Tenants Table: $TENANTS_TABLE"
echo "   API Keys Table: $API_KEYS_TABLE"
echo "   Rate Limit Table: $RATE_LIMIT_TABLE"
echo "   Alerts Topic: $ALERTS_TOPIC_ARN"

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
# DcisionAI Basic Infrastructure Configuration
ENVIRONMENT=$ENVIRONMENT
AWS_REGION=$REGION

# Authentication Configuration
USER_POOL_ID=$USER_POOL_ID
USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID

# Database Configuration
TENANTS_TABLE=$TENANTS_TABLE
API_KEYS_TABLE=$API_KEYS_TABLE
RATE_LIMIT_TABLE=$RATE_LIMIT_TABLE

# Monitoring Configuration
ALERTS_TOPIC_ARN=$ALERTS_TOPIC_ARN

# Test User
TEST_USERNAME=test@dcisionai.com
TEST_PASSWORD=TestPass123!
EOF

echo "✅ Environment configuration saved to .env.${ENVIRONMENT}"

# Step 4: Test Basic Infrastructure
echo ""
echo "🚀 Step 4: Testing Basic Infrastructure"
echo "--------------------------------------"

# Test Cognito
echo "Testing Cognito authentication..."
TOKEN_RESPONSE=$(aws cognito-idp initiate-auth \
    --client-id $USER_POOL_CLIENT_ID \
    --auth-flow USER_PASSWORD_AUTH \
    --auth-parameters USERNAME=test@dcisionai.com,PASSWORD=TestPass123! \
    --region $REGION 2>/dev/null || echo "{}")

if echo $TOKEN_RESPONSE | jq -e '.AuthenticationResult.IdToken' > /dev/null; then
    echo "✅ Cognito authentication working"
else
    echo "❌ Cognito authentication failed"
fi

# Test DynamoDB tables
echo "Testing DynamoDB tables..."
for table in $TENANTS_TABLE $API_KEYS_TABLE $RATE_LIMIT_TABLE; do
    if aws dynamodb describe-table --table-name $table --region $REGION > /dev/null 2>&1; then
        echo "✅ DynamoDB table $table accessible"
    else
        echo "❌ DynamoDB table $table not accessible"
    fi
done

# Final Summary
echo ""
echo "🎉 DcisionAI Basic Infrastructure Deployed Successfully!"
echo "======================================================="
echo ""
echo "📋 Deployment Summary:"
echo "   Environment: $ENVIRONMENT"
echo "   Region: $REGION"
echo "   Stack Name: $STACK_NAME"
echo ""
echo "🔐 Authentication:"
echo "   User Pool ID: $USER_POOL_ID"
echo "   Client ID: $USER_POOL_CLIENT_ID"
echo "   Test User: test@dcisionai.com"
echo ""
echo "🗄️ Database:"
echo "   Tenants Table: $TENANTS_TABLE"
echo "   API Keys Table: $API_KEYS_TABLE"
echo "   Rate Limit Table: $RATE_LIMIT_TABLE"
echo ""
echo "📊 Monitoring:"
echo "   Alerts Topic: $ALERTS_TOPIC_ARN"
echo ""
echo "🚀 Next Steps:"
echo "   1. Deploy gateway service to ECS"
echo "   2. Deploy MCP server to ECS"
echo "   3. Test the complete architecture"
echo ""
echo "✅ Basic infrastructure is ready!"
