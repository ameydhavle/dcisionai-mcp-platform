#!/usr/bin/env python3
"""
DcisionAI MCP Client SDK
========================

Official Python SDK for connecting to DcisionAI MCP servers.
Provides easy-to-use interfaces for manufacturing optimization tools.

Features:
- Simple connection and authentication
- Type-safe tool interfaces
- Automatic error handling and retries
- Comprehensive logging and debugging
- Async and sync support

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

import httpx
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class MCPError(Exception):
    """Base exception for MCP client errors."""
    pass

class AuthenticationError(MCPError):
    """Authentication-related errors."""
    pass

class ConnectionError(MCPError):
    """Connection-related errors."""
    pass

class ToolError(MCPError):
    """Tool execution errors."""
    pass

class RateLimitError(MCPError):
    """Rate limit exceeded errors."""
    pass

@dataclass
class MCPTool:
    """MCP tool information."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

@dataclass
class MCPResponse:
    """MCP response wrapper."""
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: Optional[float] = None
    request_id: Optional[str] = None

class DcisionAIClient:
    """
    DcisionAI MCP Client for connecting to manufacturing optimization servers.
    
    Example:
        ```python
        import asyncio
        from dcisionai_mcp import DcisionAIClient
        
        async def main():
            client = DcisionAIClient(api_key="dai_your_api_key")
            
            # List available tools
            tools = await client.list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}")
            
            # Use manufacturing tools
            result = await client.manufacturing_intent_classification(
                query="Optimize production line efficiency"
            )
            print(f"Intent: {result.intent}")
        
        asyncio.run(main())
        ```
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://agentcore.dcisionai.com",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        enable_logging: bool = True
    ):
        """
        Initialize the DcisionAI MCP client.
        
        Args:
            api_key: Your DcisionAI API key (format: dai_xxxxxxxxxxxxxxxx)
            base_url: Base URL for the MCP server
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            enable_logging: Enable client logging
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enable_logging = enable_logging
        
        # Validate API key format
        if not self._validate_api_key(api_key):
            raise ValueError("Invalid API key format. Expected format: dai_xxxxxxxxxxxxxxxx")
        
        # Configure logging
        if enable_logging:
            self._setup_logging()
        
        # HTTP client configuration
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "DcisionAI-MCP-Client/1.0.0"
        }
        
        logger.info(f"🔗 DcisionAI MCP Client initialized (base_url: {base_url})")
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key format."""
        return api_key.startswith("dai_") and len(api_key) > 20
    
    def _setup_logging(self):
        """Setup client logging."""
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | DcisionAI MCP Client | %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
    
    async def _make_request(
        self,
        method: str,
        params: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> MCPResponse:
        """
        Make a request to the MCP server.
        
        Args:
            method: MCP method name
            params: Method parameters
            request_id: Optional request ID for tracking
            
        Returns:
            MCPResponse with result or error information
        """
        if request_id is None:
            request_id = f"req_{int(time.time() * 1000)}"
        
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params
        }
        
        start_time = time.time()
        
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/mcp",
                        headers=self.headers,
                        json=payload
                    )
                    
                    # Handle HTTP errors
                    if response.status_code == 401:
                        raise AuthenticationError("Invalid API key or authentication failed")
                    elif response.status_code == 429:
                        raise RateLimitError("Rate limit exceeded. Please try again later.")
                    elif response.status_code >= 500:
                        raise ConnectionError(f"Server error: {response.status_code}")
                    elif response.status_code != 200:
                        raise ConnectionError(f"HTTP error: {response.status_code}")
                    
                    # Parse JSON response
                    try:
                        data = response.json()
                    except json.JSONDecodeError as e:
                        raise ConnectionError(f"Invalid JSON response: {e}")
                    
                    # Handle MCP protocol errors
                    if "error" in data:
                        error = data["error"]
                        error_code = error.get("code", -1)
                        error_message = error.get("message", "Unknown error")
                        
                        if error_code == -32600:
                            raise ToolError(f"Invalid request: {error_message}")
                        elif error_code == -32601:
                            raise ToolError(f"Method not found: {error_message}")
                        elif error_code == -32602:
                            raise ToolError(f"Invalid parameters: {error_message}")
                        else:
                            raise ToolError(f"MCP error {error_code}: {error_message}")
                    
                    # Success response
                    execution_time = time.time() - start_time
                    result = data.get("result")
                    
                    logger.info(f"✅ MCP request successful (method: {method}, time: {execution_time:.2f}s)")
                    
                    return MCPResponse(
                        success=True,
                        result=result,
                        execution_time=execution_time,
                        request_id=request_id
                    )
                    
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                if attempt < self.max_retries:
                    logger.warning(f"⚠️ Request failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    raise ConnectionError(f"Connection failed after {self.max_retries + 1} attempts: {e}")
            
            except (AuthenticationError, RateLimitError, ToolError):
                # Don't retry these errors
                raise
            
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"⚠️ Unexpected error (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise MCPError(f"Request failed after {self.max_retries + 1} attempts: {e}")
        
        # This should never be reached
        raise MCPError("Maximum retries exceeded")
    
    async def list_tools(self) -> List[MCPTool]:
        """
        List all available tools on the MCP server.
        
        Returns:
            List of MCPTool objects
        """
        logger.info("📋 Listing available tools...")
        
        response = await self._make_request("tools/list", {})
        
        if not response.success:
            raise ToolError(f"Failed to list tools: {response.error}")
        
        tools = []
        for tool_data in response.result.get("tools", []):
            tool = MCPTool(
                name=tool_data["name"],
                description=tool_data["description"],
                input_schema=tool_data.get("inputSchema", {}),
                output_schema=tool_data.get("outputSchema", {})
            )
            tools.append(tool)
        
        logger.info(f"✅ Found {len(tools)} tools")
        return tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a specific tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        logger.info(f"🔧 Calling tool: {tool_name}")
        
        params = {
            "name": tool_name,
            "arguments": arguments
        }
        
        response = await self._make_request("tools/call", params)
        
        if not response.success:
            raise ToolError(f"Tool call failed: {response.error}")
        
        result = response.result.get("content", [])
        if result and len(result) > 0:
            # Extract text content from MCP response
            content = result[0].get("text", "")
            try:
                # Try to parse as JSON
                return json.loads(content)
            except json.JSONDecodeError:
                # Return as string if not JSON
                return content
        
        return result
    
    # Manufacturing-specific tool methods
    
    async def manufacturing_intent_classification(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Classify manufacturing intent using 5-agent peer-to-peer swarm collaboration.
        
        Args:
            query: Manufacturing query to classify
            context: Optional context information
            
        Returns:
            Intent classification result with intent, confidence, entities, objectives, and reasoning
        """
        logger.info(f"🎯 Classifying manufacturing intent: {query[:100]}...")
        
        arguments = {"query": query}
        if context:
            arguments["context"] = context
        
        result = await self.call_tool("manufacturing_intent_classification", arguments)
        
        logger.info(f"✅ Intent classified: {result.get('intent', 'unknown')} (confidence: {result.get('confidence', 0)})")
        return result
    
    async def manufacturing_data_analysis(
        self,
        data: Dict[str, Any],
        intent_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze manufacturing data using 3-agent peer-to-peer swarm collaboration.
        
        Args:
            data: Manufacturing data to analyze
            intent_result: Intent classification result
            
        Returns:
            Data analysis result with entities, requirements, insights, and readiness score
        """
        logger.info("📊 Analyzing manufacturing data...")
        
        arguments = {
            "data": data,
            "intent_result": intent_result
        }
        
        result = await self.call_tool("manufacturing_data_analysis", arguments)
        
        logger.info(f"✅ Data analysis completed (readiness score: {result.get('optimization_readiness_score', 0)})")
        return result
    
    async def manufacturing_model_builder(
        self,
        intent_result: Dict[str, Any],
        data_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build mathematical optimization models using 4-agent peer-to-peer swarm collaboration.
        
        Args:
            intent_result: Intent classification result
            data_result: Data analysis result
            
        Returns:
            Model building result with model type, variables, constraints, and objectives
        """
        logger.info("🏗️ Building optimization model...")
        
        arguments = {
            "intent_result": intent_result,
            "data_result": data_result
        }
        
        result = await self.call_tool("manufacturing_model_builder", arguments)
        
        logger.info(f"✅ Model built: {result.get('model_type', 'unknown')} with {len(result.get('variables', []))} variables")
        return result
    
    async def manufacturing_optimization_solver(
        self,
        model_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Solve optimization problems using 6-agent peer-to-peer swarm collaboration.
        
        Args:
            model_result: Model building result
            
        Returns:
            Optimization solution with optimal values and performance metrics
        """
        logger.info("🔧 Solving optimization...")
        
        arguments = {"model_result": model_result}
        
        result = await self.call_tool("manufacturing_optimization_solver", arguments)
        
        logger.info(f"✅ Optimization solved: {result.get('status', 'unknown')} (value: {result.get('optimal_value', 0)})")
        return result
    
    async def complete_manufacturing_optimization(
        self,
        query: str,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete manufacturing optimization workflow using all tools in sequence.
        
        Args:
            query: Manufacturing optimization query
            data: Manufacturing data
            context: Optional context information
            
        Returns:
            Complete optimization result with all intermediate steps
        """
        logger.info("🚀 Starting complete manufacturing optimization workflow...")
        
        # Step 1: Intent Classification
        intent_result = await self.manufacturing_intent_classification(query, context)
        
        # Step 2: Data Analysis
        data_result = await self.manufacturing_data_analysis(data, intent_result)
        
        # Step 3: Model Building
        model_result = await self.manufacturing_model_builder(intent_result, data_result)
        
        # Step 4: Optimization Solving
        solution_result = await self.manufacturing_optimization_solver(model_result)
        
        # Combine all results
        complete_result = {
            "intent_classification": intent_result,
            "data_analysis": data_result,
            "model_building": model_result,
            "optimization_solution": solution_result,
            "workflow_status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("🎉 Complete manufacturing optimization workflow finished successfully!")
        return complete_result
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the MCP server.
        
        Returns:
            Health status information
        """
        logger.info("🏥 Checking MCP server health...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health", headers=self.headers)
                
                if response.status_code == 200:
                    health_data = response.json()
                    logger.info("✅ MCP server is healthy")
                    return health_data
                else:
                    logger.warning(f"⚠️ MCP server health check failed: {response.status_code}")
                    return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

# Convenience functions for common use cases

async def quick_optimization(
    api_key: str,
    query: str,
    data: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Quick manufacturing optimization using the complete workflow.
    
    Args:
        api_key: Your DcisionAI API key
        query: Manufacturing optimization query
        data: Manufacturing data
        **kwargs: Additional client configuration options
        
    Returns:
        Complete optimization result
    """
    client = DcisionAIClient(api_key, **kwargs)
    return await client.complete_manufacturing_optimization(query, data)

def sync_optimization(
    api_key: str,
    query: str,
    data: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Synchronous version of quick_optimization.
    
    Args:
        api_key: Your DcisionAI API key
        query: Manufacturing optimization query
        data: Manufacturing data
        **kwargs: Additional client configuration options
        
    Returns:
        Complete optimization result
    """
    return asyncio.run(quick_optimization(api_key, query, data, **kwargs))

# Example usage
if __name__ == "__main__":
    async def example():
        # Initialize client
        client = DcisionAIClient(api_key="dai_your_api_key_here")
        
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")
        
        # Complete manufacturing optimization
        result = await client.complete_manufacturing_optimization(
            query="Optimize worker assignment across production lines to maximize efficiency",
            data={
                "total_workers": 50,
                "production_lines": 3,
                "max_hours_per_week": 48
            }
        )
        
        print(f"Optimization result: {result}")
    
    # Run example
    asyncio.run(example())
