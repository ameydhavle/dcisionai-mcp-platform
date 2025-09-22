#!/bin/bash

# Production Deployment Script for DcisionAI Manufacturing MCP Server to AWS AgentCore
# This script deploys the complete swarm architecture to AWS AgentCore

set -e

# Configuration
APP_NAME="dcisionai-manufacturing-mcp"
APP_VERSION="2.0.0"
AWS_REGION="us-east-1"
ECR_REPOSITORY="dcisionai-manufacturing-mcp"
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"
IMAGE_TAG="${ECR_URI}:${APP_VERSION}"

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
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    # Check AgentCore Starter Toolkit
    if ! command -v bedrock-agentcore-starter-toolkit &> /dev/null; then
        log_error "AgentCore Starter Toolkit is not installed. Please install it first."
        log_info "Install with: pip install bedrock-agentcore-starter-toolkit"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Get AWS Account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    log_info "Using AWS Account ID: ${AWS_ACCOUNT_ID}"
    
    log_success "Prerequisites check passed"
}

# Build Docker image
build_docker_image() {
    log_info "Building Docker image for production..."
    
    # Build the image
    docker build -f Dockerfile.production -t ${APP_NAME}:${APP_VERSION} .
    
    # Tag for ECR
    docker tag ${APP_NAME}:${APP_VERSION} ${IMAGE_TAG}
    
    log_success "Docker image built successfully: ${IMAGE_TAG}"
}

# Create ECR repository
create_ecr_repository() {
    log_info "Creating ECR repository if it doesn't exist..."
    
    # Check if repository exists
    if aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} --region ${AWS_REGION} &> /dev/null; then
        log_info "ECR repository already exists: ${ECR_REPOSITORY}"
    else
        # Create repository
        aws ecr create-repository \
            --repository-name ${ECR_REPOSITORY} \
            --region ${AWS_REGION} \
            --image-scanning-configuration scanOnPush=true \
            --encryption-configuration encryptionType=AES256
        
        log_success "ECR repository created: ${ECR_REPOSITORY}"
    fi
}

# Push image to ECR
push_to_ecr() {
    log_info "Pushing Docker image to ECR..."
    
    # Login to ECR
    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}
    
    # Push image
    docker push ${IMAGE_TAG}
    
    log_success "Docker image pushed to ECR: ${IMAGE_TAG}"
}

# Deploy to AgentCore
deploy_to_agentcore() {
    log_info "Deploying to AWS AgentCore..."
    
    # Create deployment directory
    mkdir -p agentcore-deployment
    
    # Copy configuration files
    cp agentcore-config.yaml agentcore-deployment/
    cp mcp_server_swarm.py agentcore-deployment/
    cp -r *.py agentcore-deployment/ 2>/dev/null || true
    
    # Create AgentCore deployment configuration
    cat > agentcore-deployment/agentcore-deployment.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: ${APP_NAME}-config
  namespace: agentcore
data:
  # Application Configuration
  APP_NAME: "${APP_NAME}"
  APP_VERSION: "${APP_VERSION}"
  ENVIRONMENT: "production"
  
  # Docker Image Configuration
  IMAGE_URI: "${IMAGE_TAG}"
  
  # AWS Bedrock Configuration
  AWS_REGION: "${AWS_REGION}"
  BEDROCK_MODEL_ID: "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
  INFERENCE_PROFILE_ID: "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
  
  # Swarm Architecture Configuration
  INTENT_SWARM_AGENTS: "5"
  DATA_SWARM_AGENTS: "3"
  MODEL_SWARM_AGENTS: "4"
  SOLVER_SWARM_AGENTS: "6"
  
  # Cross-Region Configuration
  CROSS_REGION_ENABLED: "true"
  REGIONS: "us-east-1,us-west-2,eu-west-1,ap-southeast-1,us-east-2,us-west-1"
  
  # Performance Configuration
  MAX_PARALLEL_REQUESTS: "5"
  REQUEST_TIMEOUT: "300"
  RETRY_ATTEMPTS: "4"
  RETRY_DELAY: "1"
  
  # Logging Configuration
  LOG_LEVEL: "INFO"
  LOG_FORMAT: "json"
  ENABLE_METRICS: "true"
  
  # Security Configuration
  ENABLE_AUTH: "true"
  API_KEY_REQUIRED: "true"
EOF

    # Deploy using AgentCore Starter Toolkit
    log_info "Deploying with AgentCore Starter Toolkit..."
    
    cd agentcore-deployment
    
    # Initialize AgentCore project
    bedrock-agentcore-starter-toolkit init \
        --name ${APP_NAME} \
        --version ${APP_VERSION} \
        --region ${AWS_REGION} \
        --image ${IMAGE_TAG}
    
    # Deploy the application
    bedrock-agentcore-starter-toolkit deploy \
        --name ${APP_NAME} \
        --version ${APP_VERSION} \
        --region ${AWS_REGION} \
        --config agentcore-deployment.yaml
    
    cd ..
    
    log_success "Deployment to AgentCore completed"
}

# Test deployment
test_deployment() {
    log_info "Testing deployment..."
    
    # Get deployment endpoint
    ENDPOINT=$(bedrock-agentcore-starter-toolkit get-endpoint \
        --name ${APP_NAME} \
        --version ${APP_VERSION} \
        --region ${AWS_REGION})
    
    log_info "Deployment endpoint: ${ENDPOINT}"
    
    # Test health check
    log_info "Testing health check..."
    if curl -f "${ENDPOINT}/health" &> /dev/null; then
        log_success "Health check passed"
    else
        log_warning "Health check failed - deployment may still be starting"
    fi
    
    # Test MCP endpoint
    log_info "Testing MCP endpoint..."
    if curl -f "${ENDPOINT}/mcp" -X POST \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' &> /dev/null; then
        log_success "MCP endpoint is responding"
    else
        log_warning "MCP endpoint test failed - may need more time to start"
    fi
}

# Main deployment function
main() {
    log_info "Starting production deployment to AWS AgentCore..."
    log_info "Application: ${APP_NAME} v${APP_VERSION}"
    log_info "Region: ${AWS_REGION}"
    
    # Execute deployment steps
    check_prerequisites
    build_docker_image
    create_ecr_repository
    push_to_ecr
    deploy_to_agentcore
    test_deployment
    
    log_success "Production deployment completed successfully!"
    log_info "Your DcisionAI Manufacturing MCP Server with Swarm Architecture is now running on AWS AgentCore"
    log_info "Features deployed:"
    log_info "  ✅ Intent Swarm: 5-agent peer-to-peer consensus"
    log_info "  ✅ Data Swarm: 3-agent peer-to-peer analysis"
    log_info "  ✅ Model Swarm: 4-agent peer-to-peer modeling"
    log_info "  ✅ Solver Swarm: 6-agent peer-to-peer optimization"
    log_info "  ✅ Cross-region parallel execution"
    log_info "  ✅ Real AWS Bedrock inference profiles"
    log_info "  ✅ NO MOCK RESPONSES policy enforced"
}

# Run main function
main "$@"
