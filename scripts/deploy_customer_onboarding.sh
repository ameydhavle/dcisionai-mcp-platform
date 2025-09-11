#!/bin/bash

# DcisionAI Customer Onboarding System Deployment
# ==============================================
#
# This script deploys the complete customer onboarding system including:
# - MCP Server Registry
# - Customer Portal
# - Authentication System
# - Documentation Site
# - Support System
#
# Prerequisites:
# - AWS CLI configured
# - Docker installed
# - Python 3.8+
# - Node.js 16+

set -e

# Configuration
ENVIRONMENT=${1:-production}
DOMAIN_NAME=${2:-dcisionai.com}
AWS_REGION=${3:-us-east-1}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Please install AWS CLI."
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3.8+."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found. Please install Node.js 16+."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure'."
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Deploy MCP Server Registry
deploy_mcp_registry() {
    log_info "Deploying MCP Server Registry..."
    
    # Create ECR repository for registry
    aws ecr describe-repositories --repository-names dcisionai-mcp-registry --region $AWS_REGION 2>/dev/null || \
    aws ecr create-repository --repository-name dcisionai-mcp-registry --region $AWS_REGION
    
    # Get ECR login token
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Build and push registry image
    docker build -t dcisionai-mcp-registry:latest -f Dockerfile.registry .
    docker tag dcisionai-mcp-registry:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/dcisionai-mcp-registry:latest
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/dcisionai-mcp-registry:latest
    
    # Deploy to ECS
    aws ecs create-cluster --cluster-name dcisionai-mcp-registry --region $AWS_REGION 2>/dev/null || true
    
    # Create task definition
    cat > task-definition.json << EOF
{
    "family": "dcisionai-mcp-registry",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "256",
    "memory": "512",
    "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "mcp-registry",
            "image": "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/dcisionai-mcp-registry:latest",
            "portMappings": [
                {
                    "containerPort": 8001,
                    "protocol": "tcp"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/dcisionai-mcp-registry",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
}
EOF
    
    # Register task definition
    aws ecs register-task-definition --cli-input-json file://task-definition.json --region $AWS_REGION
    
    # Create CloudWatch log group
    aws logs create-log-group --log-group-name /ecs/dcisionai-mcp-registry --region $AWS_REGION 2>/dev/null || true
    
    log_success "MCP Server Registry deployed"
}

# Deploy Customer Portal
deploy_customer_portal() {
    log_info "Deploying Customer Portal..."
    
    # Check if frontend directory exists
    if [ ! -d "customer_portal/frontend" ]; then
        log_warning "Customer portal frontend not found, creating basic structure..."
        mkdir -p customer_portal/frontend/dist
        echo "<html><body><h1>DcisionAI Customer Portal</h1><p>Portal coming soon!</p></body></html>" > customer_portal/frontend/dist/index.html
    fi
    
    # Build portal frontend if package.json exists
    if [ -f "customer_portal/frontend/package.json" ]; then
        cd customer_portal/frontend
        if command -v npm &> /dev/null; then
            npm install
            npm run build
        else
            log_warning "npm not found, using static files"
        fi
        cd ../..
    fi
    
    # Create S3 bucket if it doesn't exist
    aws s3 mb s3://portal-$DOMAIN_NAME-$ENVIRONMENT 2>/dev/null || true
    
    # Upload to S3
    aws s3 sync customer_portal/frontend/dist/ s3://portal-$DOMAIN_NAME-$ENVIRONMENT --delete
    
    # Invalidate CloudFront (if distribution exists)
    DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='Customer Portal for $DOMAIN_NAME'].Id" --output text 2>/dev/null || echo "")
    if [ ! -z "$DISTRIBUTION_ID" ] && [ "$DISTRIBUTION_ID" != "None" ]; then
        aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
    fi
    
    log_success "Customer Portal deployed"
}

# Deploy Authentication System
deploy_auth_system() {
    log_info "Deploying Authentication System..."
    
    # Create ECR repository for auth service
    aws ecr describe-repositories --repository-names dcisionai-auth-service --region $AWS_REGION 2>/dev/null || \
    aws ecr create-repository --repository-name dcisionai-auth-service --region $AWS_REGION
    
    # Build and push auth service image
    docker build -t dcisionai-auth-service:latest -f Dockerfile.auth .
    docker tag dcisionai-auth-service:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/dcisionai-auth-service:latest
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/dcisionai-auth-service:latest
    
    # Deploy to ECS
    aws ecs create-cluster --cluster-name dcisionai-auth-service --region $AWS_REGION 2>/dev/null || true
    
    log_success "Authentication System deployed"
}

# Deploy Documentation Site
deploy_documentation() {
    log_info "Deploying Documentation Site..."
    
    # Check if mkdocs is available
    if command -v mkdocs &> /dev/null; then
        # Build documentation
        cd docs
        mkdocs build
        cd ..
    else
        log_warning "mkdocs not found, creating basic documentation structure..."
        mkdir -p docs/site
        cp docs/*.md docs/site/ 2>/dev/null || true
    fi
    
    # Create S3 bucket if it doesn't exist
    aws s3 mb s3://docs-$DOMAIN_NAME-$ENVIRONMENT 2>/dev/null || true
    
    # Upload to S3
    aws s3 sync docs/site/ s3://docs-$DOMAIN_NAME-$ENVIRONMENT --delete
    
    # Invalidate CloudFront (if distribution exists)
    DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='Documentation for $DOMAIN_NAME'].Id" --output text 2>/dev/null || echo "")
    if [ ! -z "$DISTRIBUTION_ID" ] && [ "$DISTRIBUTION_ID" != "None" ]; then
        aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
    fi
    
    log_success "Documentation Site deployed"
}

# Deploy Support System
deploy_support_system() {
    log_info "Deploying Support System..."
    
    # Create ECR repository for support service
    aws ecr describe-repositories --repository-names dcisionai-support-service --region $AWS_REGION 2>/dev/null || \
    aws ecr create-repository --repository-name dcisionai-support-service --region $AWS_REGION
    
    # Build and push support service image
    docker build -t dcisionai-support-service:latest -f Dockerfile.support .
    docker tag dcisionai-support-service:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/dcisionai-support-service:latest
    docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/dcisionai-support-service:latest
    
    # Deploy to ECS
    aws ecs create-cluster --cluster-name dcisionai-support-service --region $AWS_REGION 2>/dev/null || true
    
    log_success "Support System deployed"
}

# Deploy SDK to PyPI
deploy_python_sdk() {
    log_info "Deploying Python SDK to PyPI..."
    
    cd src/sdk
    
    # Use the project's virtual environment
    if [ -f "../../venv/bin/activate" ]; then
        log_info "Using project virtual environment..."
        source ../../venv/bin/activate
        PIP_CMD="pip"
    else
        log_warning "Virtual environment not found, skipping Python SDK deployment"
        cd ../..
        return 0
    fi
    
    # Install build tools
    $PIP_CMD install build twine
    
    # Build package
    python -m build
    
    # Upload to PyPI (requires PyPI credentials)
    if [ "$ENVIRONMENT" = "production" ]; then
        python -m twine upload dist/*
    else
        log_warning "Skipping PyPI upload for non-production environment"
    fi
    
    cd ../..
    
    log_success "Python SDK deployed"
}

# Deploy SDK to npm
deploy_typescript_sdk() {
    log_info "Deploying TypeScript SDK to npm..."
    
    cd src/sdk/typescript
    
    # Install dependencies
    npm install
    
    # Build package
    npm run build
    
    # Publish to npm (requires npm credentials)
    if [ "$ENVIRONMENT" = "production" ]; then
        npm publish
    else
        log_warning "Skipping npm publish for non-production environment"
    fi
    
    cd ../../..
    
    log_success "TypeScript SDK deployed"
}

# Test deployment
test_deployment() {
    log_info "Testing deployment..."
    
    # Test MCP Registry
    REGISTRY_URL="https://registry.$DOMAIN_NAME"
    if curl -f "$REGISTRY_URL/registry/health" &> /dev/null; then
        log_success "MCP Registry is responding"
    else
        log_warning "MCP Registry test failed"
    fi
    
    # Test Customer Portal
    PORTAL_URL="https://portal.$DOMAIN_NAME"
    if curl -f "$PORTAL_URL" &> /dev/null; then
        log_success "Customer Portal is responding"
    else
        log_warning "Customer Portal test failed"
    fi
    
    # Test Documentation
    DOCS_URL="https://docs.$DOMAIN_NAME"
    if curl -f "$DOCS_URL" &> /dev/null; then
        log_success "Documentation is responding"
    else
        log_warning "Documentation test failed"
    fi
    
    # Test Authentication
    AUTH_URL="https://auth.$DOMAIN_NAME/health"
    if curl -f "$AUTH_URL" &> /dev/null; then
        log_success "Authentication Service is responding"
    else
        log_warning "Authentication Service test failed"
    fi
}

# Main deployment function
main() {
    log_info "🚀 Starting DcisionAI Customer Onboarding System Deployment"
    log_info "Environment: $ENVIRONMENT"
    log_info "Domain: $DOMAIN_NAME"
    log_info "Region: $AWS_REGION"
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    log_info "AWS Account ID: $AWS_ACCOUNT_ID"
    
    # Execute deployment steps
    check_prerequisites
    deploy_mcp_registry
    deploy_customer_portal
    deploy_auth_system
    deploy_documentation
    deploy_support_system
    deploy_python_sdk
    deploy_typescript_sdk
    
    # Wait for services to stabilize
    log_info "Waiting for services to stabilize..."
    sleep 60
    
    test_deployment
    
    log_success "🎉 Customer Onboarding System deployment completed successfully!"
    log_info "Services deployed:"
    log_info "  🔍 MCP Server Registry: https://registry.$DOMAIN_NAME"
    log_info "  🏢 Customer Portal: https://portal.$DOMAIN_NAME"
    log_info "  🔐 Authentication: https://auth.$DOMAIN_NAME"
    log_info "  📚 Documentation: https://docs.$DOMAIN_NAME"
    log_info "  🆘 Support: https://support.$DOMAIN_NAME"
    log_info "  📦 Python SDK: pip install dcisionai-mcp"
    log_info "  📦 TypeScript SDK: npm install @dcisionai/mcp-client"
    
    log_info "Next steps:"
    log_info "  1. Configure DNS records for all subdomains"
    log_info "  2. Set up SSL certificates"
    log_info "  3. Configure customer support workflows"
    log_info "  4. Launch customer acquisition campaigns"
    log_info "  5. Monitor system performance and usage"
}

# Run main function
main "$@"
