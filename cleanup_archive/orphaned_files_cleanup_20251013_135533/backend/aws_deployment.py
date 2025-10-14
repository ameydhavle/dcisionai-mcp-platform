#!/usr/bin/env python3
"""
AWS Deployment Configuration for DcisionAI Manufacturing MCP Server
================================================================

This module provides AWS deployment configurations for hosting the MCP server
on AWS infrastructure including Lambda, ECS, and EC2.
"""

import json
import boto3
from typing import Dict, Any, Optional
from pathlib import Path

class AWSDeploymentConfig:
    """AWS deployment configuration for MCP server."""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.session = boto3.Session(region_name=region)
    
    def create_lambda_deployment_package(self) -> Dict[str, Any]:
        """Create Lambda deployment package configuration."""
        return {
            "FunctionName": "dcisionai-mcp-manufacturing",
            "Runtime": "python3.11",
            "Role": "arn:aws:iam::ACCOUNT:role/lambda-execution-role",
            "Handler": "mcp_server.lambda_handler",
            "Code": {
                "ZipFile": "mcp_server.zip"
            },
            "Description": "DcisionAI Manufacturing MCP Server",
            "Timeout": 300,
            "MemorySize": 1024,
            "Environment": {
                "Variables": {
                    "AWS_REGION": self.region,
                    "LOG_LEVEL": "INFO"
                }
            },
            "VpcConfig": {
                "SubnetIds": ["subnet-12345", "subnet-67890"],
                "SecurityGroupIds": ["sg-12345"]
            },
            "Layers": [
                "arn:aws:lambda:us-east-1:123456789012:layer:boto3-layer:1"
            ]
        }
    
    def create_ecs_task_definition(self) -> Dict[str, Any]:
        """Create ECS task definition for containerized deployment."""
        return {
            "family": "dcisionai-mcp-manufacturing",
            "networkMode": "awsvpc",
            "requiresCompatibilities": ["FARGATE"],
            "cpu": "512",
            "memory": "1024",
            "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
            "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
            "containerDefinitions": [
                {
                    "name": "dcisionai-mcp-server",
                    "image": "ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/dcisionai-mcp-manufacturing:latest",
                    "portMappings": [
                        {
                            "containerPort": 8000,
                            "protocol": "tcp"
                        }
                    ],
                    "essential": True,
                    "environment": [
                        {
                            "name": "AWS_REGION",
                            "value": self.region
                        },
                        {
                            "name": "LOG_LEVEL",
                            "value": "INFO"
                        }
                    ],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": "/ecs/dcisionai-mcp-manufacturing",
                            "awslogs-region": self.region,
                            "awslogs-stream-prefix": "ecs"
                        }
                    },
                    "healthCheck": {
                        "command": [
                            "CMD-SHELL",
                            "curl -f http://localhost:8000/health || exit 1"
                        ],
                        "interval": 30,
                        "timeout": 5,
                        "retries": 3,
                        "startPeriod": 60
                    }
                }
            ]
        }
    
    def create_ecs_service_definition(self) -> Dict[str, Any]:
        """Create ECS service definition."""
        return {
            "serviceName": "dcisionai-mcp-manufacturing-service",
            "cluster": "dcisionai-cluster",
            "taskDefinition": "dcisionai-mcp-manufacturing",
            "desiredCount": 2,
            "launchType": "FARGATE",
            "networkConfiguration": {
                "awsvpcConfiguration": {
                    "subnets": ["subnet-12345", "subnet-67890"],
                    "securityGroups": ["sg-12345"],
                    "assignPublicIp": "ENABLED"
                }
            },
            "loadBalancers": [
                {
                    "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:ACCOUNT:targetgroup/dcisionai-mcp-tg/1234567890123456",
                    "containerName": "dcisionai-mcp-server",
                    "containerPort": 8000
                }
            ],
            "healthCheckGracePeriodSeconds": 60,
            "deploymentConfiguration": {
                "maximumPercent": 200,
                "minimumHealthyPercent": 50
            }
        }
    
    def create_application_load_balancer(self) -> Dict[str, Any]:
        """Create Application Load Balancer configuration."""
        return {
            "LoadBalancerName": "dcisionai-mcp-alb",
            "Subnets": ["subnet-12345", "subnet-67890"],
            "SecurityGroups": ["sg-12345"],
            "Scheme": "internet-facing",
            "Type": "application",
            "IpAddressType": "ipv4",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "dcisionai-mcp-manufacturing-alb"
                },
                {
                    "Key": "Environment",
                    "Value": "production"
                }
            ]
        }
    
    def create_target_group(self) -> Dict[str, Any]:
        """Create target group for load balancer."""
        return {
            "Name": "dcisionai-mcp-tg",
            "Protocol": "HTTP",
            "Port": 8000,
            "VpcId": "vpc-12345",
            "TargetType": "ip",
            "HealthCheckProtocol": "HTTP",
            "HealthCheckPath": "/health",
            "HealthCheckIntervalSeconds": 30,
            "HealthCheckTimeoutSeconds": 5,
            "HealthyThresholdCount": 2,
            "UnhealthyThresholdCount": 3,
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "dcisionai-mcp-manufacturing-tg"
                }
            ]
        }
    
    def create_iam_role(self) -> Dict[str, Any]:
        """Create IAM role for MCP server."""
        return {
            "RoleName": "DcisionAIMCPServerRole",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": [
                                "ecs-tasks.amazonaws.com",
                                "lambda.amazonaws.com"
                            ]
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "Description": "IAM role for DcisionAI MCP Server",
            "Policies": [
                {
                    "PolicyName": "DcisionAIMCPServerPolicy",
                    "PolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "bedrock:InvokeModel",
                                    "bedrock:InvokeModelWithResponseStream"
                                ],
                                "Resource": "*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "logs:CreateLogGroup",
                                    "logs:CreateLogStream",
                                    "logs:PutLogEvents"
                                ],
                                "Resource": "*"
                            },
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "cloudwatch:PutMetricData",
                                    "cloudwatch:GetMetricStatistics"
                                ],
                                "Resource": "*"
                            }
                        ]
                    }
                }
            ]
        }
    
    def create_cloudformation_template(self) -> Dict[str, Any]:
        """Create CloudFormation template for complete deployment."""
        return {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "DcisionAI Manufacturing MCP Server Infrastructure",
            "Parameters": {
                "Environment": {
                    "Type": "String",
                    "Default": "production",
                    "AllowedValues": ["development", "staging", "production"]
                },
                "VpcId": {
                    "Type": "AWS::EC2::VPC::Id",
                    "Description": "VPC ID for deployment"
                },
                "SubnetIds": {
                    "Type": "CommaDelimitedList",
                    "Description": "Subnet IDs for deployment"
                }
            },
            "Resources": {
                "MCPServerRole": {
                    "Type": "AWS::IAM::Role",
                    "Properties": self.create_iam_role()
                },
                "MCPTaskDefinition": {
                    "Type": "AWS::ECS::TaskDefinition",
                    "Properties": self.create_ecs_task_definition()
                },
                "MCPCluster": {
                    "Type": "AWS::ECS::Cluster",
                    "Properties": {
                        "ClusterName": "dcisionai-mcp-cluster",
                        "CapacityProviders": ["FARGATE"]
                    }
                },
                "MCPLoadBalancer": {
                    "Type": "AWS::ElasticLoadBalancingV2::LoadBalancer",
                    "Properties": self.create_application_load_balancer()
                },
                "MCPTargetGroup": {
                    "Type": "AWS::ElasticLoadBalancingV2::TargetGroup",
                    "Properties": self.create_target_group()
                },
                "MCPService": {
                    "Type": "AWS::ECS::Service",
                    "Properties": self.create_ecs_service_definition(),
                    "DependsOn": ["MCPLoadBalancer", "MCPTargetGroup"]
                }
            },
            "Outputs": {
                "LoadBalancerDNS": {
                    "Description": "DNS name of the load balancer",
                    "Value": {"Fn::GetAtt": ["MCPLoadBalancer", "DNSName"]},
                    "Export": {"Name": {"Fn::Sub": "${AWS::StackName}-LoadBalancerDNS"}}
                },
                "MCPEndpoint": {
                    "Description": "MCP Server endpoint URL",
                    "Value": {"Fn::Sub": "http://${MCPLoadBalancer.DNSName}:8000"},
                    "Export": {"Name": {"Fn::Sub": "${AWS::StackName}-MCPEndpoint"}}
                }
            }
        }

