#!/usr/bin/env python3
"""
DcisionAI Platform - Platform Manager
=====================================

Central orchestrator for the multi-domain DcisionAI platform.
Manages domain registration, discovery, and cross-domain operations.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from shared.core.domain_manager import DomainManager
from shared.config.settings import settings

class PlatformManager:
    """
    Central platform manager for the DcisionAI multi-domain platform.
    
    Orchestrates all domains and provides unified platform operations.
    """
    
    def __init__(self):
        """Initialize the platform manager."""
        self.logger = logging.getLogger("platform_manager")
        self.logger.setLevel(logging.INFO)
        
        # Initialize domain manager
        self.domain_manager = DomainManager()
        
        # Platform metadata
        self.platform_info = {
            "name": settings.platform.platform_name,
            "version": settings.platform.platform_version,
            "environment": settings.platform.environment,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Register all configured domains
        self._register_configured_domains()
        
        self.logger.info("✅ Platform Manager initialized successfully")
    
    def _register_configured_domains(self):
        """Register all configured domains with the domain manager."""
        try:
            self.logger.info("🔧 Registering configured domains...")
            
            # Get all domain configurations
            all_domains = settings.get_all_domains()
            
            for domain_name in all_domains:
                domain_config = settings.get_domain_config(domain_name)
                if domain_config:
                    success = self.domain_manager.register_domain(
                        name=domain_name,
                        description=domain_config.get("description", f"{domain_name} domain"),
                        version=domain_config.get("version", "1.0.0"),
                        metadata=domain_config
                    )
                    
                    if success:
                        self.logger.info(f"✅ Domain '{domain_name}' registered successfully")
                    else:
                        self.logger.warning(f"⚠️ Failed to register domain '{domain_name}'")
            
            self.logger.info(f"✅ {len(all_domains)} domains configured")
            
        except Exception as e:
            self.logger.error(f"Failed to register configured domains: {e}")
    
    def get_platform_summary(self) -> Dict[str, Any]:
        """Get comprehensive platform summary."""
        try:
            domain_summary = self.domain_manager.get_platform_summary()
            
            return {
                "platform": self.platform_info,
                "domains": domain_summary,
                "configuration": settings.get_platform_summary(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get platform summary: {e}")
            return {"error": str(e)}
    
    def get_domain_info(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific domain."""
        try:
            domain_info = self.domain_manager.get_domain(domain_name)
            if domain_info:
                return {
                    "name": domain_info.name,
                    "description": domain_info.description,
                    "version": domain_info.version,
                    "status": domain_info.status,
                    "agent_count": domain_info.agent_count,
                    "tool_count": domain_info.tool_count,
                    "created_at": domain_info.created_at.isoformat(),
                    "last_updated": domain_info.last_updated.isoformat(),
                    "metadata": domain_info.metadata
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get domain info for '{domain_name}': {e}")
            return None
    
    def list_all_domains(self) -> List[Dict[str, Any]]:
        """List all registered domains with their information."""
        try:
            domains = self.domain_manager.list_domains()
            return [
                {
                    "name": domain.name,
                    "description": domain.description,
                    "version": domain.version,
                    "status": domain.status,
                    "agent_count": domain.agent_count,
                    "tool_count": domain.tool_count,
                    "created_at": domain.created_at.isoformat(),
                    "last_updated": domain.last_updated.isoformat()
                }
                for domain in domains
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to list domains: {e}")
            return []
    
    def get_domain_health(self, domain_name: str) -> Dict[str, Any]:
        """Get health status of a specific domain."""
        try:
            return self.domain_manager.get_domain_health(domain_name)
            
        except Exception as e:
            self.logger.error(f"Failed to get domain health for '{domain_name}': {e}")
            return {"error": str(e)}
    
    def get_all_domains_health(self) -> Dict[str, Any]:
        """Get health status of all domains."""
        try:
            all_domains = settings.get_all_domains()
            health_status = {}
            
            for domain_name in all_domains:
                health_status[domain_name] = self.get_domain_health(domain_name)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "domains": health_status
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get all domains health: {e}")
            return {"error": str(e)}
    
    def register_domain_agent(self, domain_name: str, agent_name: str, agent: Any) -> bool:
        """Register an agent with a specific domain."""
        try:
            return self.domain_manager.register_agent(domain_name, agent_name, agent)
            
        except Exception as e:
            self.logger.error(f"Failed to register agent '{agent_name}' with domain '{domain_name}': {e}")
            return False
    
    def register_domain_tool(self, domain_name: str, tool_name: str, tool: Any) -> bool:
        """Register a tool with a specific domain."""
        try:
            return self.domain_manager.register_tool(domain_name, tool_name, tool)
            
        except Exception as e:
            self.logger.error(f"Failed to register tool '{tool_name}' with domain '{domain_name}': {e}")
            return False
    
    def get_domain_agents(self, domain_name: str) -> Dict[str, Any]:
        """Get all agents for a specific domain."""
        try:
            return self.domain_manager.get_domain_agents(domain_name)
            
        except Exception as e:
            self.logger.error(f"Failed to get agents for domain '{domain_name}': {e}")
            return {}
    
    def get_domain_tools(self, domain_name: str) -> Dict[str, Any]:
        """Get all tools for a specific domain."""
        try:
            return self.domain_manager.get_domain_tools(domain_name)
            
        except Exception as e:
            self.logger.error(f"Failed to get tools for domain '{domain_name}': {e}")
            return {}
    
    def set_domain_status(self, domain_name: str, status: str) -> bool:
        """Set the status of a domain."""
        try:
            return self.domain_manager.set_domain_status(domain_name, status)
            
        except Exception as e:
            self.logger.error(f"Failed to set domain '{domain_name}' status: {e}")
            return False
    
    def get_cross_domain_capabilities(self) -> Dict[str, Any]:
        """Get capabilities that span across multiple domains."""
        try:
            all_domains = settings.get_all_domains()
            cross_domain_capabilities = {}
            
            for domain_name in all_domains:
                domain_config = settings.get_domain_config(domain_name)
                if domain_config and "tools" in domain_config:
                    cross_domain_capabilities[domain_name] = {
                        "tools": list(domain_config["tools"].keys()),
                        "workflow": domain_config.get("workflow", []),
                        "supported_industries": domain_config.get("supported_industries", [])
                    }
            
            return {
                "timestamp": datetime.now().isoformat(),
                "cross_domain_capabilities": cross_domain_capabilities
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cross-domain capabilities: {e}")
            return {"error": str(e)}
    
    def update_platform_info(self, **kwargs) -> bool:
        """Update platform information."""
        try:
            for key, value in kwargs.items():
                if key in self.platform_info:
                    self.platform_info[key] = value
            
            self.platform_info["last_updated"] = datetime.now().isoformat()
            self.logger.info(f"Platform info updated: {kwargs}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update platform info: {e}")
            return False
    
    def get_platform_statistics(self) -> Dict[str, Any]:
        """Get platform usage and performance statistics."""
        try:
            domain_summary = self.domain_manager.get_platform_summary()
            
            return {
                "total_domains": domain_summary["total_domains"],
                "total_agents": domain_summary["total_agents"],
                "total_tools": domain_summary["total_tools"],
                "platform_uptime": "N/A",  # Could be implemented with startup tracking
                "last_activity": datetime.now().isoformat(),
                "environment": settings.platform.environment,
                "version": settings.platform.platform_version
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get platform statistics: {e}")
            return {"error": str(e)}
    
    def export_platform_config(self) -> Dict[str, Any]:
        """Export complete platform configuration."""
        try:
            return {
                "platform_info": self.platform_info,
                "settings": settings.get_platform_summary(),
                "domains": self.domain_manager.get_platform_summary(),
                "export_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to export platform config: {e}")
            return {"error": str(e)}

# Global platform manager instance
platform_manager = PlatformManager()
