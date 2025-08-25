#!/bin/bash

# DcisionAI Rock Solid Architecture Deployment
# This script deploys the complete production-ready architecture with gateway layer

set -e

# Configuration
ENVIRONMENT=${1:-staging}
REGION=${2:-us-east-1}
STACK_NAME="DcisionAI-RockSolid-${ENVIRONMENT}"

echo "🏗️ Deploying DcisionAI Rock Solid Architecture"
echo "==============================================="
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

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
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
    --capabilities CAPABILITY_IAM \
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

# Step 2: Deploy MCP Server Infrastructure
echo ""
echo "🚀 Step 2: Deploying MCP Server Infrastructure"
echo "----------------------------------------------"

# Build and push MCP server Docker image
ECR_REPOSITORY="dcisionai-mcp-server"
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $REGION 2>/dev/null || {
    echo "Creating ECR repository: $ECR_REPOSITORY"
    aws ecr create-repository --repository-name $ECR_REPOSITORY --region $REGION
}

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build and push MCP server image
echo "🏗️ Building MCP server Docker image..."
docker build -f Dockerfile.mcp -t $ECR_REPOSITORY:$ENVIRONMENT .

ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPOSITORY"
docker tag $ECR_REPOSITORY:$ENVIRONMENT $ECR_URI:$ENVIRONMENT

echo "📤 Pushing MCP server image to ECR..."
docker push $ECR_URI:$ENVIRONMENT

# Deploy MCP server infrastructure
aws cloudformation deploy \
    --template-file cloudformation/mcp-server-infrastructure.yaml \
    --stack-name "${STACK_NAME}-MCP" \
    --parameter-overrides \
        Environment=$ENVIRONMENT \
        ECRImageUri=$ECR_URI:$ENVIRONMENT \
    --capabilities CAPABILITY_IAM \
    --region $REGION

# Get MCP server outputs
MCP_OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}-MCP" \
    --region $REGION \
    --query 'Stacks[0].Outputs' \
    --output json)

MCP_LOAD_BALANCER_DNS=$(echo $MCP_OUTPUTS | jq -r '.[] | select(.OutputKey=="LoadBalancerDNS").OutputValue')

echo "✅ MCP server infrastructure deployed"
echo "   Load Balancer DNS: $MCP_LOAD_BALANCER_DNS"

# Step 3: Deploy Gateway Service
echo ""
echo "🚀 Step 3: Deploying Gateway Service"
echo "-----------------------------------"

# Build and push gateway Docker image
GATEWAY_ECR_REPOSITORY="dcisionai-gateway"
aws ecr describe-repositories --repository-names $GATEWAY_ECR_REPOSITORY --region $REGION 2>/dev/null || {
    echo "Creating ECR repository: $GATEWAY_ECR_REPOSITORY"
    aws ecr create-repository --repository-name $GATEWAY_ECR_REPOSITORY --region $REGION
}

# Create Dockerfile for gateway
cat > Dockerfile.gateway << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.gateway.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.gateway.txt

# Copy application code
COPY src/gateway ./src/gateway

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=40s \
            --retries=3 \
            CMD curl -f http://localhost:8080/health || exit 1

