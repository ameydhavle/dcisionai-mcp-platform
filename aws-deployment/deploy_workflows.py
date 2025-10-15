#!/usr/bin/env python3
"""
Deploy Enhanced Lambda with Workflow Support
===========================================

Deploy the enhanced lambda function with predefined workflow capabilities.
"""

import boto3
import json
import zipfile
import os
from datetime import datetime

def create_workflow_lambda_package():
    """Create deployment package for workflow-enabled lambda."""
    
    package_name = f"enhanced-workflows-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add the main lambda function
        zip_file.write('enhanced_lambda_with_workflows.py', 'lambda_function.py')
        
        # Add workflow modules
        zip_file.write('workflow_templates.py', 'workflow_templates.py')
        zip_file.write('workflow_api.py', 'workflow_api.py')
        
        # Add any additional dependencies if needed
        # Note: boto3 is already available in Lambda runtime
    
    print(f"✅ Created deployment package: {package_name}")
    return package_name

def deploy_lambda_function(package_name: str, function_name: str = "dcisionai-enhanced-workflows"):
    """Deploy the lambda function with workflow support."""
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Read the deployment package
        with open(package_name, 'rb') as f:
            zip_content = f.read()
        
        # Check if function exists
        try:
            lambda_client.get_function(FunctionName=function_name)
            print(f"📝 Updating existing function: {function_name}")
            
            # Update function code
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            
        except lambda_client.exceptions.ResourceNotFoundException:
            print(f"🆕 Creating new function: {function_name}")
            
            # Create new function
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.9',
                Role='arn:aws:iam::808953421331:role/dcisionai-lambda-execution-role-production',  # Production role
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='DcisionAI Enhanced Lambda with Predefined Workflows',
                Timeout=300,  # 5 minutes
                MemorySize=1024,
                Environment={
                    'Variables': {
                        'ENVIRONMENT': 'production',
                        'WORKFLOWS_ENABLED': 'true'
                    }
                }
            )
        
        print(f"✅ Lambda function deployed successfully!")
        print(f"   Function ARN: {response['FunctionArn']}")
        print(f"   Function Name: {response['FunctionName']}")
        print(f"   Runtime: {response['Runtime']}")
        print(f"   Handler: {response['Handler']}")
        
        return response
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return None

def update_api_gateway_integration(function_name: str):
    """Update API Gateway to use the new lambda function."""
    
    try:
        api_gateway = boto3.client('apigateway', region_name='us-east-1')
        
        # Get the API Gateway ID (you'll need to update this with your actual API ID)
        api_id = "h5w9r03xkf"  # Update with your API Gateway ID
        
        # Get all resources
        resources = api_gateway.get_resources(restApiId=api_id)
        
        # Find the root resource
        root_resource_id = None
        for resource in resources['items']:
            if resource['path'] == '/':
                root_resource_id = resource['id']
                break
        
        if not root_resource_id:
            print("❌ Could not find root resource in API Gateway")
            return False
        
        # Update the integration for the root resource
        try:
            api_gateway.put_integration(
                restApiId=api_id,
                resourceId=root_resource_id,
                httpMethod='ANY',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:808953421331:function:{function_name}/invocations'
            )
            
            print(f"✅ API Gateway integration updated for function: {function_name}")
            return True
            
        except Exception as e:
            print(f"⚠️  API Gateway integration update failed: {str(e)}")
            print("   You may need to update the integration manually in the AWS Console")
            return False
            
    except Exception as e:
        print(f"❌ API Gateway update failed: {str(e)}")
        return False

def test_workflow_endpoints():
    """Test the deployed workflow endpoints."""
    
    import requests
    
    base_url = "https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod"
    
    test_endpoints = [
        "/health",
        "/workflows",
        "/workflows/manufacturing",
        "/workflows/healthcare",
        "/workflows/retail"
    ]
    
    print("\n🧪 Testing workflow endpoints...")
    
    for endpoint in test_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}: {response.status_code}")
                if 'workflows' in data:
                    print(f"   Found {len(data['workflows'])} workflows")
                elif 'industries' in data:
                    print(f"   Found {len(data['industries'])} industries")
            else:
                print(f"❌ {endpoint}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ {endpoint}: Error - {str(e)}")

def main():
    """Main deployment function."""
    
    print("🚀 Deploying DcisionAI Enhanced Lambda with Workflows")
    print("=" * 60)
    
    # Step 1: Create deployment package
    print("\n📦 Creating deployment package...")
    package_name = create_workflow_lambda_package()
    
    # Step 2: Deploy lambda function
    print("\n🚀 Deploying lambda function...")
    function_name = "dcisionai-enhanced-workflows"
    deployment_result = deploy_lambda_function(package_name, function_name)
    
    if not deployment_result:
        print("❌ Deployment failed. Exiting.")
        return
    
    # Step 3: Update API Gateway (optional)
    print("\n🔗 Updating API Gateway integration...")
    update_api_gateway_integration(function_name)
    
    # Step 4: Test endpoints
    print("\n🧪 Testing deployment...")
    test_workflow_endpoints()
    
    # Step 5: Cleanup
    print(f"\n🧹 Cleaning up deployment package: {package_name}")
    try:
        os.remove(package_name)
        print("✅ Cleanup completed")
    except:
        print("⚠️  Could not remove deployment package")
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Update your frontend to use the new workflow endpoints")
    print("2. Test the predefined workflows in your application")
    print("3. Monitor the lambda function logs for any issues")
    print("4. Update your API documentation with the new workflow endpoints")

if __name__ == "__main__":
    main()
