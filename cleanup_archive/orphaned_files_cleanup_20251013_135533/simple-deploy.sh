#!/bin/bash

# Simple AWS Deployment Script for DcisionAI Manufacturing Optimizer
# =================================================================

set -e

# Configuration
STACK_NAME="dcisionai-manufacturing"
REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

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

# Create ECS cluster
create_ecs_cluster() {
    log_info "Creating ECS cluster..."
    
    aws ecs create-cluster \
        --cluster-name "$STACK_NAME-cluster" \
        --region "$REGION" \
        --capacity-providers FARGATE \
        --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1 \
        --region "$REGION" || log_info "Cluster may already exist"
    
    log_success "ECS cluster ready"
}

# Create task definitions
create_task_definitions() {
    log_info "Creating ECS task definitions..."
    
    # Backend task definition
    cat > backend-task-definition.json << EOF
{
    "family": "$STACK_NAME-backend",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024",
    "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
    "taskRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskRole",
    "containerDefinitions": [
        {
            "name": "backend",
            "image": "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$STACK_NAME-dcisionai:backend-latest",
            "portMappings": [
                {
                    "containerPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "AWS_DEFAULT_REGION",
                    "value": "$REGION"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/$STACK_NAME-backend",
                    "awslogs-region": "$REGION",
                    "awslogs-stream-prefix": "backend"
                }
            },
            "healthCheck": {
                "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
                "interval": 30,
                "timeout": 5,
                "retries": 3,
                "startPeriod": 60
            }
        }
    ]
}
EOF

    # Frontend task definition
    cat > frontend-task-definition.json << EOF
{
    "family": "$STACK_NAME-frontend",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "256",
    "memory": "512",
    "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
    "taskRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskRole",
    "containerDefinitions": [
        {
            "name": "frontend",
            "image": "$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$STACK_NAME-dcisionai:frontend-latest",
            "portMappings": [
                {
                    "containerPort": 3000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "NODE_ENV",
                    "value": "production"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/$STACK_NAME-frontend",
                    "awslogs-region": "$REGION",
                    "awslogs-stream-prefix": "frontend"
                }
            }
        }
    ]
}
EOF

    # Register task definitions
    aws ecs register-task-definition --cli-input-json file://backend-task-definition.json --region "$REGION"
    aws ecs register-task-definition --cli-input-json file://frontend-task-definition.json --region "$REGION"
    
    log_success "Task definitions created"
}

# Create log groups
create_log_groups() {
    log_info "Creating CloudWatch log groups..."
    
    aws logs create-log-group --log-group-name "/ecs/$STACK_NAME-backend" --region "$REGION" || log_info "Backend log group may already exist"
    aws logs create-log-group --log-group-name "/ecs/$STACK_NAME-frontend" --region "$REGION" || log_info "Frontend log group may already exist"
    
    log_success "Log groups created"
}

# Create IAM roles
create_iam_roles() {
    log_info "Creating IAM roles..."
    
    # ECS Task Execution Role
    cat > ecs-task-execution-role-trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ecs-tasks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

    aws iam create-role \
        --role-name ecsTaskExecutionRole \
        --assume-role-policy-document file://ecs-task-execution-role-trust-policy.json \
        --region "$REGION" || log_info "ECS Task Execution Role may already exist"

    aws iam attach-role-policy \
        --role-name ecsTaskExecutionRole \
        --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy \
        --region "$REGION" || log_info "Policy may already be attached"

    # ECS Task Role
    cat > ecs-task-role-trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ecs-tasks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

    aws iam create-role \
        --role-name ecsTaskRole \
        --assume-role-policy-document file://ecs-task-role-trust-policy.json \
        --region "$REGION" || log_info "ECS Task Role may already exist"

    # Bedrock access policy
    cat > bedrock-access-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "*"
        }
    ]
}
EOF

    aws iam put-role-policy \
        --role-name ecsTaskRole \
        --policy-name BedrockAccess \
        --policy-document file://bedrock-access-policy.json \
        --region "$REGION" || log_info "Bedrock policy may already exist"

    log_success "IAM roles created"
}

