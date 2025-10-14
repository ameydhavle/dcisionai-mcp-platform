#!/usr/bin/env python3
"""
Deploy Context-Aware Lambda Function
"""

import boto3
import zipfile
import os
import json
from pathlib import Path

def create_lambda_package():
    """Create deployment package for the context-aware Lambda function."""
    print("📦 Creating Lambda deployment package...")
    
    # Create a temporary directory for the package
    package_dir = Path("/tmp/lambda_package")
    package_dir.mkdir(exist_ok=True)
    
    # Copy the Lambda function
    lambda_file = Path("aws-deployment/context_aware_lambda.py")
    if lambda_file.exists():
        import shutil
        shutil.copy2(lambda_file, package_dir / "lambda_function.py")
        print("✅ Lambda function copied")
    else:
        print("❌ Lambda function file not found")
        return None
    
    # Create zip file
    zip_path = Path("context_aware_lambda.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                zipf.write(file_path, file_path.relative_to(package_dir))
    
    print(f"✅ Package created: {zip_path}")
    return str(zip_path)

def deploy_lambda():
    """Deploy the context-aware Lambda function."""
    print("🚀 Deploying Context-Aware Lambda Function")
    print("=" * 50)
    
    # Create deployment package
    package_path = create_lambda_package()
    if not package_path:
        return False
    
    # Initialize AWS clients
    lambda_client = boto3.client('lambda')
    iam_client = boto3.client('iam')
    
    # Create IAM role for Lambda
    role_name = 'dcisionai-context-aware-lambda-role'
    try:
        # Try to get existing role
        role_response = iam_client.get_role(RoleName=role_name)
        role_arn = role_response['Role']['Arn']
        print(f"✅ Using existing IAM role: {role_arn}")
    except iam_client.exceptions.NoSuchEntityException:
        # Create new role
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
        
        role_response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for DcisionAI Context-Aware Lambda Function'
        )
        role_arn = role_response['Role']['Arn']
        print(f"✅ Created IAM role: {role_arn}")
        
        # Attach policies
        policies = [
            'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
            'arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
        ]
        
        for policy_arn in policies:
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
        
        print("✅ Attached IAM policies")
    
    # Wait for role to be ready
    import time
    time.sleep(10)
    
    # Read the deployment package
    with open(package_path, 'rb') as f:
        zip_content = f.read()
    
    # Create or update Lambda function
    function_name = 'dcisionai-context-aware-manufacturing'
    try:
        # Try to update existing function
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        print(f"✅ Updated Lambda function: {function_name}")
    except lambda_client.exceptions.ResourceNotFoundException:
        # Create new function
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='DcisionAI Context-Aware Manufacturing Optimizer',
            Timeout=60,
            MemorySize=512
        )
        print(f"✅ Created Lambda function: {function_name}")
    
    # Create API Gateway
    api_gateway = boto3.client('apigateway')
    
    # Check if API already exists
    try:
        apis = api_gateway.get_rest_apis()
        api_id = None
        for api in apis['items']:
            if api['name'] == 'dcisionai-context-aware-api':
                api_id = api['id']
                break
        
        if not api_id:
            # Create new API
            api_response = api_gateway.create_rest_api(
                name='dcisionai-context-aware-api',
                description='DcisionAI Context-Aware Manufacturing API',
                endpointConfiguration={'types': ['REGIONAL']}
            )
            api_id = api_response['id']
            print(f"✅ Created API Gateway: {api_id}")
        else:
            print(f"✅ Using existing API Gateway: {api_id}")
        
        # Get root resource
        resources = api_gateway.get_resources(restApiId=api_id)
        root_resource_id = None
        for resource in resources['items']:
            if resource['path'] == '/':
                root_resource_id = resource['id']
                break
        
        # Create endpoints
        endpoints = ['health', 'intent', 'data', 'model', 'solve']
        for endpoint in endpoints:
            # Create resource
            resource_response = api_gateway.create_resource(
                restApiId=api_id,
                parentId=root_resource_id,
                pathPart=endpoint
            )
            resource_id = resource_response['id']
            
            # Create method
            api_gateway.put_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='POST',
                authorizationType='NONE'
            )
            
            # Create integration
            lambda_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:808953421331:function:{function_name}/invocations"
            api_gateway.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='POST',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=lambda_uri
            )
            
            # Add Lambda permission
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=f'api-gateway-{endpoint}',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f'arn:aws:execute-api:us-east-1:808953421331:{api_id}/*/*'
            )
            
            print(f"✅ Created endpoint: /{endpoint}")
        
        # Deploy API
        deployment_response = api_gateway.create_deployment(
            restApiId=api_id,
            stageName='prod'
        )
        print(f"✅ Deployed API to prod stage")
        
        # Get API URL
        api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
        print(f"🌐 API URL: {api_url}")
        
        return api_url
        
    except Exception as e:
        print(f"❌ API Gateway setup failed: {e}")
        return None

if __name__ == "__main__":
    api_url = deploy_lambda()
    if api_url:
        print(f"\n🎉 Context-Aware Lambda deployed successfully!")
        print(f"🌐 API URL: {api_url}")
        print(f"🔧 Test with: curl {api_url}/health")
    else:
        print("\n❌ Deployment failed!")
