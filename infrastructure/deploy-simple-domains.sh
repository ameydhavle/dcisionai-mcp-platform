#!/bin/bash

# 🚀 DcisionAI Platform - Simple Domain Infrastructure Deployment
# ==============================================================
# This script deploys the basic domain infrastructure (Phase 1)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="dcisionai-simple-domains"
TEMPLATE_FILE="simple-domain-infrastructure.yaml"
REGION="us-east-1"
ENVIRONMENT="production"
DOMAIN_NAME="dcisionai.com"

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

print_header() {
    echo -e "${PURPLE}🎯 $1${NC}"
}

print_step() {
    echo -e "${CYAN}📋 $1${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if AWS credentials are configured
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check if template file exists
    if [ ! -f "$TEMPLATE_FILE" ]; then
        print_error "Template file $TEMPLATE_FILE not found."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to get AWS account ID
get_aws_account_id() {
    print_status "Getting AWS Account ID..."
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    print_success "AWS Account ID: $AWS_ACCOUNT_ID"
}

# Function to deploy the stack
deploy_stack() {
    print_header "Deploying Simple Domain Infrastructure..."
    
    # Check if stack already exists
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" &> /dev/null; then
        print_warning "Stack $STACK_NAME already exists. Updating..."
        OPERATION="update-stack"
        WAIT_OPERATION="stack-update-complete"
    else
        print_status "Creating new stack: $STACK_NAME"
        OPERATION="create-stack"
        WAIT_OPERATION="stack-create-complete"
    fi
    
    # Deploy the stack
    print_step "Deploying CloudFormation stack: $STACK_NAME"
    
    aws cloudformation $OPERATION \
        --stack-name "$STACK_NAME" \
        --template-body "file://$TEMPLATE_FILE" \
        --parameters \
            ParameterKey=Environment,ParameterValue="$ENVIRONMENT" \
            ParameterKey=DomainName,ParameterValue="$DOMAIN_NAME" \
        --capabilities CAPABILITY_NAMED_IAM \
        --tags \
            Key=Environment,Value="$ENVIRONMENT" \
            Key=Purpose,Value="Simple Domain Infrastructure" \
            Key=Project,Value="DcisionAI Platform" \
            Key=Phase,Value="3B-Phase1"
    
    if [ $? -eq 0 ]; then
        print_success "Stack deployment initiated successfully"
    else
        print_error "Stack deployment failed"
        exit 1
    fi
}

# Function to wait for stack completion
wait_for_stack() {
    print_step "Waiting for stack deployment to complete..."
    
    if aws cloudformation wait "$WAIT_OPERATION" --stack-name "$STACK_NAME"; then
        print_success "Stack deployment completed successfully!"
    else
        print_error "Stack deployment failed or timed out"
        print_status "Checking stack status..."
        aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query 'Stacks[0].StackStatus' --output text
        exit 1
    fi
}

# Function to get stack outputs
get_stack_outputs() {
    print_header "Getting Stack Outputs..."
    
    # Get the hosted zone ID
    HOSTED_ZONE_ID=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`HostedZoneId`].OutputValue' \
        --output text)
    
    # Get the name servers
    NAME_SERVERS=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`HostedZoneNameServers`].OutputValue' \
        --output text)
    
    # Get S3 bucket names
    MCP_DOCS_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`MCPDocsBucketName`].OutputValue' \
        --output text)
    
    SDK_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`SDKBucketName`].OutputValue' \
        --output text)
    
    API_DOCS_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`APIDocsBucketName`].OutputValue' \
        --output text)
    
    STATUS_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`StatusPageBucketName`].OutputValue' \
        --output text)
    
    print_success "Stack outputs retrieved successfully"
}

# Function to display deployment summary
display_deployment_summary() {
    print_header "🎉 Simple Domain Infrastructure Deployment Complete!"
    echo
    echo "📊 Deployment Summary:"
    echo "======================"
    echo "Stack Name: $STACK_NAME"
    echo "Environment: $ENVIRONMENT"
    echo "Domain: $DOMAIN_NAME"
    echo "Region: $REGION"
    echo
    echo "🌐 DNS Configuration:"
    echo "===================="
    echo "Hosted Zone ID: $HOSTED_ZONE_ID"
    echo "Name Servers:"
    echo "$NAME_SERVERS" | tr '\t' '\n'
    echo
    echo "📦 S3 Buckets Created:"
    echo "======================"
    echo "MCP Documentation: $MCP_DOCS_BUCKET"
    echo "SDK Downloads: $SDK_BUCKET"
    echo "API Documentation: $API_DOCS_BUCKET"
    echo "Status Page: $STATUS_BUCKET"
    echo
    echo "🎯 Phase 1 Complete - Basic Infrastructure Ready:"
    echo "================================================="
    echo "✅ Route 53 Hosted Zone created"
    echo "✅ S3 buckets for static content ready"
    echo "✅ Basic DNS records configured"
    echo "✅ Foundation for enhanced features"
    echo
}

