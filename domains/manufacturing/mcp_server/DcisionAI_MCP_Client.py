#!/usr/bin/env python3
"""
DcisionAI MCP Client - AgentCore Integration
============================================

MCP client for communicating with our deployed AgentCore MCP server.
Implements proper MCP protocol compliance and tool discovery.

Features:
- MCP protocol compliance (JSON-RPC 2.0)
- Tool discovery and registration
- Multi-tenant context support
- Real-time tool execution
- Comprehensive error handling
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    """MCP tool definition."""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    tool_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.inputSchema,
            "toolId": self.tool_id
        }

@dataclass
class MCPRequest:
    """MCP request structure."""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
            "method": self.method,
            "params": self.params
        }

@dataclass
class MCPResponse:
    """MCP response structure."""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPResponse':
        """Create from dictionary."""
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            result=data.get("result"),
            error=data.get("error")
        )

class DcisionAIMCPClient:
    """MCP client for DcisionAI manufacturing tools."""
    
    def __init__(self, agent_runtime_arn: str, region: str = "us-east-1"):
        """Initialize MCP client."""
        self.agent_runtime_arn = agent_runtime_arn
        self.region = region
        self.session_id = None
        self.tenant_context = {}
        
        # MCP protocol state
        self.initialized = False
        self.capabilities = {}
        self.server_info = {}
        
        # Tool registry
        self.available_tools: List[MCPTool] = []
        
        logger.info(f"🚀 DcisionAI MCP Client initialized")
        logger.info(f"📡 Agent Runtime: {agent_runtime_arn}")
        logger.info(f"🌍 Region: {region}")
    
    def _get_invocation_url(self) -> str:
        """Get the AgentCore invocation URL."""
        # URL encode the ARN for the endpoint
        encoded_arn = self.agent_runtime_arn.replace(':', '%3A').replace('/', '%2F')
        return f"https://bedrock-agentcore.{self.region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    
    async def _send_request(self, request: MCPRequest) -> MCPResponse:
        """Send MCP request to AgentCore using AWS CLI for authentication."""
        import subprocess
        import json
        
        try:
            # Use AWS CLI to invoke the AgentCore runtime with proper authentication
            # This ensures we use the configured AWS credentials and IAM permissions
            
            # Prepare the request payload
            request_payload = {
                "prompt": request.params.get("prompt", ""),
                "tenantContext": request.params.get("tenantContext", {})
            }
            
            # Convert to JSON string and then base64 encode for AWS CLI
            request_json = json.dumps(request_payload)
            import base64
            request_base64 = base64.b64encode(request_json.encode()).decode()
            
            # Build AWS CLI command with proper MCP protocol headers
            cmd = [
                "aws", "bedrock-agentcore", "invoke-agent-runtime",
                "--agent-runtime-arn", self.agent_runtime_arn,
                "--payload", request_base64,
                "--content-type", "application/json",
                "--accept", "application/json",
                "--mcp-session-id", f"session-{int(time.time())}",
                "--mcp-protocol-version", "2024-11-05",
                "--region", self.region,
                "--output", "json",
                "/tmp/agentcore_response.json"  # outfile parameter
            ]
            
            logger.debug(f"Executing AWS CLI command: {' '.join(cmd)}")
            
            # Execute the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # Parse the response from the output file
                try:
                    import os
                    if os.path.exists("/tmp/agentcore_response.json"):
                        with open("/tmp/agentcore_response.json", "r") as f:
                            response_data = json.load(f)
                        
                        # Clean up the temporary file
                        os.remove("/tmp/agentcore_response.json")
                        
                        return MCPResponse(
                            id=request.id,
                            result=response_data
                        )
                    else:
                        logger.error("Response file not found")
                        return MCPResponse(
                            id=request.id,
                            error={
                                "code": -32603,
                                "message": "Response file not found"
                            }
                        )
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse response: {e}")
                    return MCPResponse(
                        id=request.id,
                        error={
                            "code": -32603,
                            "message": f"Invalid response format: {str(e)}"
                        }
                    )
            else:
                # Handle AWS CLI errors
                error_message = result.stderr.strip()
                logger.error(f"AWS CLI error: {error_message}")
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32603,
                        "message": f"AWS CLI error: {error_message}"
                    }
                )
                        
        except subprocess.TimeoutExpired:
            logger.error("Request timed out")
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": "Request timed out"
                }
            )
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Request failed: {str(e)}"
                }
            )
    
    async def initialize(self, client_info: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize MCP session."""
        try:
            logger.info("🔌 Initializing MCP session...")
            
            # Create initialization request
            request = MCPRequest(
                method="initialize",
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": client_info or {
                        "name": "DcisionAI-MCP-Client",
                        "version": "1.0.0"
                    }
                }
            )
            
            # Send request
            response = await self._send_request(request)
            
            if response.error:
                logger.error(f"Initialization failed: {response.error}")
                return False
            
            # Store server capabilities and info
            if response.result:
                self.capabilities = response.result.get("capabilities", {})
                self.server_info = response.result.get("serverInfo", {})
                self.initialized = True
                
                logger.info("✅ MCP session initialized successfully")
                logger.info(f"📋 Server: {self.server_info.get('name', 'Unknown')} v{self.server_info.get('version', 'Unknown')}")
                logger.info(f"🔧 Capabilities: {list(self.capabilities.keys())}")
                
                return True
            else:
                logger.error("❌ No result in initialization response")
                return False
                
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def list_tools(self) -> List[MCPTool]:
        """List available tools."""
        try:
            if not self.initialized:
                logger.error("❌ Session not initialized")
                return []
            
            logger.info("🔍 Discovering available tools...")
            
            # Create tools/list request
            request = MCPRequest(method="tools/list")
            response = await self._send_request(request)
            
            if response.error:
                logger.error(f"Tool discovery failed: {response.error}")
                return []
            
            # Parse tools from response
            if response.result and "tools" in response.result:
                tools_data = response.result["tools"]
                self.available_tools = []
                
                for tool_data in tools_data:
                    tool = MCPTool(
                        name=tool_data.get("name", ""),
                        description=tool_data.get("description", ""),
                        inputSchema=tool_data.get("inputSchema", {}),
                        tool_id=tool_data.get("toolId")
                    )
                    self.available_tools.append(tool)
                
                logger.info(f"✅ Discovered {len(self.available_tools)} tools")
                for tool in self.available_tools:
                    logger.info(f"   🔧 {tool.name}: {tool.description}")
                
                return self.available_tools
            else:
                logger.warning("⚠️ No tools found in response")
                return []
                
        except Exception as e:
            logger.error(f"❌ Tool discovery failed: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a specific tool."""
        try:
            if not self.initialized:
                logger.error("❌ Session not initialized")
                return None
            
            # Find the tool
            tool = next((t for t in self.available_tools if t.name == tool_name), None)
            if not tool:
                logger.error(f"❌ Tool '{tool_name}' not found")
                return None
            
            logger.info(f"🔧 Calling tool: {tool_name}")
            logger.info(f"   Arguments: {arguments}")
            
            # Create tools/call request
            request = MCPRequest(
                method="tools/call",
                params={
                    "name": tool_name,
                    "arguments": arguments
                }
            )
            
            response = await self._send_request(request)
            
            if response.error:
                logger.error(f"❌ Tool execution failed: {response.error}")
                return None
            
            if response.result:
                logger.info(f"✅ Tool '{tool_name}' executed successfully")
                return response.result
            else:
                logger.warning(f"⚠️ No result from tool '{tool_name}'")
                return None
                
        except Exception as e:
            logger.error(f"❌ Tool execution failed: {e}")
            return None
    
    async def execute_manufacturing_workflow(self, user_message: str, tenant_context: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> Dict[str, Any]:
        """Execute the complete manufacturing optimization workflow with retry logic."""
        try:
            logger.info("🚀 Executing manufacturing optimization workflow...")
            logger.info(f"   Message: {user_message}")
            logger.info(f"   Tenant: {tenant_context}")
            logger.info(f"   Max Retries: {max_retries}")
            
            # Set tenant context
            if tenant_context:
                self.tenant_context = tenant_context
            
            # Execute the workflow using the invoke method with retry logic
            for attempt in range(max_retries):
                try:
                    logger.info(f"🔄 Attempt {attempt + 1}/{max_retries}")
                    
                    workflow_request = MCPRequest(
                        method="invoke",
                        params={
                            "jsonrpc": "2.0",
                            "id": f"mcp-{int(time.time())}",
                            "method": "invoke",
                            "params": {
                                "prompt": user_message,
                                "tenantContext": tenant_context or {
                                    "tenant_id": "default",
                                    "sla_tier": "free",
                                    "region": "us-east-1"
                                },
                                "session_id": f"mcp-session-{int(time.time())}"
                            }
                        }
                    )
                    
                    response = await self._send_request(workflow_request)
                    
                    if response.error:
                        error_message = str(response.error)
                        
                        # Check if it's a cold start issue
                        if "starting the runtime" in error_message.lower() or "runtimeclienterror" in error_message.lower():
                            if attempt < max_retries - 1:
                                wait_time = (attempt + 1) * 5  # Progressive backoff: 5s, 10s, 15s
                                logger.warning(f"⚠️ Cold start detected. Waiting {wait_time}s before retry...")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                logger.error("❌ Max retries reached for cold start")
                                return {
                                    "error": "RUNTIME_COLD_START_MAX_RETRIES",
                                    "message": "Runtime failed to start after multiple attempts",
                                    "suggestion": "Please wait a few minutes and try again"
                                }
                        else:
                            logger.error(f"❌ Workflow execution failed: {response.error}")
                            return {"error": f"Workflow failed: {response.error}"}
                    
                    if response.result:
                        logger.info("✅ Manufacturing workflow completed successfully")
                        return response.result
                    else:
                        logger.warning("⚠️ No result from workflow execution")
                        return {"error": "No workflow result"}
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}. Retrying...")
                        await asyncio.sleep(2)  # Brief pause before retry
                        continue
                    else:
                        logger.error(f"❌ All attempts failed: {e}")
                        raise
                        
        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {e}")
            return {"error": f"Workflow failed: {str(e)}"}
    
    def set_tenant_context(self, tenant_context: Dict[str, Any]):
        """Set tenant context for subsequent requests."""
        self.tenant_context = tenant_context
        logger.info(f"🏷️ Tenant context set: {tenant_context}")
    
    async def close(self):
        """Close the MCP session."""
        try:
            if self.initialized:
                logger.info("🔌 Closing MCP session...")
                
                # Send shutdown request
                request = MCPRequest(method="notifications/shutdown")
                await self._send_request(request)
                
                self.initialized = False
                logger.info("✅ MCP session closed")
                
        except Exception as e:
            logger.error(f"❌ Error closing session: {e}")

# Example usage and testing
async def main():
    """Test the MCP client."""
    # AgentCore runtime ARN from our deployment
    agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_Agent_v1_1756943746-0OgdtC2Je6"
    
    # Create client
    client = DcisionAIMCPClient(agent_runtime_arn)
    
    try:
        # Test different tenant scenarios
        test_cases = [
            {
                "message": "Optimize production scheduling for 3 manufacturing lines",
                "tenant": {"tenant_id": "gold_tenant", "sla_tier": "gold", "region": "us-east-1"}
            },
            {
                "message": "Minimize costs in supply chain operations",
                "tenant": {"tenant_id": "pro_tenant", "sla_tier": "pro", "region": "us-west-2"}
            },
            {
                "message": "Improve quality in assembly line",
                "tenant": {"tenant_id": "free_tenant", "sla_tier": "free", "region": "us-east-1"}
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🧪 Testing: {test_case['message']}")
            print(f"Tenant: {test_case['tenant']}")
            
            result = await client.execute_manufacturing_workflow(
                test_case['message'], 
                test_case['tenant']
            )
            
            print(f"Result: {json.dumps(result, indent=2)}")
            print("-" * 80)
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
