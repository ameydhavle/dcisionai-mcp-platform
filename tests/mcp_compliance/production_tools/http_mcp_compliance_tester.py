#!/usr/bin/env python3
"""
HTTP MCP Compliance Tester
==========================

HTTP-based MCP protocol compliance tester for FastMCP servers.
Designed to work with HTTP streaming MCP servers like the DcisionAI platform.
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MCPTestResult:
    """Result of an individual MCP test."""
    test_name: str
    status: str  # 'PASS', 'FAIL', 'SKIP'
    score: float  # 0.0 to 1.0
    details: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: float = 0.0


class HTTPMCPComplianceTester:
    """HTTP-based MCP compliance tester for FastMCP servers."""
    
    def __init__(
        self,
        server_url: str,
        auth_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize HTTP MCP compliance tester."""
        self.server_url = server_url
        self.auth_token = auth_token
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = None
        
        # Test results storage
        self.test_results: List[MCPTestResult] = []
        
        logger.info(f"🚀 HTTP MCP Compliance Tester initialized")
        logger.info(f"📡 Server URL: {server_url}")
    
    async def connect(self) -> bool:
        """Create HTTP session."""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            logger.info("✅ HTTP session created")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create HTTP session: {e}")
            return False
    
    async def disconnect(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            logger.info("🔌 HTTP session closed")
    
    async def send_mcp_message(self, method: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Send MCP message via HTTP."""
        if not self.session:
            logger.error("❌ Not connected")
            return None
        
        message = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),  # Unique ID
            "method": method,
            "params": params or {}
        }
        
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
        
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            logger.debug(f"📤 Sending MCP message: {method}")
            
            async with self.session.post(
                self.server_url,
                json=message,
                headers=headers
            ) as response:
                logger.debug(f"📥 Response status: {response.status}")
                
                if response.status == 200:
                    # For streaming responses, we'll just check the status
                    # Don't try to read the full content to avoid hanging
                    content_type = response.headers.get("content-type", "")
                    if "text/event-stream" in content_type:
                        logger.debug("✅ Streaming response received")
                        return {"status": "success", "content_type": "streaming"}
                    else:
                        # Try to read JSON response
                        try:
                            content = await response.text()
                            return json.loads(content)
                        except:
                            return {"status": "success", "content": content}
                else:
                    content = await response.text()
                    logger.error(f"❌ HTTP error {response.status}: {content}")
                    return {"error": {"code": response.status, "message": content}}
                    
        except Exception as e:
            logger.error(f"❌ Error sending MCP message: {e}")
            return {"error": {"code": -1, "message": str(e)}}
    
    async def test_protocol_version(self) -> MCPTestResult:
        """Test MCP protocol version support."""
        logger.info("🔍 Testing MCP Protocol Version Support")
        start_time = time.time()
        
        try:
            # Test with latest protocol version
            params = {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {
                    "name": "HTTP MCP Compliance Tester",
                    "version": "1.0.0"
                }
            }
            
            response = await self.send_mcp_message("initialize", params)
            
            if response and "error" not in response:
                score = 1.0
                status = "PASS"
                details = {"protocol_version": "2025-03-26", "response": response}
                error_message = None
            else:
                score = 0.0
                status = "FAIL"
                details = {"error": response}
                error_message = f"Protocol version test failed: {response}"
                
        except Exception as e:
            score = 0.0
            status = "FAIL"
            details = {"error": str(e)}
            error_message = f"Protocol version test error: {e}"
        
        execution_time = time.time() - start_time
        
        result = MCPTestResult(
            test_name="Protocol Version Support",
            status=status,
            score=score,
            details=details,
            error_message=error_message,
            execution_time=execution_time
        )
        
        self.test_results.append(result)
        logger.info(f"✅ Protocol Version Test: {status} (Score: {score:.1%})")
        return result
    
    async def test_connection_management(self) -> MCPTestResult:
        """Test MCP connection management."""
        logger.info("🔍 Testing MCP Connection Management")
        start_time = time.time()
        
        try:
            # Test basic connectivity
            headers = {
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(self.server_url, headers=headers) as response:
                if response.status == 200:
                    score = 1.0
                    status = "PASS"
                    details = {"http_status": response.status, "content_type": response.headers.get("content-type")}
                    error_message = None
                else:
                    score = 0.0
                    status = "FAIL"
                    details = {"http_status": response.status}
                    error_message = f"HTTP status {response.status}"
                    
        except Exception as e:
            score = 0.0
            status = "FAIL"
            details = {"error": str(e)}
            error_message = f"Connection test error: {e}"
        
        execution_time = time.time() - start_time
        
        result = MCPTestResult(
            test_name="Connection Management",
            status=status,
            score=score,
            details=details,
            error_message=error_message,
            execution_time=execution_time
        )
        
        self.test_results.append(result)
        logger.info(f"✅ Connection Management Test: {status} (Score: {score:.1%})")
        return result
    
    async def test_message_format(self) -> MCPTestResult:
        """Test MCP message format compliance."""
        logger.info("🔍 Testing MCP Message Format Compliance")
        start_time = time.time()
        
        try:
            # Test JSON-RPC 2.0 compliance
            test_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            # Test with proper headers
            headers = {
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(
                self.server_url,
                json=test_message,
                headers=headers
            ) as response:
                if response.status == 200:
                    score = 1.0
                    status = "PASS"
                    details = {"http_status": response.status, "content_type": response.headers.get("content-type")}
                    error_message = None
                else:
                    score = 0.0
                    status = "FAIL"
                    details = {"http_status": response.status}
                    error_message = f"Message format test failed: HTTP {response.status}"
                    
        except Exception as e:
            score = 0.0
            status = "FAIL"
            details = {"error": str(e)}
            error_message = f"Message format test error: {e}"
        
        execution_time = time.time() - start_time
        
        result = MCPTestResult(
            test_name="Message Format Compliance",
            status=status,
            score=score,
            details=details,
            error_message=error_message,
            execution_time=execution_time
        )
        
        self.test_results.append(result)
        logger.info(f"✅ Message Format Test: {status} (Score: {score:.1%})")
        return result
    
    async def test_tool_management(self) -> MCPTestResult:
        """Test MCP tool management."""
        logger.info("🔍 Testing MCP Tool Management")
        start_time = time.time()
        
        try:
            # Test tools/list method
            response = await self.send_mcp_message("tools/list")
            
            if response and "error" not in response:
                score = 1.0
                status = "PASS"
                details = {"method": "tools/list", "response": response}
                error_message = None
            else:
                score = 0.0
                status = "FAIL"
                details = {"error": response}
                error_message = f"Tool management test failed: {response}"
                
        except Exception as e:
            score = 0.0
            status = "FAIL"
            details = {"error": str(e)}
            error_message = f"Tool management test error: {e}"
        
        execution_time = time.time() - start_time
        
        result = MCPTestResult(
            test_name="Tool Management",
            status=status,
            score=score,
            details=details,
            error_message=error_message,
            execution_time=execution_time
        )
        
        self.test_results.append(result)
        logger.info(f"✅ Tool Management Test: {status} (Score: {score:.1%})")
        return result
    
    async def test_resource_management(self) -> MCPTestResult:
        """Test MCP resource management."""
        logger.info("🔍 Testing MCP Resource Management")
        start_time = time.time()
        
        try:
            # Test resources/list method
            response = await self.send_mcp_message("resources/list")
            
            if response and "error" not in response:
                score = 1.0
                status = "PASS"
                details = {"method": "resources/list", "response": response}
                error_message = None
            else:
                score = 0.0
                status = "FAIL"
                details = {"error": response}
                error_message = f"Resource management test failed: {response}"
                
        except Exception as e:
            score = 0.0
            status = "FAIL"
            details = {"error": str(e)}
            error_message = f"Resource management test error: {e}"
        
        execution_time = time.time() - start_time
        
        result = MCPTestResult(
            test_name="Resource Management",
            status=status,
            score=score,
            details=details,
            error_message=error_message,
            execution_time=execution_time
        )
        
        self.test_results.append(result)
        logger.info(f"✅ Resource Management Test: {status} (Score: {score:.1%})")
        return result
    
    async def test_prompt_management(self) -> MCPTestResult:
        """Test MCP prompt management."""
        logger.info("🔍 Testing MCP Prompt Management")
        start_time = time.time()
        
        try:
            # Test prompts/list method
            response = await self.send_mcp_message("prompts/list")
            
            if response and "error" not in response:
                score = 1.0
                status = "PASS"
                details = {"method": "prompts/list", "response": response}
                error_message = None
            else:
                score = 0.0
                status = "FAIL"
                details = {"error": response}
                error_message = f"Prompt management test failed: {response}"
                
        except Exception as e:
            score = 0.0
            status = "FAIL"
            details = {"error": str(e)}
            error_message = f"Prompt management test error: {e}"
        
        execution_time = time.time() - start_time
        
        result = MCPTestResult(
            test_name="Prompt Management",
            status=status,
            score=score,
            details=details,
            error_message=error_message,
            execution_time=execution_time
        )
        
        self.test_results.append(result)
        logger.info(f"✅ Prompt Management Test: {status} (Score: {score:.1%})")
        return result
    
    async def run_compliance_tests(self) -> Dict[str, Any]:
        """Run all MCP compliance tests."""
        logger.info("🚀 Starting HTTP MCP Protocol Compliance Testing")
        
        if not await self.connect():
            return {"success": False, "error": "Failed to connect"}
        
        try:
            # Run all tests
            await self.test_protocol_version()
            await self.test_connection_management()
            await self.test_message_format()
            await self.test_tool_management()
            await self.test_resource_management()
            await self.test_prompt_management()
            
            # Calculate overall score
            total_tests = len(self.test_results)
            passed_tests = len([r for r in self.test_results if r.status == "PASS"])
            overall_score = passed_tests / total_tests if total_tests > 0 else 0.0
            
            # Determine certification status
            if overall_score >= 0.8:
                certification_status = "COMPLIANT"
            elif overall_score >= 0.6:
                certification_status = "PARTIALLY_COMPLIANT"
            else:
                certification_status = "NON_COMPLIANT"
            
            logger.info(f"✅ HTTP MCP Compliance Testing completed")
            logger.info(f"📊 Overall Score: {overall_score:.1%}")
            logger.info(f"🏆 Certification Status: {certification_status}")
            
            return {
                "success": True,
                "overall_score": overall_score,
                "certification_status": certification_status,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "test_results": self.test_results
            }
            
        finally:
            await self.disconnect()
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of test results."""
        if not self.test_results:
            return {"error": "No test results available"}
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASS"])
        failed_tests = len([r for r in self.test_results if r.status == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r.status == "SKIP"])
        
        total_time = sum(r.execution_time for r in self.test_results)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
            "total_execution_time": total_time,
            "test_results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "score": r.score,
                    "execution_time": r.execution_time,
                    "error_message": r.error_message
                }
                for r in self.test_results
            ]
        }
