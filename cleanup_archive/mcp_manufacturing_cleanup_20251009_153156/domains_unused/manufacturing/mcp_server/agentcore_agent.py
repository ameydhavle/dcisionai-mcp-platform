#!/usr/bin/env python3
"""
DcisionAI Manufacturing Agent for AWS Bedrock AgentCore

This is the main agent file that will be deployed to AgentCore Runtime.
It wraps our MCP server with swarm architecture for AgentCore deployment.
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional

# Import the MCP server components
from mcp_server_swarm import ManufacturingSwarmTools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | AgentCore Agent | %(message)s"
)
logger = logging.getLogger(__name__)

class DcisionAIManufacturingAgent:
    """DcisionAI Manufacturing Agent for AgentCore deployment."""
    
    def __init__(self):
        logger.info("🚀 Initializing DcisionAI Manufacturing Agent...")
        self.mcp_tools = ManufacturingSwarmTools()
        logger.info("✅ Agent initialized with swarm architecture")
    
    def invoke(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for AgentCore invocations."""
        try:
            logger.info(f"📥 Received payload: {json.dumps(payload, indent=2)}")
            
            # Extract the request details
            prompt = payload.get("prompt", "")
            tool_name = payload.get("tool", "manufacturing_intent_classification")
            arguments = payload.get("arguments", {})
            
            # Route to appropriate tool
            if tool_name == "manufacturing_intent_classification":
                result = self.mcp_tools.manufacturing_intent_classification(
                    query=prompt,
                    **arguments
                )
            elif tool_name == "manufacturing_data_analysis":
                result = self.mcp_tools.manufacturing_data_analysis(
                    data={"query": prompt},
                    **arguments
                )
            elif tool_name == "manufacturing_model_builder":
                result = self.mcp_tools.manufacturing_model_builder(
                    intent_result=arguments.get("intent_result", {}),
                    data_result=arguments.get("data_result", {})
                )
            elif tool_name == "manufacturing_optimization_solver":
                result = self.mcp_tools.manufacturing_optimization_solver(
                    model_result=arguments.get("model_result", {})
                )
            elif tool_name == "manufacturing_health_check":
                result = self.mcp_tools.manufacturing_health_check()
            else:
                # Default to intent classification
                result = self.mcp_tools.manufacturing_intent_classification(
                    query=prompt,
                    **arguments
                )
            
            # Check if the result indicates failure
            if isinstance(result, dict):
                if result.get("status") == "error":
                    logger.error("❌ Tool execution failed - all agents failed")
                    return {
                        "status": "error",
                        "error": result.get("error", "All agents failed"),
                        "result": result,
                        "tool_attempted": tool_name,
                        "timestamp": payload.get("timestamp", "")
                    }
                elif result.get("status") == "partial_failure":
                    logger.warning(f"⚠️ Tool execution partially failed - {result.get('failure_reason', 'Some agents failed')}")
                    return {
                        "status": "partial_failure",
                        "error": result.get("failure_reason", "Some agents failed"),
                        "result": result,
                        "tool_used": tool_name,
                        "timestamp": payload.get("timestamp", "")
                    }
            
            logger.info("✅ Tool execution completed successfully")
            return {
                "status": "success",
                "result": result,
                "tool_used": tool_name,
                "timestamp": payload.get("timestamp", "")
            }
            
        except Exception as e:
            logger.error(f"❌ Tool execution failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "tool_attempted": tool_name,
                "timestamp": payload.get("timestamp", "")
            }

# Create the agent instance
agent = DcisionAIManufacturingAgent()

# Main entry point for AgentCore
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Entry point function for AgentCore Runtime."""
    return agent.invoke(payload)

# For local testing
if __name__ == "__main__":
    import asyncio
    
    # Test the agent locally
    def test_agent():
        test_payload = {
            "prompt": "Optimize production scheduling for 3 lines with 45 workers",
            "tool": "manufacturing_intent_classification",
            "arguments": {},
            "timestamp": "2025-09-04T18:00:00Z"
        }
        
        result = invoke(test_payload)
        print(json.dumps(result, indent=2))
    
    # Run the test
    test_agent()
