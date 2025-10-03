#!/bin/bash

# DcisionAI Manufacturing Optimizer - AWS Deployment Script
# =======================================================

set -e

# Configuration
STACK_NAME="dcisionai-manufacturing"
REGION="us-east-1"
ENVIRONMENT="prod"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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
    
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Please install AWS CLI."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure'."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Get AWS account ID
get_account_id() {
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    log_info "AWS Account ID: $AWS_ACCOUNT_ID"
}

# Create ECR repository
create_ecr_repository() {
    log_info "Creating ECR repository..."
    
    # Check if repository exists
    if aws ecr describe-repositories --repository-names "$STACK_NAME-dcisionai" --region "$REGION" &> /dev/null; then
        log_info "ECR repository already exists"
    else
        aws ecr create-repository --repository-name "$STACK_NAME-dcisionai" --region "$REGION"
        log_success "ECR repository created"
    fi
}

# Login to ECR
login_ecr() {
    log_info "Logging in to ECR..."
    aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
    log_success "ECR login successful"
}

# Build and push backend image
build_backend() {
    log_info "Building backend Docker image..."
    
    cd backend
    docker build -t "$STACK_NAME-backend" .
    docker tag "$STACK_NAME-backend:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$STACK_NAME-dcisionai:backend-latest"
    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$STACK_NAME-dcisionai:backend-latest"
    cd ..
    
    log_success "Backend image built and pushed"
}

# Build and push frontend image
build_frontend() {
    log_info "Building frontend Docker image..."
    
    cd frontend
    docker build -f Dockerfile.simple -t "$STACK_NAME-frontend" .
    docker tag "$STACK_NAME-frontend:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$STACK_NAME-dcisionai:frontend-latest"
    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$STACK_NAME-dcisionai:frontend-latest"
    cd ..
    
    log_success "Frontend image built and pushed"
}

# Deploy CloudFormation stack
deploy_infrastructure() {
    log_info "Deploying CloudFormation stack..."
    
    aws cloudformation deploy \
        --template-file infrastructure/cloudformation-template.yaml \
        --stack-name "$STACK_NAME" \
        --parameter-overrides \
            Environment="$ENVIRONMENT" \
        --capabilities CAPABILITY_IAM \
        --region "$REGION"
    
    log_success "Infrastructure deployed"
}

# Get deployment outputs
get_outputs() {
    log_info "Getting deployment outputs..."
    
    APPLICATION_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
        --output text)
    
    BACKEND_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`BackendURL`].OutputValue' \
        --output text)
    
    log_success "Deployment completed!"
    echo ""
    echo "🎉 DcisionAI Manufacturing Optimizer is now live!"
    echo ""
    echo "📱 Application URL: $APPLICATION_URL"
    echo "🔧 Backend API URL: $BACKEND_URL"
    echo ""
    echo "🚀 You can now access the application at: $APPLICATION_URL"
}

# Main deployment function
main() {
    echo "🚀 Starting DcisionAI Manufacturing Optimizer AWS Deployment"
    echo "=============================================================="
    echo ""
    
    check_prerequisites
    get_account_id
    create_ecr_repository
    login_ecr
    build_backend
    build_frontend
    deploy_infrastructure
    get_outputs
    
    echo ""
    echo "✅ Deployment completed successfully!"
    echo "🌐 Your application is now running on AWS!"
}

# Run main function
main "$@"
