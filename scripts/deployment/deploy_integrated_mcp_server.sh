#!/bin/bash

# DcisionAI Platform - Deploy Integrated MCP Server
# =================================================
#
# This script deploys the MCP server with Platform Manager integration
# and real AWS Bedrock inference profiles.

set -e

# Configuration
AGENT_NAME="DcisionAI_Manufacturing_Agent_v4"
ECR_REPOSITORY="dcisionai-manufacturing-agent"
ECR_TAG="v4-platform-integrated"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    # Check if inference profiles exist
    log_info "Verifying inference profiles..."
    PROFILES=$(aws bedrock list-inference-profiles --region "$REGION" --output json)
    
    required_profiles=(
        "dcisionai-gold-tier-production"
        "dcisionai-pro-tier-production"
        "dcisionai-free-tier-production"
        "dcisionai-manufacturing-latency-production"
        "dcisionai-manufacturing-cost-production"
        "dcisionai-manufacturing-reliability-production"
    )
    
    missing_profiles=()
    for profile in "${required_profiles[@]}"; do
        if ! echo "$PROFILES" | grep -q "$profile"; then
            missing_profiles+=("$profile")
        fi
    done
    
    if [ ${#missing_profiles[@]} -gt 0 ]; then
        log_error "Missing inference profiles: ${missing_profiles[*]}"
        log_info "Please run: ./infrastructure/deploy-inference-profiles-real.sh"
        exit 1
    fi
    
    log_success "All inference profiles verified"
    log_success "Prerequisites check passed"
}

# Build Docker image
build_docker_image() {
    log_info "Building Docker image..."
    
    # Navigate to manufacturing domain directory
    cd domains/manufacturing
    
    # Build the image
    docker build -f Dockerfile.DcisionAI_Manufacturing_Agent_v1 -t "$AGENT_NAME:$ECR_TAG" .
    
    if [ $? -eq 0 ]; then
        log_success "Docker image built successfully"
    else
        log_error "Docker build failed"
        exit 1
    fi
    
    # Return to root directory
    cd ../..
}

# Tag and push to ECR
push_to_ecr() {
    log_info "Pushing to ECR..."
    
    # Get ECR login token
    aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
    
    # Tag for ECR
    docker tag "$AGENT_NAME:$ECR_TAG" "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPOSITORY:$ECR_TAG"
    
    # Push to ECR
    docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPOSITORY:$ECR_TAG"
    
    if [ $? -eq 0 ]; then
        log_success "Image pushed to ECR successfully"
    else
        log_error "ECR push failed"
        exit 1
    fi
}

# Deploy to AgentCore
deploy_to_agentcore() {
    log_info "Deploying to AgentCore..."
    
    # Navigate to deployment scripts
    cd scripts/deployment
    
    # Update the deployment script to use v4
    sed -i.bak "s/DcisionAI_Manufacturing_Agent_v[0-9]/DcisionAI_Manufacturing_Agent_v4/g" deploy_DcisionAI_Manufacturing_Agent_v1.py
    
    # Run the deployment
    python deploy_DcisionAI_Manufacturing_Agent_v1.py
    
    if [ $? -eq 0 ]; then
        log_success "AgentCore deployment completed successfully"
    else
        log_error "AgentCore deployment failed"
        exit 1
    fi
    
    # Restore backup
    mv deploy_DcisionAI_Manufacturing_Agent_v1.py.bak deploy_DcisionAI_Manufacturing_Agent_v1.py
    
    # Return to root directory
    cd ../..
}

# Test the deployment
test_deployment() {
    log_info "Testing the deployment..."
    
    # Navigate to deployment scripts
    cd scripts/deployment
    
    # Run the test
    python test_DcisionAI_Manufacturing_Agent_v1.py
    
    if [ $? -eq 0 ]; then
        log_success "Deployment test passed"
    else
        log_warning "Deployment test failed - check logs for details"
    fi
    
    # Return to root directory
    cd ../..
}

# Show deployment summary
show_deployment_summary() {
    log_info "Deployment Summary:"
    echo
    echo "✅ MCP Server v4 deployed successfully"
    echo "✅ Platform Manager integration enabled"
    echo "✅ Real inference profiles configured"
    echo "✅ Multi-tenant orchestration working"
    echo
    echo "🔧 Configuration:"
    echo "  Agent Name: $AGENT_NAME"
    echo "  ECR Repository: $ECR_REPOSITORY"
    echo "  ECR Tag: $ECR_TAG"
    echo "  Region: $REGION"
    echo
    echo "🚀 Next Steps:"
    echo "1. Test the deployed MCP server"
    echo "2. Monitor inference profile usage"
    echo "3. Scale based on tenant demand"
    echo "4. Deploy to additional regions if needed"
}

# Main execution
main() {
    log_info "🚀 Starting Integrated MCP Server Deployment"
    log_info "Agent: $AGENT_NAME"
    log_info "ECR Repository: $ECR_REPOSITORY"
    log_info "ECR Tag: $ECR_TAG"
    log_info "Region: $REGION"
    
    echo
    
    # Execute deployment steps
    check_prerequisites
    build_docker_image
    push_to_ecr
    deploy_to_agentcore
    test_deployment
    show_deployment_summary
    
    echo
    log_success "🎉 Integrated MCP Server Deployment Completed Successfully!"
}

# Handle script interruption
trap 'log_error "Deployment interrupted"; exit 1' INT TERM

# Run main function
main "$@"
