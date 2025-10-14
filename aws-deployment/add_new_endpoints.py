#!/usr/bin/env python3
"""
Add New Endpoints to API Gateway
===============================
"""

import boto3
import json

# AWS Configuration
REST_API_ID = '2dtpy57vn2'
ROOT_RESOURCE_ID = 'w05e0amsze'
LAMBDA_ARN = 'arn:aws:lambda:us-east-1:808953421331:function:dcisionai-streaming-mcp-manufacturing'

# New endpoints to add
NEW_ENDPOINTS = [
    'sensitivity',
    'monte-carlo', 
    'business-impact'
]

def add_endpoint(endpoint_name):
    """Add a new endpoint to API Gateway."""
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
        
        # Add Lambda integration
        integration_response = apigateway.put_integration(
            restApiId=REST_API_ID,
            resourceId=resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{LAMBDA_ARN}/invocations'
        )
        print(f"✅ Added Lambda integration to {endpoint_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to add endpoint {endpoint_name}: {str(e)}")
        return False

def main():
    """Add all new endpoints."""
    print("🚀 Adding new endpoints to API Gateway...")
    
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
    else:
        print("⚠️  Some endpoints failed to add")

if __name__ == "__main__":
    main()
