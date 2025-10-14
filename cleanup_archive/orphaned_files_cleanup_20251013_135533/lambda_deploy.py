#!/usr/bin/env python3
"""
Lambda Deployment Script for DcisionAI Manufacturing MCP Server
==============================================================

This script creates a Lambda function that can handle MCP requests
with zero downtime and automatic scaling.
"""

import boto3
import json
import zipfile
import os
import tempfile
from pathlib import Path

def create_lambda_package():
    """Create a deployment package for Lambda."""
    print("📦 Creating Lambda deployment package...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Copy source files
        source_dir = Path(__file__).parent / "backend"
        lambda_dir = temp_path / "lambda"
        lambda_dir.mkdir()
        
        # Copy essential files
        essential_files = [
            "mcp_server.py",
            "simple_http_server.py", 
            "requirements.txt"
        ]
        
        for file in essential_files:
            if (source_dir / file).exists():
                with open(source_dir / file, 'r') as src:
                    with open(lambda_dir / file, 'w') as dst:
                        dst.write(src.read())
        
        # Create Lambda handler
        lambda_handler = """
import json
import logging
from mcp_server import manufacturing_health_check, manufacturing_optimize

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    \"\"\"Lambda handler for MCP server.\"\"\"
    try:
        # Handle health check
        if event.get('httpMethod') == 'GET' and event.get('path') == '/health':
            result = manufacturing_health_check()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(result)
            }
        
        # Handle MCP requests
        if event.get('httpMethod') == 'POST' and event.get('path') == '/mcp':
            body = json.loads(event.get('body', '{}'))
            
            if body.get('method') == 'tools/call':
                tool_name = body.get('params', {}).get('name')
                arguments = body.get('params', {}).get('arguments', {})
                
                if tool_name == 'manufacturing_health_check':
                    result = manufacturing_health_check()
                elif tool_name == 'manufacturing_optimize':
                    problem_description = arguments.get('problem_description', '')
                    result = manufacturing_optimize(problem_description)
                else:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'Unknown tool'})
                    }
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'jsonrpc': '2.0',
                        'id': body.get('id'),
                        'result': result
                    })
                }
        
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not found'})
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
"""
        
        with open(lambda_dir / "lambda_function.py", 'w') as f:
            f.write(lambda_handler)
        
        # Create deployment package
        zip_path = temp_path / "mcp-server.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in lambda_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(lambda_dir)
                    zipf.write(file_path, arcname)
        
        # Copy zip to current directory for persistence
        persistent_zip = Path(__file__).parent / "mcp-server.zip"
        with open(zip_path, 'rb') as src:
            with open(persistent_zip, 'wb') as dst:
                dst.write(src.read())
        
        return persistent_zip

def deploy_lambda():
    """Deploy the Lambda function."""
    print("🚀 Deploying Lambda function...")
    
    # Create deployment package
    zip_path = create_lambda_package()
    
    # Initialize AWS clients
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')
    
    # Create IAM role for Lambda
    role_name = 'dcisionai-mcp-lambda-role'
    try:
        # Create role
        assume_role_policy = {
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
        
        iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy),
            Description='Role for DcisionAI MCP Lambda function'
        )
        
        # Attach policies
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        # Add Bedrock access
        bedrock_policy = {
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
        
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName='BedrockAccess',
            PolicyDocument=json.dumps(bedrock_policy)
        )
        
        print("✅ IAM role created")
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        print("ℹ️  IAM role already exists")
    
    # Wait for role to be ready
    import time
    time.sleep(10)
    
    # Get role ARN
    role_arn = iam_client.get_role(RoleName=role_name)['Role']['Arn']
    
    # Create or update Lambda function
    function_name = 'dcisionai-mcp-manufacturing'
    
    try:
        # Read deployment package
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        # Create function
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='DcisionAI Manufacturing MCP Server',
            Timeout=300,
            MemorySize=1024,
        )
        print("✅ Lambda function created")
        
    except lambda_client.exceptions.ResourceConflictException:
        # Update function code
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        print("✅ Lambda function updated")
    
    # Create API Gateway
    api_client = boto3.client('apigateway', region_name='us-east-1')
    
    try:
        # Create REST API
        api_response = api_client.create_rest_api(
            name='dcisionai-mcp-api',
            description='API Gateway for DcisionAI MCP Server'
        )
        api_id = api_response['id']
        
        # Get root resource
        resources = api_client.get_resources(restApiId=api_id)
        root_resource_id = resources['items'][0]['id']
        
        # Create /health resource
        health_resource = api_client.create_resource(
            restApiId=api_id,
            parentId=root_resource_id,
            pathPart='health'
        )
        health_resource_id = health_resource['id']
        
        # Create /mcp resource
        mcp_resource = api_client.create_resource(
            restApiId=api_id,
            parentId=root_resource_id,
            pathPart='mcp'
        )
        mcp_resource_id = mcp_resource['id']
        
        # Create methods
        # GET /health
        api_client.put_method(
            restApiId=api_id,
            resourceId=health_resource_id,
            httpMethod='GET',
            authorizationType='NONE'
        )
        
        # POST /mcp
        api_client.put_method(
            restApiId=api_id,
            resourceId=mcp_resource_id,
            httpMethod='POST',
            authorizationType='NONE'
        )
        
        # Create Lambda integration
        account_id = boto3.client('sts').get_caller_identity()['Account']
        lambda_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:{account_id}:function:{function_name}/invocations"
        
        # Add Lambda permission for API Gateway
        try:
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId='apigateway-invoke',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:us-east-1:{account_id}:{api_id}/*/*"
            )
        except lambda_client.exceptions.ResourceConflictException:
            pass  # Permission already exists
        
        # Health integration
        api_client.put_integration(
            restApiId=api_id,
            resourceId=health_resource_id,
            httpMethod='GET',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=lambda_uri
        )
        
        # MCP integration
        api_client.put_integration(
            restApiId=api_id,
            resourceId=mcp_resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=lambda_uri
        )
        
        # Deploy API
        api_client.create_deployment(
            restApiId=api_id,
            stageName='prod'
        )
        
        # Get API URL
        api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
        
        print("✅ API Gateway created")
        print(f"🌐 API URL: {api_url}")
        print(f"🔧 Health Check: {api_url}/health")
        print(f"📡 MCP Endpoint: {api_url}/mcp")
        
        return api_url
        
    except Exception as e:
        print(f"❌ API Gateway creation failed: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting Lambda deployment for DcisionAI MCP Server")
    print("=" * 60)
    
    api_url = deploy_lambda()
    
    if api_url:
        print("\n✅ Deployment completed successfully!")
        print(f"🎉 Your MCP server is now running on AWS Lambda!")
        print(f"🌐 Access URL: {api_url}")
    else:
        print("\n❌ Deployment failed!")
