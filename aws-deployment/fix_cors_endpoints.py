#!/usr/bin/env python3
"""
Fix CORS for New Endpoints
=========================
"""

import boto3

# AWS Configuration
REST_API_ID = 'h5w9r03xkf'
LAMBDA_ARN = 'arn:aws:lambda:us-east-1:808953421331:function:dcisionai-streaming-mcp-manufacturing'

# Endpoint resource IDs (from previous output)
ENDPOINTS = {
    '3d-landscape': 'hvxh4f',
    'sensitivity': 'sfpw3m',
    'monte-carlo': '1k2933',
    'business-impact': '5d7d6f'
}

def fix_cors_for_endpoint(endpoint_name, resource_id):
    """Fix CORS for a specific endpoint."""
    try:
        print(f"Fixing CORS for {endpoint_name} (ID: {resource_id})")
        
        apigateway = boto3.client('apigateway')
        
        # Add simple CORS integration for OPTIONS
        cors_integration = apigateway.put_integration(
            restApiId=REST_API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            type='MOCK',
            requestTemplates={
                'application/json': '{"statusCode": 200}'
            }
        )
        print(f"✅ Added CORS integration for {endpoint_name}")
        
        # Add method response for OPTIONS
        method_response = apigateway.put_method_response(
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
        print(f"✅ Added method response for {endpoint_name}")
        
        # Add integration response for OPTIONS
        integration_response = apigateway.put_integration_response(
            restApiId=REST_API_ID,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                'method.response.header.Access-Control-Allow-Origin': "'*'",
                'method.response.header.Access-Control-Allow-Methods': "'POST,OPTIONS'"
            }
        )
        print(f"✅ Added integration response for {endpoint_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix CORS for {endpoint_name}: {str(e)}")
        return False

def main():
    """Fix CORS for all new endpoints."""
    print("🔧 Fixing CORS for new endpoints...")
    
    success_count = 0
    for endpoint_name, resource_id in ENDPOINTS.items():
        if fix_cors_for_endpoint(endpoint_name, resource_id):
            success_count += 1
    
    print(f"\n✅ Successfully fixed CORS for {success_count}/{len(ENDPOINTS)} endpoints")
    
    if success_count == len(ENDPOINTS):
        print("🎉 All CORS issues fixed!")
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
        print("⚠️  Some CORS fixes failed")

if __name__ == "__main__":
    main()
