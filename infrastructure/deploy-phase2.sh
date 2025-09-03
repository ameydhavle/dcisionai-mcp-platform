#!/bin/bash

# 🚀 DcisionAI Enhanced Domain Infrastructure - Phase 2 Deployment
# ================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="dcisionai-enhanced-domains-phase2"
TEMPLATE_FILE="enhanced-domain-phase2.yaml"
REGION="us-east-1"

echo -e "${BLUE}🚀 DcisionAI Enhanced Domain Infrastructure - Phase 2${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo ""

# Function to print colored output
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Check if template file exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    print_error "Template file '$TEMPLATE_FILE' not found."
    exit 1
fi

print_success "Prerequisites check passed"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
print_status "AWS Account ID: $AWS_ACCOUNT_ID"

# Check if stack already exists
STACK_EXISTS=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "STACK_NOT_FOUND")

if [ "$STACK_EXISTS" = "STACK_NOT_FOUND" ]; then
    print_status "Creating new stack: $STACK_NAME"
    
    # Create stack
    aws cloudformation create-stack \
        --stack-name "$STACK_NAME" \
        --template-body "file://$TEMPLATE_FILE" \
        --region "$REGION" \
        --capabilities CAPABILITY_IAM \
        --parameters ParameterKey=DomainName,ParameterValue=dcisionai.com \
                   ParameterKey=Environment,ParameterValue=production
    
    print_success "Stack creation initiated"
    echo "Stack ID: $(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].StackId' --output text)"
    
    print_status "Waiting for stack deployment to complete..."
    aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME" --region "$REGION"
    
else
    print_status "Stack already exists. Updating: $STACK_NAME"
    
    # Update stack
    aws cloudformation update-stack \
        --stack-name "$STACK_NAME" \
        --template-body "file://$TEMPLATE_FILE" \
        --region "$REGION" \
        --capabilities CAPABILITY_IAM \
        --parameters ParameterKey=DomainName,ParameterValue=dcisionai.com \
                   ParameterKey=Environment,ParameterValue=production
    
    print_success "Stack update initiated"
    
    print_status "Waiting for stack update to complete..."
    aws cloudformation wait stack-update-complete --stack-name "$STACK_NAME" --region "$REGION"
fi

print_success "Stack deployment completed successfully!"

# Display outputs
echo ""
print_status "Stack outputs:"
aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs' \
    --output table

echo ""
print_success "Phase 2 deployment completed!"
echo ""
print_status "Next steps:"
echo "1. Wait for SSL certificate validation (can take 10-30 minutes)"
echo "2. Test the new subdomains:"
echo "   - https://mcp.dcisionai.com (MCP Documentation)"
echo "   - https://sdk.dcisionai.com (SDK Downloads)"
echo "   - https://docs.dcisionai.com (API Documentation)"
echo "   - https://status.dcisionai.com (Status Page)"
echo "3. Proceed to Phase 3: Deploy actual services"
echo ""
print_status "You can monitor the SSL certificate status with:"
echo "aws acm list-certificates --region us-east-1 --query 'CertificateSummaryList[?DomainName==\`dcisionai.com\`].Status' --output text"
