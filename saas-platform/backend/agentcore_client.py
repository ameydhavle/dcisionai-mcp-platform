#!/usr/bin/env python3
"""
AgentCore Client for DcisionAI SaaS Platform
============================================

Client to communicate with the deployed DcisionAI MCP server on AWS AgentCore Runtime.
"""

import requests
import json
import logging
import time
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

class AgentCoreClient:
    """Client for communicating with AgentCore Runtime."""
    
    def __init__(self, agent_arn: str = None, region: str = "us-east-1"):
        """
        Initialize AgentCore client.
        
        Args:
            agent_arn: The AgentCore runtime ARN
            region: AWS region
        """
        self.agent_arn = agent_arn or "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/mcp_server-IkOAiK3aOz"
        self.region = region
        self.base_url = f"https://bedrock-agentcore.{region}.amazonaws.com"
        
        # Extract runtime ID from ARN - handle different ARN formats
        if '/runtimes/' in self.agent_arn:
            # Full runtime ARN format
            runtime_id = self.agent_arn.split('/runtimes/')[-1]
        else:
            # Agent ARN format
            runtime_id = self.agent_arn.split('/')[-1]
        
        self.invoke_url = f"{self.base_url}/runtimes/{runtime_id}/invocations"
        
        logger.info(f"AgentCore client initialized for: {self.agent_arn}")
    
    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to AgentCore Runtime using boto3 client."""
        try:
            # Use boto3 AgentCore client directly
            import boto3
            
            client = boto3.client('bedrock-agentcore', region_name=self.region)
            
            # Use the invoke_agent_runtime method with correct parameters
            response = client.invoke_agent_runtime(
                agentRuntimeArn=self.agent_arn,
                payload=json.dumps(payload),
                runtimeSessionId='dcisionai-session-' + str(int(time.time() * 1000000))
            )
            
            # Extract the response - handle StreamingBody in 'response' field
            logger.info(f"AgentCore response keys: {list(response.keys())}")
            
            # The actual response is in the 'response' field as a StreamingBody
            if 'response' in response:
                response_body = response['response']
                if hasattr(response_body, 'read'):
                    # It's a StreamingBody, read the content
                    content = response_body.read().decode('utf-8')
                    logger.info(f"StreamingBody content: {content[:200]}...")
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return {"raw_response": content}
                else:
                    return response_body
            else:
                # Fallback: return the full response but make it serializable
                serializable_response = {}
                for key, value in response.items():
                    if hasattr(value, 'read'):
                        # It's a StreamingBody, convert to string
                        serializable_response[key] = f"<StreamingBody: {str(value)}>"
                    else:
                        serializable_response[key] = value
                return serializable_response
                
        except Exception as e:
            logger.error(f"AgentCore request error: {e}")
            return {"error": str(e)}
    
    def classify_intent(self, problem_description: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Classify optimization problem intent."""
        # Use MCP format that the standalone agent expects
        payload = {
            "method": "tools/call",
            "params": {
                "name": "classify_intent",
                "arguments": {
                    "problem_description": problem_description,
                    "context": context
                }
            }
        }
        
        result = self._make_request(payload)
        
        # Extract the actual result from the AgentCore response format
        if "content" in result and result["content"]:
            content = result["content"][0]
            if "text" in content:
                try:
                    return json.loads(content["text"])
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response from AgentCore"}
        
        return result
    
    def analyze_data(self, problem_description: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data readiness and quality."""
        payload = {
            "method": "tools/call",
            "params": {
                "name": "analyze_data",
                "arguments": {
                    "problem_description": problem_description,
                    "intent_data": intent_data
                }
            }
        }
        
        result = self._make_request(payload)
        
        if "content" in result and result["content"]:
            content = result["content"][0]
            if "text" in content:
                try:
                    return json.loads(content["text"])
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response from AgentCore"}
        
        return result
    
    def build_model(self, problem_description: str, intent_data: Dict[str, Any], data_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Build mathematical optimization model."""
        payload = {
            "method": "tools/call",
            "params": {
                "name": "build_model",
                "arguments": {
                    "problem_description": problem_description,
                    "intent_data": intent_data,
                    "data_analysis": data_analysis
                }
            }
        }
        
        result = self._make_request(payload)
        
        if "content" in result and result["content"]:
            content = result["content"][0]
            if "text" in content:
                try:
                    return json.loads(content["text"])
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response from AgentCore"}
        
        return result
    
    def solve_optimization(self, problem_description: str, intent_data: Dict[str, Any], 
                          data_analysis: Dict[str, Any], model_building: Dict[str, Any]) -> Dict[str, Any]:
        """Solve optimization problem."""
        payload = {
            "method": "tools/call",
            "params": {
                "name": "solve_optimization",
                "arguments": {
                    "problem_description": problem_description,
                    "intent_data": intent_data,
                    "data_analysis": data_analysis,
                    "model_building": model_building
                }
            }
        }
        
        result = self._make_request(payload)
        
        if "content" in result and result["content"]:
            content = result["content"][0]
            if "text" in content:
                try:
                    return json.loads(content["text"])
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response from AgentCore"}
        
        return result
    
    def explain_optimization(self, problem_description: str, intent_data: Dict[str, Any],
                           data_analysis: Dict[str, Any], model_building: Dict[str, Any],
                           optimization_solution: Dict[str, Any]) -> Dict[str, Any]:
        """Provide business-facing explanation of optimization results."""
        payload = {
            "method": "tools/call",
            "params": {
                "name": "explain_optimization",
                "arguments": {
                    "problem_description": problem_description,
                    "intent_data": intent_data,
                    "data_analysis": data_analysis,
                    "model_building": model_building,
                    "optimization_solution": optimization_solution
                }
            }
        }
        
        result = self._make_request(payload)
        
        if "content" in result and result["content"]:
            content = result["content"][0]
            if "text" in content:
                try:
                    return json.loads(content["text"])
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response from AgentCore"}
        
        return result
    
    def health_check(self) -> Dict[str, Any]:
        """Check if AgentCore runtime is healthy."""
        payload = {
            "prompt": "Health check - are you running?"
        }
        
        result = self._make_request(payload)
        
        if "error" in result:
            return {"status": "unhealthy", "error": result["error"]}
        else:
            return {"status": "healthy", "message": "AgentCore runtime is responding"}

# Global client instance
_agentcore_client = None

def get_agentcore_client() -> AgentCoreClient:
    """Get or create global AgentCore client instance."""
    global _agentcore_client
    if _agentcore_client is None:
        _agentcore_client = AgentCoreClient()
    return _agentcore_client
