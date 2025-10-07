#!/usr/bin/env python3
"""
Fix CORS Configuration for Streaming API
=======================================

This script fixes the CORS configuration for the streaming API Gateway.
"""

import boto3
import json

def fix_cors_configuration():
    """Fix CORS configuration for the streaming API."""
    print("🔧 Fixing CORS configuration for streaming API...")
    
    api_client = boto3.client('apigateway')
    api_id = 'h5w9r03xkf'
    
    # Get all resources
    resources = api_client.get_resources(restApiId=api_id)
    
    # Enable CORS for each resource
    for resource in resources['items']:
        resource_id = resource['id']
        path = resource['path']
        
        if path != '/':  # Skip root resource
            try:
                # Add OPTIONS method for CORS
                api_client.put_method(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    authorizationType='NONE'
                )
                
                # Add CORS integration
                api_client.put_integration(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    type='MOCK',
                    integrationResponses={
                        '200': {
                            'statusCode': '200',
                            'responseParameters': {
                                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                                'method.response.header.Access-Control-Allow-Origin': "'*'",
                                'method.response.header.Access-Control-Allow-Methods': "'GET,POST,PUT,DELETE,OPTIONS'"
                            },
                            'responseTemplates': {
                                'application/json': '{"statusCode": 200}'
                            }
                        }
                    },
                    requestTemplates={
                        'application/json': '{"statusCode": 200}'
                    }
                )
                
                # Add method response
                api_client.put_method_response(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    statusCode='200',
                    responseParameters={
                        'method.response.header.Access-Control-Allow-Headers': True,
                        'method.response.header.Access-Control-Allow-Origin': True,
                        'method.response.header.Access-Control-Allow-Methods': True
                    }
                )
                
                # Add integration response
                api_client.put_integration_response(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    statusCode='200',
                    responseParameters={
                        'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                        'method.response.header.Access-Control-Allow-Origin': "'*'",
                        'method.response.header.Access-Control-Allow-Methods': "'GET,POST,PUT,DELETE,OPTIONS'"
                    }
                )
                
                print(f"✅ Added CORS for {path}")
                
            except Exception as e:
                print(f"⚠️  CORS warning for {path}: {e}")
    
    # Update existing methods to include CORS headers
    for resource in resources['items']:
        resource_id = resource['id']
        path = resource['path']
        
        if path != '/':  # Skip root resource
            try:
                # Get methods for this resource
                methods = api_client.get_method(restApiId=api_id, resourceId=resource_id, httpMethod='POST')
                
                # Update method response to include CORS headers
                try:
                    api_client.put_method_response(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='POST',
                        statusCode='200',
                        responseParameters={
                            'method.response.header.Access-Control-Allow-Origin': True
                        }
                    )
                except:
                    pass  # Method response might already exist
                
                # Update integration response to include CORS headers
                try:
                    api_client.put_integration_response(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='POST',
                        statusCode='200',
                        responseParameters={
                            'method.response.header.Access-Control-Allow-Origin': "'*'"
                        }
                    )
                except:
                    pass  # Integration response might already exist
                
                print(f"✅ Updated CORS headers for {path}")
                
            except Exception as e:
                print(f"⚠️  CORS header update warning for {path}: {e}")
    
    # Deploy the changes
    try:
        api_client.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='CORS fix deployment'
        )
        print("✅ Deployed CORS fixes to prod stage")
    except Exception as e:
        print(f"⚠️  Deployment warning: {e}")
    
    print("\n🌐 CORS Configuration Complete!")
    print("The API should now accept requests from your frontend domain.")

def main():
    """Main function."""
    fix_cors_configuration()

if __name__ == "__main__":
    main()
