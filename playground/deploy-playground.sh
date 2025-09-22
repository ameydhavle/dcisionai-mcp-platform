#!/bin/bash

# DcisionAI Manufacturing Playground Deployment Script
# ===================================================

set -e

# Configuration
STACK_NAME="DcisionAI-Playground"
REGION="us-east-1"
DOMAIN_NAME="dcisionai.com"
SUBDOMAIN="playground"
CERTIFICATE_ARN="arn:aws:acm:us-east-1:808953421331:certificate/cee8347e-40c7-48c6-8953-c723e3d1f0be"
HOSTED_ZONE_ID="Z0178448QST5UHZB6URE"

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
    
    # Check if AWS credentials are configured
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "infrastructure/playground-stack.yaml" ]; then
        log_error "Please run this script from the playground directory."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create deployment package
create_deployment_package() {
    log_info "Creating Lambda deployment package..."
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    
    # Copy Lambda function
    cp api/lambda_function.py "$TEMP_DIR/"
    
    # Install dependencies
    cd "$TEMP_DIR"
    pip install boto3 -t .
    
    # Create ZIP file
    zip -r lambda-deployment.zip .
    
    # Move back to original directory
    cd - > /dev/null
    
    # Move ZIP file to current directory
    mv "$TEMP_DIR/lambda-deployment.zip" .
    
    # Clean up
    rm -rf "$TEMP_DIR"
    
    log_success "Deployment package created"
}

# Deploy CloudFormation stack
deploy_stack() {
    log_info "Deploying CloudFormation stack..."
    
    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &> /dev/null; then
        log_info "Stack exists, updating..."
        OPERATION="update-stack"
    else
        log_info "Stack does not exist, creating..."
        OPERATION="create-stack"
    fi
    
    # Deploy the stack
    aws cloudformation $OPERATION \
        --stack-name "$STACK_NAME" \
        --template-body file://infrastructure/playground-stack.yaml \
        --parameters \
            ParameterKey=DomainName,ParameterValue="$DOMAIN_NAME" \
            ParameterKey=Subdomain,ParameterValue="$SUBDOMAIN" \
            ParameterKey=CertificateArn,ParameterValue="$CERTIFICATE_ARN" \
            ParameterKey=HostedZoneId,ParameterValue="$HOSTED_ZONE_ID" \
        --capabilities CAPABILITY_IAM \
        --region "$REGION"
    
    # Wait for stack operation to complete
    log_info "Waiting for stack operation to complete..."
    aws cloudformation wait stack-${OPERATION%-stack}-complete \
        --stack-name "$STACK_NAME" \
        --region "$REGION"
    
    log_success "Stack deployment completed"
}

# Update Lambda function
update_lambda() {
    log_info "Updating Lambda function with deployment package..."
    
    # Get Lambda function name from stack outputs
    LAMBDA_FUNCTION_NAME=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`PlaygroundLambdaArn`].OutputValue' \
        --output text | cut -d: -f7)
    
    # Update function code
    aws lambda update-function-code \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --zip-file fileb://lambda-deployment.zip \
        --region "$REGION"
    
    log_success "Lambda function updated"
}

# Upload static files to S3
upload_static_files() {
    log_info "Uploading static files to S3..."
    
    # Get S3 bucket name from stack outputs
    S3_BUCKET_NAME=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`PlaygroundBucketName`].OutputValue' \
        --output text)
    
    # Upload index.html
    aws s3 cp index.html "s3://$S3_BUCKET_NAME/" \
        --content-type "text/html" \
        --cache-control "max-age=3600" \
        --region "$REGION"
    
    # Upload any additional static files
    if [ -d "static" ]; then
        aws s3 sync static/ "s3://$S3_BUCKET_NAME/static/" \
            --cache-control "max-age=86400" \
            --region "$REGION"
    fi
    
    log_success "Static files uploaded"
}

# Invalidate CloudFront cache
invalidate_cache() {
    log_info "Invalidating CloudFront cache..."
    
    # Get CloudFront distribution ID from stack outputs
    DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`PlaygroundDistributionId`].OutputValue' \
        --output text)
    
    # Create invalidation
    INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --distribution-id "$DISTRIBUTION_ID" \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text)
    
    log_info "Cache invalidation created: $INVALIDATION_ID"
    log_success "Cache invalidation completed"
}

# Display deployment information
display_info() {
    log_info "Deployment completed successfully!"
    echo
    echo "=========================================="
    echo "  DcisionAI Manufacturing Playground"
    echo "=========================================="
    echo
    
    # Get stack outputs
    OUTPUTS=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs')
    
    echo "🌐 Playground URL:"
    echo "$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="PlaygroundURL") | .OutputValue')"
    echo
    
    echo "🔗 API Endpoint:"
    echo "$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="PlaygroundAPIEndpoint") | .OutputValue')"
    echo
    
    echo "📦 S3 Bucket:"
    echo "$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="PlaygroundBucketName") | .OutputValue')"
    echo
    
    echo "☁️  CloudFront Distribution:"
    echo "$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="PlaygroundDistributionId") | .OutputValue')"
    echo
    
    echo "=========================================="
    echo
    log_success "Playground is ready for demos!"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    rm -f lambda-deployment.zip
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    log_info "Starting DcisionAI Manufacturing Playground deployment..."
    echo
    
    # Check prerequisites
    check_prerequisites
    
    # Create deployment package
    create_deployment_package
    
    # Deploy CloudFormation stack
    deploy_stack
    
    # Update Lambda function
    update_lambda
    
    # Upload static files
    upload_static_files
    
    # Invalidate cache
    invalidate_cache
    
    # Display information
    display_info
    
    # Cleanup
    cleanup
}

# Handle script interruption
trap cleanup EXIT

# Run main function
main "$@"
