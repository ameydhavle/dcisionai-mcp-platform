#!/usr/bin/env python3
"""
DcisionAI Platform - Central Platform Manager
=============================================

Enterprise-grade platform management with:
- Multi-tenant orchestration and lifecycle management
- Platform-wide monitoring and observability
- Resource management and scaling
- Policy enforcement and compliance
- Business intelligence and analytics

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
from typing import Dict, Any, List, Optional, Union
from contextvars import ContextVar

from shared.core.base_agent import TenantContext, get_current_tenant
from shared.core.inference_manager import BedrockInferenceManager
from shared.core.gateway_client import GatewayClient

logger = logging.getLogger(__name__)

class PlatformStatus(Enum):
    """Platform operational status."""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"

class TenantTier(Enum):
    """Tenant service tiers."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    GOLD = "gold"

@dataclass
class PlatformMetrics:
    """Platform-wide performance metrics."""
    total_tenants: int
    active_tenants: int
    total_requests: int
    successful_requests: int
    avg_response_time: float
    total_cost: float
    uptime_percentage: float
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_tenants": self.total_tenants,
            "active_tenants": self.active_tenants,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "avg_response_time": self.avg_response_time,
            "total_cost": self.total_cost,
            "uptime_percentage": self.uptime_percentage,
            "last_updated": self.last_updated.isoformat()
        }

@dataclass
class TenantMetrics:
    """Per-tenant performance metrics."""
    tenant_id: str
    request_count: int
    success_rate: float
    avg_response_time: float
    total_cost: float
    last_activity: datetime
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "request_count": self.request_count,
            "success_rate": self.success_rate,
            "avg_response_time": self.avg_response_time,
            "total_cost": self.total_cost,
            "last_activity": self.last_activity.isoformat(),
            "resource_usage": self.resource_usage
        }

