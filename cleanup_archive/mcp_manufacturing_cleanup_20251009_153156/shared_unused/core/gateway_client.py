#!/usr/bin/env python3
"""
DcisionAI Platform - Multi-Tenant Gateway Client
================================================

Enterprise-grade gateway client for:
- Tool discovery and registry management
- Multi-tenant tool routing and orchestration
- Policy-based access control
- Fallback strategies and load balancing

Based on enterprise multi-tenant platform blueprint.
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional, Union, Callable
from contextvars import ContextVar

from .base_agent import TenantContext, get_current_tenant

logger = logging.getLogger(__name__)

class ToolStatus(Enum):
    """Tool availability status."""
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"

class ToolCategory(Enum):
    """Tool categories for organization."""
    SOLVER = "solver"
    DATA = "data"
    MODEL = "model"
    INTENT = "intent"
    EXPLAIN = "explain"
    CRITIQUE = "critique"
    UTILITY = "utility"

@dataclass
class ToolDefinition:
    """Tool definition with metadata and capabilities."""
    tool_id: str
    name: str
    description: str
    category: ToolCategory
    version: str
    status: ToolStatus = ToolStatus.AVAILABLE
    
    # Capabilities and requirements
    capabilities: List[str] = field(default_factory=list)
    required_entitlements: List[str] = field(default_factory=list)
    pii_handling: str = "none"
    
    # Performance characteristics
    avg_response_time: float = 0.1  # seconds
    max_concurrent_requests: int = 100
    cost_per_request: float = 0.001
    
    # Multi-tenant support
    supports_multi_tenancy: bool = True
    tenant_isolation: str = "logical"  # logical, physical, hybrid
    
    # Health and monitoring
    last_health_check: Optional[datetime] = None
    error_rate: float = 0.0
    uptime_percentage: float = 99.9
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "version": self.version,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "required_entitlements": self.required_entitlements,
            "pii_handling": self.pii_handling,
            "avg_response_time": self.avg_response_time,
            "max_concurrent_requests": self.max_concurrent_requests,
            "cost_per_request": self.cost_per_request,
            "supports_multi_tenancy": self.supports_multi_tenancy,
            "tenant_isolation": self.tenant_isolation,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "error_rate": self.error_rate,
            "uptime_percentage": self.uptime_percentage
        }
    
    def is_available_for_tenant(self, tenant_context: TenantContext) -> bool:
        """Check if tool is available for the given tenant."""
        if self.status != ToolStatus.AVAILABLE:
            return False
        
        # Check entitlements
        if self.required_entitlements:
            tenant_entitlements = set(tenant_context.entitlements)
            required_entitlements = set(self.required_entitlements)
            if not required_entitlements.issubset(tenant_entitlements):
                return False
        
        # Check PII handling requirements
        if self.pii_handling != "none" and tenant_context.pii_scope.value == "none":
            return False
        
        return True

@dataclass
class ToolRequest:
    """Tool execution request."""
    request_id: str
    tool_id: str
    tenant_context: TenantContext
    parameters: Dict[str, Any]
    priority: str = "normal"
    timeout: int = 60
    fallback_strategy: str = "auto"  # auto, manual, none
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())

@dataclass
class ToolResponse:
    """Tool execution response."""
    request_id: str
    tool_id: str
    success: bool
    result: Dict[str, Any]
    execution_time: float
    cost: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    fallback_used: Optional[str] = None
    completed_at: datetime = field(default_factory=datetime.utcnow)

class GatewayClient:
    """
    Multi-tenant gateway client for tool orchestration and discovery.
    
    Features:
    - Tool registry management with tenant filtering
    - Policy-based access control
    - Automatic fallback strategies
    - Load balancing and health monitoring
    - Multi-tenant isolation
    """
    
    def __init__(self, 
                 registry_url: Optional[str] = None,
                 enable_auto_discovery: bool = True):
        """
        Initialize the gateway client.
        
        Args:
            registry_url: URL for external tool registry
            enable_auto_discovery: Enable automatic tool discovery
        """
        self.registry_url = registry_url
        self.enable_auto_discovery = enable_auto_discovery
        
        # Tool registry
        self.tool_registry: Dict[str, ToolDefinition] = {}
        self.tool_instances: Dict[str, Any] = {}
        
        # Performance tracking
        self.request_history: List[ToolRequest] = []
        self.response_history: List[ToolResponse] = []
        
        # Health monitoring
        self.health_check_interval = 30  # seconds
        self.health_check_task: Optional[asyncio.Task] = None
        
        # Fallback strategies
        self.fallback_strategies: Dict[str, List[str]] = {}
        
        # Multi-tenant policies
        self.tenant_policies: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default tools
        self._initialize_default_tools()
        
        logger.info("✅ Gateway Client initialized successfully")
    
    def _initialize_default_tools(self):
        """Initialize default tools for the platform."""
        default_tools = {
            "solver-ortools": ToolDefinition(
                tool_id="solver-ortools",
                name="OR-Tools Solver",
                description="Google OR-Tools optimization solver",
                category=ToolCategory.SOLVER,
                version="1.0.0",
                capabilities=["linear_programming", "integer_programming", "constraint_programming"],
                required_entitlements=["solver.ortools"],
                cost_per_request=0.001
            ),
            "solver-highs": ToolDefinition(
                tool_id="solver-highs",
                name="HiGHS Solver",
                description="High-performance optimization solver",
                category=ToolCategory.SOLVER,
                version="1.0.0",
                capabilities=["linear_programming", "mixed_integer_programming"],
                required_entitlements=["solver.highs"],
                cost_per_request=0.002
            ),
            "data-analyzer": ToolDefinition(
                tool_id="data-analyzer",
                name="Data Analyzer",
                description="Multi-tenant data analysis tool",
                category=ToolCategory.DATA,
                version="1.0.0",
                capabilities=["data_analysis", "statistics", "visualization"],
                required_entitlements=["data.analysis"],
                pii_handling="basic"
            ),
            "model-builder": ToolDefinition(
                tool_id="model-builder",
                name="Model Builder",
                description="Optimization model construction tool",
                category=ToolCategory.MODEL,
                version="1.0.0",
                capabilities=["model_construction", "constraint_definition", "variable_creation"],
                required_entitlements=["model.builder"]
            )
        }
        
        self.tool_registry.update(default_tools)
        
        # Initialize fallback strategies
        self.fallback_strategies = {
            "solver-ortools": ["solver-highs", "solver-cbc"],
            "solver-highs": ["solver-ortools", "solver-cbc"],
            "data-analyzer": ["data-basic"],
            "model-builder": ["model-simple"]
        }
        
        logger.info(f"✅ Initialized {len(default_tools)} default tools")
    
    async def start(self):
        """Start the gateway client."""
        try:
            # Start health monitoring
            self.health_check_task = asyncio.create_task(self._health_monitor_loop())
            
            # Discover tools if enabled
            if self.enable_auto_discovery:
                await self._discover_tools()
            
            logger.info("✅ Gateway Client started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Gateway Client: {e}")
            raise
    
    async def stop(self):
        """Stop the gateway client."""
        try:
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("✅ Gateway Client stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping Gateway Client: {e}")
    
    async def execute_tool(self, request: ToolRequest) -> ToolResponse:
        """
        Execute a tool with tenant context and fallback support.
        
        Args:
            request: Tool execution request
            
        Returns:
            Tool execution response
        """
        start_time = time.time()
        
        try:
            # Validate tool availability
            tool_def = self.tool_registry.get(request.tool_id)
            if not tool_def:
                return ToolResponse(
                    request_id=request.request_id,
                    tool_id=request.tool_id,
                    success=False,
                    result={},
                    execution_time=0.0,
                    cost=0.0,
                    error=f"Tool {request.tool_id} not found"
                )
            
            # Check tenant access
            if not tool_def.is_available_for_tenant(request.tenant_context):
                return ToolResponse(
                    request_id=request.request_id,
                    tool_id=request.tool_id,
                    success=False,
                    result={},
                    execution_time=0.0,
                    cost=0.0,
                    error=f"Tool {request.tool_id} not available for tenant {request.tenant_context.tenant_id}"
                )
            
            # Execute tool
            result = await self._execute_tool_instance(request, tool_def)
            
            # Update metrics
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            result.completed_at = datetime.utcnow()
            
            # Store results
            self.response_history.append(result)
            
            logger.info(f"✅ Tool {request.tool_id} executed successfully in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Tool execution failed: {e}")
            
            # Try fallback if enabled
            if request.fallback_strategy == "auto":
                fallback_result = await self._try_fallback(request, execution_time)
                if fallback_result:
                    return fallback_result
            
            return ToolResponse(
                request_id=request.request_id,
                tool_id=request.tool_id,
                success=False,
                result={},
                execution_time=execution_time,
                cost=0.0,
                error=str(e)
            )
    
    async def _execute_tool_instance(self, request: ToolRequest, 
                                    tool_def: ToolDefinition) -> ToolResponse:
        """Execute the actual tool instance."""
        try:
            # Get tool instance
            tool_instance = self.tool_instances.get(request.tool_id)
            if not tool_instance:
                # Create tool instance if needed
                tool_instance = await self._create_tool_instance(tool_def)
                self.tool_instances[request.tool_id] = tool_instance
            
            # Execute tool
            if hasattr(tool_instance, 'execute'):
                result = await tool_instance.execute(request.parameters)
            elif callable(tool_instance):
                result = await tool_instance(request.parameters)
            else:
                raise ValueError(f"Tool {request.tool_id} is not callable")
            
            # Estimate cost
            estimated_cost = tool_def.cost_per_request
            
            return ToolResponse(
                request_id=request.request_id,
                tool_id=request.tool_id,
                success=True,
                result=result,
                execution_time=0.0,  # Will be set by caller
                cost=estimated_cost,
                metadata={
                    "tool_version": tool_def.version,
                    "tool_category": tool_def.category.value,
                    "tenant_id": request.tenant_context.tenant_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error executing tool {request.tool_id}: {e}")
            raise
    
    async def _create_tool_instance(self, tool_def: ToolDefinition) -> Any:
        """Create a tool instance based on the tool definition."""
        # Import and instantiate real tools from the manufacturing domain
        try:
            if tool_def.category == ToolCategory.SOLVER:
                from domains.manufacturing.tools.solver.DcisionAI_Solver_Tool import DcisionAI_Solver_Tool
                return DcisionAI_Solver_Tool()
            elif tool_def.category == ToolCategory.DATA:
                from domains.manufacturing.tools.data.DcisionAI_Data_Tool import DcisionAI_Data_Tool
                return DcisionAI_Data_Tool()
            elif tool_def.category == ToolCategory.MODEL:
                from domains.manufacturing.tools.model.DcisionAI_Model_Builder import DcisionAI_Model_Builder
                return DcisionAI_Model_Builder()
            elif tool_def.category == ToolCategory.INTENT:
                from domains.manufacturing.tools.intent.DcisionAI_Intent_Tool import DcisionAI_Intent_Tool
                return DcisionAI_Intent_Tool()
            else:
                raise ValueError(f"Unsupported tool category: {tool_def.category}")
                
        except ImportError as e:
            logger.error(f"Failed to import tool {tool_def.tool_id}: {e}")
            raise ValueError(f"Tool {tool_def.tool_id} not available")
    
    async def _try_fallback(self, request: ToolRequest, 
                           original_execution_time: float) -> Optional[ToolResponse]:
        """Try to execute a fallback tool."""
        try:
            fallback_tools = self.fallback_strategies.get(request.tool_id, [])
            
            for fallback_tool_id in fallback_tools:
                fallback_tool_def = self.tool_registry.get(fallback_tool_id)
                if not fallback_tool_def:
                    continue
                
                if not fallback_tool_def.is_available_for_tenant(request.tenant_context):
                    continue
                
                # Create fallback request
                fallback_request = ToolRequest(
                    request_id=str(uuid.uuid4()),
                    tool_id=fallback_tool_id,
                    tenant_context=request.tenant_context,
                    parameters=request.parameters,
                    priority=request.priority,
                    timeout=request.timeout,
                    fallback_strategy="none"  # Prevent infinite fallback loops
                )
                
                # Execute fallback tool
                fallback_result = await self._execute_tool_instance(fallback_request, fallback_tool_def)
                
                # Update fallback metadata
                fallback_result.fallback_used = request.tool_id
                fallback_result.execution_time = original_execution_time
                
                logger.info(f"🔄 Fallback to {fallback_tool_id} successful")
                return fallback_result
            
            return None
            
        except Exception as e:
            logger.error(f"Error during fallback execution: {e}")
            return None
    
    async def discover_tools(self, tenant_context: Optional[TenantContext] = None) -> List[ToolDefinition]:
        """
        Discover available tools for a tenant.
        
        Args:
            tenant_context: Tenant context for filtering
            
        Returns:
            List of available tools
        """
        try:
            if self.registry_url:
                # External registry discovery
                await self._discover_external_tools()
            
            # Filter tools based on tenant context
            if tenant_context:
                available_tools = [
                    tool for tool in self.tool_registry.values()
                    if tool.is_available_for_tenant(tenant_context)
                ]
            else:
                available_tools = list(self.tool_registry.values())
            
            logger.info(f"✅ Discovered {len(available_tools)} tools")
            return available_tools
            
        except Exception as e:
            logger.error(f"Error discovering tools: {e}")
            return []
    
    async def _discover_external_tools(self):
        """Discover tools from external registry."""
        # TODO: Implement external tool discovery
        # This would typically involve API calls to external registries
        pass
    
    async def _discover_tools(self):
        """Internal tool discovery."""
        # This is called during startup
        await self.discover_tools()
    
    async def _health_monitor_loop(self):
        """Continuous health monitoring loop."""
        while True:
            try:
                await self._check_all_tools_health()
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor loop: {e}")
                await asyncio.sleep(5)
    
    async def _check_all_tools_health(self):
        """Check health of all tools."""
        for tool_id, tool_def in self.tool_registry.items():
            try:
                await self._check_tool_health(tool_id, tool_def)
            except Exception as e:
                logger.error(f"Error checking health for tool {tool_id}: {e}")
    
    async def _check_tool_health(self, tool_id: str, tool_def: ToolDefinition):
        """Check health of a specific tool."""
        try:
            # This would typically involve actual health checks
            # For now, we'll simulate health checks
            
            # Simulate health check
            import random
            
            # Randomly vary health metrics
            error_rate_variation = random.uniform(-0.01, 0.01)
            new_error_rate = max(0, min(1, tool_def.error_rate + error_rate_variation))
            
            # Update tool status based on error rate
            if new_error_rate > 0.1:
                tool_def.status = ToolStatus.UNAVAILABLE
            elif new_error_rate > 0.05:
                tool_def.status = ToolStatus.DEGRADED
            else:
                tool_def.status = ToolStatus.AVAILABLE
            
            # Update health metrics
            tool_def.error_rate = new_error_rate
            tool_def.last_health_check = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error checking health for tool {tool_id}: {e}")
    
    def get_tool_catalog(self, tenant_context: Optional[TenantContext] = None) -> Dict[str, Any]:
        """Get tool catalog with tenant filtering."""
        if tenant_context:
            available_tools = [
                tool for tool in self.tool_registry.values()
                if tool.is_available_for_tenant(tenant_context)
            ]
        else:
            available_tools = list(self.tool_registry.values())
        
        # Group by category
        catalog = {}
        for tool in available_tools:
            category = tool.category.value
            if category not in catalog:
                catalog[category] = []
            catalog[category].append(tool.to_dict())
        
        return {
            "total_tools": len(available_tools),
            "categories": catalog,
            "tenant_id": tenant_context.tenant_id if tenant_context else None
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        total_requests = len(self.response_history)
        successful_requests = len([r for r in self.response_history if r.success])
        
        if total_requests == 0:
            return {"error": "No requests processed yet"}
        
        avg_execution_time = sum(r.execution_time for r in self.response_history) / total_requests
        avg_cost = sum(r.cost for r in self.response_history) / total_requests
        success_rate = successful_requests / total_requests
        
        # Tool usage statistics
        tool_stats = {}
        for tool_id in set(r.tool_id for r in self.response_history):
            tool_results = [r for r in self.response_history if r.tool_id == tool_id]
            if tool_results:
                tool_stats[tool_id] = {
                    "requests": len(tool_results),
                    "avg_execution_time": sum(r.execution_time for r in tool_results) / len(tool_results),
                    "avg_cost": sum(r.cost for r in tool_results) / len(tool_results),
                    "success_rate": len([r for r in tool_results if r.success]) / len(tool_results)
                }
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": success_rate,
            "avg_execution_time": avg_execution_time,
            "avg_cost": avg_cost,
            "tool_stats": tool_stats,
            "available_tools": len(self.tool_registry),
            "fallback_usage": len([r for r in self.response_history if r.fallback_used])
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform system health check."""
        available_tools = sum(1 for t in self.tool_registry.values() if t.status == ToolStatus.AVAILABLE)
        total_tools = len(self.tool_registry)
        
        return {
            "status": "healthy" if available_tools > 0 else "unhealthy",
            "available_tools": available_tools,
            "total_tools": total_tools,
            "tool_health": {t.tool_id: t.status.value for t in self.tool_registry.values()},
            "registry_url": self.registry_url,
            "auto_discovery": self.enable_auto_discovery
        }
    
    async def cleanup(self):
        """Cleanup gateway client resources."""
        try:
            await self.stop()
            logger.info("✅ Gateway Client cleanup completed")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")

# Real tool implementations will be imported from actual tool modules
# No mock implementations allowed - production code only
