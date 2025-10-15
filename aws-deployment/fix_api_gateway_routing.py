#!/usr/bin/env python3
"""
Fix API Gateway routing for industry-specific workflow endpoints
"""

import boto3
import json
import time

def fix_api_gateway_routing():
    """Fix API Gateway routing for workflow endpoints"""
    
    # API Gateway details
    api_id = "h5w9r03xkf"
    lambda_function_name = "dcisionai-enhanced-workflows"
    lambda_arn = f"arn:aws:lambda:us-east-1:808953421331:function:{lambda_function_name}"
    
    print("🔧 Fixing API Gateway Routing for Workflow Endpoints")
    print("=" * 60)
    
    # Initialize API Gateway client
    apigateway = boto3.client('apigateway')
    
    try:
        # Get the workflows resource ID
        resources = apigateway.get_resources(restApiId=api_id)
        workflows_resource_id = None
        
        for resource in resources['items']:
            if resource['pathPart'] == 'workflows':
                workflows_resource_id = resource['id']
                break
        
        if not workflows_resource_id:
            print("❌ Workflows resource not found")
            return False
        
        print(f"✅ Found workflows resource: {workflows_resource_id}")
        
        # Create industry resource (e.g., /workflows/{industry})
        try:
            industry_resource = apigateway.create_resource(
                restApiId=api_id,
                parentId=workflows_resource_id,
                pathPart='{industry}'
            )
            industry_resource_id = industry_resource['id']
            print(f"✅ Created industry resource: {industry_resource_id}")
        except apigateway.exceptions.ConflictException:
            # Resource already exists, get its ID
            resources = apigateway.get_resources(restApiId=api_id)
            for resource in resources['items']:
                if resource.get('pathPart') == '{industry}' and resource.get('parentId') == workflows_resource_id:
                    industry_resource_id = resource['id']
                    print(f"✅ Found existing industry resource: {industry_resource_id}")
                    break
        
        # Create workflow_id resource (e.g., /workflows/{industry}/{workflow_id})
        try:
            workflow_resource = apigateway.create_resource(
                restApiId=api_id,
                parentId=industry_resource_id,
                pathPart='{workflow_id}'
            )
            workflow_resource_id = workflow_resource['id']
            print(f"✅ Created workflow resource: {workflow_resource_id}")
        except apigateway.exceptions.ConflictException:
            # Resource already exists, get its ID
            resources = apigateway.get_resources(restApiId=api_id)
            for resource in resources['items']:
                if resource.get('pathPart') == '{workflow_id}' and resource.get('parentId') == industry_resource_id:
                    workflow_resource_id = resource['id']
                    print(f"✅ Found existing workflow resource: {workflow_resource_id}")
                    break
        
        # Create execute resource (e.g., /workflows/{industry}/{workflow_id}/execute)
        try:
            execute_resource = apigateway.create_resource(
                restApiId=api_id,
                parentId=workflow_resource_id,
                pathPart='execute'
            )
            execute_resource_id = execute_resource['id']
            print(f"✅ Created execute resource: {execute_resource_id}")
        except apigateway.exceptions.ConflictException:
            # Resource already exists, get its ID
            resources = apigateway.get_resources(restApiId=api_id)
            for resource in resources['items']:
                if resource.get('pathPart') == 'execute' and resource.get('parentId') == workflow_resource_id:
                    execute_resource_id = resource['id']
                    print(f"✅ Found existing execute resource: {execute_resource_id}")
                    break
        
        # Add GET method to industry resource
        try:
            apigateway.put_method(
                restApiId=api_id,
                resourceId=industry_resource_id,
                httpMethod='GET',
                authorizationType='NONE'
            )
            print("✅ Added GET method to industry resource")
        except apigateway.exceptions.ConflictException:
            print("✅ GET method already exists on industry resource")
        
        # Add POST method to execute resource
        try:
            apigateway.put_method(
                restApiId=api_id,
                resourceId=execute_resource_id,
                httpMethod='POST',
                authorizationType='NONE'
            )
            print("✅ Added POST method to execute resource")
        except apigateway.exceptions.ConflictException:
            print("✅ POST method already exists on execute resource")
        
        # Add OPTIONS method to industry resource for CORS
        try:
            apigateway.put_method(
                restApiId=api_id,
                resourceId=industry_resource_id,
                httpMethod='OPTIONS',
                authorizationType='NONE'
            )
            print("✅ Added OPTIONS method to industry resource")
        except apigateway.exceptions.ConflictException:
            print("✅ OPTIONS method already exists on industry resource")
        
        # Add OPTIONS method to execute resource for CORS
        try:
            apigateway.put_method(
                restApiId=api_id,
                resourceId=execute_resource_id,
                httpMethod='OPTIONS',
                authorizationType='NONE'
            )
            print("✅ Added OPTIONS method to execute resource")
        except apigateway.exceptions.ConflictException:
            print("✅ OPTIONS method already exists on execute resource")
        
        # Create Lambda integration for industry GET method
        try:
            apigateway.put_integration(
                restApiId=api_id,
                resourceId=industry_resource_id,
                httpMethod='GET',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
            )
            print("✅ Created Lambda integration for industry GET method")
        except apigateway.exceptions.ConflictException:
            print("✅ Lambda integration already exists for industry GET method")
        
        # Create Lambda integration for execute POST method
        try:
            apigateway.put_integration(
                restApiId=api_id,
                resourceId=execute_resource_id,
                httpMethod='POST',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
            )
            print("✅ Created Lambda integration for execute POST method")
        except apigateway.exceptions.ConflictException:
            print("✅ Lambda integration already exists for execute POST method")
        
        # Add method responses for industry GET method
        try:
            apigateway.put_method_response(
                restApiId=api_id,
                resourceId=industry_resource_id,
                httpMethod='GET',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Origin': True
                }
            )
            print("✅ Added method response for industry GET method")
        except apigateway.exceptions.ConflictException:
            print("✅ Method response already exists for industry GET method")
        
        # Add method responses for execute POST method
        try:
            apigateway.put_method_response(
                restApiId=api_id,
                resourceId=execute_resource_id,
                httpMethod='POST',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Origin': True
                }
            )
            print("✅ Added method response for execute POST method")
        except apigateway.exceptions.ConflictException:
            print("✅ Method response already exists for execute POST method")
        
        # Add method responses for OPTIONS methods
        try:
            apigateway.put_method_response(
                restApiId=api_id,
                resourceId=industry_resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': True,
                    'method.response.header.Access-Control-Allow-Methods': True,
                    'method.response.header.Access-Control-Allow-Origin': True
                }
            )
            print("✅ Added method response for industry OPTIONS method")
        except apigateway.exceptions.ConflictException:
            print("✅ Method response already exists for industry OPTIONS method")
        
        try:
            apigateway.put_method_response(
                restApiId=api_id,
                resourceId=execute_resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': True,
                    'method.response.header.Access-Control-Allow-Methods': True,
                    'method.response.header.Access-Control-Allow-Origin': True
                }
            )
            print("✅ Added method response for execute OPTIONS method")
        except apigateway.exceptions.ConflictException:
            print("✅ Method response already exists for execute OPTIONS method")
        
        # Create CORS integration for industry OPTIONS method
        try:
            apigateway.put_integration(
                restApiId=api_id,
                resourceId=industry_resource_id,
                httpMethod='OPTIONS',
                type='MOCK',
                requestTemplates={
                    'application/json': '{"statusCode": 200}'
                }
            )
            # Add integration response
            apigateway.put_integration_response(
                restApiId=api_id,
                resourceId=industry_resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Methods': "'GET,OPTIONS'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'"
                }
            )
            print("✅ Created CORS integration for industry OPTIONS method")
        except apigateway.exceptions.ConflictException:
            print("✅ CORS integration already exists for industry OPTIONS method")
        
        # Create CORS integration for execute OPTIONS method
        try:
            apigateway.put_integration(
                restApiId=api_id,
                resourceId=execute_resource_id,
                httpMethod='OPTIONS',
                type='MOCK',
                requestTemplates={
                    'application/json': '{"statusCode": 200}'
                }
            )
            # Add integration response
            apigateway.put_integration_response(
                restApiId=api_id,
                resourceId=execute_resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Methods': "'POST,OPTIONS'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'"
                }
            )
            print("✅ Created CORS integration for execute OPTIONS method")
        except apigateway.exceptions.ConflictException:
            print("✅ CORS integration already exists for execute OPTIONS method")
        
        # Deploy the API
        print("\n🚀 Deploying API Gateway changes...")
        deployment = apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Fix workflow routing'
        )
        print(f"✅ API deployed successfully: {deployment['id']}")
        
        print("\n" + "=" * 60)
        print("🎉 API Gateway Routing Fixed!")
        print("\n📋 Available Endpoints:")
        print("   • GET  /workflows - List all industries")
        print("   • GET  /workflows/{industry} - Get workflows for industry")
        print("   • POST /workflows/{industry}/{workflow_id}/execute - Execute workflow")
        print("\n🔗 Test URLs:")
        print("   • https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod/workflows")
        print("   • https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod/workflows/manufacturing")
        print("   • https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod/workflows/marketing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing API Gateway routing: {e}")
        return False

if __name__ == "__main__":
    success = fix_api_gateway_routing()
    if success:
        print("\n✅ API Gateway routing fixed successfully!")
    else:
        print("\n❌ Failed to fix API Gateway routing")