def create_lambda_handler():
    """Create Lambda handler for serverless deployment."""
    lambda_handler_code = '''
import json
from mcp_server import mcp

def lambda_handler(event, context):
    """Lambda handler for MCP server."""
    try:
        # Handle MCP requests
        if 'httpMethod' in event:
            # API Gateway event
            body = json.loads(event.get('body', '{}'))
            method = event.get('httpMethod')
            path = event.get('path')
            
            if path == '/health':
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'status': 'healthy'})
                }
            elif path == '/mcp':
                # Process MCP request
                response = mcp.process_request(body)
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps(response)
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': 'Not found'})
                }
        else:
            # Direct invocation
            return mcp.process_request(event)
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
'''
    
    return lambda_handler_code

if __name__ == "__main__":
    # Example usage
    config = AWSDeploymentConfig()
    
    print("🚀 AWS Deployment Configuration for DcisionAI MCP Server")
    print("=" * 60)
    
    # Save CloudFormation template
    template = config.create_cloudformation_template()
    with open("cloudformation-template.json", "w") as f:
        json.dump(template, f, indent=2)
    print("✅ CloudFormation template saved to cloudformation-template.json")
    
    # Save Lambda handler
    lambda_code = create_lambda_handler()
    with open("lambda_handler.py", "w") as f:
        f.write(lambda_code)
    print("✅ Lambda handler saved to lambda_handler.py")
    
    print("\n📋 Deployment Options:")
    print("1. ECS Fargate (Recommended for production)")
    print("2. Lambda (Serverless, good for variable workloads)")
    print("3. EC2 (Full control, good for development)")
    
    print("\n🔧 Next Steps:")
    print("1. Update the CloudFormation template with your VPC and subnet IDs")
    print("2. Deploy using: aws cloudformation deploy --template-file cloudformation-template.json --stack-name dcisionai-mcp-server")
    print("3. Configure your domain and SSL certificate")
    print("4. Set up monitoring and alerting")