# Run services
run_services() {
    log_info "Running ECS services..."
    
    # Get default VPC and subnets
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text --region "$REGION")
    SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[0:2].SubnetId' --output text --region "$REGION")
    SUBNET_1=$(echo $SUBNET_IDS | cut -d' ' -f1)
    SUBNET_2=$(echo $SUBNET_IDS | cut -d' ' -f2)
    
    # Security group
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name "$STACK_NAME-sg" \
        --description "Security group for DcisionAI Manufacturing" \
        --vpc-id "$VPC_ID" \
        --region "$REGION" \
        --query 'GroupId' \
        --output text 2>/dev/null || aws ec2 describe-security-groups \
        --filters "Name=group-name,Values=$STACK_NAME-sg" \
        --query 'SecurityGroups[0].GroupId' \
        --output text \
        --region "$REGION")

    # Allow HTTP traffic
    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0 \
        --region "$REGION" 2>/dev/null || log_info "Port 8000 rule may already exist"

    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 3000 \
        --cidr 0.0.0.0/0 \
        --region "$REGION" 2>/dev/null || log_info "Port 3000 rule may already exist"

    # Run backend service
    aws ecs run-task \
        --cluster "$STACK_NAME-cluster" \
        --task-definition "$STACK_NAME-backend" \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_1,$SUBNET_2],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" \
        --region "$REGION" || log_info "Backend task may already be running"

    # Run frontend service
    aws ecs run-task \
        --cluster "$STACK_NAME-cluster" \
        --task-definition "$STACK_NAME-frontend" \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_1,$SUBNET_2],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" \
        --region "$REGION" || log_info "Frontend task may already be running"

    log_success "Services started"
}

# Get service URLs
get_service_urls() {
    log_info "Getting service URLs..."
    
    # Get task ARNs
    BACKEND_TASK_ARN=$(aws ecs list-tasks --cluster "$STACK_NAME-cluster" --family "$STACK_NAME-backend" --query 'taskArns[0]' --output text --region "$REGION")
    FRONTEND_TASK_ARN=$(aws ecs list-tasks --cluster "$STACK_NAME-cluster" --family "$STACK_NAME-frontend" --query 'taskArns[0]' --output text --region "$REGION")
    
    if [ "$BACKEND_TASK_ARN" != "None" ] && [ "$BACKEND_TASK_ARN" != "null" ]; then
        BACKEND_IP=$(aws ecs describe-tasks --cluster "$STACK_NAME-cluster" --tasks "$BACKEND_TASK_ARN" --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text --region "$REGION" | xargs -I {} aws ec2 describe-network-interfaces --network-interface-ids {} --query 'NetworkInterfaces[0].Association.PublicIp' --output text --region "$REGION")
        log_success "Backend URL: http://$BACKEND_IP:8000"
    fi
    
    if [ "$FRONTEND_TASK_ARN" != "None" ] && [ "$FRONTEND_TASK_ARN" != "null" ]; then
        FRONTEND_IP=$(aws ecs describe-tasks --cluster "$STACK_NAME-cluster" --tasks "$FRONTEND_TASK_ARN" --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text --region "$REGION" | xargs -I {} aws ec2 describe-network-interfaces --network-interface-ids {} --query 'NetworkInterfaces[0].Association.PublicIp' --output text --region "$REGION")
        log_success "Frontend URL: http://$FRONTEND_IP:3000"
    fi
}

# Main deployment function
main() {
    echo "🚀 Starting Simple DcisionAI Manufacturing Optimizer AWS Deployment"
    echo "=================================================================="
    echo ""
    
    create_iam_roles
    create_log_groups
    create_ecs_cluster
    create_task_definitions
    run_services
    
    echo ""
    log_success "Deployment completed!"
    echo ""
    echo "🎉 DcisionAI Manufacturing Optimizer is now running on AWS!"
    echo ""
    get_service_urls
    echo ""
    echo "✅ Your application is now live on AWS!"
}

# Run main function
main "$@"
