#!/bin/bash

# DcisionAI MCP Server Deployment to AgentCore
# This script deploys the MCP server to AWS AgentCore infrastructure

set -e

# Configuration
ECR_REPOSITORY="dcisionai-mcp-server"
AWS_REGION="us-east-1"
STACK_NAME="DcisionAI-MCP-Server"
ENVIRONMENT=${1:-staging}

echo "🚀 Deploying DcisionAI MCP Server to AgentCore ($ENVIRONMENT)"
echo "=================================================="

# Check AWS CLI and Docker
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

# Create ECR repository if it doesn't exist
echo "📦 Setting up ECR repository..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>/dev/null || {
    echo "Creating ECR repository: $ECR_REPOSITORY"
    aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION
}

# Get ECR login token
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build Docker image
echo "🏗️ Building MCP server Docker image..."
docker build -f Dockerfile.mcp -t $ECR_REPOSITORY:$ENVIRONMENT .

# Tag and push to ECR
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY"
docker tag $ECR_REPOSITORY:$ENVIRONMENT $ECR_URI:$ENVIRONMENT

echo "📤 Pushing image to ECR..."
docker push $ECR_URI:$ENVIRONMENT

# Deploy CloudFormation stack
echo "☁️ Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file cloudformation/mcp-server-infrastructure.yaml \
    --stack-name $STACK_NAME-$ENVIRONMENT \
    --parameter-overrides \
        Environment=$ENVIRONMENT \
        ECRImageUri=$ECR_URI:$ENVIRONMENT \
    --capabilities CAPABILITY_IAM \
    --region $AWS_REGION

# Get stack outputs
echo "📊 Getting deployment outputs..."
STACK_OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME-$ENVIRONMENT \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs' \
    --output json)

# Extract important values
TASK_DEFINITION_ARN=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="TaskDefinitionArn").OutputValue')
CLUSTER_NAME=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="ClusterName").OutputValue')
SERVICE_NAME=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="ServiceName").OutputValue')

echo "✅ Deployment complete!"
echo "📋 Deployment Details:"
echo "   Environment: $ENVIRONMENT"
echo "   ECR Image: $ECR_URI:$ENVIRONMENT"
echo "   Cluster: $CLUSTER_NAME"
echo "   Service: $SERVICE_NAME"
echo "   Task Definition: $TASK_DEFINITION_ARN"

# Wait for service to be stable
echo "⏳ Waiting for service to be stable..."
aws ecs wait services-stable \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION

echo "🎉 MCP Server successfully deployed to AgentCore!"
echo "🔗 Service URL: https://$SERVICE_NAME.$CLUSTER_NAME.amazonaws.com"
