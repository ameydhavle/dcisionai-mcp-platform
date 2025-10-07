#!/usr/bin/env python3
"""
Deploy Streaming Lambda Function
===============================

This script deploys the streaming Lambda function with separate endpoints
for each optimization step.
"""

import boto3
import json
import zipfile
import tempfile
import os
from pathlib import Path

def create_lambda_package():
    """Create deployment package for streaming Lambda."""
    print("📦 Creating Lambda deployment package...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Copy the streaming Lambda function
        lambda_file = temp_path / "lambda_function.py"
        with open("streaming_lambda.py", "r") as f:
            lambda_file.write_text(f.read())
        
        # Create zip file
        zip_path = Path("streaming-mcp-server.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(lambda_file, "lambda_function.py")
        
        print(f"✅ Created deployment package: {zip_path}")
        return str(zip_path)

def create_iam_role():
    """Create IAM role for streaming Lambda function."""
    print("🔐 Creating IAM role for streaming Lambda...")
    
    iam_client = boto3.client('iam')
    role_name = 'dcisionai-streaming-lambda-role'
    
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
    
    try:
        # Create role
        iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for DcisionAI Streaming Lambda function'
        )
        print(f"✅ Created IAM role: {role_name}")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"ℹ️  IAM role already exists: {role_name}")
    
    # Attach policies
    policies = [
        'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
        'arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
    ]
    
    for policy_arn in policies:
        try:
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            print(f"✅ Attached policy: {policy_arn}")
        except Exception as e:
            print(f"⚠️  Policy attachment warning: {e}")
    
    return f"arn:aws:iam::{boto3.client('sts').get_caller_identity()['Account']}:role/{role_name}"

def create_lambda_function(package_path, role_arn):
    """Create streaming Lambda function."""
    print("🚀 Creating streaming Lambda function...")
    
    lambda_client = boto3.client('lambda')
    function_name = 'dcisionai-streaming-mcp-manufacturing'
    
    # Read the deployment package
    with open(package_path, 'rb') as f:
        zip_content = f.read()
    
    try:
        # Create function
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='DcisionAI Streaming Manufacturing Optimization Lambda',
            Timeout=60,  # 60 seconds timeout
            MemorySize=512,
            Environment={
                'Variables': {
                    'LOG_LEVEL': 'INFO'
                }
            }
        )
        print(f"✅ Created Lambda function: {function_name}")
        return response['FunctionArn']
        
    except lambda_client.exceptions.ResourceConflictException:
        print(f"ℹ️  Lambda function already exists, updating...")
        
        # Update function code
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        # Update function configuration
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Timeout=60,
            MemorySize=512,
            Environment={
                'Variables': {
                    'LOG_LEVEL': 'INFO'
                }
            }
        )
        
        print(f"✅ Updated Lambda function: {function_name}")
        return f"arn:aws:lambda:us-east-1:{boto3.client('sts').get_caller_identity()['Account']}:function:{function_name}"

def create_api_gateway(function_arn):
    """Create API Gateway for streaming endpoints."""
    print("🌐 Creating API Gateway for streaming endpoints...")
    
    api_client = boto3.client('apigateway')
    lambda_client = boto3.client('lambda')
    
    # Create API
    api_name = 'dcisionai-streaming-mcp-api'
    try:
        api_response = api_client.create_rest_api(
            name=api_name,
            description='DcisionAI Streaming Manufacturing Optimization API',
            endpointConfiguration={'types': ['REGIONAL']}
        )
        api_id = api_response['id']
        print(f"✅ Created API Gateway: {api_id}")
    except Exception as e:
        print(f"⚠️  API creation warning: {e}")
        # Try to find existing API
        apis = api_client.get_rest_apis()
        for api in apis['items']:
            if api['name'] == api_name:
                api_id = api['id']
                print(f"ℹ️  Using existing API: {api_id}")
                break
        else:
            raise Exception("Could not create or find API Gateway")
    
    # Get root resource
    resources = api_client.get_resources(restApiId=api_id)
    root_resource_id = None
    for resource in resources['items']:
        if resource['path'] == '/':
            root_resource_id = resource['id']
            break
    
    # Create resources for each endpoint
    endpoints = ['health', 'intent', 'data', 'model', 'solve', 'mcp']
    
    for endpoint in endpoints:
        try:
            # Create resource
            resource_response = api_client.create_resource(
                restApiId=api_id,
                parentId=root_resource_id,
                pathPart=endpoint
            )
            resource_id = resource_response['id']
            
            # Create method
            api_client.put_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='POST',
                authorizationType='NONE'
            )
            
            # Create integration
            lambda_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations"
            api_client.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='POST',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=lambda_uri
            )
            
            print(f"✅ Created endpoint: /{endpoint}")
            
        except Exception as e:
            print(f"⚠️  Endpoint creation warning for /{endpoint}: {e}")
    
    # Add GET method for health endpoint
    try:
        health_resource = None
        for resource in resources['items']:
            if resource['path'] == '/health':
                health_resource = resource
                break
        
        if health_resource:
            api_client.put_method(
                restApiId=api_id,
                resourceId=health_resource['id'],
                httpMethod='GET',
                authorizationType='NONE'
            )
            
            lambda_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations"
            api_client.put_integration(
                restApiId=api_id,
                resourceId=health_resource['id'],
                httpMethod='GET',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=lambda_uri
            )
            
            print("✅ Added GET method for /health")
    except Exception as e:
        print(f"⚠️  GET method warning: {e}")
    
    # Deploy API
    try:
        deployment_response = api_client.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Production deployment for streaming endpoints'
        )
        print(f"✅ Deployed API to prod stage")
    except Exception as e:
        print(f"⚠️  Deployment warning: {e}")
    
    # Add Lambda permission for API Gateway
    try:
        account_id = boto3.client('sts').get_caller_identity()['Account']
        lambda_client.add_permission(
            FunctionName=function_arn.split(':')[-1],
            StatementId=f'api-gateway-invoke-{api_id}',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f'arn:aws:execute-api:us-east-1:{account_id}:{api_id}/*/*'
        )
        print("✅ Added Lambda permission for API Gateway")
    except Exception as e:
        print(f"⚠️  Permission warning: {e}")
    
    # Get API URL
    api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
    print(f"🌐 API URL: {api_url}")
    
    return api_url

def main():
    """Main deployment function."""
    print("🚀 Deploying DcisionAI Streaming Lambda Function")
    print("=" * 50)
    
    try:
        # Create deployment package
        package_path = create_lambda_package()
        
        # Create IAM role
        role_arn = create_iam_role()
        
        # Create Lambda function
        function_arn = create_lambda_function(package_path, role_arn)
        
        # Create API Gateway
        api_url = create_api_gateway(function_arn)
        
        print("\n" + "=" * 50)
        print("✅ STREAMING DEPLOYMENT COMPLETE!")
        print("=" * 50)
        print(f"🌐 API URL: {api_url}")
        print(f"🔗 Health Check: {api_url}/health")
        print(f"🎯 Intent Classification: {api_url}/intent")
        print(f"📊 Data Analysis: {api_url}/data")
        print(f"🔧 Model Building: {api_url}/model")
        print(f"⚡ Optimization Solving: {api_url}/solve")
        print(f"🔄 Backward Compatibility: {api_url}/mcp")
        print("\n📝 Next Steps:")
        print("1. Update frontend to use streaming endpoints")
        print("2. Test each endpoint individually")
        print("3. Implement real-time UI updates")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        raise

if __name__ == "__main__":
    main()
