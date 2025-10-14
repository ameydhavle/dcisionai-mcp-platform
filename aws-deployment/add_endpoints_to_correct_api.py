#!/usr/bin/env python3
"""
Add New Endpoints to Correct API Gateway
=======================================
"""

import boto3
import json

# AWS Configuration - CORRECT API Gateway
REST_API_ID = 'h5w9r03xkf'  # This is the correct API Gateway
ROOT_RESOURCE_ID = 'y40hoeuzo7'  # Root resource ID
LAMBDA_ARN = 'arn:aws:lambda:us-east-1:808953421331:function:dcisionai-streaming-mcp-manufacturing'

# New endpoints to add
NEW_ENDPOINTS = [
    '3d-landscape',
    'sensitivity',
    'monte-carlo', 
    'business-impact'
]

def add_endpoint(endpoint_name):
    """Add a new endpoint to the correct API Gateway."""
    try:
        print(f"Adding endpoint: {endpoint_name}")
        
        # Create resource
        apigateway = boto3.client('apigateway')
        
        resource_response = apigateway.create_resource(
            restApiId=REST_API_ID,
            parentId=ROOT_RESOURCE_ID,
            pathPart=endpoint_name
        )
        
        resource_id = resource_response['id']
        print(f"✅ Created resource {endpoint_name} with ID: {resource_id}")
        
        # Add POST method
        method_response = apigateway.put_method(
            restApiId=REST_API_ID,
            resourceId=resource_id,
            httpMethod='POST',
            authorizationType='NONE'
        )
        print(f"✅ Added POST method to {endpoint_name}")
        
        # Add OPTIONS method for CORS
        options_response = apigateway.put_method(
            restApiId=REST_API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            authorizationType='NONE'
        )
        print(f"✅ Added OPTIONS method to {endpoint_name}")
        
        # Add Lambda integration for POST
        integration_response = apigateway.put_integration(
            restApiId=REST_API_ID,
            resourceId=resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{LAMBDA_ARN}/invocations'
        )
        print(f"✅ Added Lambda integration to {endpoint_name}")
        
        # Add CORS integration for OPTIONS
        cors_integration = apigateway.put_integration(
            restApiId=REST_API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            type='MOCK',
            integrationResponses={
                '200': {
                    'statusCode': '200',
                    'responseParameters': {
                        'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                        'method.response.header.Access-Control-Allow-Origin': "'*'",
                        'method.response.header.Access-Control-Allow-Methods': "'POST,OPTIONS'"
                    }
                }
            }
        )
        print(f"✅ Added CORS integration to {endpoint_name}")
        
        # Add method responses for OPTIONS
        method_response_options = apigateway.put_method_response(
            restApiId=REST_API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': True,
                'method.response.header.Access-Control-Allow-Origin': True,
                'method.response.header.Access-Control-Allow-Methods': True
            }
        )
        print(f"✅ Added method response for OPTIONS to {endpoint_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to add endpoint {endpoint_name}: {str(e)}")
        return False

def main():
    """Add all new endpoints to the correct API Gateway."""
    print("🚀 Adding new endpoints to CORRECT API Gateway (h5w9r03xkf)...")
    
    success_count = 0
    for endpoint in NEW_ENDPOINTS:
        if add_endpoint(endpoint):
            success_count += 1
    
    print(f"\n✅ Successfully added {success_count}/{len(NEW_ENDPOINTS)} endpoints")
    
    if success_count == len(NEW_ENDPOINTS):
        print("🎉 All new endpoints added successfully!")
        print("\nNew endpoints available:")
        for endpoint in NEW_ENDPOINTS:
            print(f"  - POST /{endpoint}")
        print("\nDeploying API Gateway...")
        
        # Deploy the API Gateway
        try:
            apigateway = boto3.client('apigateway')
            deployment = apigateway.create_deployment(
                restApiId=REST_API_ID,
                stageName='prod'
            )
            print(f"✅ API Gateway deployed successfully: {deployment['id']}")
        except Exception as e:
            print(f"❌ Failed to deploy API Gateway: {str(e)}")
    else:
        print("⚠️  Some endpoints failed to add")

if __name__ == "__main__":
    main()
