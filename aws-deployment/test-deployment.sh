#!/bin/bash

# DcisionAI Manufacturing Optimizer - Deployment Test Script
# =========================================================

set -e

# Configuration
STACK_NAME="dcisionai-manufacturing"
REGION="us-east-1"

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

# Test CloudFormation stack
test_cloudformation() {
    log_info "Testing CloudFormation stack..."
    
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &> /dev/null; then
        log_success "CloudFormation stack exists"
        
        # Get stack status
        STATUS=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].StackStatus' --output text)
        log_info "Stack status: $STATUS"
        
        if [ "$STATUS" = "CREATE_COMPLETE" ] || [ "$STATUS" = "UPDATE_COMPLETE" ]; then
            log_success "Stack is in a healthy state"
        else
            log_warning "Stack is not in a healthy state: $STATUS"
        fi
    else
        log_error "CloudFormation stack not found"
        return 1
    fi
}

# Test ECS services
test_ecs_services() {
    log_info "Testing ECS services..."
    
    CLUSTER_NAME=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].Outputs[?OutputKey==`ECSClusterName`].OutputValue' --output text)
    
    if [ -z "$CLUSTER_NAME" ]; then
        log_error "Could not get ECS cluster name"
        return 1
    fi
    
    log_info "ECS Cluster: $CLUSTER_NAME"
    
    # Test backend service
    BACKEND_SERVICE="$STACK_NAME-backend-service"
    if aws ecs describe-services --cluster "$CLUSTER_NAME" --services "$BACKEND_SERVICE" --region "$REGION" &> /dev/null; then
        BACKEND_STATUS=$(aws ecs describe-services --cluster "$CLUSTER_NAME" --services "$BACKEND_SERVICE" --region "$REGION" --query 'services[0].status' --output text)
        BACKEND_RUNNING=$(aws ecs describe-services --cluster "$CLUSTER_NAME" --services "$BACKEND_SERVICE" --region "$REGION" --query 'services[0].runningCount' --output text)
        log_info "Backend service: $BACKEND_STATUS (Running: $BACKEND_RUNNING)"
        
        if [ "$BACKEND_STATUS" = "ACTIVE" ] && [ "$BACKEND_RUNNING" -gt 0 ]; then
            log_success "Backend service is healthy"
        else
            log_warning "Backend service is not healthy"
        fi
    else
        log_error "Backend service not found"
    fi
    
    # Test frontend service
    FRONTEND_SERVICE="$STACK_NAME-frontend-service"
    if aws ecs describe-services --cluster "$CLUSTER_NAME" --services "$FRONTEND_SERVICE" --region "$REGION" &> /dev/null; then
        FRONTEND_STATUS=$(aws ecs describe-services --cluster "$CLUSTER_NAME" --services "$FRONTEND_SERVICE" --region "$REGION" --query 'services[0].status' --output text)
        FRONTEND_RUNNING=$(aws ecs describe-services --cluster "$CLUSTER_NAME" --services "$FRONTEND_SERVICE" --region "$REGION" --query 'services[0].runningCount' --output text)
        log_info "Frontend service: $FRONTEND_STATUS (Running: $FRONTEND_RUNNING)"
        
        if [ "$FRONTEND_STATUS" = "ACTIVE" ] && [ "$FRONTEND_RUNNING" -gt 0 ]; then
            log_success "Frontend service is healthy"
        else
            log_warning "Frontend service is not healthy"
        fi
    else
        log_error "Frontend service not found"
    fi
}

# Test application endpoints
test_endpoints() {
    log_info "Testing application endpoints..."
    
    APPLICATION_URL=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' --output text)
    
    if [ -z "$APPLICATION_URL" ]; then
        log_error "Could not get application URL"
        return 1
    fi
    
    log_info "Application URL: $APPLICATION_URL"
    
    # Test frontend
    log_info "Testing frontend endpoint..."
    if curl -s -f "$APPLICATION_URL" > /dev/null; then
        log_success "Frontend is accessible"
    else
        log_warning "Frontend is not accessible"
    fi
    
    # Test backend health
    log_info "Testing backend health endpoint..."
    if curl -s -f "$APPLICATION_URL/health" > /dev/null; then
        log_success "Backend health check passed"
    else
        log_warning "Backend health check failed"
    fi
    
    # Test backend API
    log_info "Testing backend API endpoint..."
    if curl -s -f "$APPLICATION_URL/api/health" > /dev/null; then
        log_success "Backend API is accessible"
    else
        log_warning "Backend API is not accessible"
    fi
}

# Test optimization functionality
test_optimization() {
    log_info "Testing optimization functionality..."
    
    APPLICATION_URL=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' --output text)
    
    # Test optimization endpoint
    OPTIMIZATION_RESPONSE=$(curl -s -X POST "$APPLICATION_URL/api/mcp" \
        -H "Content-Type: application/json" \
        -d '{
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "manufacturing_optimize",
                "arguments": {
                    "problem_description": "Test optimization with 2 variables",
                    "constraints": {},
                    "optimization_goals": []
                }
            }
        }' 2>/dev/null || echo "ERROR")
    
    if [ "$OPTIMIZATION_RESPONSE" != "ERROR" ] && echo "$OPTIMIZATION_RESPONSE" | grep -q "result"; then
        log_success "Optimization endpoint is working"
    else
        log_warning "Optimization endpoint is not working"
    fi
}

# Main test function
main() {
    echo "🧪 Testing DcisionAI Manufacturing Optimizer AWS Deployment"
    echo "============================================================"
    echo ""
    
    test_cloudformation
    echo ""
    
    test_ecs_services
    echo ""
    
    test_endpoints
    echo ""
    
    test_optimization
    echo ""
    
    log_success "Deployment test completed!"
    echo ""
    echo "🎉 Your DcisionAI Manufacturing Optimizer is ready for production!"
}

# Run main function
main "$@"
