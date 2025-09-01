#!/usr/bin/env python3
"""
DcisionAI Platform - Enhanced Gateway Client
============================================

Phase 2: Multi-domain tool management with inference profile integration.
Provides MCP protocol support and intelligent tool routing.
"""

import logging
import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import aiohttp
import jwt
import yaml
from pathlib import Path

from .inference_manager import InferenceManager, InferenceRequest, InferenceResult

@dataclass
class GatewayTool:
    """Represents a tool available through the Gateway."""
    name: str
    domain: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    capabilities: List[str]
    inference_profile: str
    max_execution_time: int
    version: str
    status: str  # "active", "inactive", "maintenance"

@dataclass
class GatewayRequest:
    """Represents a request to the Gateway."""
    request_id: str
    tool_name: str
    domain: str
    payload: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    priority: str = "normal"
    timeout: int = 300
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class GatewayResponse:
    """Represents a response from the Gateway."""
    request_id: str
    success: bool
    data: Any
    tool_used: str
    domain: str
    execution_time: float
    cost: float
    metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class GatewayClient:
    """
    Enhanced Gateway client for multi-domain tool management.
    
    Features:
    - MCP protocol support
    - Intelligent tool routing
    - Inference profile integration
    - Authentication and authorization
    - Performance monitoring
    """
    
    def __init__(self, config_path: str = "shared/config/gateway_config.yaml"):
        """Initialize the Gateway client with configuration."""
        self.logger = logging.getLogger("gateway_client")
        self.logger.setLevel(logging.INFO)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize inference manager
        self.inference_manager = InferenceManager()
        
        # Initialize HTTP session
        self.session = None
        
        # Tool registry
        self.tools: Dict[str, GatewayTool] = {}
        
        # Performance metrics
        self.request_count = 0
        self.total_execution_time = 0.0
        self.total_cost = 0.0
        
        # Initialize tools
        self._initialize_tools()
        
        self.logger.info("✅ Enhanced Gateway Client initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load Gateway configuration from YAML file."""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                self.logger.info(f"✅ Loaded Gateway configuration from {config_path}")
                return config
            else:
                self.logger.warning(f"⚠️ Configuration file not found: {config_path}")
                return self._get_default_config()
        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file loading fails."""
        return {
            "gateway": {
                "name": "DcisionAI_Enhanced_Gateway",
                "endpoints": {
                    "primary": "https://gateway.dcisionai.com"
                }
            },
            "mcp": {
                "protocol_version": "2025-03-26",
                "search_type": "SEMANTIC"
            },
            "domains": {
                "manufacturing": {"status": "active"},
                "finance": {"status": "active"},
                "pharma": {"status": "active"}
            }
        }
    
    def _initialize_tools(self):
        """Initialize the tool registry with domain-specific tools."""
        try:
            # Manufacturing Domain Tools
            self.tools["manufacturing_intent"] = GatewayTool(
                name="intent_classification",
                domain="manufacturing",
                description="Classify manufacturing optimization intent",
                input_schema={"query": "string", "context": "object"},
                output_schema={"intent": "string", "confidence": "float"},
                capabilities=["intent_classification", "manufacturing"],
                inference_profile="manufacturing",
                max_execution_time=300,
                version="1.0.0",
                status="active"
            )
            
            self.tools["manufacturing_data"] = GatewayTool(
                name="data_analysis",
                domain="manufacturing",
                description="Analyze manufacturing data for optimization",
                input_schema={"data": "object", "analysis_type": "string"},
                output_schema={"insights": "array", "recommendations": "array"},
                capabilities=["data_analysis", "manufacturing"],
                inference_profile="manufacturing",
                max_execution_time=300,
                version="1.0.0",
                status="active"
            )
            
            self.tools["manufacturing_model"] = GatewayTool(
                name="model_building",
                domain="manufacturing",
                description="Build optimization models for manufacturing",
                input_schema={"parameters": "object", "constraints": "array"},
                output_schema={"model": "object", "validation": "object"},
                capabilities=["model_building", "manufacturing"],
                inference_profile="manufacturing",
                max_execution_time=300,
                version="1.0.0",
                status="active"
            )
            
            self.tools["manufacturing_solver"] = GatewayTool(
                name="optimization_solving",
                domain="manufacturing",
                description="Solve manufacturing optimization problems",
                input_schema={"model": "object", "solver_params": "object"},
                output_schema={"solution": "object", "performance": "object"},
                capabilities=["optimization_solving", "manufacturing"],
                inference_profile="manufacturing",
                max_execution_time=300,
                version="1.0.0",
                status="active"
            )
            
            # Finance Domain Tools
            self.tools["finance_risk"] = GatewayTool(
                name="risk_assessment",
                domain="finance",
                description="Assess financial risk and exposure",
                input_schema={"portfolio": "object", "risk_metrics": "array"},
                output_schema={"risk_score": "float", "recommendations": "array"},
                capabilities=["risk_assessment", "finance"],
                inference_profile="finance",
                max_execution_time=180,
                version="1.0.0",
                status="active"
            )
            
            self.tools["finance_portfolio"] = GatewayTool(
                name="portfolio_optimization",
                domain="finance",
                description="Optimize financial portfolio allocation",
                input_schema={"assets": "array", "constraints": "object"},
                output_schema={"allocation": "object", "expected_return": "float"},
                capabilities=["portfolio_optimization", "finance"],
                inference_profile="finance",
                max_execution_time=180,
                version="1.0.0",
                status="active"
            )
            
            self.tools["finance_fraud"] = GatewayTool(
                name="fraud_detection",
                domain="finance",
                description="Detect fraudulent financial activities",
                input_schema={"transactions": "array", "patterns": "array"},
                output_schema={"fraud_score": "float", "alerts": "array"},
                capabilities=["fraud_detection", "finance"],
                inference_profile="finance",
                max_execution_time=180,
                version="1.0.0",
                status="active"
            )
            
            self.tools["finance_compliance"] = GatewayTool(
                name="compliance_checking",
                domain="finance",
                description="Check financial compliance requirements",
                input_schema={"operations": "array", "regulations": "array"},
                output_schema={"compliance_status": "string", "violations": "array"},
                capabilities=["compliance_checking", "finance"],
                inference_profile="finance",
                max_execution_time=180,
                version="1.0.0",
                status="active"
            )
            
            # Pharma Domain Tools
            self.tools["pharma_drug"] = GatewayTool(
                name="drug_discovery",
                domain="pharma",
                description="Discover new drug candidates",
                input_schema={"target": "object", "screening_data": "array"},
                output_schema={"candidates": "array", "success_probability": "float"},
                capabilities=["drug_discovery", "pharma"],
                inference_profile="pharma",
                max_execution_time=600,
                version="1.0.0",
                status="active"
            )
            
            self.tools["pharma_trial"] = GatewayTool(
                name="clinical_trial_optimization",
                domain="pharma",
                description="Optimize clinical trial design and execution",
                input_schema={"trial_params": "object", "constraints": "array"},
                output_schema={"design": "object", "timeline": "object"},
                capabilities=["clinical_trial_optimization", "pharma"],
                inference_profile="pharma",
                max_execution_time=600,
                version="1.0.0",
                status="active"
            )
            
            self.tools["pharma_supply"] = GatewayTool(
                name="supply_chain_management",
                domain="pharma",
                description="Manage pharmaceutical supply chain",
                input_schema={"supply_data": "object", "demand_forecast": "object"},
                output_schema={"optimization": "object", "cost_savings": "float"},
                capabilities=["supply_chain_management", "pharma"],
                inference_profile="pharma",
                max_execution_time=600,
                version="1.0.0",
                status="active"
            )
            
            self.tools["pharma_regulatory"] = GatewayTool(
                name="regulatory_compliance",
                domain="pharma",
                description="Ensure regulatory compliance for pharmaceuticals",
                input_schema={"product_data": "object", "regulations": "array"},
                output_schema={"compliance_status": "string", "requirements": "array"},
                capabilities=["regulatory_compliance", "pharma"],
                inference_profile="pharma",
                max_execution_time=600,
                version="1.0.0",
                status="active"
            )
            
            self.logger.info(f"✅ Initialized {len(self.tools)} tools across all domains")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize tools: {e}")
            raise
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def discover_tools(self, domain: Optional[str] = None, 
                           query: Optional[str] = None) -> List[GatewayTool]:
        """
        Discover available tools through the Gateway.
        
        Args:
            domain: Optional domain filter
            query: Optional semantic search query
            
        Returns:
            List of available tools
        """
        try:
            if domain:
                # Filter by domain
                domain_tools = [
                    tool for tool in self.tools.values() 
                    if tool.domain == domain and tool.status == "active"
                ]
                return domain_tools
            
            elif query:
                # Semantic search (simplified implementation)
                matching_tools = []
                query_lower = query.lower()
                
                for tool in self.tools.values():
                    if tool.status != "active":
                        continue
                    
                    # Simple keyword matching
                    if (query_lower in tool.name.lower() or 
                        query_lower in tool.description.lower() or
                        any(query_lower in cap.lower() for cap in tool.capabilities)):
                        matching_tools.append(tool)
                
                return matching_tools
            
            else:
                # Return all active tools
                return [tool for tool in self.tools.values() if tool.status == "active"]
                
        except Exception as e:
            self.logger.error(f"❌ Tool discovery failed: {e}")
            return []
    
    async def invoke_tool(self, tool_name: str, payload: Dict[str, Any], 
                         user_id: Optional[str] = None, 
                         session_id: Optional[str] = None) -> GatewayResponse:
        """
        Invoke a tool through the Gateway with inference optimization.
        
        Args:
            tool_name: Name of the tool to invoke
            payload: Tool input data
            user_id: Optional user identifier
            session_id: Optional session identifier
            
        Returns:
            GatewayResponse with tool execution results
        """
        start_time = time.time()
        
        try:
            # Validate tool exists and is active
            if tool_name not in self.tools:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            tool = self.tools[tool_name]
            if tool.status != "active":
                raise ValueError(f"Tool '{tool_name}' is not active (status: {tool.status})")
            
            # Create Gateway request
            gateway_request = GatewayRequest(
                request_id=f"req_{int(time.time() * 1000)}",
                tool_name=tool_name,
                domain=tool.domain,
                payload=payload,
                user_id=user_id,
                session_id=session_id,
                timeout=tool.max_execution_time
            )
            
            # Create inference request
            inference_request = InferenceRequest(
                request_id=gateway_request.request_id,
                domain=tool.domain,
                request_type=tool.name,
                payload=payload,
                timeout=tool.max_execution_time
            )
            
            # Execute through inference manager
            inference_result = await self.inference_manager.execute_inference(inference_request)
            
            # Calculate execution time and cost
            execution_time = time.time() - start_time
            cost = inference_result.cost
            
            # Update metrics
            self.request_count += 1
            self.total_execution_time += execution_time
            self.total_cost += cost
            
            # Create Gateway response
            response = GatewayResponse(
                request_id=gateway_request.request_id,
                success=inference_result.success,
                data=inference_result.data,
                tool_used=tool_name,
                domain=tool.domain,
                execution_time=execution_time,
                cost=cost,
                metadata={
                    "tool_version": tool.version,
                    "inference_profile": tool.inference_profile,
                    "region_used": inference_result.region_used,
                    "user_id": user_id,
                    "session_id": session_id
                }
            )
            
            self.logger.info(f"✅ Tool '{tool_name}' executed successfully "
                           f"({execution_time:.2f}s, ${cost:.4f})")
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"❌ Tool invocation failed: {e}")
            
            return GatewayResponse(
                request_id=f"req_{int(time.time() * 1000)}",
                success=False,
                data=None,
                tool_used=tool_name,
                domain="unknown",
                execution_time=execution_time,
                cost=0.0,
                metadata={"error": str(e)}
            )
    
    async def invoke_with_profile(self, profile_arn: str, region: str, 
                                request: Dict[str, Any], timeout: int = 300) -> Dict[str, Any]:
        """
        Invoke inference with a specific profile and region.
        
        Args:
            profile_arn: ARN of the inference profile
            region: AWS region to use
            request: Inference request data
            timeout: Request timeout in seconds
            
        Returns:
            Inference result
        """
        try:
            # This would integrate with actual AWS Bedrock inference
            # For now, simulate the execution
            
            # Create inference request
            inference_request = InferenceRequest(
                request_id=f"profile_{int(time.time() * 1000)}",
                domain="unknown",
                request_type="profile_inference",
                payload=request,
                timeout=timeout
            )
            
            # Execute through inference manager
            result = await self.inference_manager.execute_inference(inference_request)
            
            return {
                "success": result.success,
                "data": result.data,
                "region": region,
                "profile_arn": profile_arn,
                "execution_time": result.execution_time,
                "cost": result.cost
            }
            
        except Exception as e:
            self.logger.error(f"❌ Profile inference failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "region": region,
                "profile_arn": profile_arn
            }
    
    def get_tool_info(self, tool_name: str) -> Optional[GatewayTool]:
        """Get information about a specific tool."""
        return self.tools.get(tool_name)
    
    def get_domain_tools(self, domain: str) -> List[GatewayTool]:
        """Get all tools for a specific domain."""
        return [tool for tool in self.tools.values() if tool.domain == domain]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            "timestamp": datetime.now().isoformat(),
            "request_count": self.request_count,
            "total_execution_time": self.total_execution_time,
            "total_cost": self.total_cost,
            "average_execution_time": (
                self.total_execution_time / self.request_count 
                if self.request_count > 0 else 0.0
            ),
            "average_cost_per_request": (
                self.total_cost / self.request_count 
                if self.request_count > 0 else 0.0
            ),
            "tools_count": len(self.tools),
            "active_tools": len([t for t in self.tools.values() if t.status == "active"]),
            "domains": list(set(tool.domain for tool in self.tools.values()))
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the Gateway client."""
        try:
            # Check inference manager health
            inference_health = self.inference_manager.health_check()
            
            # Check tool registry health
            tool_health = {
                "total_tools": len(self.tools),
                "active_tools": len([t for t in self.tools.values() if t.status == "active"]),
                "inactive_tools": len([t for t in self.tools.values() if t.status == "inactive"]),
                "maintenance_tools": len([t for t in self.tools.values() if t.status == "maintenance"])
            }
            
            # Determine overall health
            overall_status = "healthy"
            if inference_health["status"] != "healthy":
                overall_status = "degraded"
            if tool_health["active_tools"] == 0:
                overall_status = "unhealthy"
            
            return {
                'status': overall_status,
                'timestamp': datetime.now().isoformat(),
                'gateway_client': 'healthy',
                'inference_manager': inference_health,
                'tool_registry': tool_health,
                'performance_metrics': self.get_performance_metrics()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def close(self):
        """Close the Gateway client and cleanup resources."""
        try:
            if self.session:
                await self.session.close()
            
            # Cleanup inference manager
            await self.inference_manager.cleanup()
            
            self.logger.info("✅ Gateway client closed successfully")
        except Exception as e:
            self.logger.error(f"❌ Error closing Gateway client: {e}")

# Utility functions for MCP protocol support
def create_mcp_tool_description(tool: GatewayTool) -> Dict[str, Any]:
    """Create MCP-compatible tool description."""
    return {
        "name": tool.name,
        "description": tool.description,
        "inputSchema": tool.input_schema,
        "outputSchema": tool.output_schema,
        "capabilities": tool.capabilities,
        "domain": tool.domain,
        "version": tool.version,
        "status": tool.status,
        "maxExecutionTime": tool.max_execution_time
    }

def create_mcp_response(gateway_response: GatewayResponse) -> Dict[str, Any]:
    """Create MCP-compatible response."""
    return {
        "requestId": gateway_response.request_id,
        "success": gateway_response.success,
        "data": gateway_response.data,
        "toolUsed": gateway_response.tool_used,
        "domain": gateway_response.domain,
        "executionTime": gateway_response.execution_time,
        "cost": gateway_response.cost,
        "metadata": gateway_response.metadata,
        "timestamp": gateway_response.timestamp.isoformat()
    }
