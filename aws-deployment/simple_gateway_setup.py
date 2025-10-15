#!/usr/bin/env python3
"""
Simple AgentCore Gateway Setup for DcisionAI
==========================================

This script creates a simplified AgentCore Gateway setup focusing on
the core optimization workflow functionality.
"""

import boto3
import json
from datetime import datetime

def create_simple_gateway():
    """Create a simple AgentCore Gateway for optimization workflows."""
    print("🚀 Creating Simple AgentCore Gateway")
    print("=" * 50)
    
    try:
        # Initialize clients
        gateway_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        iam_client = boto3.client('iam', region_name='us-east-1')
        
        # Get account ID
        sts_client = boto3.client('sts')
        account_id = sts_client.get_caller_identity()['Account']
        
        # Create or get IAM role
        role_name = 'dcisionai-agentcore-gateway-role'
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
        
        print(f"✅ Using IAM role: {role_arn}")
        
        # Create Gateway with minimal configuration
        gateway_name = 'dcisionai-optimization-gateway'
        
        print("🔧 Creating Gateway...")
        
        # Try creating Gateway with minimal auth config
        try:
            response = gateway_client.create_gateway(
                name=gateway_name,
                roleArn=role_arn,
                protocolType='MCP',
                authorizerType='NONE',  # Start with no auth for testing
                description='DcisionAI Optimization Workflow Gateway'
            )
            
            gateway_id = response['gatewayId']
            print(f"✅ Created Gateway: {gateway_id}")
            
            # Get Gateway details
            gateway_details = gateway_client.get_gateway(gatewayId=gateway_id)
            gateway_endpoint = gateway_details.get('gatewayEndpoint', 'N/A')
            
            print(f"✅ Gateway Endpoint: {gateway_endpoint}")
            
            return {
                'gateway_id': gateway_id,
                'gateway_endpoint': gateway_endpoint,
                'status': 'success'
            }
            
        except Exception as e:
            print(f"❌ Failed to create Gateway: {e}")
            
            # Try to get existing Gateway
            try:
                gateways = gateway_client.list_gateways()
                for gateway in gateways.get('gateways', []):
                    if gateway['name'] == gateway_name:
                        gateway_id = gateway['gatewayId']
                        gateway_details = gateway_client.get_gateway(gatewayId=gateway_id)
                        gateway_endpoint = gateway_details.get('gatewayEndpoint', 'N/A')
                        
                        print(f"✅ Found existing Gateway: {gateway_id}")
                        print(f"✅ Gateway Endpoint: {gateway_endpoint}")
                        
                        return {
                            'gateway_id': gateway_id,
                            'gateway_endpoint': gateway_endpoint,
                            'status': 'success'
                        }
            except Exception as e2:
                print(f"❌ Could not find existing Gateway: {e2}")
            
            return {'status': 'error', 'error': str(e)}
            
    except Exception as e:
        print(f"❌ Gateway setup failed: {e}")
        return {'status': 'error', 'error': str(e)}

def create_lambda_target(gateway_id: str):
    """Create Lambda target for optimization workflows."""
    print(f"🔧 Creating Lambda target for Gateway: {gateway_id}")
    
    try:
        gateway_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        sts_client = boto3.client('sts')
        account_id = sts_client.get_caller_identity()['Account']
        
        lambda_target_config = {
            "mcp": {
                "lambda": {
                    "functionArn": f"arn:aws:lambda:us-east-1:{account_id}:function:dcisionai-enhanced-workflows"
                }
            }
        }
        
        response = gateway_client.create_gateway_target(
            gatewayId=gateway_id,
            name='optimization-workflows',
            targetType='LAMBDA',
            targetConfiguration=lambda_target_config,
            description='Lambda functions for optimization workflows'
        )
        
        target_id = response['targetId']
        print(f"✅ Created Lambda target: {target_id}")
        return target_id
        
    except Exception as e:
        print(f"❌ Failed to create Lambda target: {e}")
        return None

def test_gateway(gateway_endpoint: str):
    """Test the Gateway with a simple request."""
    print(f"🧪 Testing Gateway: {gateway_endpoint}")
    
    try:
        import requests
        
        # Simple test request
        test_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = requests.post(
            gateway_endpoint,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Gateway is responding")
            return True
        else:
            print(f"⚠️  Gateway responded with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Gateway test failed: {e}")
        return False

def main():
    """Main function to set up simple Gateway."""
    print("🚀 DcisionAI Simple AgentCore Gateway Setup")
    print("=" * 60)
    
    # Create Gateway
    result = create_simple_gateway()
    
    if result['status'] == 'success':
        gateway_id = result['gateway_id']
        gateway_endpoint = result['gateway_endpoint']
        
        # Create Lambda target
        target_id = create_lambda_target(gateway_id)
        
        # Test Gateway
        if gateway_endpoint != 'N/A':
            test_gateway(gateway_endpoint)
        
        # Save configuration
        config = {
            'gateway_id': gateway_id,
            'gateway_endpoint': gateway_endpoint,
            'target_id': target_id,
            'created_at': datetime.now().isoformat(),
            'status': 'success'
        }
        
        config_file = f"simple_gateway_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\n" + "=" * 60)
        print("🎉 Simple Gateway Setup Complete!")
        print("=" * 60)
        print(f"Gateway ID: {gateway_id}")
        print(f"Gateway Endpoint: {gateway_endpoint}")
        print(f"Target ID: {target_id}")
        print(f"Config saved to: {config_file}")
        
        print("\n📋 Next Steps:")
        print("1. Test optimization workflows through the Gateway")
        print("2. Add authentication if needed")
        print("3. Enable semantic search")
        print("4. Update frontend to use Gateway")
        
    else:
        print(f"\n❌ Setup failed: {result['error']}")
        print("\n📋 Alternative Options:")
        print("1. Use existing Lambda + API Gateway setup")
        print("2. Implement optimization workflows with LangGraph")
        print("3. Use CrewAI for multi-agent optimization")
        print("4. Wait for AgentCore Gateway to be fully available")

if __name__ == "__main__":
    main()
