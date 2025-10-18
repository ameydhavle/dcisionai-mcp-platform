#!/usr/bin/env python3
"""
AgentCore Gateway Client for DcisionAI SaaS Platform
===================================================

Client to communicate with the DcisionAI MCP server through Amazon Bedrock AgentCore Gateway.
This provides enterprise-grade security and scalability for our optimization tools.

Based on: https://aws.amazon.com/blogs/machine-learning/introducing-amazon-bedrock-agentcore-gateway-transforming-enterprise-ai-agent-tool-development/
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
import os
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

logger = logging.getLogger(__name__)

class DcisionAIGatewayClient:
    """Client for communicating with DcisionAI tools through AgentCore Gateway."""
    
    def __init__(self, gateway_endpoint: str = None, region: str = "us-east-1"):
        """
        Initialize Gateway client.
        
        Args:
            gateway_endpoint: The Gateway endpoint URL
            region: AWS region
        """
        self.gateway_endpoint = gateway_endpoint or os.getenv(
            'DcisionAI_GATEWAY_ENDPOINT',
            'https://your-gateway-endpoint.amazonaws.com'  # Will be updated after Gateway setup
        )
        self.region = region
        
        # OAuth configuration
        self.cognito_pool_id = "us-west-2_pEQfTkscK"
        self.cognito_client_id = "5h4o4dpu7r7qreusrjhu54umqo"
        
        logger.info(f"Gateway client initialized for: {self.gateway_endpoint}")
    
    def _get_oauth_token(self) -> str:
        """Get OAuth token from Cognito."""
        # In production, this would use proper OAuth flow
        # For now, we'll use the existing bearer token
        return os.getenv('BEARER_TOKEN', 'your-oauth-token-here')
    
    def _make_gateway_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated request to AgentCore Gateway."""
        try:
            # Get OAuth token
            oauth_token = self._get_oauth_token()
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {oauth_token}'
            }
            
            # Make request to Gateway
            response = requests.post(
                self.gateway_endpoint,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Gateway request failed: {response.status_code} - {response.text}")
                return {"error": f"Request failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Gateway request error: {e}")
            return {"error": str(e)}
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools from Gateway."""
        payload = {
            "method": "tools/list",
            "params": {}
        }
        
        result = self._make_gateway_request(payload)
        
        if "tools" in result:
            return {
                "status": "success",
                "tools": result["tools"]
            }
        else:
            return {
                "status": "error",
                "error": result.get("error", "Failed to list tools")
            }
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool through Gateway."""
        payload = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        result = self._make_gateway_request(payload)
        
        # Extract content from Gateway response
        if "content" in result and result["content"]:
            content = result["content"][0]
            if "text" in content:
                try:
                    return json.loads(content["text"])
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response from Gateway"}
        
        return result
    
    def classify_intent(self, problem_description: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Classify optimization problem intent."""
        return self.call_tool("classify_intent", {
            "problem_description": problem_description,
            "context": context
        })
    
    def analyze_data(self, problem_description: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data readiness and quality."""
        return self.call_tool("analyze_data", {
            "problem_description": problem_description,
            "intent_data": intent_data
        })
    
    def build_model(self, problem_description: str, intent_data: Dict[str, Any], 
                   data_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Build mathematical optimization model."""
        return self.call_tool("build_model", {
            "problem_description": problem_description,
            "intent_data": intent_data,
            "data_analysis": data_analysis
        })
    
    def solve_optimization(self, problem_description: str, intent_data: Dict[str, Any],
                          data_analysis: Dict[str, Any], model_building: Dict[str, Any]) -> Dict[str, Any]:
        """Solve optimization problem."""
        return self.call_tool("solve_optimization", {
            "problem_description": problem_description,
            "intent_data": intent_data,
            "data_analysis": data_analysis,
            "model_building": model_building
        })
    
    def explain_optimization(self, problem_description: str, intent_data: Dict[str, Any],
                           data_analysis: Dict[str, Any], model_building: Dict[str, Any],
                           optimization_solution: Dict[str, Any]) -> Dict[str, Any]:
        """Provide business-facing explanation of optimization results."""
        return self.call_tool("explain_optimization", {
            "problem_description": problem_description,
            "intent_data": intent_data,
            "data_analysis": data_analysis,
            "model_building": model_building,
            "optimization_solution": optimization_solution
        })
    
    def simulate_scenarios(self, problem_description: str, optimization_solution: Dict[str, Any],
                          num_trials: int = 1000) -> Dict[str, Any]:
        """Run simulation analysis on optimization scenarios."""
        return self.call_tool("simulate_scenarios", {
            "problem_description": problem_description,
            "optimization_solution": optimization_solution,
            "num_trials": num_trials
        })
    
    def search_tools(self, query: str) -> Dict[str, Any]:
        """Use semantic search to find relevant tools."""
        return self.call_tool("x_amz_bedrock_agentcore_search", {
            "query": query
        })
    
    def health_check(self) -> Dict[str, Any]:
        """Check if Gateway is healthy."""
        try:
            tools_result = self.list_tools()
            if tools_result["status"] == "success":
                return {
                    "status": "healthy",
                    "message": "Gateway is responding",
                    "available_tools": len(tools_result["tools"])
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": tools_result["error"]
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Global client instance
_gateway_client = None

def get_gateway_client() -> DcisionAIGatewayClient:
    """Get or create global Gateway client instance."""
    global _gateway_client
    if _gateway_client is None:
        _gateway_client = DcisionAIGatewayClient()
    return _gateway_client
