#!/bin/bash

# DcisionAI Simple MCP Server Deployment to ECS
# This script deploys the MCP server to ECS Fargate without load balancer

set -e

# Configuration
ENVIRONMENT=${1:-staging}
REGION=${2:-us-east-1}
STACK_NAME="DcisionAI-MCP-Simple-${ENVIRONMENT}"

echo "🚀 Deploying DcisionAI Simple MCP Server to ECS"
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

# Build MCP server Docker image for AMD64 platform
echo "🏗️ Building MCP server Docker image for AMD64 platform..."
docker buildx build --platform linux/amd64 -f Dockerfile.mcp -t $ECR_REPOSITORY:$ENVIRONMENT --load .

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
DEPLOYMENT_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
aws cloudformation deploy \
    --template-file cloudformation/mcp-server-simple.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        Environment=$ENVIRONMENT \
        ECRImageUri=$ECR_URI:$ENVIRONMENT \
        DeploymentTimestamp=$DEPLOYMENT_TIMESTAMP \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --region $REGION

# Get MCP server outputs
echo "📊 Getting MCP server outputs..."
MCP_OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs' \
    --output json)

CLUSTER_NAME=$(echo $MCP_OUTPUTS | jq -r '.[] | select(.OutputKey=="ClusterName").OutputValue')
SERVICE_NAME=$(echo $MCP_OUTPUTS | jq -r '.[] | select(.OutputKey=="ServiceName").OutputValue')

echo "✅ MCP server infrastructure deployed"
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

# Step 4: Get Task Details
echo ""
echo "🚀 Step 4: Getting Task Details"
echo "-------------------------------"

# Get task details
TASK_ARN=$(aws ecs list-tasks \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --region $REGION \
    --query 'taskArns[0]' \
    --output text)

if [ "$TASK_ARN" != "None" ] && [ -n "$TASK_ARN" ]; then
    TASK_DETAILS=$(aws ecs describe-tasks \
        --cluster $CLUSTER_NAME \
        --tasks $TASK_ARN \
        --region $REGION \
        --query 'tasks[0]' \
        --output json)
    
    ENI_ID=$(echo $TASK_DETAILS | jq -r '.attachments[0].details[] | select(.name=="networkInterfaceId").value')
    PUBLIC_IP=$(aws ec2 describe-network-interfaces \
        --network-interface-ids $ENI_ID \
        --region $REGION \
        --query 'NetworkInterfaces[0].Association.PublicIp' \
        --output text)
    
    echo "✅ Task Details:"
    echo "   Task ARN: $TASK_ARN"
    echo "   Public IP: $PUBLIC_IP"
    echo "   MCP Server URL: http://$PUBLIC_IP:8080"
    
    # Update environment file
    if [ -f ".env.${ENVIRONMENT}" ]; then
        # Backup existing file
        cp ".env.${ENVIRONMENT}" ".env.${ENVIRONMENT}.backup"
        
        # Update MCP server URL
        sed -i.bak "s|MCP_SERVER_URL=.*|MCP_SERVER_URL=http://$PUBLIC_IP:8080|" ".env.${ENVIRONMENT}"
        
        echo "✅ Environment configuration updated"
        echo "   MCP Server URL: http://$PUBLIC_IP:8080"
    else
        echo "⚠️ Environment file not found, creating new one..."
        cat > ".env.${ENVIRONMENT}" << EOF
# DcisionAI MCP Server Configuration
ENVIRONMENT=$ENVIRONMENT
AWS_REGION=$REGION

# MCP Server Configuration
MCP_SERVER_URL=http://$PUBLIC_IP:8080

# ECS Configuration
CLUSTER_NAME=$CLUSTER_NAME
SERVICE_NAME=$SERVICE_NAME

# ECR Configuration
ECR_URI=$ECR_URI
EOF
    fi
else
    echo "❌ No tasks found for the service"
fi

# Step 5: Final Validation
echo ""
echo "🚀 Step 5: Final Validation"
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
echo "🎉 DcisionAI Simple MCP Server Deployed Successfully!"
echo "===================================================="
echo ""
echo "📋 Deployment Summary:"
echo "   Environment: $ENVIRONMENT"
echo "   Region: $REGION"
echo "   Stack Name: $STACK_NAME"
echo ""
echo "🔗 MCP Server URLs:"
if [ -n "$PUBLIC_IP" ]; then
    echo "   MCP Server URL: http://$PUBLIC_IP:8080"
    echo "   Health Check: http://$PUBLIC_IP:8080/health"
    echo "   Root Endpoint: http://$PUBLIC_IP:8080/"
fi
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
echo "   2. Test the complete end-to-end flow"
echo "   3. Add load balancer when needed"
echo ""
echo "✅ MCP server is ready for testing!"
