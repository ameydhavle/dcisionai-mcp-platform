#!/usr/bin/env python3
"""
Deploy Simple Test Lambda Function
=================================
"""

import boto3
import json
import zipfile
import os
import tempfile

def create_lambda_package():
    """Create a simple Lambda deployment package."""
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
        with zipfile.ZipFile(tmp_file.name, 'w') as zip_file:
            zip_file.write('simple_test_lambda.py', 'lambda_function.py')
        
        # Copy to current directory for persistence
        persistent_zip = 'test-lambda.zip'
        with open(tmp_file.name, 'rb') as src, open(persistent_zip, 'wb') as dst:
            dst.write(src.read())
        
        os.unlink(tmp_file.name)
        return persistent_zip

def deploy_test_lambda():
    """Deploy the test Lambda function."""
    print("🚀 Deploying Simple Test Lambda Function")
    print("=" * 50)
    
    # Create deployment package
    print("📦 Creating Lambda deployment package...")
    zip_path = create_lambda_package()
    print(f"✅ Package created: {zip_path}")
    
    # Initialize AWS clients
    lambda_client = boto3.client('lambda')
    iam_client = boto3.client('iam')
    
    # Create IAM role if it doesn't exist
    role_name = 'dcisionai-test-lambda-role'
    try:
        iam_client.get_role(RoleName=role_name)
        print(f"ℹ️  IAM role {role_name} already exists")
    except iam_client.exceptions.NoSuchEntityException:
        print(f"🔧 Creating IAM role: {role_name}")
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for DcisionAI Test Lambda function'
        )
        
        # Attach basic execution policy
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        print(f"✅ IAM role created: {role_name}")
    
    # Get role ARN
    role_arn = iam_client.get_role(RoleName=role_name)['Role']['Arn']
    
    # Create or update Lambda function
    function_name = 'dcisionai-test-mcp-server'
    try:
        print(f"🔄 Updating Lambda function: {function_name}")
        with open(zip_path, 'rb') as zip_file:
            lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_file.read()
            )
        
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Runtime='python3.11',
            Handler='lambda_function.lambda_handler',
            Role=role_arn,
            Timeout=30,
            MemorySize=256
        )
        print(f"✅ Lambda function updated: {function_name}")
        
    except lambda_client.exceptions.ResourceNotFoundException:
        print(f"🆕 Creating Lambda function: {function_name}")
        with open(zip_path, 'rb') as zip_file:
            lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.11',
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_file.read()},
                Description='Simple test MCP server for DcisionAI',
                Timeout=30,
                MemorySize=256
            )
        print(f"✅ Lambda function created: {function_name}")
    
    # Create API Gateway
    api_gateway = boto3.client('apigateway')
    
    try:
        # Get existing API
        apis = api_gateway.get_rest_apis()
        api_id = None
        for api in apis['items']:
            if api['name'] == 'dcisionai-test-api':
                api_id = api['id']
                break
        
        if not api_id:
            print("🆕 Creating API Gateway...")
            api_response = api_gateway.create_rest_api(
                name='dcisionai-test-api',
                description='Test API for DcisionAI MCP Server',
                endpointConfiguration={'types': ['REGIONAL']}
            )
            api_id = api_response['id']
            print(f"✅ API Gateway created: {api_id}")
        else:
            print(f"ℹ️  Using existing API Gateway: {api_id}")
        
        # Get root resource
        resources = api_gateway.get_resources(restApiId=api_id)
        root_resource_id = None
        for resource in resources['items']:
            if resource['path'] == '/':
                root_resource_id = resource['id']
                break
        
        # Create /health resource
        health_resource = api_gateway.create_resource(
            restApiId=api_id,
            parentId=root_resource_id,
            pathPart='health'
        )
        
        # Create /mcp resource
        mcp_resource = api_gateway.create_resource(
            restApiId=api_id,
            parentId=root_resource_id,
            pathPart='mcp'
        )
        
        # Create methods
        for resource, method in [(health_resource, 'GET'), (mcp_resource, 'POST')]:
            api_gateway.put_method(
                restApiId=api_id,
                resourceId=resource['id'],
                httpMethod=method,
                authorizationType='NONE'
            )
            
            api_gateway.put_integration(
                restApiId=api_id,
                resourceId=resource['id'],
                httpMethod=method,
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:808953421331:function:{function_name}/invocations'
            )
        
        # Add CORS
        for resource in [health_resource, mcp_resource]:
            api_gateway.put_method(
                restApiId=api_id,
                resourceId=resource['id'],
                httpMethod='OPTIONS',
                authorizationType='NONE'
            )
            
            api_gateway.put_integration(
                restApiId=api_id,
                resourceId=resource['id'],
                httpMethod='OPTIONS',
                type='MOCK',
                integrationResponses={
                    '200': {
                        'statusCode': '200',
                        'responseParameters': {
                            'method.response.header.Access-Control-Allow-Origin': "'*'",
                            'method.response.header.Access-Control-Allow-Headers': "'Content-Type'",
                            'method.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'"
                        }
                    }
                },
                requestTemplates={'application/json': '{"statusCode": 200}'}
            )
            
            api_gateway.put_method_response(
                restApiId=api_id,
                resourceId=resource['id'],
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Origin': True,
                    'method.response.header.Access-Control-Allow-Headers': True,
                    'method.response.header.Access-Control-Allow-Methods': True
                }
            )
        
        # Deploy API
        deployment = api_gateway.create_deployment(
            restApiId=api_id,
            stageName='prod'
        )
        
        # Add Lambda permission
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId='api-gateway-invoke',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f'arn:aws:execute-api:us-east-1:808953421331:{api_id}/*/*'
        )
        
        api_url = f'https://{api_id}.execute-api.us-east-1.amazonaws.com/prod'
        print(f"✅ API Gateway deployed: {api_url}")
        
        return {
            'api_url': api_url,
            'health_url': f'{api_url}/health',
            'mcp_url': f'{api_url}/mcp'
        }
        
    except Exception as e:
        print(f"❌ API Gateway setup failed: {e}")
        return None

if __name__ == "__main__":
    result = deploy_test_lambda()
    
    if result:
        print("\n🎉 Test Lambda deployment completed!")
        print(f"🌐 API URL: {result['api_url']}")
        print(f"🔧 Health Check: {result['health_url']}")
        print(f"📡 MCP Endpoint: {result['mcp_url']}")
    else:
        print("\n❌ Test Lambda deployment failed!")