# Run the gateway
CMD ["python", "-m", "uvicorn", "src.gateway.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Create gateway requirements
cat > requirements.gateway.txt << 'EOF'
fastapi>=0.104.0
uvicorn>=0.24.0
boto3>=1.39.7
PyJWT>=2.8.0
httpx>=0.25.0
redis>=5.0.0
pydantic>=2.0.0
EOF

# Build and push gateway image
echo "🏗️ Building gateway Docker image..."
docker build -f Dockerfile.gateway -t $GATEWAY_ECR_REPOSITORY:$ENVIRONMENT .

GATEWAY_ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$GATEWAY_ECR_REPOSITORY"
docker tag $GATEWAY_ECR_REPOSITORY:$ENVIRONMENT $GATEWAY_ECR_URI:$ENVIRONMENT

echo "📤 Pushing gateway image to ECR..."
docker push $GATEWAY_ECR_URI:$ENVIRONMENT

# Deploy gateway service
aws cloudformation deploy \
    --template-file cloudformation/gateway-service.yaml \
    --stack-name "${STACK_NAME}-Gateway" \
    --parameter-overrides \
        Environment=$ENVIRONMENT \
        ECRImageUri=$GATEWAY_ECR_URI:$ENVIRONMENT \
        UserPoolId=$USER_POOL_ID \
        UserPoolClientId=$USER_POOL_CLIENT_ID \
        TenantsTable=$TENANTS_TABLE \
        APIKeysTable=$API_KEYS_TABLE \
        MCPServerUrl=http://localhost:8000 \
    --capabilities CAPABILITY_IAM \
    --region $REGION

# Step 4: Setup Monitoring and Alerting
echo ""
echo "🚀 Step 4: Setting up Monitoring and Alerting"
echo "---------------------------------------------"

# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
    --dashboard-name "DcisionAI-RockSolid-${ENVIRONMENT}" \
    --dashboard-body file://monitoring/dashboard.json \
    --region $REGION

# Setup SNS topic for alerts
ALERT_TOPIC_ARN=$(aws sns create-topic \
    --name "DcisionAI-Alerts-${ENVIRONMENT}" \
    --region $REGION \
    --query 'TopicArn' \
    --output text)

echo "✅ Monitoring and alerting configured"
echo "   Alert Topic ARN: $ALERT_TOPIC_ARN"

# Step 5: Create Test User
echo ""
echo "🚀 Step 5: Creating Test User"
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

# Step 6: Final Configuration
echo ""
echo "🚀 Step 6: Final Configuration"
echo "------------------------------"

# Create environment file for local testing
cat > .env.${ENVIRONMENT} << EOF
# DcisionAI Rock Solid Architecture Configuration
ENVIRONMENT=$ENVIRONMENT
AWS_REGION=$REGION

# Gateway Configuration
USER_POOL_ID=$USER_POOL_ID
USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID
TENANTS_TABLE=$TENANTS_TABLE
API_KEYS_TABLE=$API_KEYS_TABLE
MCP_SERVER_URL=http://$MCP_LOAD_BALANCER_DNS

# Gateway URL
GATEWAY_URL=$GATEWAY_URL

# Test User
TEST_USERNAME=test@dcisionai.com
TEST_PASSWORD=TestPass123!
EOF

echo "✅ Environment configuration saved to .env.${ENVIRONMENT}"

# Step 7: Validation
echo ""
echo "🚀 Step 7: Validating Deployment"
echo "--------------------------------"

# Test gateway health
echo "Testing gateway health..."
curl -f $GATEWAY_URL/health || {
    echo "❌ Gateway health check failed"
    exit 1
}

echo "✅ Gateway health check passed"

# Final Summary
echo ""
echo "🎉 DcisionAI Rock Solid Architecture Deployed Successfully!"
echo "=========================================================="
echo ""
echo "📋 Deployment Summary:"
echo "   Environment: $ENVIRONMENT"
echo "   Region: $REGION"
echo "   Gateway URL: $GATEWAY_URL"
echo "   MCP Server: http://$MCP_LOAD_BALANCER_DNS"
echo ""
echo "🔐 Authentication:"
echo "   User Pool ID: $USER_POOL_ID"
echo "   Client ID: $USER_POOL_CLIENT_ID"
echo "   Test User: test@dcisionai.com"
echo ""
echo "📊 Monitoring:"
echo "   CloudWatch Dashboard: DcisionAI-RockSolid-${ENVIRONMENT}"
echo "   Alert Topic: $ALERT_TOPIC_ARN"
echo ""
echo "🚀 Next Steps:"
echo "   1. Test the gateway with: curl $GATEWAY_URL/health"
echo "   2. Get authentication token for test user"
echo "   3. Test MCP protocol through gateway"
echo "   4. Add remaining manufacturing tools"
echo ""
echo "✅ Rock solid architecture is ready for production!"
