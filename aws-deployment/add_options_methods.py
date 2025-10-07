#!/usr/bin/env python3
"""
Add OPTIONS Methods to API Gateway
=================================

This script adds OPTIONS methods to all resources for CORS support.
"""

import boto3

def add_options_methods():
    """Add OPTIONS methods to all API Gateway resources."""
    print("🔧 Adding OPTIONS methods for CORS...")
    
    api_client = boto3.client('apigateway')
    api_id = 'h5w9r03xkf'
    
    # Get all resources
    resources = api_client.get_resources(restApiId=api_id)
    
    for resource in resources['items']:
        resource_id = resource['id']
        path = resource['path']
        
        if path != '/':  # Skip root resource
            try:
                # Check if OPTIONS method already exists
                try:
                    api_client.get_method(restApiId=api_id, resourceId=resource_id, httpMethod='OPTIONS')
                    print(f"ℹ️  OPTIONS method already exists for {path}")
                    continue
                except:
                    pass  # Method doesn't exist, continue to create it
                
                # Create OPTIONS method
                api_client.put_method(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    authorizationType='NONE'
                )
                
                # Create mock integration for OPTIONS
                api_client.put_integration(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod='OPTIONS',
                    type='MOCK',
                    requestTemplates={
                        'application/json': '{"statusCode": 200}'
                    }
                )
                
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
                
                print(f"✅ Added OPTIONS method for {path}")
                
            except Exception as e:
                print(f"⚠️  Error adding OPTIONS for {path}: {e}")
    
    # Deploy the changes
    try:
        api_client.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Add OPTIONS methods for CORS'
        )
        print("✅ Deployed OPTIONS methods to prod stage")
    except Exception as e:
        print(f"⚠️  Deployment warning: {e}")
    
    print("\n🌐 OPTIONS Methods Added!")
    print("CORS should now work properly for all endpoints.")

def main():
    """Main function."""
    add_options_methods()

if __name__ == "__main__":
    main()
