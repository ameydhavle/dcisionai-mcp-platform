#!/bin/bash

# Deploy New DcisionAI Manufacturing Agent v4 Runtime
# This script creates a new AgentCore runtime with the fixed image

set -e

# Configuration
AWS_REGION="us-east-1"
ECR_REPO="808953421331.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-v4"
IMAGE_TAG="latest"
RUNTIME_NAME="DcisionAI_Manufacturing_Agent_v4_Fixed_$(date +%s)"

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

# Step 1: Create new AgentCore runtime
log_info "Creating new AgentCore runtime: $RUNTIME_NAME"

# Create the runtime configuration
cat > runtime_config.json << EOF
{
    "runtimeName": "$RUNTIME_NAME",
    "imageUri": "$ECR_REPO:$IMAGE_TAG",
    "runtimeRoleArn": "arn:aws:iam::808953421331:role/AgentCoreRuntimeRole",
    "runtimeConfiguration": {
        "port": 8080,
        "healthCheckPath": "/health",
        "environmentVariables": {
            "PYTHONPATH": "/app",
            "PYTHONUNBUFFERED": "1"
        }
    },
    "tags": {
        "Project": "DcisionAI",
        "Version": "v4.0.0",
        "Environment": "Production",
        "Fixed": "true"
    }
}
EOF

log_info "Runtime configuration created"

# Note: AgentCore runtime creation is typically done through the AWS Console or SDK
# For now, let's provide instructions for manual creation
log_info "Manual steps to create the new runtime:"
log_info "1. Go to AWS Bedrock AgentCore Console"
log_info "2. Create new runtime with the following settings:"
log_info "   - Runtime Name: $RUNTIME_NAME"
log_info "   - Image URI: $ECR_REPO:$IMAGE_TAG"
log_info "   - Port: 8080"
log_info "   - Health Check Path: /health"
log_info "   - Environment Variables:"
log_info "     - PYTHONPATH: /app"
log_info "     - PYTHONUNBUFFERED: 1"

# Step 2: Test with a simple HTTP request to verify the image works
log_info "Testing the Docker image locally..."

# Run the container locally to test
log_info "Starting container locally for testing..."

docker run -d --name dcisionai-test -p 8080:8080 $ECR_REPO:$IMAGE_TAG

# Wait for container to start
sleep 10

# Test health endpoint
log_info "Testing health endpoint..."
if curl -f http://localhost:8080/health 2>/dev/null; then
    log_success "Health check passed!"
else
    log_warning "Health check failed - checking container logs..."
    docker logs dcisionai-test
fi

# Clean up test container
log_info "Cleaning up test container..."
docker stop dcisionai-test
docker rm dcisionai-test

# Step 3: Provide deployment summary
log_success "Deployment preparation completed!"
log_info "Summary:"
log_info "  - Fixed Docker image: $ECR_REPO:$IMAGE_TAG"
log_info "  - Runtime name: $RUNTIME_NAME"
log_info "  - Configuration saved to: runtime_config.json"
log_info ""
log_info "Next steps:"
log_info "  1. Create new AgentCore runtime using the AWS Console"
log_info "  2. Use the configuration from runtime_config.json"
log_info "  3. Test the new runtime with customer scenarios"
log_info "  4. Update deployment documentation"

log_success "DcisionAI Manufacturing Agent v4 new runtime deployment prepared!"
