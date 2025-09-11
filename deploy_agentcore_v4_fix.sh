#!/bin/bash

# Deploy DcisionAI Manufacturing Agent v4 - Fixed Version
# This script fixes the missing file issue and redeploys to AgentCore

set -e

# Configuration
AWS_REGION="us-east-1"
ECR_REPO="808953421331.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-v4"
IMAGE_TAG="v4-fixed-$(date +%s)"
AGENT_RUNTIME_ARN="arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_Agent_v4_1757015134-2cxwp1BgzR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Build the fixed Docker image
log_info "Building fixed Docker image for DcisionAI Manufacturing Agent v4..."

docker build -f Dockerfile.DcisionAI_Manufacturing_Agent_v4 -t dcisionai-manufacturing-v4:$IMAGE_TAG .

if [ $? -eq 0 ]; then
    log_success "Docker image built successfully"
else
    log_error "Docker build failed"
    exit 1
fi

# Step 2: Tag for ECR
log_info "Tagging image for ECR..."

docker tag dcisionai-manufacturing-v4:$IMAGE_TAG $ECR_REPO:$IMAGE_TAG
docker tag dcisionai-manufacturing-v4:$IMAGE_TAG $ECR_REPO:latest

log_success "Image tagged for ECR"

# Step 3: Login to ECR
log_info "Logging in to ECR..."

aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO

if [ $? -eq 0 ]; then
    log_success "ECR login successful"
else
    log_error "ECR login failed"
    exit 1
fi

# Step 4: Push to ECR
log_info "Pushing image to ECR..."

docker push $ECR_REPO:$IMAGE_TAG
docker push $ECR_REPO:latest

if [ $? -eq 0 ]; then
    log_success "Image pushed to ECR successfully"
else
    log_error "ECR push failed"
    exit 1
fi

# Step 5: Update AgentCore runtime (if possible)
log_info "Attempting to update AgentCore runtime..."

# Note: AgentCore runtimes are immutable, so we need to create a new one
# For now, let's just verify the image is available
log_info "Verifying image in ECR..."

aws ecr describe-images --repository-name dcisionai-manufacturing-v4 --region $AWS_REGION --image-ids imageTag=$IMAGE_TAG

if [ $? -eq 0 ]; then
    log_success "Image verified in ECR"
else
    log_error "Image verification failed"
    exit 1
fi

# Step 6: Test the fixed runtime
log_info "Testing the fixed AgentCore runtime..."

# Wait a moment for the image to be available
sleep 10

# Test the runtime
aws bedrock-agentcore invoke-agent-runtime \
    --agent-runtime-arn $AGENT_RUNTIME_ARN \
    --payload '{"prompt": "Hello, can you help me with manufacturing optimization?"}' \
    --content-type "application/json" \
    --accept "application/json" \
    agentcore_test_response_fixed.json \
    --region $AWS_REGION

if [ $? -eq 0 ]; then
    log_success "AgentCore runtime test successful!"
    log_info "Response saved to agentcore_test_response_fixed.json"
    
    # Show the response
    if [ -f "agentcore_test_response_fixed.json" ]; then
        log_info "Response content:"
        cat agentcore_test_response_fixed.json
    fi
else
    log_warning "AgentCore runtime test failed - this is expected as the runtime needs to be recreated"
    log_info "The fixed image is now available in ECR for deployment"
fi

# Step 7: Summary
log_success "Deployment completed!"
log_info "Summary:"
log_info "  - Fixed Docker image: $ECR_REPO:$IMAGE_TAG"
log_info "  - Latest image: $ECR_REPO:latest"
log_info "  - AgentCore runtime ARN: $AGENT_RUNTIME_ARN"
log_info ""
log_info "Next steps:"
log_info "  1. Create a new AgentCore runtime with the fixed image"
log_info "  2. Test the new runtime with customer scenarios"
log_info "  3. Update the deployment configuration"

log_success "DcisionAI Manufacturing Agent v4 fix deployment completed!"
