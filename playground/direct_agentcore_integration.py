#!/usr/bin/env python3
"""
Direct AgentCore Integration
===========================

Direct integration with AgentCore runtime, bypassing Lambda complications.
This uses the working MCP client approach that we know works.
"""

import json
import subprocess
import tempfile
import os
import time
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AgentCore runtime ARN
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_Agent_v1_1756943746-0OgdtC2Je6"

def call_agentcore_direct(prompt: str, tenant_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call AgentCore runtime directly using the working MCP client approach.
    
    Args:
        prompt: User prompt
        tenant_context: Tenant context
        
    Returns:
        AgentCore response
    """
    try:
        # Create MCP protocol request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": f"playground-{int(time.time())}",
            "method": "invoke",
            "params": {
                "prompt": prompt,
                "tenantContext": tenant_context,
                "session_id": f"playground-session-{int(time.time())}"
            }
        }
        
        # Create temporary file with the request
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(mcp_request, f)
            temp_file = f.name
        
        # Create output file
        output_file = temp_file.replace('.json', '_output.json')
        
        # Use AWS CLI to invoke AgentCore (this works reliably)
        cmd = [
            'aws', 'bedrock-agentcore', 'invoke-agent-runtime',
            '--agent-runtime-arn', AGENT_RUNTIME_ARN,
            '--qualifier', 'DEFAULT',
            '--payload', f'file://{temp_file}',
            '--content-type', 'application/json',
            '--accept', 'application/json',
            '--region', 'us-east-1',
            output_file
        ]
        
        logger.info(f"Calling AgentCore with prompt: {prompt[:50]}...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # Clean up temp files
        os.unlink(temp_file)
        if os.path.exists(output_file):
            os.unlink(output_file)
        
        if result.returncode != 0:
            logger.error(f"AgentCore call failed: {result.stderr}")
            return {
                "error": True,
                "message": f"AgentCore runtime error: {result.stderr}",
                "cold_start_issue": "RuntimeClientError" in result.stderr
            }
        
        # Parse the response
        response_data = json.loads(result.stdout)
        logger.info("AgentCore call successful!")
        
        # Extract completion from response
        if 'completion' in response_data:
            completion_data = json.loads(response_data['completion'])
            
            if 'result' in completion_data:
                return {
                    "success": True,
                    "workflow_results": completion_data['result'].get('workflow_results', {}),
                    "message": completion_data['result'].get('message', 'Optimization completed'),
                    "tools_used": completion_data['result'].get('tools_used', []),
                    "tenant_context": completion_data['result'].get('tenant_context', {}),
                    "inference_profiles_used": completion_data['result'].get('inference_profiles_used', []),
                    "mcp_protocol": completion_data['result'].get('mcp_protocol', {}),
                    "execution_time": response_data.get('executionTime', 0),
                    "session_id": response_data.get('runtimeSessionId', 'unknown')
                }
            elif 'error' in completion_data:
                return {
                    "error": True,
                    "message": f"Optimization failed: {completion_data['error'].get('message', 'Unknown error')}"
                }
            else:
                return {
                    "success": True,
                    "workflow_results": completion_data,
                    "message": "Optimization completed"
                }
        else:
            return {
                "error": True,
                "message": "Invalid response from AgentCore runtime"
            }
            
    except Exception as e:
        logger.error(f"Error calling AgentCore: {e}")
        return {
            "error": True,
            "message": f"Error calling AgentCore: {str(e)}"
        }

def test_direct_integration():
    """Test the direct AgentCore integration."""
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
        print(f"DIRECT AGENTCORE TEST {i}")
        print(f"{'='*60}")
        print(f"Prompt: {test_case['prompt']}")
        print(f"Tenant: {test_case['tenant_context']}")
        
        result = call_agentcore_direct(test_case['prompt'], test_case['tenant_context'])
        
        print(f"\nResult:")
        print(json.dumps(result, indent=2))
        
        if result.get('success'):
            print("✅ SUCCESS: Real AgentCore tools executed!")
        else:
            print("❌ FAILED: AgentCore call failed")

if __name__ == "__main__":
    test_direct_integration()
