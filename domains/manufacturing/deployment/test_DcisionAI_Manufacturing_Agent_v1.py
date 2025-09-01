#!/usr/bin/env python3
"""
DcisionAI Manufacturing Agent v1 - Production AgentCore Test
============================================================

Test script for the production AgentCore deployment v1.
This tests the complete end-to-end manufacturing workflow.

Usage:
    python scripts/deployment/test_DcisionAI_Manufacturing_Agent_v1.py

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
    format="%(asctime)s | %(levelname)s | DcisionAI Intent Test | %(message)s"
)
logger = logging.getLogger(__name__)

def test_intent_only():
    """Test just the intent classification part"""
    
    # Configuration
    region = "us-east-1"
    agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_Agent_v1_1756746910-rwnUTu8UaT"
    
    # Generate session ID (must be 33+ characters)
    session_id = f"test-session-{int(time.time())}-dcisionai-intent-only"
    
    logger.info("🧪 TESTING DcisionAI Manufacturing Agent v1 (Full E2E - All Tools)")
    logger.info("=" * 70)
    logger.info(f"📋 Test Configuration:")
    logger.info(f"   Region: {region}")
    logger.info(f"   Agent Runtime ARN: {agent_runtime_arn}")
    logger.info(f"   Session ID: {session_id}")
    logger.info("")
    
    try:
        # Create Bedrock AgentCore client
        client = boto3.client('bedrock-agentcore', region_name=region)
        
        # Test payload - simple intent classification
        test_payload = json.dumps({
            "prompt": "I need to optimize my production schedule to minimize costs while meeting customer demand for our automotive parts manufacturing"
        })
        
        logger.info("🔄 Invoking AgentCore agent for full E2E workflow (all tools)...")
        
        # Invoke the agent with a shorter timeout
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            qualifier="DEFAULT",
            payload=test_payload
        )
        
        logger.info("✅ AgentCore invocation completed successfully!")
        logger.info("=" * 70)
        
        # Parse response
        response_data = json.loads(response['completion'])
        
        logger.info("📊 Response Summary:")
        logger.info(f"   Raw Response: {json.dumps(response_data, indent=2)}")
        logger.info("")
        
        # Check if we got a successful response
        if "error" not in response_data:
            logger.info("🎉 SUCCESS: Full E2E workflow completed!")
            
            # Extract workflow results
            workflow_results = response_data.get("workflow_results", {})
            
            logger.info("📋 Full E2E Workflow Results:")
            
            # Intent Classification
            intent_result = workflow_results.get("intent_classification", {})
            logger.info("🔍 Intent Classification:")
            logger.info(f"   Primary Intent: {intent_result.get('primary_intent', 'Unknown')}")
            logger.info(f"   Confidence: {intent_result.get('confidence', 0.0)}")
            logger.info(f"   Objectives: {intent_result.get('objectives', [])}")
            logger.info(f"   Reasoning: {intent_result.get('reasoning', '')[:100]}...")
            
            # Data Analysis
            data_result = workflow_results.get("data_analysis", {})
            logger.info("📊 Data Analysis:")
            logger.info(f"   Data Entities: {len(data_result.get('data_entities', []))}")
            logger.info(f"   Missing Data: {len(data_result.get('missing_data', []))}")
            logger.info(f"   Sample Data Keys: {list(data_result.get('sample_data', {}).keys())}")
            
            # Model Building
            model_result = workflow_results.get("model_building", {})
            logger.info("🏗️ Model Building:")
            logger.info(f"   Model Type: {model_result.get('model_type', 'Unknown')}")
            logger.info(f"   Decision Variables: {model_result.get('decision_variables', 0)}")
            logger.info(f"   Constraints: {model_result.get('constraints', 0)}")
            
            # Optimization Solution
            solver_result = workflow_results.get("optimization_solution", {})
            logger.info("⚡ Optimization Solution:")
            logger.info(f"   Status: {solver_result.get('status', 'Unknown')}")
            logger.info(f"   Objective Value: {solver_result.get('objective_value', 0.0)}")
            logger.info(f"   Solve Time: {solver_result.get('solve_time', 0.0)}s")
            
            # Summary
            summary = response_data.get("summary", {})
            logger.info("📋 Summary:")
            logger.info(f"   Intent: {summary.get('intent', 'Unknown')}")
            logger.info(f"   Confidence: {summary.get('confidence', 0.0)}")
            logger.info(f"   Data Entities Analyzed: {summary.get('data_entities_analyzed', 0)}")
            logger.info(f"   Model Type: {summary.get('model_type', 'Unknown')}")
            logger.info(f"   Solution Status: {summary.get('solution_status', 'Unknown')}")
            logger.info(f"   Objective Value: {summary.get('objective_value', 0.0)}")
            
            return True
        else:
            logger.error(f"❌ ERROR: {response_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {e}")
        logger.error("💡 Troubleshooting Tips:")
        logger.error("1. Make sure the agent runtime ARN is correct")
        logger.error("2. Verify the agent runtime is in READY status")
        logger.error("3. Check that the deployment completed successfully")
        logger.error("4. Ensure AWS credentials are configured correctly")
        return False

def list_agent_runtimes():
    """List available agent runtimes"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        response = client.list_agent_runtimes()
        
        logger.info("📋 Available Agent Runtimes:")
        for runtime in response.get('agentRuntimeSummaries', []):
            logger.info(f"   • {runtime.get('agentRuntimeName', 'Unknown')}")
            logger.info(f"     ARN: {runtime.get('agentRuntimeArn', 'Unknown')}")
            logger.info(f"     Status: {runtime.get('status', 'Unknown')}")
            logger.info("")
            
    except Exception as e:
        logger.error(f"Failed to list agent runtimes: {e}")

if __name__ == "__main__":
    # First, list available runtimes to help identify the correct ARN
    list_agent_runtimes()
    
    logger.info("")
    logger.info("💡 To test a specific agent runtime, update the agent_runtime_arn variable")
    logger.info("   in this script with the correct ARN from the list above.")
    logger.info("")
    
    # Run the intent-only test
    test_intent_only()
