#!/bin/bash

# 🚀 DcisionAI Platform - Enhanced Domain Infrastructure Deployment
# ================================================================
# This script deploys the enhanced domain infrastructure for our dual-track architecture

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
STACK_NAME="dcisionai-enhanced-domains"
TEMPLATE_FILE="enhanced-domain-infrastructure.yaml"
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
    print_header "Deploying Enhanced Domain Infrastructure..."
    
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
            ParameterKey=CertificateValidationMethod,ParameterValue=DNS \
        --capabilities CAPABILITY_NAMED_IAM \
        --tags \
            Key=Environment,Value="$ENVIRONMENT" \
            Key=Purpose,Value="Enhanced Domain Infrastructure" \
            Key=Project,Value="DcisionAI Platform" \
            Key=Phase,Value="3B"
    
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
    
    # Get the wildcard certificate ARN
    CERTIFICATE_ARN=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`WildcardCertificateArn`].OutputValue' \
        --output text)
    
    # Get the application load balancer DNS
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApplicationLoadBalancerDNS`].OutputValue' \
        --output text)
    
    # Get CloudFront distribution domains
    MCP_DOCS_DOMAIN=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`MCPDocsDistributionDomain`].OutputValue' \
        --output text)
    
    SDK_DOMAIN=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`SDKDistributionDomain`].OutputValue' \
        --output text)
    
    API_DOCS_DOMAIN=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`APIDocsDistributionDomain`].OutputValue' \
        --output text)
    
    STATUS_DOMAIN=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`StatusPageDistributionDomain`].OutputValue' \
        --output text)
    
    print_success "Stack outputs retrieved successfully"
}

# Function to display deployment summary
display_deployment_summary() {
    print_header "🎉 Enhanced Domain Infrastructure Deployment Complete!"
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
    echo "🔐 SSL Certificate:"
    echo "==================="
    echo "Wildcard Certificate ARN: $CERTIFICATE_ARN"
    echo
    echo "🚀 Service Endpoints:"
    echo "====================="
    echo "Application Load Balancer: $ALB_DNS"
    echo "MCP Documentation: $MCP_DOCS_DOMAIN"
    echo "SDK Downloads: $SDK_DOMAIN"
    echo "API Documentation: $API_DOCS_DOMAIN"
    echo "Status Page: $STATUS_DOMAIN"
    echo
    echo "🎯 Dual-Track Architecture:"
    echo "==========================="
    echo "MCP Track (Ecosystem):"
    echo "  - mcp.$DOMAIN_NAME → MCP Protocol Server"
    echo "  - mcp-docs.$DOMAIN_NAME → MCP Documentation"
    echo "  - mcp-status.$DOMAIN_NAME → MCP Service Status"
    echo
    echo "Commercial Track (Enterprise):"
    echo "  - api.$DOMAIN_NAME → Commercial API Gateway"
    echo "  - sdk.$DOMAIN_NAME → SDK Downloads"
    echo "  - portal.$DOMAIN_NAME → Customer Portal"
    echo "  - docs.$DOMAIN_NAME → API Documentation"
    echo
    echo "Shared Services:"
    echo "  - auth.$DOMAIN_NAME → Authentication Service"
    echo "  - monitoring.$DOMAIN_NAME → System Monitoring"
    echo "  - status.$DOMAIN_NAME → Service Status"
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
    echo "3. 🔐 SSL Certificate Validation:"
    echo "   - Certificates will automatically validate once DNS is updated"
    echo "   - Monitor certificate status in AWS Certificate Manager"
    echo
    echo "4. 🧪 Test Subdomains:"
    echo "   - Test each subdomain for proper resolution"
    echo "   - Verify SSL certificates are working"
    echo   "   - Check CloudFront distributions are accessible"
    echo
    echo "5. 🚀 Deploy Services:"
    echo "   - Deploy MCP server to mcp.$DOMAIN_NAME"
    echo "   - Deploy commercial API to api.$DOMAIN_NAME"
    echo "   - Deploy customer portal to portal.$DOMAIN_NAME"
    echo "   - Upload documentation to docs.$DOMAIN_NAME"
    echo "   - Upload SDK files to sdk.$DOMAIN_NAME"
    echo
    echo "6. 📊 Monitor and Optimize:"
    echo "   - Monitor CloudFront performance"
    echo "   - Check SSL certificate health"
    echo "   - Monitor DNS resolution performance"
    echo
    echo "7. 🎯 Phase 3C: Production Hardening:"
    echo "   - Implement WAF rules"
    echo "   - Add advanced monitoring"
    echo "   - Performance optimization"
    echo
}

# Function to save deployment info to file
save_deployment_info() {
    DEPLOYMENT_FILE="deployment-info-$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$DEPLOYMENT_FILE" << EOF
# DcisionAI Platform - Enhanced Domain Infrastructure Deployment Info
# Generated: $(date)
# Stack: $STACK_NAME
# Environment: $ENVIRONMENT
# Domain: $DOMAIN_NAME

## DNS Configuration
Hosted Zone ID: $HOSTED_ZONE_ID
Name Servers:
$NAME_SERVERS

## SSL Certificate
Wildcard Certificate ARN: $CERTIFICATE_ARN

## Service Endpoints
Application Load Balancer: $ALB_DNS
MCP Documentation: $MCP_DOCS_DOMAIN
SDK Downloads: $SDK_DOMAIN
API Documentation: $API_DOCS_DOMAIN
Status Page: $STATUS_DOMAIN

## Dual-Track Architecture
MCP Track (Ecosystem):
- mcp.$DOMAIN_NAME → MCP Protocol Server
- mcp-docs.$DOMAIN_NAME → MCP Documentation
- mcp-status.$DOMAIN_NAME → MCP Service Status

Commercial Track (Enterprise):
- api.$DOMAIN_NAME → Commercial API Gateway
- sdk.$DOMAIN_NAME → SDK Downloads
- portal.$DOMAIN_NAME → Customer Portal
- docs.$DOMAIN_NAME → API Documentation

Shared Services:
- auth.$DOMAIN_NAME → Authentication Service
- monitoring.$DOMAIN_NAME → System Monitoring
- status.$DOMAIN_NAME → Service Status

## Next Steps
1. Update GoDaddy DNS with AWS Name Servers
2. Wait for DNS propagation (24-48 hours)
3. SSL certificates will auto-validate
4. Deploy services to each subdomain
5. Test all subdomains and SSL certificates
6. Monitor performance and security
7. Phase 3C: Production Hardening
EOF

    print_success "Deployment information saved to: $DEPLOYMENT_FILE"
}

# Main execution
main() {
    echo "🚀 DcisionAI Platform - Enhanced Domain Infrastructure Deployment"
    echo "================================================================"
    echo
    echo "This script will deploy the enhanced domain infrastructure for our dual-track architecture:"
    echo "• MCP Track (mcp.*) for ecosystem integration"
    echo "• Commercial Track (api.*, sdk.*, portal.*) for enterprise sales"
    echo "• Shared Services (auth.*, monitoring.*, status.*) for infrastructure"
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
    print_success "🎉 Enhanced Domain Infrastructure deployment completed successfully!"
    echo
    echo "Next: Update your GoDaddy DNS settings with the AWS Name Servers above"
    echo "Then wait 24-48 hours for DNS propagation before testing subdomains."
}

# Run main function
main "$@"
