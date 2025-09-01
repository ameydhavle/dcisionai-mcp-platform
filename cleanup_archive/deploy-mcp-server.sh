#!/bin/bash

# DcisionAI MCP Server Deployment to ECS
# This script deploys the MCP server to ECS Fargate

set -e

# Configuration
ENVIRONMENT=${1:-staging}
REGION=${2:-us-east-1}
STACK_NAME="DcisionAI-MCP-${ENVIRONMENT}"

echo "🚀 Deploying DcisionAI MCP Server to ECS"
echo "========================================="
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

# Step 1: Build and Push MCP Server Docker Image
echo ""
echo "🚀 Step 1: Building and Pushing MCP Server Docker Image"
echo "------------------------------------------------------"

# Create ECR repository for MCP server
ECR_REPOSITORY="dcisionai-mcp-server"
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $REGION 2>/dev/null || {
    echo "Creating ECR repository: $ECR_REPOSITORY"
    aws ecr create-repository --repository-name $ECR_REPOSITORY --region $REGION
}

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build MCP server Docker image
echo "🏗️ Building MCP server Docker image..."
docker build -f Dockerfile.mcp -t $ECR_REPOSITORY:$ENVIRONMENT .

ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPOSITORY"
docker tag $ECR_REPOSITORY:$ENVIRONMENT $ECR_URI:$ENVIRONMENT

# Push MCP server image to ECR
echo "📤 Pushing MCP server image to ECR..."
docker push $ECR_URI:$ENVIRONMENT

echo "✅ MCP server image pushed to ECR: $ECR_URI:$ENVIRONMENT"

# Step 2: Deploy MCP Server Infrastructure
echo ""
echo "🚀 Step 2: Deploying MCP Server Infrastructure"
echo "----------------------------------------------"

# Deploy MCP server infrastructure
aws cloudformation deploy \
    --template-file cloudformation/mcp-server-infrastructure.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        Environment=$ENVIRONMENT \
        ECRImageUri=$ECR_URI:$ENVIRONMENT \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --region $REGION

# Get MCP server outputs
echo "📊 Getting MCP server outputs..."
MCP_OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs' \
    --output json)

MCP_LOAD_BALANCER_DNS=$(echo $MCP_OUTPUTS | jq -r '.[] | select(.OutputKey=="LoadBalancerDNS").OutputValue')
MCP_SERVICE_URL=$(echo $MCP_OUTPUTS | jq -r '.[] | select(.OutputKey=="ServiceURL").OutputValue')
CLUSTER_NAME=$(echo $MCP_OUTPUTS | jq -r '.[] | select(.OutputKey=="ClusterName").OutputValue')
SERVICE_NAME=$(echo $MCP_OUTPUTS | jq -r '.[] | select(.OutputKey=="ServiceName").OutputValue')

echo "✅ MCP server infrastructure deployed"
echo "   Load Balancer DNS: $MCP_LOAD_BALANCER_DNS"
echo "   Service URL: $MCP_SERVICE_URL"
echo "   Cluster Name: $CLUSTER_NAME"
echo "   Service Name: $SERVICE_NAME"

# Step 3: Wait for Service to be Ready
echo ""
echo "🚀 Step 3: Waiting for MCP Server to be Ready"
echo "---------------------------------------------"

echo "⏳ Waiting for ECS service to be stable..."
aws ecs wait services-stable \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $REGION

echo "✅ MCP server service is stable"

# Step 4: Test MCP Server Health
echo ""
echo "🚀 Step 4: Testing MCP Server Health"
echo "-----------------------------------"

# Wait a bit for the service to be fully ready
sleep 30

# Test health endpoint
echo "🏥 Testing MCP server health..."
HEALTH_RESPONSE=$(curl -s -f $MCP_SERVICE_URL/health 2>/dev/null || echo "{}")

if echo $HEALTH_RESPONSE | jq -e '.status' > /dev/null; then
    echo "✅ MCP server health check passed"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo "❌ MCP server health check failed"
    echo "   Response: $HEALTH_RESPONSE"
fi

# Step 5: Update Environment Configuration
echo ""
echo "🚀 Step 5: Updating Environment Configuration"
echo "--------------------------------------------"

# Update environment file with MCP server URL
if [ -f ".env.${ENVIRONMENT}" ]; then
    # Backup existing file
    cp ".env.${ENVIRONMENT}" ".env.${ENVIRONMENT}.backup"
    
    # Update MCP server URL
    sed -i.bak "s|MCP_SERVER_URL=.*|MCP_SERVER_URL=$MCP_SERVICE_URL|" ".env.${ENVIRONMENT}"
    
    echo "✅ Environment configuration updated"
    echo "   MCP Server URL: $MCP_SERVICE_URL"
else
    echo "⚠️ Environment file not found, creating new one..."
    cat > ".env.${ENVIRONMENT}" << EOF
# DcisionAI MCP Server Configuration
ENVIRONMENT=$ENVIRONMENT
AWS_REGION=$REGION

# MCP Server Configuration
MCP_SERVER_URL=$MCP_SERVICE_URL
MCP_LOAD_BALANCER_DNS=$MCP_LOAD_BALANCER_DNS

# ECS Configuration
CLUSTER_NAME=$CLUSTER_NAME
SERVICE_NAME=$SERVICE_NAME

# ECR Configuration
ECR_URI=$ECR_URI
EOF
fi

# Step 6: Final Validation
echo ""
echo "🚀 Step 6: Final Validation"
echo "---------------------------"

# Check ECS service status
echo "📊 Checking ECS service status..."
SERVICE_STATUS=$(aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $REGION \
    --query 'services[0].status' \
    --output text)

RUNNING_TASKS=$(aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $REGION \
    --query 'services[0].runningCount' \
    --output text)

DESIRED_TASKS=$(aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $REGION \
    --query 'services[0].desiredCount' \
    --output text)

echo "✅ ECS Service Status:"
echo "   Status: $SERVICE_STATUS"
echo "   Running Tasks: $RUNNING_TASKS/$DESIRED_TASKS"

# Final Summary
echo ""
echo "🎉 DcisionAI MCP Server Deployed Successfully!"
echo "=============================================="
echo ""
echo "📋 Deployment Summary:"
echo "   Environment: $ENVIRONMENT"
echo "   Region: $REGION"
echo "   Stack Name: $STACK_NAME"
echo ""
echo "🔗 MCP Server URLs:"
echo "   Service URL: $MCP_SERVICE_URL"
echo "   Load Balancer DNS: $MCP_LOAD_BALANCER_DNS"
echo ""
echo "🐳 Docker Image:"
echo "   ECR URI: $ECR_URI:$ENVIRONMENT"
echo ""
echo "📊 ECS Service:"
echo "   Cluster: $CLUSTER_NAME"
echo "   Service: $SERVICE_NAME"
echo "   Status: $SERVICE_STATUS"
echo "   Tasks: $RUNNING_TASKS/$DESIRED_TASKS"
echo ""
echo "🚀 Next Steps:"
echo "   1. Test MCP protocol with the deployed server"
echo "   2. Deploy gateway service to complete architecture"
echo "   3. Test complete end-to-end flow"
echo ""
echo "✅ MCP server is ready for testing!"
