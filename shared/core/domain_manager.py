#!/usr/bin/env python3
"""
DcisionAI Platform - Domain Manager
==================================

Central manager for all domains in the DcisionAI platform.
Handles domain registration, discovery, and orchestration.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class DomainInfo:
    """Information about a registered domain."""
    name: str
    description: str
    version: str
    status: str  # 'active', 'inactive', 'error'
    agent_count: int
    tool_count: int
    created_at: datetime
    last_updated: datetime
    metadata: Dict[str, Any]

class DomainManager:
    """
    Central manager for all domains in the DcisionAI platform.
    
    Provides domain registration, discovery, and management capabilities.
    """
    
    def __init__(self):
        """Initialize the domain manager."""
        self.logger = logging.getLogger("domain_manager")
        self.logger.setLevel(logging.INFO)
        
        # Domain registry
        self.domains: Dict[str, DomainInfo] = {}
        
        # Agent registry per domain
        self.domain_agents: Dict[str, Dict[str, Any]] = {}
        
        # Tool registry per domain
        self.domain_tools: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("✅ Domain Manager initialized successfully")
    
    def register_domain(self, name: str, description: str, version: str = "1.0.0", 
                       metadata: Dict[str, Any] = None) -> bool:
        """Register a new domain with the platform."""
        try:
            if name in self.domains:
                self.logger.warning(f"Domain '{name}' already registered, updating...")
                return self.update_domain(name, description, version, metadata)
            
            domain_info = DomainInfo(
                name=name,
                description=description,
                version=version,
                status="active",
                agent_count=0,
                tool_count=0,
                created_at=datetime.now(),
                last_updated=datetime.now(),
                metadata=metadata or {}
            )
            
            self.domains[name] = domain_info
            self.domain_agents[name] = {}
            self.domain_tools[name] = {}
            
            self.logger.info(f"✅ Domain '{name}' registered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register domain '{name}': {e}")
            return False
    
    def update_domain(self, name: str, description: str = None, version: str = None,
                     metadata: Dict[str, Any] = None) -> bool:
        """Update an existing domain."""
        try:
            if name not in self.domains:
                self.logger.error(f"Domain '{name}' not found")
                return False
            
            domain_info = self.domains[name]
            
            if description:
                domain_info.description = description
            if version:
                domain_info.version = version
            if metadata:
                domain_info.metadata.update(metadata)
            
            domain_info.last_updated = datetime.now()
            
            self.logger.info(f"✅ Domain '{name}' updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update domain '{name}': {e}")
            return False
    
    def unregister_domain(self, name: str) -> bool:
        """Unregister a domain from the platform."""
        try:
            if name not in self.domains:
                self.logger.warning(f"Domain '{name}' not found")
                return False
            
            # Remove domain and all associated data
            del self.domains[name]
            del self.domain_agents[name]
            del self.domain_tools[name]
            
            self.logger.info(f"✅ Domain '{name}' unregistered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister domain '{name}': {e}")
            return False
    
    def register_agent(self, domain: str, agent_name: str, agent: Any) -> bool:
        """Register an agent with a specific domain."""
        try:
            if domain not in self.domains:
                self.logger.error(f"Domain '{domain}' not found")
                return False
            
            self.domain_agents[domain][agent_name] = agent
            self.domains[domain].agent_count = len(self.domain_agents[domain])
            self.domains[domain].last_updated = datetime.now()
            
            self.logger.info(f"✅ Agent '{agent_name}' registered with domain '{domain}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent '{agent_name}' with domain '{domain}': {e}")
            return False
    
    def register_tool(self, domain: str, tool_name: str, tool: Any) -> bool:
        """Register a tool with a specific domain."""
        try:
            if domain not in self.domains:
                self.logger.error(f"Domain '{domain}' not found")
                return False
            
            self.domain_tools[domain][tool_name] = tool
            self.domains[domain].tool_count = len(self.domain_tools[domain])
            self.domains[domain].last_updated = datetime.now()
            
            self.logger.info(f"✅ Tool '{tool_name}' registered with domain '{domain}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register tool '{tool_name}' with domain '{domain}': {e}")
            return False
    
    def get_domain(self, name: str) -> Optional[DomainInfo]:
        """Get information about a specific domain."""
        return self.domains.get(name)
    
    def list_domains(self) -> List[DomainInfo]:
        """List all registered domains."""
        return list(self.domains.values())
    
    def get_domain_agents(self, domain: str) -> Dict[str, Any]:
        """Get all agents for a specific domain."""
        return self.domain_agents.get(domain, {})
    
    def get_domain_tools(self, domain: str) -> Dict[str, Any]:
        """Get all tools for a specific domain."""
        return self.domain_tools.get(domain, {})
    
    def get_agent(self, domain: str, agent_name: str) -> Optional[Any]:
        """Get a specific agent from a domain."""
        return self.domain_agents.get(domain, {}).get(agent_name)
    
    def get_tool(self, domain: str, tool_name: str) -> Optional[Any]:
        """Get a specific tool from a domain."""
        return self.domain_tools.get(domain, {}).get(tool_name)
    
    def get_platform_summary(self) -> Dict[str, Any]:
        """Get a summary of the entire platform."""
        total_agents = sum(len(agents) for agents in self.domain_agents.values())
        total_tools = sum(len(tools) for tools in self.domain_tools.values())
        
        return {
            "total_domains": len(self.domains),
            "total_agents": total_agents,
            "total_tools": total_tools,
            "domains": [
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
                for domain in self.domains.values()
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    def set_domain_status(self, name: str, status: str) -> bool:
        """Set the status of a domain."""
        try:
            if name not in self.domains:
                self.logger.error(f"Domain '{name}' not found")
                return False
            
            valid_statuses = ["active", "inactive", "error"]
            if status not in valid_statuses:
                self.logger.error(f"Invalid status '{status}'. Must be one of: {valid_statuses}")
                return False
            
            self.domains[name].status = status
            self.domains[name].last_updated = datetime.now()
            
            self.logger.info(f"✅ Domain '{name}' status set to '{status}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set domain '{name}' status: {e}")
            return False
    
    def get_domain_health(self, name: str) -> Dict[str, Any]:
        """Get health status of a specific domain."""
        try:
            if name not in self.domains:
                return {"error": f"Domain '{name}' not found"}
            
            domain = self.domains[name]
            agents = self.domain_agents.get(name, {})
            tools = self.domain_tools.get(name, {})
            
            # Check agent health
            agent_health = {}
            for agent_name, agent in agents.items():
                if hasattr(agent, 'get_health_status'):
                    agent_health[agent_name] = agent.get_health_status()
                else:
                    agent_health[agent_name] = {"status": "unknown"}
            
            # Check tool health
            tool_health = {}
            for tool_name, tool in tools.items():
                if hasattr(tool, 'get_health_status'):
                    tool_health[tool_name] = tool.get_health_status()
                else:
                    tool_health[tool_name] = {"status": "unknown"}
            
            return {
                "domain": name,
                "status": domain.status,
                "version": domain.version,
                "agent_count": domain.agent_count,
                "tool_count": domain.tool_count,
                "agent_health": agent_health,
                "tool_health": tool_health,
                "last_updated": domain.last_updated.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to get domain health: {e}"}
