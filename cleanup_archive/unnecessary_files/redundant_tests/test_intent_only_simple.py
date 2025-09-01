#!/usr/bin/env python3
"""
Simple Test - Intent Only AgentCore
==================================

Simple test to check if AgentCore is responding at all.
"""

import json
import boto3

# Configuration
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_Intent_Only_1756311160-Xzt9Lu7iva"
REGION = "us-east-1"

def test_simple():
    """Simple test to check AgentCore response."""
    print("🧪 SIMPLE AGENTCORE TEST")
    print("=" * 30)
    
    client = boto3.client('bedrock-agentcore', region_name=REGION)
    
    # Very simple request
    request_body = {
        "input": {
            "prompt": "Hello"
        }
    }
    
    print(f"📤 Sending simple request...")
    
    try:
        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_RUNTIME_ARN,
            payload=json.dumps(request_body),
            mcpSessionId="simple_test_123",
            contentType="application/json"
        )
        
        print(f"✅ Response received!")
        print(f"Response keys: {list(response.keys())}")
        
        # Try to parse response
        if 'response' in response:
            response_body = json.loads(response['response'].read())
            print(f"📄 Response: {response_body}")
        elif 'payload' in response:
            response_body = json.loads(response['payload'].read())
            print(f"📄 Response: {response_body}")
        else:
            print(f"📄 Raw response: {response}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_simple()
