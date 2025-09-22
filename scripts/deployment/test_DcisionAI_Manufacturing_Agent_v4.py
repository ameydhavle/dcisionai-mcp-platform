#!/usr/bin/env python3
"""
DcisionAI Manufacturing Agent v4 - Production AgentCore Test
============================================================

Test script for the production AgentCore deployment v4.
This tests the complete end-to-end manufacturing workflow with real tools.

Usage:
    python scripts/deployment/test_DcisionAI_Manufacturing_Agent_v4.py

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import boto3
import json
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | DcisionAI Manufacturing Agent v4 Test | %(message)s"
)
logger = logging.getLogger(__name__)

def load_deployment_info():
    """Load deployment information from the deployment file."""
    try:
        with open("agentcore_v4_deployment.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("❌ Deployment info file not found. Please run deployment first.")
        return None

def test_agentcore_v4():
    """Test the AgentCore v4 deployment."""
    
    # Load deployment info
    deployment_info = load_deployment_info()
    if not deployment_info:
        return False
    
    # Configuration
    region = "us-east-1"
    agent_runtime_arn = deployment_info["agent_runtime_arn"]
    
    # Generate session ID (must be 33+ characters)
    session_id = f"test-session-{int(time.time())}-dcisionai-v4-full-workflow"
    
    logger.info("🧪 TESTING DcisionAI Manufacturing Agent v4 (Full E2E - All Tools)")
    logger.info("=" * 70)
    logger.info(f"📋 Test Configuration:")
    logger.info(f"   Region: {region}")
    logger.info(f"   Agent Runtime ARN: {agent_runtime_arn}")
    logger.info(f"   Session ID: {session_id}")
    logger.info(f"   Version: {deployment_info.get('version', 'v4')}")
    logger.info("")
    
    try:
        # Create Bedrock AgentCore client
        client = boto3.client('bedrock-agentcore', region_name=region)
        
        # Test payload with proper MCP protocol
        test_payload = json.dumps({
            "jsonrpc": "2.0",
            "id": f"test-{int(time.time())}",
            "method": "invoke",
            "params": {
                "prompt": "I need to optimize my production schedule to minimize costs while meeting customer demand for our automotive parts manufacturing",
                "tenantContext": {
                    "tenant_id": "test_tenant",
                    "sla_tier": "pro",
                    "region": "us-east-1"
                },
                "session_id": session_id
            }
        })
        
        logger.info("🔄 Invoking AgentCore agent for full E2E workflow (all tools)...")
        logger.info("📋 Using MCP Protocol Version: 2024-11-05")
        
        # Invoke the agent with proper MCP protocol
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            qualifier="DEFAULT",
            payload=test_payload,
            contentType="application/json",
            accept="application/json"
        )
        
        logger.info("✅ AgentCore invocation completed successfully!")
        logger.info("=" * 70)
        
        # Parse response
        response_data = json.loads(response['completion'])
        
        logger.info("📊 Response Summary:")
        logger.info(f"   Raw Response: {json.dumps(response_data, indent=2)}")
        logger.info("")
        
        # Check if we got a successful response (JSON-RPC 2.0 format)
        if "error" not in response_data and "result" in response_data:
            logger.info("🎉 SUCCESS: Full E2E workflow completed!")
            logger.info("✅ MCP Protocol: JSON-RPC 2.0 response received")
            
            # Extract workflow results from JSON-RPC result
            result_data = response_data.get("result", {})
            workflow_results = result_data.get("workflow_results", {})
            
            logger.info("📋 Full E2E Workflow Results:")
            
            # Intent Classification
            intent_result = workflow_results.get("intent_classification", {})
            logger.info("🔍 Intent Classification:")
            logger.info(f"   Primary Intent: {intent_result.get('primary_intent', 'Unknown')}")
            logger.info(f"   Confidence: {intent_result.get('confidence', 0.0)}")
            logger.info(f"   Objectives: {intent_result.get('objectives', [])}")
            logger.info(f"   Inference Profile: {intent_result.get('inference_profile_used', 'Unknown')}")
            
            # Data Analysis
            data_result = workflow_results.get("data_analysis", {})
            logger.info("📊 Data Analysis:")
            logger.info(f"   Data Entities: {len(data_result.get('data_entities', []))}")
            logger.info(f"   Missing Data: {len(data_result.get('missing_data', []))}")
            logger.info(f"   Sample Data Keys: {list(data_result.get('sample_data', {}).keys())}")
            logger.info(f"   Inference Profile: {data_result.get('inference_profile_used', 'Unknown')}")
            
            # Model Building
            model_result = workflow_results.get("model_building", {})
            logger.info("🏗️ Model Building:")
            logger.info(f"   Model Type: {model_result.get('model_type', 'Unknown')}")
            logger.info(f"   Decision Variables: {model_result.get('decision_variables', 0)}")
            logger.info(f"   Constraints: {model_result.get('constraints', 0)}")
            logger.info(f"   Complexity: {model_result.get('complexity', 'Unknown')}")
            logger.info(f"   Inference Profile: {model_result.get('inference_profile_used', 'Unknown')}")
            
            # Optimization Solving
            solver_result = workflow_results.get("optimization_solving", {})
            logger.info("⚡ Optimization Solving:")
            logger.info(f"   Status: {solver_result.get('status', 'Unknown')}")
            logger.info(f"   Objective Value: {solver_result.get('objective_value', 0.0)}")
            logger.info(f"   Solve Time: {solver_result.get('solve_time', 0.0)}s")
            logger.info(f"   Recommended Solver: {solver_result.get('recommended_solver', 'Unknown')}")
            logger.info(f"   Solution Quality: {solver_result.get('solution_quality', 'Unknown')}")
            logger.info(f"   Inference Profile: {solver_result.get('inference_profile_used', 'Unknown')}")
            
            # MCP Protocol Info
            mcp_info = result_data.get("mcp_protocol", {})
            logger.info("🔧 MCP Protocol Info:")
            logger.info(f"   Version: {mcp_info.get('version', 'Unknown')}")
            logger.info(f"   Content Type: {mcp_info.get('content_type', 'Unknown')}")
            logger.info(f"   Session ID: {mcp_info.get('session_id', 'Unknown')}")
            
            # Tools Used
            tools_used = result_data.get("tools_used", [])
            logger.info("🔧 Tools Used:")
            for tool in tools_used:
                logger.info(f"   • {tool}")
            
            # Inference Profiles Used
            inference_profiles = result_data.get("inference_profiles_used", [])
            logger.info("🔧 Inference Profiles Used:")
            for profile in inference_profiles:
                logger.info(f"   • {profile}")
            
            return True
        elif "error" in response_data:
            # Handle JSON-RPC 2.0 error format
            error_data = response_data.get("error", {})
            logger.error(f"❌ JSON-RPC ERROR: {error_data.get('message', 'Unknown error')}")
            logger.error(f"   Error Code: {error_data.get('code', 'Unknown')}")
            if "data" in error_data:
                logger.error(f"   Error Data: {error_data.get('data', {})}")
            return False
        else:
            logger.error(f"❌ UNKNOWN ERROR: Invalid response format")
            logger.error(f"   Response: {response_data}")
            return False
            
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {e}")
        logger.error("💡 Troubleshooting Tips:")
        logger.error("1. Make sure the agent runtime ARN is correct")
        logger.error("2. Verify the agent runtime is in READY status")
        logger.error("3. Check that the deployment completed successfully")
        logger.error("4. Ensure AWS credentials are configured correctly")
        return False

def test_multiple_queries():
    """Test multiple different queries to verify dynamic responses."""
    deployment_info = load_deployment_info()
    if not deployment_info:
        return False
    
    region = "us-east-1"
    agent_runtime_arn = deployment_info["agent_runtime_arn"]
    client = boto3.client('bedrock-agentcore', region_name=region)
    
    test_cases = [
        {
            "prompt": "Optimize production scheduling for 3 manufacturing lines",
            "tenantContext": {"tenant_id": "gold_tenant", "sla_tier": "gold", "region": "us-east-1"},
            "expected_intent": "production_scheduling"
        },
        {
            "prompt": "Minimize costs in supply chain operations",
            "tenantContext": {"tenant_id": "pro_tenant", "sla_tier": "pro", "region": "us-west-2"},
            "expected_intent": "cost_optimization"
        },
        {
            "prompt": "Improve quality in assembly line",
            "tenantContext": {"tenant_id": "free_tenant", "sla_tier": "free", "region": "us-east-1"},
            "expected_intent": "quality_optimization"
        }
    ]
    
    logger.info("🧪 TESTING Multiple Queries (Dynamic Response Verification)")
    logger.info("=" * 70)
    
    success_count = 0
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n📋 Test Case {i}: {test_case['prompt']}")
        logger.info(f"   Expected Intent: {test_case['expected_intent']}")
        logger.info(f"   Tenant: {test_case['tenantContext']}")
        
        try:
            session_id = f"test-session-{int(time.time())}-{i}-dcisionai-v4"
            
            test_payload = json.dumps({
                "jsonrpc": "2.0",
                "id": f"test-{i}-{int(time.time())}",
                "method": "invoke",
                "params": {
                    "prompt": test_case["prompt"],
                    "tenantContext": test_case["tenantContext"],
                    "session_id": session_id
                }
            })
            
            response = client.invoke_agent_runtime(
                agentRuntimeArn=agent_runtime_arn,
                qualifier="DEFAULT",
                payload=test_payload,
                contentType="application/json",
                accept="application/json"
            )
            
            response_data = json.loads(response['completion'])
            
            if "result" in response_data:
                result_data = response_data.get("result", {})
                workflow_results = result_data.get("workflow_results", {})
                intent_result = workflow_results.get("intent_classification", {})
                
                actual_intent = intent_result.get('primary_intent', 'Unknown')
                confidence = intent_result.get('confidence', 0.0)
                inference_profile = intent_result.get('inference_profile_used', 'Unknown')
                
                logger.info(f"   ✅ SUCCESS: Intent classified as '{actual_intent}' (confidence: {confidence})")
                logger.info(f"   🔧 Inference Profile: {inference_profile}")
                
                if actual_intent == test_case['expected_intent']:
                    logger.info(f"   🎯 INTENT MATCH: Expected '{test_case['expected_intent']}', got '{actual_intent}'")
                    success_count += 1
                else:
                    logger.warning(f"   ⚠️ INTENT MISMATCH: Expected '{test_case['expected_intent']}', got '{actual_intent}'")
            else:
                logger.error(f"   ❌ FAILED: {response_data}")
                
        except Exception as e:
            logger.error(f"   ❌ ERROR: {e}")
    
    logger.info(f"\n📊 Multiple Query Test Results: {success_count}/{len(test_cases)} successful")
    return success_count == len(test_cases)

if __name__ == "__main__":
    # Test the main workflow
    main_success = test_agentcore_v4()
    
    if main_success:
        # Test multiple queries for dynamic response verification
        multi_success = test_multiple_queries()
        
        if multi_success:
            logger.info("\n🎉 ALL TESTS PASSED! AgentCore v4 is working correctly with dynamic responses.")
        else:
            logger.warning("\n⚠️ Main test passed but multiple query test had issues.")
    else:
        logger.error("\n❌ Main test failed. Please check the deployment.")
