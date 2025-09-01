#!/usr/bin/env python3
"""
Simple AgentCore Test
====================

Basic test to verify AgentCore runtime is responding.
"""

import json
import time
import boto3
from datetime import datetime

# Configuration
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_MCP_v1_v2_1756310225-cfaY5Q8xSl"
REGION = "us-east-1"

def test_agentcore_basic():
    """Test basic AgentCore functionality."""
    print("🚀 AGENTCORE BASIC TEST")
    print("=" * 50)
    
    client = boto3.client('bedrock-agentcore', region_name=REGION)
    
    # Simple test prompt
    test_prompt = "Hello, can you help me with manufacturing optimization?"
    
    print(f"📝 Test Prompt: {test_prompt}")
    print(f"🔗 AgentCore Runtime: {AGENT_RUNTIME_ARN}")
    print(f"⏱️ Starting test...")
    
    start_time = time.time()
    
    try:
        # Prepare request
        request_body = {
            "input": {
                "prompt": test_prompt
            }
        }
        
        print(f"📤 Sending request to AgentCore...")
        
        # Invoke AgentCore with timeout
        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_RUNTIME_ARN,
            payload=json.dumps(request_body),
            mcpSessionId=f"simple_test_{int(time.time())}",
            contentType="application/json"
        )
        
        execution_time = time.time() - start_time
        print(f"✅ Response received in {execution_time:.2f}s")
        
        # Parse response
        if 'response' in response:
            response_body = json.loads(response['response'].read())
        elif 'payload' in response:
            response_body = json.loads(response['payload'].read())
        elif 'responseBody' in response:
            response_body = json.loads(response['responseBody'].read())
        else:
            print(f"⚠️ Unexpected response format")
            print(f"Response keys: {list(response.keys())}")
            return False
        
        print(f"📄 Response received successfully!")
        print(f"📊 Response length: {len(str(response_body))} characters")
        
        # Show response preview
        response_str = str(response_body)
        preview = response_str[:300] + "..." if len(response_str) > 300 else response_str
        print(f"📋 Response Preview:")
        print(f"   {preview}")
        
        # Check if response contains expected content
        response_lower = response_str.lower()
        if any(keyword in response_lower for keyword in ["manufacturing", "optimization", "intent", "data", "model", "solver"]):
            print(f"✅ Response contains manufacturing optimization content")
            return True
        else:
            print(f"⚠️ Response doesn't contain expected manufacturing content")
            return False
            
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ Test failed after {execution_time:.2f}s: {str(e)}")
        return False

def main():
    """Main test execution."""
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_agentcore_basic()
    
    if success:
        print(f"\n🎉 AGENTCORE BASIC TEST PASSED!")
        print(f"✅ AgentCore runtime is responding correctly")
    else:
        print(f"\n❌ AGENTCORE BASIC TEST FAILED!")
        print(f"🔧 AgentCore runtime needs attention")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
