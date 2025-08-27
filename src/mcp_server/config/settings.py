"""
MCP Server Configuration Settings
================================

Configuration management for the DcisionAI MCP server.
"""

import os
from typing import Dict, Any, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPServerSettings(BaseSettings):
    """MCP Server configuration settings."""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Server Configuration
    server_host: str = Field(default="0.0.0.0", description="MCP server host")
    server_port: int = Field(default=8000, description="MCP server port")
    server_debug: bool = Field(default=False, description="Enable debug mode")
    
    # AWS Configuration
    aws_region: str = Field(default="us-east-1", description="AWS region")
    aws_profile: Optional[str] = Field(default=None, description="AWS profile")
    
    # Cost Tracking Configuration
    cost_tracking_enabled: bool = Field(default=False, description="Enable cost tracking")  # Disabled for testing
    cost_tracking_namespace: str = Field(default="DcisionAI/MCPRequests", description="CloudWatch namespace")
    cost_tracking_table: str = Field(default="dcisionai-tenant-costs", description="DynamoDB table for cost tracking")
    
    # Multi-tenancy Configuration
    multi_tenancy_enabled: bool = Field(default=True, description="Enable multi-tenancy")
    default_tenant_plan: str = Field(default="basic", description="Default tenant plan")
    session_timeout_minutes: int = Field(default=60, description="Session timeout in minutes")
    
    # Tool Configuration
    max_concurrent_requests: int = Field(default=10, description="Maximum concurrent requests per tenant")
    request_timeout_seconds: int = Field(default=300, description="Request timeout in seconds")
    
    # Logging Configuration
    log_level: str = Field(default="ERROR", description="Logging level")  # Set to ERROR for testing
    log_format: str = Field(default="json", description="Log format (json or text)")
    
    # Monitoring Configuration
    metrics_enabled: bool = Field(default=False, description="Enable metrics collection")  # Disabled for testing
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    
    # Tool Cost Rates (per request)
    tool_cost_rates: Dict[str, float] = Field(
        default={
            "manufacturing_intent_classification": 0.05,
            "data_requirements_analysis": 0.10,
            "optimization_model_building": 0.15,
            "optimization_solving": 0.20,
            "comprehensive_workflow": 0.50,
        },
        description="Cost rates for each tool"
    )
    
    # Tenant Plans
    tenant_plans: Dict[str, Dict[str, Any]] = Field(
        default={
            "basic": {
                "monthly_cost": 500,
                "request_limit": 1000,
                "concurrent_limit": 5,
                "tools": ["manufacturing_intent_classification", "data_requirements_analysis"]
            },
            "professional": {
                "monthly_cost": 2000,
                "request_limit": 5000,
                "concurrent_limit": 10,
                "tools": ["manufacturing_intent_classification", "data_requirements_analysis", "optimization_model_building", "optimization_solving"]
            },
            "enterprise": {
                "monthly_cost": 10000,
                "request_limit": 25000,
                "concurrent_limit": 20,
                "tools": ["manufacturing_intent_classification", "data_requirements_analysis", "optimization_model_building", "optimization_solving", "comprehensive_workflow"]
            }
        },
        description="Tenant plan configurations"
    )
    
    @classmethod
    def get_settings(cls) -> "MCPServerSettings":
        """Get settings instance."""
        return cls()
    
    def get_tool_cost(self, tool_name: str) -> float:
        """Get cost for a specific tool."""
        return self.tool_cost_rates.get(tool_name, 0.0)
    
    def get_tenant_plan(self, plan_name: str) -> Dict[str, Any]:
        """Get tenant plan configuration."""
        return self.tenant_plans.get(plan_name, self.tenant_plans["basic"])


# Global settings instance
settings = MCPServerSettings.get_settings()
