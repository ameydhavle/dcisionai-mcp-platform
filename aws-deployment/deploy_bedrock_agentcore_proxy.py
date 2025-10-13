#!/usr/bin/env python3
"""
Deploy Bedrock AgentCore Proxy to AWS Lambda
============================================

This script deploys the Bedrock AgentCore proxy as a Lambda function
that handles AWS authentication and forwards MCP requests to Bedrock AgentCore.

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import boto3
import json
import zipfile
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | Bedrock AgentCore Proxy Deploy | %(message)s"
)
logger = logging.getLogger(__name__)

def create_lambda_package():
    """Use the existing Lambda package with dependencies."""
    logger.info("📦 Using existing Lambda deployment package with dependencies...")
    
    # Use the zip file created by create_lambda_package.py
    zip_filename = "bedrock_agentcore_proxy_with_deps.zip"
    
    if not os.path.exists(zip_filename):
        logger.error(f"❌ Zip file {zip_filename} not found. Please run create_lambda_package.py first.")
        raise FileNotFoundError(f"Zip file {zip_filename} not found.")
    
    logger.info(f"✅ Lambda package ready: {zip_filename}")
    return zip_filename

def deploy_lambda_function():
    """Deploy the Lambda function."""
    logger.info("🚀 Deploying Bedrock AgentCore Proxy to Lambda...")
    
    # Create Lambda client
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Create the deployment package
    zip_filename = create_lambda_package()
    
    # Read the zip file
    with open(zip_filename, 'rb') as f:
        zip_content = f.read()
    
    function_name = "bedrock-agentcore-proxy"
    
    try:
        # Try to update existing function
        logger.info(f"🔄 Updating existing Lambda function: {function_name}")
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        logger.info(f"✅ Lambda function updated: {response['FunctionArn']}")
        
    except lambda_client.exceptions.ResourceNotFoundException:
        # Create new function
        logger.info(f"🆕 Creating new Lambda function: {function_name}")
        
        # Create IAM role for Lambda
        iam_client = boto3.client('iam', region_name='us-east-1')
        role_name = f"{function_name}-execution-role"
        
        try:
            # Try to get existing role
            role_response = iam_client.get_role(RoleName=role_name)
            role_arn = role_response['Role']['Arn']
            logger.info(f"✅ Using existing IAM role: {role_arn}")
        except iam_client.exceptions.NoSuchEntityException:
            # Create new role
            logger.info(f"🆕 Creating IAM role: {role_name}")
            
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            role_response = iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Execution role for Bedrock AgentCore Proxy Lambda"
            )
            role_arn = role_response['Role']['Arn']
            
            # Attach policies
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            # Attach Bedrock AgentCore policy
            bedrock_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "bedrock-agentcore:InvokeAgentRuntime"
                        ],
                        "Resource": "*"
                    }
                ]
            }
            
            iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName="BedrockAgentCorePolicy",
                PolicyDocument=json.dumps(bedrock_policy)
            )
            
            logger.info(f"✅ IAM role created: {role_arn}")
        
        # Wait for role to be ready
        import time
        time.sleep(10)
        
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Bedrock AgentCore Proxy for DcisionAI Frontend',
            Timeout=30,
            MemorySize=512,
            Environment={
                'Variables': {
                    'BEDROCK_AGENTCORE_ARN': 'arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/bedrock_agentcore_mcp_server-uZ4MxJ2bNZ'
                }
            }
        )
        logger.info(f"✅ Lambda function created: {response['FunctionArn']}")
    
    # Clean up (only if the directory exists)
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
    import shutil
    if os.path.exists("bedrock_agentcore_proxy_package"):
        shutil.rmtree("bedrock_agentcore_proxy_package")
    
    return response['FunctionArn']

def create_api_gateway():
    """Create or update API Gateway for the Lambda function."""
    logger.info("🌐 Setting up API Gateway...")
    
    api_gateway_client = boto3.client('apigateway', region_name='us-east-1')
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Check if API already exists
    try:
        apis = api_gateway_client.get_rest_apis()
        existing_api = None
        for api in apis['items']:
            if api['name'] == 'bedrock-agentcore-proxy-api':
                existing_api = api
                break
        
        if existing_api:
            api_id = existing_api['id']
            logger.info(f"✅ Using existing API Gateway: {api_id}")
        else:
            # Create new API
            logger.info("🆕 Creating new API Gateway...")
            api_response = api_gateway_client.create_rest_api(
                name='bedrock-agentcore-proxy-api',
                description='API Gateway for Bedrock AgentCore Proxy',
                endpointConfiguration={'types': ['REGIONAL']}
            )
            api_id = api_response['id']
            logger.info(f"✅ API Gateway created: {api_id}")
        
        # Get root resource
        resources = api_gateway_client.get_resources(restApiId=api_id)
        root_resource_id = None
        for resource in resources['items']:
            if resource['path'] == '/':
                root_resource_id = resource['id']
                break
        
        # Create proxy resource
        proxy_resource = api_gateway_client.create_resource(
            restApiId=api_id,
            parentId=root_resource_id,
            pathPart='{proxy+}'
        )
        proxy_resource_id = proxy_resource['id']
        
        # Create ANY method
        api_gateway_client.put_method(
            restApiId=api_id,
            resourceId=proxy_resource_id,
            httpMethod='ANY',
            authorizationType='NONE'
        )
        
        # Create integration
        function_arn = f"arn:aws:lambda:us-east-1:{boto3.client('sts').get_caller_identity()['Account']}:function:bedrock-agentcore-proxy"
        
        api_gateway_client.put_integration(
            restApiId=api_id,
            resourceId=proxy_resource_id,
            httpMethod='ANY',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations"
        )
        
        # Add Lambda permission
        try:
            lambda_client.add_permission(
                FunctionName='bedrock-agentcore-proxy',
                StatementId='apigateway-invoke',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:us-east-1:{boto3.client('sts').get_caller_identity()['Account']}:{api_id}/*/*"
            )
        except lambda_client.exceptions.ResourceConflictException:
            logger.info("✅ Lambda permission already exists")
        
        # Deploy API
        deployment_response = api_gateway_client.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description=f'Deployment at {datetime.now().isoformat()}'
        )
        
        api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
        logger.info(f"✅ API Gateway deployed: {api_url}")
        
        return api_url
        
    except Exception as e:
        logger.error(f"❌ API Gateway setup failed: {e}")
        raise

def main():
    """Main deployment function."""
    logger.info("🚀 Starting Bedrock AgentCore Proxy deployment...")
    
    try:
        # Deploy Lambda function
        function_arn = deploy_lambda_function()
        logger.info(f"✅ Lambda function deployed: {function_arn}")
        
        # Create API Gateway
        api_url = create_api_gateway()
        logger.info(f"✅ API Gateway created: {api_url}")
        
        logger.info("🎉 Bedrock AgentCore Proxy deployment completed!")
        logger.info(f"🌐 API URL: {api_url}")
        logger.info("📋 Next steps:")
        logger.info("1. Update frontend to use the new API URL")
        logger.info("2. Test the proxy with a health check")
        logger.info("3. Deploy updated frontend")
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        raise

if __name__ == "__main__":
    main()
