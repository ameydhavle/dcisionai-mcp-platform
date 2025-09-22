#!/bin/bash

# DcisionAI Manufacturing Playground - Direct AgentCore Deployment
# ===============================================================

set -e

# Configuration
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
    if [ ! -f "index.html" ]; then
        log_error "Please run this script from the playground directory."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create S3 bucket for static hosting
create_s3_bucket() {
    log_info "Creating S3 bucket for static hosting..."
    
    BUCKET_NAME="dcisionai-playground-$(date +%s)"
    
    # Create bucket
    aws s3 mb "s3://$BUCKET_NAME" --region "$REGION"
    
    # Configure for static website hosting
    aws s3 website "s3://$BUCKET_NAME" \
        --index-document index.html \
        --error-document index.html
    
    # Disable block public access
    aws s3api put-public-access-block \
        --bucket "$BUCKET_NAME" \
        --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
    
    # Create bucket policy for public read access
    cat > /tmp/bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF
    
    aws s3api put-bucket-policy \
        --bucket "$BUCKET_NAME" \
        --policy file:///tmp/bucket-policy.json
    
    rm -f /tmp/bucket-policy.json
    
    log_success "S3 bucket created: $BUCKET_NAME"
    echo "$BUCKET_NAME" > .bucket-name
}

# Upload static files to S3
upload_static_files() {
    log_info "Uploading static files to S3..."
    
    BUCKET_NAME=$(cat .bucket-name)
    
    # Upload all HTML files
    aws s3 sync . "s3://$BUCKET_NAME" \
        --exclude "*" \
        --include "*.html" \
        --include "*.css" \
        --include "*.js" \
        --include "*.json" \
        --exclude "*.sh" \
        --exclude "*.zip" \
        --exclude "infrastructure/*" \
        --exclude "api/*" \
        --exclude ".*"
    
    log_success "Static files uploaded"
}

# Create CloudFront distribution
create_cloudfront_distribution() {
    log_info "Creating CloudFront distribution..."
    
    BUCKET_NAME=$(cat .bucket-name)
    
    # Create CloudFront distribution configuration
    cat > /tmp/cloudfront-config.json << EOF
{
    "CallerReference": "dcisionai-playground-$(date +%s)",
    "Comment": "DcisionAI Manufacturing Playground - Direct AgentCore Integration",
    "DefaultRootObject": "index.html",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$BUCKET_NAME",
                "DomainName": "$BUCKET_NAME.s3-website-$REGION.amazonaws.com",
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "http-only"
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$BUCKET_NAME",
        "ViewerProtocolPolicy": "redirect-to-https",
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "MinTTL": 0,
        "DefaultTTL": 3600,
        "MaxTTL": 86400
    },
    "Enabled": true,
    "PriceClass": "PriceClass_100"
}
EOF
    
    # Create distribution
    DISTRIBUTION_ID=$(aws cloudfront create-distribution \
        --distribution-config file:///tmp/cloudfront-config.json \
        --query 'Distribution.Id' \
        --output text)
    
    rm -f /tmp/cloudfront-config.json
    
    log_success "CloudFront distribution created: $DISTRIBUTION_ID"
    echo "$DISTRIBUTION_ID" > .distribution-id
}

# Get AgentCore runtime ARN
get_agentcore_arn() {
    log_info "Getting AgentCore runtime ARN..."
    
    # Check for deployment info file
    if [ -f "../agentcore_v4_deployment.json" ]; then
        AGENTCORE_ARN=$(cat ../agentcore_v4_deployment.json | grep '"agent_runtime_arn"' | cut -d'"' -f4)
        log_success "Found AgentCore ARN: $AGENTCORE_ARN"
    else
        log_warning "No AgentCore deployment found. Please deploy AgentCore first."
        log_info "Run: python3 ../scripts/deployment/deploy_DcisionAI_Manufacturing_Agent_v4.py"
        exit 1
    fi
}

# Update playground HTML with AgentCore ARN
update_playground_config() {
    log_info "Updating playground configuration with AgentCore ARN..."
    
    # Create a simple config file for the playground
    cat > agentcore-config.js << EOF
// DcisionAI Playground - AgentCore Configuration
window.AGENTCORE_CONFIG = {
    agentRuntimeArn: "$AGENTCORE_ARN",
    region: "$REGION",
    directIntegration: true
};
EOF
    
    log_success "Playground configuration updated"
}

# Invalidate CloudFront cache
invalidate_cache() {
    log_info "Invalidating CloudFront cache..."
    
    DISTRIBUTION_ID=$(cat .distribution-id)
    
    aws cloudfront create-invalidation \
        --distribution-id "$DISTRIBUTION_ID" \
        --paths "/*"
    
    log_success "CloudFront cache invalidated"
}

# Display deployment information
display_deployment_info() {
    log_info "Deployment completed successfully!"
    echo
    echo "=========================================="
    echo "🎉 DcisionAI Playground Deployment"
    echo "=========================================="
    echo
    echo "📋 Deployment Information:"
    echo "   S3 Bucket: $(cat .bucket-name)"
    echo "   CloudFront Distribution: $(cat .distribution-id)"
    echo "   AgentCore ARN: $AGENTCORE_ARN"
    echo "   Region: $REGION"
    echo
    echo "🌐 Access URLs:"
    echo "   S3 Website: http://$(cat .bucket-name).s3-website-$REGION.amazonaws.com"
    echo "   CloudFront: https://$(aws cloudfront get-distribution --id $(cat .distribution-id) --query 'Distribution.DomainName' --output text)"
    echo
    echo "📋 Next Steps:"
    echo "1. Wait 5-10 minutes for CloudFront distribution to deploy"
    echo "2. Test the playground interface"
    echo "3. Verify direct AgentCore integration"
    echo
    echo "🔧 Configuration Files:"
    echo "   - .bucket-name: S3 bucket name"
    echo "   - .distribution-id: CloudFront distribution ID"
    echo "   - agentcore-config.js: AgentCore configuration"
    echo
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    rm -f /tmp/bucket-policy.json /tmp/cloudfront-config.json
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    log_info "🚀 Starting DcisionAI Playground - Direct AgentCore Deployment"
    log_info "Region: $REGION"
    log_info "Domain: $SUBDOMAIN.$DOMAIN_NAME"
    echo
    
    # Execute deployment steps
    check_prerequisites
    get_agentcore_arn
    create_s3_bucket
    update_playground_config
    upload_static_files
    create_cloudfront_distribution
    invalidate_cache
    display_deployment_info
    cleanup
    
    log_success "🎉 Playground deployment completed successfully!"
}

# Handle script interruption
trap 'log_error "Deployment interrupted"; cleanup; exit 1' INT TERM

# Run main function
main "$@"