# Function to display next steps
display_next_steps() {
    print_header "🔄 Next Steps for Phase 3B"
    echo
    echo "1. 🌐 Update GoDaddy DNS Settings:"
    echo "   - Go to GoDaddy DNS Management for $DOMAIN_NAME"
    echo "   - Update Name Servers to use AWS Route 53:"
    echo "$NAME_SERVERS" | tr '\t' '\n' | sed 's/^/     /'
    echo
    echo "2. ⏳ Wait for DNS Propagation:"
    echo "   - DNS changes can take 24-48 hours to propagate globally"
    echo "   - Use online DNS propagation checkers to monitor progress"
    echo
    echo "3. 🎯 Phase 2: Add CloudFront Distributions"
    echo "   - Deploy CloudFront for static content delivery"
    echo "   - Set up SSL certificates"
    echo "   - Configure custom domains for each subdomain"
    echo
    echo "4. 🚀 Phase 3: Deploy Services"
    echo "   - Deploy MCP server to mcp.$DOMAIN_NAME"
    echo "   - Deploy commercial API to api.$DOMAIN_NAME"
    echo "   - Deploy customer portal to portal.$DOMAIN_NAME"
    echo "   - Deploy documentation to docs.$DOMAIN_NAME"
    echo
    echo "5. 📊 Monitor and Optimize:"
    echo "   - Monitor DNS resolution performance"
    echo "   - Check S3 bucket access and security"
    echo "   - Plan CloudFront distribution deployment"
    echo
}

# Function to save deployment info to file
save_deployment_info() {
    DEPLOYMENT_FILE="simple-deployment-info-$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$DEPLOYMENT_FILE" << EOF
# DcisionAI Platform - Simple Domain Infrastructure Deployment Info
# Generated: $(date)
# Stack: $STACK_NAME
# Environment: $ENVIRONMENT
# Domain: $DOMAIN_NAME
# Phase: 3B-Phase1

## DNS Configuration
Hosted Zone ID: $HOSTED_ZONE_ID
Name Servers:
$NAME_SERVERS

## S3 Buckets Created
MCP Documentation: $MCP_DOCS_BUCKET
SDK Downloads: $SDK_BUCKET
API Documentation: $API_DOCS_BUCKET
Status Page: $STATUS_BUCKET

## Current Status
Phase 1 Complete: Basic Domain Infrastructure
- Route 53 Hosted Zone created
- S3 buckets for static content ready
- Basic DNS records configured
- Foundation for enhanced features

## Next Steps
1. Update GoDaddy DNS with AWS Name Servers
2. Wait for DNS propagation (24-48 hours)
3. Phase 2: Add CloudFront Distributions
4. Phase 3: Deploy Services to Subdomains
5. Phase 3C: Production Hardening
EOF

    print_success "Deployment information saved to: $DEPLOYMENT_FILE"
}

# Main execution
main() {
    echo "🚀 DcisionAI Platform - Simple Domain Infrastructure Deployment"
    echo "============================================================="
    echo
    echo "This script will deploy Phase 1 of our enhanced domain infrastructure:"
    echo "• Route 53 Hosted Zone for DNS management"
    echo "• S3 buckets for static content storage"
    echo "• Basic DNS records for subdomains (preserving existing website)"
    echo "• Foundation for CloudFront and SSL certificates"
    echo
    
    # Check prerequisites
    check_prerequisites
    
    # Get AWS account ID
    get_aws_account_id
    
    # Deploy the stack
    deploy_stack
    
    # Wait for completion
    wait_for_stack
    
    # Get outputs
    get_stack_outputs
    
    # Display summary
    display_deployment_summary
    
    # Display next steps
    display_next_steps
    
    # Save deployment info
    save_deployment_info
    
    echo
    print_success "🎉 Simple Domain Infrastructure deployment completed successfully!"
    echo
    echo "Next: Update your GoDaddy DNS settings with the AWS Name Servers above"
    echo "Then wait 24-48 hours for DNS propagation before proceeding to Phase 2."
}

# Run main function
main "$@"
