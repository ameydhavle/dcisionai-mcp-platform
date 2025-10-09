#!/usr/bin/env python3
"""
Complete CORS Fix for API Gateway
"""

import boto3
import json

def fix_cors_for_all_endpoints():
    """Fix CORS for all API Gateway endpoints."""
    
    api_gateway = boto3.client('apigateway')
    api_id = 'ryjnyrgm19'
    
    print(f"🔧 Fixing CORS for API Gateway: {api_id}")
    
    # Get all resources
    resources = api_gateway.get_resources(restApiId=api_id)
    
    for resource in resources['items']:
        if resource.get('pathPart') in ['health', 'intent', 'data', 'model', 'solve']:
            resource_id = resource['id']
            path_part = resource['pathPart']
            
            print(f"🔧 Fixing CORS for /{path_part}")
            
            try:
                # Delete existing OPTIONS method if it exists
                try:
                    api_gateway.delete_method(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='OPTIONS'
                    )
                    print(f"  ✅ Deleted existing OPTIONS method")
                except:
                    pass
                
                # Create OPTIONS method
                api_gateway.put_method(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    authorizationType='NONE'
                )
                print(f"  ✅ Created OPTIONS method")
                
                # Create MOCK integration
                api_gateway.put_integration(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    type='MOCK',
                    integrationHttpMethod='OPTIONS',
                    requestTemplates={
                        'application/json': '{"statusCode": 200}'
                    }
                )
                print(f"  ✅ Created MOCK integration")
                
                # Create method response
                api_gateway.put_method_response(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    statusCode='200',
                    responseParameters={
                        'method.response.header.Access-Control-Allow-Headers': True,
                        'method.response.header.Access-Control-Allow-Methods': True,
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
                print(f"  ✅ Created method response")
                
                # Create integration response with proper header mapping
                api_gateway.put_integration_response(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    statusCode='200',
                    responseParameters={
                        'integration.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                        'integration.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'",
                        'integration.response.header.Access-Control-Allow-Origin': "'*'"
                    },
                    responseTemplates={
                        'application/json': ''
                    }
                )
                print(f"  ✅ Created integration response")
                
            except Exception as e:
                print(f"  ❌ Error fixing CORS for /{path_part}: {e}")
    
    # Deploy the API
    print(f"🚀 Deploying API with CORS fixes...")
    deployment = api_gateway.create_deployment(
        restApiId=api_id,
        stageName='prod'
    )
    print(f"✅ API deployed successfully")
    
    return True

if __name__ == "__main__":
    fix_cors_for_all_endpoints()