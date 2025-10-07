#!/usr/bin/env python3
"""
Complete CORS Fix for Streaming API
==================================

This script completely fixes CORS for all endpoints.
"""

import boto3
import json

def fix_cors_complete():
    """Completely fix CORS for all endpoints."""
    print("🔧 Completely fixing CORS for streaming API...")
    
    api_client = boto3.client('apigateway')
    api_id = 'h5w9r03xkf'
    
    # Get all resources
    resources = api_client.get_resources(restApiId=api_id)
    
    endpoints = ['intent', 'data', 'model', 'solve', 'mcp', 'health']
    
    for resource in resources['items']:
        resource_id = resource['id']
        path_part = resource.get('pathPart', '')
        
        if path_part in endpoints:
            print(f"🔧 Fixing CORS for /{path_part}...")
            
            try:
                # Delete existing OPTIONS method if it exists
                try:
                    api_client.delete_method(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='OPTIONS'
                    )
                    print(f"  ✅ Deleted existing OPTIONS method for /{path_part}")
                except:
                    pass
                
                # Create new OPTIONS method
                api_client.put_method(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    authorizationType='NONE'
                )
                print(f"  ✅ Created OPTIONS method for /{path_part}")
                
                # Create mock integration
                api_client.put_integration(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    type='MOCK',
                    requestTemplates={
                        'application/json': '{"statusCode": 200}'
                    }
                )
                print(f"  ✅ Created integration for /{path_part}")
                
                # Create method response
                api_client.put_method_response(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    statusCode='200',
                    responseParameters={
                        'method.response.header.Access-Control-Allow-Origin': True,
                        'method.response.header.Access-Control-Allow-Methods': True,
                        'method.response.header.Access-Control-Allow-Headers': True
                    }
                )
                print(f"  ✅ Created method response for /{path_part}")
                
                # Create integration response
                api_client.put_integration_response(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    statusCode='200',
                    responseParameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'",
                        'method.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'",
                        'method.response.header.Access-Control-Allow-Headers': "'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token'"
                    }
                )
                print(f"  ✅ Created integration response for /{path_part}")
                
            except Exception as e:
                print(f"  ❌ Error fixing /{path_part}: {e}")
    
    # Deploy the changes
    try:
        api_client.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Complete CORS fix deployment'
        )
        print("✅ Deployed CORS fixes to prod stage")
    except Exception as e:
        print(f"⚠️  Deployment warning: {e}")
    
    print("\n🌐 Complete CORS Fix Applied!")
    print("All endpoints should now support CORS properly.")

def main():
    """Main function."""
    fix_cors_complete()

if __name__ == "__main__":
    main()
