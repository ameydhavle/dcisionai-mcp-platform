#!/usr/bin/env python3
"""
Direct AgentCore Test
====================

Test script to directly call AgentCore from the playground without API Gateway.
"""

import json
import boto3
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AWS clients
bedrock_client = boto3.client('bedrock-agentcore', region_name='us-east-1')

# AgentCore runtime ARN
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_Agent_v1_1756943746-0OgdtC2Je6"

def test_agentcore_direct(prompt: str, tenant_context: dict):
    """Test direct AgentCore invocation."""
    try:
        # Create MCP protocol request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": f"playground-test-{int(time.time())}",
            "method": "invoke",
            "params": {
                "prompt": prompt,
                "tenantContext": tenant_context,
                "session_id": f"playground-session-{int(time.time())}"
            }
        }
        
        request_json = json.dumps(mcp_request)
        logger.info(f"Request: {request_json}")
        
        # Call AgentCore runtime
        logger.info(f"Invoking AgentCore runtime: {AGENT_RUNTIME_ARN}")
        response = bedrock_client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_RUNTIME_ARN,
            qualifier='DEFAULT',
            payload=request_json,
            contentType='application/json',
            accept='application/json'
        )
        
        logger.info(f"Response: {response}")
        
        # Parse the response
        if 'completion' in response:
            completion_data = json.loads(response['completion'])
            logger.info(f"Completion: {json.dumps(completion_data, indent=2)}")
            
            if 'result' in completion_data:
                return completion_data['result']
            elif 'error' in completion_data:
                return {"error": completion_data['error']}
            else:
                return completion_data
        else:
            return {"error": "No completion in response"}
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Test with different prompts
    test_cases = [
        {
            "prompt": "Test different query: optimize inventory management for automotive parts",
            "tenant_context": {
                "tenant_id": "test_tenant",
                "sla_tier": "premium",
                "region": "us-east-1"
            }
        },
        {
            "prompt": "Optimize production scheduling for 3 manufacturing lines",
            "tenant_context": {
                "tenant_id": "gold_tenant",
                "sla_tier": "gold",
                "region": "us-east-1"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST CASE {i}")
        print(f"{'='*60}")
        print(f"Prompt: {test_case['prompt']}")
        print(f"Tenant: {test_case['tenant_context']}")
        
        result = test_agentcore_direct(test_case['prompt'], test_case['tenant_context'])
        
        print(f"\nResult:")
        print(json.dumps(result, indent=2))
