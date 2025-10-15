#!/usr/bin/env python3
"""
Update API Gateway timeout for workflow execution
"""

import boto3
import json

def update_api_gateway_timeout():
    """Update API Gateway timeout to 60 seconds for workflow execution."""
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    api_id = 'h5w9r03xkf'
    
    # Get the execute resource ID
    resources = apigateway.get_resources(restApiId=api_id)
    execute_resource_id = None
    
    for resource in resources['items']:
        if resource.get('path') == '/workflows/{industry}/{workflow_id}/execute':
            execute_resource_id = resource['id']
            break
    
    if not execute_resource_id:
        print("❌ Could not find execute resource")
        return
    
    print(f"✅ Found execute resource: {execute_resource_id}")
    
    # Update the integration timeout
    try:
        response = apigateway.update_integration(
            restApiId=api_id,
            resourceId=execute_resource_id,
            httpMethod='POST',
            patchOperations=[
                {
                    'op': 'replace',
                    'path': '/timeoutInMillis',
                    'value': '60000'
                }
            ]
        )
        print("✅ Updated API Gateway timeout to 60 seconds")
        
        # Deploy the changes
        deployment = apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Updated timeout for workflow execution'
        )
        print(f"✅ Deployed changes: {deployment['id']}")
        
    except Exception as e:
        print(f"❌ Error updating timeout: {e}")

if __name__ == "__main__":
    update_api_gateway_timeout()