class PlatformManager:
    """
    Central platform manager for DcisionAI.
    
    Features:
    - Multi-tenant orchestration and lifecycle management
    - Platform-wide monitoring and observability
    - Resource management and scaling
    - Policy enforcement and compliance
    - Business intelligence and analytics
    """
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 enable_monitoring: bool = True,
                 enable_auto_scaling: bool = True):
        """
        Initialize the platform manager.
        
        Args:
            config_path: Path to platform configuration
            enable_monitoring: Enable platform monitoring
            enable_auto_scaling: Enable automatic scaling
        """
        self.config_path = config_path
        self.enable_monitoring = enable_monitoring
        self.enable_auto_scaling = enable_auto_scaling
        
        # Platform status
        self.status = PlatformStatus.OPERATIONAL
        self.status_message = "Platform operating normally"
        self.last_status_update = datetime.utcnow()
        
        # Core components
        self.inference_manager: Optional[BedrockInferenceManager] = None
        self.gateway_client: Optional[GatewayClient] = None
        
        # Tenant management
        self.tenants: Dict[str, TenantContext] = {}
        self.tenant_metrics: Dict[str, TenantMetrics] = {}
        self.tenant_policies: Dict[str, Dict[str, Any]] = {}
        
        # Platform metrics
        self.platform_metrics = PlatformMetrics(
            total_tenants=0,
            active_tenants=0,
            total_requests=0,
            successful_requests=0,
            avg_response_time=0.0,
            total_cost=0.0,
            uptime_percentage=99.9,
            last_updated=datetime.utcnow()
        )
        
        # Monitoring and scaling
        self.monitoring_task: Optional[asyncio.Task] = None
        self.scaling_task: Optional[asyncio.Task] = None
        self.monitoring_interval = 60  # seconds
        self.scaling_interval = 300  # seconds
        
        # Configuration
        self.config = self._load_config()
        
        logger.info("✅ Platform Manager initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load platform configuration."""
        # Default configuration
        default_config = {
            "platform": {
                "name": "DcisionAI Platform",
                "version": "2.0.0",
                "environment": "production"
            },
            "tenancy": {
                "max_tenants": 1000,
                "default_tier": "pro",
                "auto_provisioning": True
            },
            "monitoring": {
                "metrics_retention_days": 90,
                "alert_thresholds": {
                    "error_rate": 0.05,
                    "response_time_p95": 2.0,
                    "cost_per_request": 0.01
                }
            },
            "scaling": {
                "auto_scaling": True,
                "min_instances": 2,
                "max_instances": 20,
                "scale_up_threshold": 0.8,
                "scale_down_threshold": 0.3
            }
        }
        
        # TODO: Load from config file if provided
        return default_config
    
    async def start(self):
        """Start the platform manager."""
        try:
            # Initialize core components
            await self._initialize_core_components()
            
            # Start monitoring and scaling tasks
            if self.enable_monitoring:
                self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            if self.enable_auto_scaling:
                self.scaling_task = asyncio.create_task(self._scaling_loop())
            
            # Update platform status
            self.status = PlatformStatus.OPERATIONAL
            self.status_message = "Platform started successfully"
            self.last_status_update = datetime.utcnow()
            
            logger.info("✅ Platform Manager started successfully")
            
        except Exception as e:
            self.status = PlatformStatus.EMERGENCY
            self.status_message = f"Failed to start platform: {e}"
            logger.error(f"❌ Failed to start Platform Manager: {e}")
            raise
    
    async def stop(self):
        """Stop the platform manager."""
        try:
            # Stop monitoring and scaling tasks
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            if self.scaling_task:
                self.scaling_task.cancel()
                try:
                    await self.scaling_task
                except asyncio.CancelledError:
                    pass
            
            # Stop core components
            if self.inference_manager:
                await self.inference_manager.cleanup()
            
            if self.gateway_client:
                await self.gateway_client.cleanup()
            
            # Update platform status
            self.status = PlatformStatus.MAINTENANCE
            self.status_message = "Platform stopped"
            self.last_status_update = datetime.utcnow()
            
            logger.info("✅ Platform Manager stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping Platform Manager: {e}")
    
    async def _initialize_core_components(self):
        """Initialize core platform components."""
        try:
            # Initialize inference manager
            self.inference_manager = BedrockInferenceManager()
            await self.inference_manager.start()
            logger.info("✅ Inference Manager initialized")
            
            # Initialize gateway client
            self.gateway_client = GatewayClient()
            await self.gateway_client.start()
            logger.info("✅ Gateway Client initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize core components: {e}")
            raise
    
    async def register_tenant(self, tenant_context: TenantContext) -> bool:
        """
        Register a new tenant with the platform.
        
        Args:
            tenant_context: Tenant context to register
            
        Returns:
            True if registration successful
        """
        try:
            tenant_id = tenant_context.tenant_id
            
            # Check if tenant already exists
            if tenant_id in self.tenants:
                logger.warning(f"⚠️ Tenant {tenant_id} already registered")
                return False
            
            # Validate tenant context
            if not self._validate_tenant_context(tenant_context):
                logger.error(f"❌ Invalid tenant context for {tenant_id}")
                return False
            
            # Register tenant
            self.tenants[tenant_id] = tenant_context
            
            # Initialize tenant metrics
            self.tenant_metrics[tenant_id] = TenantMetrics(
                tenant_id=tenant_id,
                request_count=0,
                success_rate=100.0,
                avg_response_time=0.0,
                total_cost=0.0,
                last_activity=datetime.utcnow(),
                resource_usage={}
            )
            
            # Update platform metrics
            self.platform_metrics.total_tenants += 1
            self.platform_metrics.active_tenants += 1
            self.platform_metrics.last_updated = datetime.utcnow()
            
            logger.info(f"✅ Tenant {tenant_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register tenant {tenant_context.tenant_id}: {e}")
            return False
    
    async def unregister_tenant(self, tenant_id: str) -> bool:
        """
        Unregister a tenant from the platform.
        
        Args:
            tenant_id: ID of tenant to unregister
            
        Returns:
            True if unregistration successful
        """
        try:
            if tenant_id not in self.tenants:
                logger.warning(f"⚠️ Tenant {tenant_id} not found")
                return False
            
            # Remove tenant
            del self.tenants[tenant_id]
            
            # Remove tenant metrics
            if tenant_id in self.tenant_metrics:
                del self.tenant_metrics[tenant_id]
            
            # Update platform metrics
            self.platform_metrics.active_tenants = max(0, self.platform_metrics.active_tenants - 1)
            self.platform_metrics.last_updated = datetime.utcnow()
            
            logger.info(f"✅ Tenant {tenant_id} unregistered successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to unregister tenant {tenant_id}: {e}")
            return False
    
    def _validate_tenant_context(self, tenant_context: TenantContext) -> bool:
        """Validate tenant context for registration."""
        try:
            # Check required fields
            if not tenant_context.tenant_id or not tenant_context.org_id:
                return False
            
            # Check tenant ID format
            if not tenant_context.tenant_id.startswith("t_"):
                return False
            
            # Check entitlements
            if not tenant_context.entitlements:
                return False
            
            return True
            
        except Exception:
            return False
    
    async def process_tenant_request(self, tenant_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request for a specific tenant.
        
        Args:
            tenant_id: ID of the tenant
            request: Request payload
            
        Returns:
            Response with tenant-scoped results
        """
        try:
            # Validate tenant
            if tenant_id not in self.tenants:
                return {
                    "success": False,
                    "error": f"Tenant {tenant_id} not found",
                    "status_code": 404
                }
            
            tenant_context = self.tenants[tenant_id]
            
            # Check tenant status and quotas
            if not await self._check_tenant_status(tenant_id):
                return {
                    "success": False,
                    "error": f"Tenant {tenant_id} is not active",
                    "status_code": 403
                }
            
            # Route request through appropriate component
            if "inference" in request.get("type", ""):
                # Route to inference manager
                result = await self._route_inference_request(tenant_context, request)
            elif "tool" in request.get("type", ""):
                # Route to gateway client
                result = await self._route_tool_request(tenant_context, request)
            else:
                # Generic platform request
                result = await self._process_platform_request(tenant_context, request)
            
            # Update tenant metrics
            await self._update_tenant_metrics(tenant_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing request for tenant {tenant_id}: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "status_code": 500
            }
    
    async def _check_tenant_status(self, tenant_id: str) -> bool:
        """Check if tenant is active and within quotas."""
        try:
            tenant = self.tenants.get(tenant_id)
            if not tenant:
                return False
            
            # Check tenant metrics
            metrics = self.tenant_metrics.get(tenant_id)
            if not metrics:
                return True  # New tenant, no metrics yet
            
            # Check request limits (simplified)
            if metrics.request_count > 10000:  # Example limit
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking tenant status: {e}")
            return False
    
    async def _route_inference_request(self, tenant_context: TenantContext, 
                                     request: Dict[str, Any]) -> Dict[str, Any]:
        """Route inference request to inference manager."""
        if not self.inference_manager:
            return {
                "success": False,
                "error": "Inference manager not available",
                "status_code": 503
            }
        
        # Create inference request
        from shared.core.inference_manager import InferenceRequest
        inference_request = InferenceRequest(
            request_id=str(uuid.uuid4()),
            tenant_context=tenant_context,
            domain=request.get("domain", "unknown"),
            request_type=request.get("request_type", "inference"),
            payload=request.get("payload", {}),
            inference_profile=request.get("inference_profile")
        )
        
        # Execute inference
        result = await self.inference_manager.execute_inference(inference_request)
        
        return {
            "success": result.success,
            "result": result.result,
            "metadata": {
                "profile_used": result.profile_used,
                "region_used": result.region_used,
                "execution_time": result.execution_time,
                "cost": result.cost
            }
        }
    
    async def _route_tool_request(self, tenant_context: TenantContext, 
                                 request: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool request to gateway client."""
        if not self.gateway_client:
            return {
                "success": False,
                "error": "Gateway client not available",
                "status_code": 503
            }
        
        # Create tool request
        from shared.core.gateway_client import ToolRequest
        tool_request = ToolRequest(
            request_id=str(uuid.uuid4()),
            tool_id=request.get("tool_id"),
            tenant_context=tenant_context,
            parameters=request.get("parameters", {}),
            priority=request.get("priority", "normal"),
            timeout=request.get("timeout", 60),
            fallback_strategy=request.get("fallback_strategy", "auto")
        )
        
        # Execute tool
        result = await self.gateway_client.execute_tool(tool_request)
        
        return {
            "success": result.success,
            "result": result.result,
            "metadata": {
                "tool_id": result.tool_id,
                "execution_time": result.execution_time,
                "cost": result.cost,
                "fallback_used": result.fallback_used
            }
        }
    
    async def _process_platform_request(self, tenant_context: TenantContext, 
                                      request: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic platform request."""
        request_type = request.get("type", "unknown")
        
        if request_type == "status":
            return await self.get_tenant_status(tenant_context.tenant_id)
        elif request_type == "metrics":
            return await self.get_tenant_metrics(tenant_context.tenant_id)
        elif request_type == "catalog":
            return await self.get_tenant_catalog(tenant_context.tenant_id)
        else:
            return {
                "success": False,
                "error": f"Unknown request type: {request_type}",
                "status_code": 400
            }
    
    async def _update_tenant_metrics(self, tenant_id: str, result: Dict[str, Any]):
        """Update tenant metrics after request processing."""
        try:
            if tenant_id not in self.tenant_metrics:
                return
            
            metrics = self.tenant_metrics[tenant_id]
            
            # Update request count
            metrics.request_count += 1
            
            # Update success rate
            if result.get("success", False):
                # Calculate new success rate
                total_requests = metrics.request_count
                successful_requests = metrics.success_count if hasattr(metrics, 'success_count') else 0
                successful_requests += 1
                metrics.success_rate = (successful_requests / total_requests) * 100
                
                # Update platform metrics
                self.platform_metrics.successful_requests += 1
            
            # Update last activity
            metrics.last_activity = datetime.utcnow()
            
            # Update platform metrics
            self.platform_metrics.total_requests += 1
            self.platform_metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error updating tenant metrics: {e}")
    
    async def get_tenant_status(self, tenant_id: str) -> Dict[str, Any]:
        """Get status for a specific tenant."""
        try:
            if tenant_id not in self.tenants:
                return {
                    "success": False,
                    "error": f"Tenant {tenant_id} not found",
                    "status_code": 404
                }
            
            tenant = self.tenants[tenant_id]
            metrics = self.tenant_metrics.get(tenant_id)
            
            return {
                "success": True,
                "tenant_id": tenant_id,
                "status": "active",
                "tier": tenant.sla_tier.value,
                "entitlements": tenant.entitlements,
                "metrics": metrics.to_dict() if metrics else None
            }
            
        except Exception as e:
            logger.error(f"Error getting tenant status: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": 500
            }
    
    async def get_tenant_metrics(self, tenant_id: str) -> Dict[str, Any]:
        """Get metrics for a specific tenant."""
        try:
            if tenant_id not in self.tenant_metrics:
                return {
                    "success": False,
                    "error": f"Tenant {tenant_id} not found",
                    "status_code": 404
                }
            
            metrics = self.tenant_metrics[tenant_id]
            
            return {
                "success": True,
                "tenant_id": tenant_id,
                "metrics": metrics.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting tenant metrics: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": 500
            }
    
    async def get_tenant_catalog(self, tenant_id: str) -> Dict[str, Any]:
        """Get available tools catalog for a tenant."""
        try:
            if tenant_id not in self.tenants:
                return {
                    "success": False,
                    "error": f"Tenant {tenant_id} not found",
                    "status_code": 404
                }
            
            tenant = self.tenants[tenant_id]
            
            if not self.gateway_client:
                return {
                    "success": False,
                    "error": "Gateway client not available",
                    "status_code": 503
                }
            
            # Get tool catalog for tenant
            catalog = self.gateway_client.get_tool_catalog(tenant)
            
            return {
                "success": True,
                "tenant_id": tenant_id,
                "catalog": catalog
            }
            
        except Exception as e:
            logger.error(f"Error getting tenant catalog: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": 500
            }
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop."""
        while True:
            try:
                await self._update_platform_metrics()
                await self._check_platform_health()
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _scaling_loop(self):
        """Continuous scaling loop."""
        while True:
            try:
                await self._check_scaling_needs()
                await asyncio.sleep(self.scaling_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scaling loop: {e}")
                await asyncio.sleep(5)
    
    async def _update_platform_metrics(self):
        """Update platform-wide metrics."""
        try:
            # Aggregate metrics from components
            if self.inference_manager:
                inference_metrics = self.inference_manager.get_performance_summary()
                # Update platform metrics with inference data
                pass
            
            if self.gateway_client:
                gateway_metrics = self.gateway_client.get_performance_summary()
                # Update platform metrics with gateway data
                pass
            
            # Update uptime
            uptime_start = datetime.utcnow() - timedelta(days=30)  # Example
            total_uptime = (datetime.utcnow() - uptime_start).total_seconds()
            self.platform_metrics.uptime_percentage = 99.9  # Simplified
            
            self.platform_metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error updating platform metrics: {e}")
    
    async def _check_platform_health(self):
        """Check overall platform health."""
        try:
            # Check component health
            component_health = {}
            
            if self.inference_manager:
                component_health["inference_manager"] = self.inference_manager.health_check()
            
            if self.gateway_client:
                component_health["gateway_client"] = self.gateway_client.health_check()
            
            # Determine overall platform status
            all_healthy = all(
                health.get("status") == "healthy" 
                for health in component_health.values()
            )
            
            if all_healthy:
                self.status = PlatformStatus.OPERATIONAL
                self.status_message = "All components healthy"
            else:
                self.status = PlatformStatus.DEGRADED
                self.status_message = "Some components degraded"
            
            self.last_status_update = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error checking platform health: {e}")
            self.status = PlatformStatus.DEGRADED
            self.status_message = f"Health check error: {e}"
    
    async def _check_scaling_needs(self):
        """Check if scaling is needed."""
        try:
            # This would implement actual scaling logic
            # For now, just log that scaling check was performed
            logger.debug("Scaling check performed")
            
        except Exception as e:
            logger.error(f"Error checking scaling needs: {e}")
    
    def get_platform_status(self) -> Dict[str, Any]:
        """Get current platform status."""
        return {
            "status": self.status.value,
            "status_message": self.status_message,
            "last_update": self.last_status_update.isoformat(),
            "uptime_percentage": self.platform_metrics.uptime_percentage,
            "total_tenants": self.platform_metrics.total_tenants,
            "active_tenants": self.platform_metrics.active_tenants
        }
    
    def get_platform_metrics(self) -> Dict[str, Any]:
        """Get comprehensive platform metrics."""
        return {
            "platform": self.platform_metrics.to_dict(),
            "tenants": {
                tenant_id: metrics.to_dict() 
                for tenant_id, metrics in self.tenant_metrics.items()
            },
            "components": {
                "inference_manager": self.inference_manager.health_check() if self.inference_manager else None,
                "gateway_client": self.gateway_client.health_check() if self.gateway_client else None
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive platform health check."""
        try:
            return {
                "status": "healthy" if self.status == PlatformStatus.OPERATIONAL else "degraded",
                "platform_status": self.get_platform_status(),
                "component_health": {
                    "inference_manager": self.inference_manager.health_check() if self.inference_manager else "not_initialized",
                    "gateway_client": self.gateway_client.health_check() if self.gateway_client else "not_initialized"
                },
                "tenant_summary": {
                    "total": self.platform_metrics.total_tenants,
                    "active": self.platform_metrics.active_tenants
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def cleanup(self):
        """Cleanup platform manager resources."""
        try:
            await self.stop()
            logger.info("✅ Platform Manager cleanup completed")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
