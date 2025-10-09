#!/usr/bin/env python3
"""
MCP Compliance Testing Environments
==================================

Environment-specific configurations for different MCP server instances.
This file defines the settings for local, development, staging, and production
environments to enable easy testing against different server configurations.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MCPEnvironment:
    """MCP server environment configuration."""
    
    name: str
    description: str
    server_url: str
    auth_token: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    parallel_tests: int = 5
    output_dir: str = "compliance_reports"
    
    # Server capabilities
    supports_websocket: bool = True
    supports_http: bool = False
    auth_required: bool = True
    rate_limiting: bool = True
    circuit_breaker: bool = True
    health_checks: bool = True
    
    # Expected features
    expected_protocol_version: str = "2025-03-26"
    expected_tools: int = 10
    expected_resources: int = 5
    
    # Security settings
    tls_version: str = "1.3"
    encryption_required: bool = True
    audit_logging: bool = True
    
    # Performance expectations
    max_response_time: float = 5.0
    max_tool_execution_time: float = 10.0
    max_connection_time: float = 2.0


# Environment configurations
ENVIRONMENTS: Dict[str, MCPEnvironment] = {
    "local": MCPEnvironment(
        name="Local Development",
        description="Local MCP server for development and testing",
        server_url="ws://localhost:8080/mcp",
        auth_token=None,  # No auth for local development
        timeout=15,
        max_retries=2,
        parallel_tests=3,
        output_dir="compliance_reports/local",
        
        # Local server capabilities
        supports_websocket=True,
        supports_http=True,
        auth_required=False,
        rate_limiting=False,
        circuit_breaker=False,
        health_checks=True,
        
        # Expected features
        expected_protocol_version="2025-03-26",
        expected_tools=5,
        expected_resources=3,
        
        # Security settings
        tls_version="1.2",
        encryption_required=False,
        audit_logging=False,
        
        # Performance expectations
        max_response_time=2.0,
        max_tool_execution_time=5.0,
        max_connection_time=1.0
    ),
    
    "dev": MCPEnvironment(
        name="Development Environment",
        description="Development MCP server with basic features",
        server_url="wss://dev-mcp.dcisionai.com/mcp",
        auth_token=os.getenv("DCISIONAI_DEV_AUTH_TOKEN"),
        timeout=30,
        max_retries=3,
        parallel_tests=5,
        output_dir="compliance_reports/dev",
        
        # Dev server capabilities
        supports_websocket=True,
        supports_http=False,
        auth_required=True,
        rate_limiting=True,
        circuit_breaker=False,
        health_checks=True,
        
        # Expected features
        expected_protocol_version="2025-03-26",
        expected_tools=8,
        expected_resources=4,
        
        # Security settings
        tls_version="1.3",
        encryption_required=True,
        audit_logging=True,
        
        # Performance expectations
        max_response_time=3.0,
        max_tool_execution_time=8.0,
        max_connection_time=1.5
    ),
    
    "staging": MCPEnvironment(
        name="Staging Environment",
        description="Staging MCP server with production-like features",
        server_url="wss://staging-mcp.dcisionai.com/mcp",
        auth_token=os.getenv("DCISIONAI_STAGING_AUTH_TOKEN"),
        timeout=45,
        max_retries=3,
        parallel_tests=8,
        output_dir="compliance_reports/staging",
        
        # Staging server capabilities
        supports_websocket=True,
        supports_http=True,
        auth_required=True,
        rate_limiting=True,
        circuit_breaker=True,
        health_checks=True,
        
        # Expected features
        expected_protocol_version="2025-03-26",
        expected_tools=12,
        expected_resources=6,
        
        # Security settings
        tls_version="1.3",
        encryption_required=True,
        audit_logging=True,
        
        # Performance expectations
        max_response_time=4.0,
        max_tool_execution_time=10.0,
        max_connection_time=2.0
    ),
    
    "prod": MCPEnvironment(
        name="Production Environment",
        description="Production MCP server with full enterprise features",
        server_url="wss://mcp.dcisionai.com/mcp",
        auth_token=os.getenv("DCISIONAI_PROD_AUTH_TOKEN"),
        timeout=60,
        max_retries=5,
        parallel_tests=10,
        output_dir="compliance_reports/prod",
        
        # Production server capabilities
        supports_websocket=True,
        supports_http=True,
        auth_required=True,
        rate_limiting=True,
        circuit_breaker=True,
        health_checks=True,
        
        # Expected features
        expected_protocol_version="2025-03-26",
        expected_tools=15,
        expected_resources=8,
        
        # Security settings
        tls_version="1.3",
        encryption_required=True,
        audit_logging=True,
        
        # Performance expectations
        max_response_time=5.0,
        max_tool_execution_time=15.0,
        max_connection_time=2.0
    ),
    
    "enterprise": MCPEnvironment(
        name="Enterprise Environment",
        description="Enterprise MCP server with advanced security and compliance",
        server_url="wss://enterprise-mcp.dcisionai.com/mcp",
        auth_token=os.getenv("DCISIONAI_ENTERPRISE_AUTH_TOKEN"),
        timeout=90,
        max_retries=7,
        parallel_tests=15,
        output_dir="compliance_reports/enterprise",
        
        # Enterprise server capabilities
        supports_websocket=True,
        supports_http=True,
        auth_required=True,
        rate_limiting=True,
        circuit_breaker=True,
        health_checks=True,
        
        # Expected features
        expected_protocol_version="2025-03-26",
        expected_tools=20,
        expected_resources=10,
        
        # Security settings
        tls_version="1.3",
        encryption_required=True,
        audit_logging=True,
        
        # Performance expectations
        max_response_time=7.0,
        max_tool_execution_time=20.0,
        max_connection_time=3.0
    )
}


def get_environment(env_name: str) -> Optional[MCPEnvironment]:
    """
    Get environment configuration by name.
    
    Args:
        env_name: Environment name (local, dev, staging, prod, enterprise)
        
    Returns:
        MCPEnvironment configuration or None if not found
    """
    return ENVIRONMENTS.get(env_name.lower())


def list_environments() -> Dict[str, str]:
    """
    List available environments with descriptions.
    
    Returns:
        Dictionary of environment names and descriptions
    """
    return {name: env.description for name, env in ENVIRONMENTS.items()}


def validate_environment(env_name: str) -> bool:
    """
    Validate that an environment exists and has required configuration.
    
    Args:
        env_name: Environment name to validate
        
    Returns:
        True if environment is valid, False otherwise
    """
    env = get_environment(env_name)
    if not env:
        return False
    
    # Check required fields
    if not env.server_url:
        return False
    
    # Check auth token for environments that require it
    if env.auth_required and not env.auth_token:
        return False
    
    return True


def get_environment_config(env_name: str) -> Dict[str, Any]:
    """
    Get environment configuration as dictionary.
    
    Args:
        env_name: Environment name
        
    Returns:
        Dictionary with environment configuration
    """
    env = get_environment(env_name)
    if not env:
        return {}
    
    return {
        "name": env.name,
        "description": env.description,
        "server_url": env.server_url,
        "auth_token": env.auth_token,
        "timeout": env.timeout,
        "max_retries": env.max_retries,
        "parallel_tests": env.parallel_tests,
        "output_dir": env.output_dir,
        "server_config": {
            "supports_websocket": env.supports_websocket,
            "supports_http": env.supports_http,
            "auth_required": env.auth_required,
            "rate_limiting": env.rate_limiting,
            "circuit_breaker": env.circuit_breaker,
            "health_checks": env.health_checks,
            "expected_protocol_version": env.expected_protocol_version,
            "expected_tools": env.expected_tools,
            "expected_resources": env.expected_resources,
            "tls_version": env.tls_version,
            "encryption_required": env.encryption_required,
            "audit_logging": env.audit_logging,
            "max_response_time": env.max_response_time,
            "max_tool_execution_time": env.max_tool_execution_time,
            "max_connection_time": env.max_connection_time
        }
    }


def print_environment_info(env_name: str) -> None:
    """
    Print detailed environment information.
    
    Args:
        env_name: Environment name to display
    """
    env = get_environment(env_name)
    if not env:
        print(f"❌ Environment '{env_name}' not found")
        return
    
    print(f"\n📋 Environment: {env.name}")
    print("=" * 50)
    print(f"Description: {env.description}")
    print(f"Server URL: {env.server_url}")
    print(f"Auth Required: {'Yes' if env.auth_required else 'No'}")
    print(f"Timeout: {env.timeout}s")
    print(f"Max Retries: {env.max_retries}")
    print(f"Parallel Tests: {env.parallel_tests}")
    print(f"Output Directory: {env.output_dir}")
    
    print(f"\n🔧 Server Capabilities:")
    print(f"  WebSocket: {'✅' if env.supports_websocket else '❌'}")
    print(f"  HTTP: {'✅' if env.supports_http else '❌'}")
    print(f"  Rate Limiting: {'✅' if env.rate_limiting else '❌'}")
    print(f"  Circuit Breaker: {'✅' if env.circuit_breaker else '❌'}")
    print(f"  Health Checks: {'✅' if env.health_checks else '❌'}")
    
    print(f"\n📊 Expected Features:")
    print(f"  Protocol Version: {env.expected_protocol_version}")
    print(f"  Tools: {env.expected_tools}")
    print(f"  Resources: {env.expected_resources}")
    
    print(f"\n🔒 Security:")
    print(f"  TLS Version: {env.tls_version}")
    print(f"  Encryption: {'Required' if env.encryption_required else 'Optional'}")
    print(f"  Audit Logging: {'✅' if env.audit_logging else '❌'}")
    
    print(f"\n⚡ Performance Expectations:")
    print(f"  Max Response Time: {env.max_response_time}s")
    print(f"  Max Tool Execution: {env.max_tool_execution_time}s")
    print(f"  Max Connection Time: {env.max_connection_time}s")


if __name__ == "__main__":
    """Display available environments when run directly."""
    print("🚀 Available MCP Compliance Testing Environments")
    print("=" * 60)
    
    for name, env in ENVIRONMENTS.items():
        print(f"\n🔧 {name.upper()}: {env.name}")
        print(f"   {env.description}")
        print(f"   URL: {env.server_url}")
        print(f"   Auth: {'Required' if env.auth_required else 'None'}")
    
    print(f"\n💡 Usage:")
    print(f"   python environments.py <environment_name>  # Show detailed info")
    print(f"   python run_real_tests.py <environment_name>  # Run tests")
