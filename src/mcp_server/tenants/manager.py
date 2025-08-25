"""
MCP Server Tenant Management
===========================

Multi-tenancy system for the DcisionAI MCP server.
"""

import uuid
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from ..config.settings import settings
from ..utils.logging import MCPLogger
from ..utils.metrics import metrics_collector


class TenantStatus(Enum):
    """Tenant status enumeration."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


@dataclass
class Tenant:
    """Tenant data structure."""
    tenant_id: str
    name: str
    plan: str
    status: TenantStatus
    created_at: datetime
    last_active: datetime
    request_count: int = 0
    monthly_cost: float = 0.0
    concurrent_requests: int = 0
    max_concurrent_requests: int = 5
    request_limit: int = 1000
    allowed_tools: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """Session data structure."""
    session_id: str
    tenant_id: str
    created_at: datetime
    last_activity: datetime
    request_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class TenantManager:
    """Manages tenants and sessions for the MCP server."""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.sessions: Dict[str, Session] = {}
        self.logger = MCPLogger("dcisionai.mcp.tenants")
        self._lock = asyncio.Lock()
        
        # Initialize with default tenant for testing
        self._create_default_tenant()
    
    def _create_default_tenant(self) -> None:
        """Create a default tenant for testing."""
        default_tenant = Tenant(
            tenant_id="default",
            name="Default Tenant",
            plan="basic",
            status=TenantStatus.ACTIVE,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            max_concurrent_requests=settings.tenant_plans["basic"]["concurrent_limit"],
            request_limit=settings.tenant_plans["basic"]["request_limit"],
            allowed_tools=settings.tenant_plans["basic"]["tools"]
        )
        self.tenants["default"] = default_tenant
        self.logger.info("Created default tenant", tenant_id="default")
    
    async def create_tenant(self, name: str, plan: str = "basic", 
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new tenant."""
        async with self._lock:
            tenant_id = str(uuid.uuid4())
            plan_config = settings.get_tenant_plan(plan)
            
            tenant = Tenant(
                tenant_id=tenant_id,
                name=name,
                plan=plan,
                status=TenantStatus.ACTIVE,
                created_at=datetime.utcnow(),
                last_active=datetime.utcnow(),
                max_concurrent_requests=plan_config["concurrent_limit"],
                request_limit=plan_config["request_limit"],
                allowed_tools=plan_config["tools"],
                metadata=metadata or {}
            )
            
            self.tenants[tenant_id] = tenant
            self.logger.info("Created new tenant", tenant_id=tenant_id, name=name, plan=plan)
            return tenant_id
    
    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self.tenants.get(tenant_id)
    
    async def update_tenant(self, tenant_id: str, **updates) -> bool:
        """Update tenant information."""
        async with self._lock:
            tenant = self.tenants.get(tenant_id)
            if not tenant:
                return False
            
            for key, value in updates.items():
                if hasattr(tenant, key):
                    setattr(tenant, key, value)
            
            tenant.last_active = datetime.utcnow()
            self.logger.info("Updated tenant", tenant_id=tenant_id, updates=list(updates.keys()))
            return True
    
    async def create_session(self, tenant_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new session for a tenant."""
        async with self._lock:
            tenant = self.tenants.get(tenant_id)
            if not tenant or tenant.status != TenantStatus.ACTIVE:
                raise ValueError(f"Invalid or inactive tenant: {tenant_id}")
            
            session_id = str(uuid.uuid4())
            session = Session(
                session_id=session_id,
                tenant_id=tenant_id,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            self.sessions[session_id] = session
            self.logger.info("Created new session", session_id=session_id, tenant_id=tenant_id)
            return session_id
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        return self.sessions.get(session_id)
    
    async def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity."""
        async with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return False
            
            session.last_activity = datetime.utcnow()
            session.request_count += 1
            
            # Update tenant activity
            tenant = self.tenants.get(session.tenant_id)
            if tenant:
                tenant.last_active = datetime.utcnow()
                tenant.request_count += 1
            
            return True
    
    async def validate_request(self, tenant_id: str, tool_name: str) -> Dict[str, Any]:
        """Validate if a tenant can make a request for a specific tool."""
        async with self._lock:
            tenant = self.tenants.get(tenant_id)
            if not tenant:
                return {"valid": False, "error": "Tenant not found"}
            
            if tenant.status != TenantStatus.ACTIVE:
                return {"valid": False, "error": "Tenant is not active"}
            
            if tool_name not in tenant.allowed_tools:
                return {"valid": False, "error": f"Tool {tool_name} not allowed for tenant plan {tenant.plan}"}
            
            if tenant.request_count >= tenant.request_limit:
                return {"valid": False, "error": "Request limit exceeded"}
            
            if tenant.concurrent_requests >= tenant.max_concurrent_requests:
                return {"valid": False, "error": "Concurrent request limit exceeded"}
            
            # Increment concurrent requests
            tenant.concurrent_requests += 1
            
            return {
                "valid": True,
                "tenant": tenant,
                "cost": settings.get_tool_cost(tool_name)
            }
    
    async def complete_request(self, tenant_id: str, tool_name: str, cost: float) -> None:
        """Complete a request and update metrics."""
        async with self._lock:
            tenant = self.tenants.get(tenant_id)
            if tenant:
                tenant.concurrent_requests = max(0, tenant.concurrent_requests - 1)
                tenant.monthly_cost += cost
                
                # Record metrics
                metrics_collector.record_tool_cost(tenant_id, tool_name, cost)
                metrics_collector.record_concurrent_requests(tenant_id, tenant.concurrent_requests)
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        async with self._lock:
            now = datetime.utcnow()
            expired_sessions = []
            
            for session_id, session in self.sessions.items():
                if now - session.last_activity > timedelta(minutes=settings.session_timeout_minutes):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
            
            if expired_sessions:
                self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
            return len(expired_sessions)
    
    async def get_tenant_stats(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant statistics."""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None
        
        active_sessions = sum(1 for s in self.sessions.values() if s.tenant_id == tenant_id)
        
        return {
            "tenant_id": tenant_id,
            "name": tenant.name,
            "plan": tenant.plan,
            "status": tenant.status.value,
            "request_count": tenant.request_count,
            "monthly_cost": tenant.monthly_cost,
            "concurrent_requests": tenant.concurrent_requests,
            "max_concurrent_requests": tenant.max_concurrent_requests,
            "request_limit": tenant.request_limit,
            "active_sessions": active_sessions,
            "created_at": tenant.created_at.isoformat(),
            "last_active": tenant.last_active.isoformat()
        }


# Global tenant manager instance
tenant_manager = TenantManager()
