#!/usr/bin/env python3
"""
MCP Compliance Testing Configuration
==================================

Configuration file for connecting to the real DcisionAI MCP server
and running comprehensive compliance tests.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

# Import environment configurations
try:
    from .environments import get_environment_config, validate_environment, print_environment_info
except ImportError:
    # Fallback if environments module is not available
    def get_environment_config(env_name: str) -> Dict[str, Any]:
        return {}
    
    def validate_environment(env_name: str) -> bool:
        return False
    
    def print_environment_info(env_name: str) -> None:
        print(f"Environment '{env_name}' not available")


class MCPComplianceConfig:
    """Configuration for MCP compliance testing."""
    
    def __init__(self):
        """Initialize configuration with environment variables."""
        self.server_url = os.getenv("MCP_SERVER_URL", "ws://localhost:8080/mcp")
        self.auth_token = os.getenv("MCP_AUTH_TOKEN")
        self.timeout = int(os.getenv("MCP_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MCP_MAX_RETRIES", "3"))
        self.output_dir = os.getenv("COMPLIANCE_OUTPUT_DIR", "compliance_reports")
        self.export_formats = os.getenv("EXPORT_FORMATS", "json,yaml,html").split(",")
        
        # Test configuration
        self.run_real_tests = os.getenv("RUN_REAL_TESTS", "true").lower() == "true"
        self.test_timeout = int(os.getenv("TEST_TIMEOUT", "300"))
        self.parallel_tests = int(os.getenv("PARALLEL_TESTS", "1"))
        
        # Environment configuration
        self.current_environment = os.getenv("MCP_ENVIRONMENT", "default")
        
        # Server-specific configuration
        self.server_config = self._get_server_config()
    
    def _get_server_config(self) -> Dict[str, Any]:
        """Get server-specific configuration based on URL."""
        # First try to get environment-specific config
        if self.current_environment != "default":
            env_config = get_environment_config(self.current_environment)
            if env_config:
                return env_config
        
        # Fall back to URL-based detection
        if "localhost" in self.server_url or "127.0.0.1" in self.server_url:
            return self._get_local_config()
        elif "dcisionai" in self.server_url.lower():
            return self._get_dcisionai_config()
        elif "aws" in self.server_url.lower():
            return self._get_aws_config()
        else:
            return self._get_default_config()
    
    def _get_local_config(self) -> Dict[str, Any]:
        """Configuration for local development server."""
        return {
            "name": "Local Development Server",
            "expected_tools": ["intent", "data", "model", "solver"],
            "expected_protocol_version": "2025-03-26",
            "supports_websocket": True,
            "supports_http": False,
            "auth_required": False,
            "rate_limiting": False,
            "circuit_breaker": False,
            "health_checks": True,
            "timeout_multiplier": 1.0
        }
    
    def _get_dcisionai_config(self) -> Dict[str, Any]:
        """Configuration for DcisionAI production server."""
        return {
            "name": "DcisionAI Production Server",
            "expected_tools": [
                "intent.classify",
                "data.analyze", 
                "model.build",
                "solver.optimize",
                "critique.analyze",
                "explain.generate",
                "swarm.orchestrate"
            ],
            "expected_protocol_version": "2025-03-26",
            "supports_websocket": True,
            "supports_http": True,
            "auth_required": True,
            "rate_limiting": True,
            "circuit_breaker": True,
            "health_checks": True,
            "timeout_multiplier": 2.0
        }
    
    def _get_aws_config(self) -> Dict[str, Any]:
        """Configuration for AWS-hosted server."""
        return {
            "name": "AWS Hosted Server",
            "expected_tools": ["intent", "data", "model", "solver"],
            "expected_protocol_version": "2025-03-26",
            "supports_websocket": True,
            "supports_http": True,
            "auth_required": True,
            "rate_limiting": True,
            "circuit_breaker": True,
            "health_checks": True,
            "timeout_multiplier": 1.5
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for unknown servers."""
        return {
            "name": "Unknown Server",
            "expected_tools": [],
            "expected_protocol_version": "2025-03-26",
            "supports_websocket": True,
            "supports_http": True,
            "auth_required": False,
            "rate_limiting": False,
            "circuit_breaker": False,
            "health_checks": False,
            "timeout_multiplier": 1.0
        }
    
    def get_test_config(self) -> Dict[str, Any]:
        """Get configuration for test execution."""
        return {
            "server_url": self.server_url,
            "auth_token": self.auth_token,
            "timeout": int(self.timeout * self.server_config["timeout_multiplier"]),
            "max_retries": self.max_retries,
            "output_dir": self.output_dir,
            "export_formats": self.export_formats,
            "server_config": self.server_config,
            "run_real_tests": self.run_real_tests,
            "test_timeout": self.test_timeout,
            "parallel_tests": self.parallel_tests
        }
    
    def validate_config(self) -> bool:
        """Validate configuration for testing."""
        errors = []
        
        if not self.server_url:
            errors.append("MCP_SERVER_URL is required")
        
        if self.server_config["auth_required"] and not self.auth_token:
            errors.append("MCP_AUTH_TOKEN is required for this server")
        
        if self.timeout <= 0:
            errors.append("MCP_TIMEOUT must be positive")
        
        if self.max_retries < 0:
            errors.append("MCP_MAX_RETRIES must be non-negative")
        
        if errors:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        return True
    
    def print_config(self) -> None:
        """Print current configuration."""
        print("🔧 MCP Compliance Testing Configuration")
        print("=" * 50)
        print(f"Server URL: {self.server_url}")
        print(f"Server Name: {self.server_config['name']}")
        print(f"Protocol Version: {self.server_config['expected_protocol_version']}")
        print(f"Authentication: {'Required' if self.server_config['auth_required'] else 'Optional'}")
        print(f"WebSocket Support: {'Yes' if self.server_config['supports_websocket'] else 'No'}")
        print(f"HTTP Support: {'Yes' if self.server_config['supports_http'] else 'No'}")
        print(f"Rate Limiting: {'Yes' if self.server_config['rate_limiting'] else 'No'}")
        print(f"Circuit Breaker: {'Yes' if self.server_config['circuit_breaker'] else 'No'}")
        print(f"Health Checks: {'Yes' if self.server_config['health_checks'] else 'No'}")
        print(f"Timeout: {self.timeout}s (adjusted: {int(self.timeout * self.server_config['timeout_multiplier'])}s)")
        print(f"Max Retries: {self.max_retries}")
        print(f"Output Directory: {self.output_dir}")
        print(f"Export Formats: {', '.join(self.export_formats)}")
        print(f"Run Real Tests: {self.run_real_tests}")
        print(f"Test Timeout: {self.test_timeout}s")
        print(f"Parallel Tests: {self.parallel_tests}")
        print("=" * 50)


# Environment-specific configurations
ENVIRONMENTS = {
    "local": {
        "MCP_SERVER_URL": "ws://localhost:8080/mcp",
        "MCP_AUTH_TOKEN": None,
        "MCP_TIMEOUT": "30",
        "MCP_MAX_RETRIES": "3",
        "COMPLIANCE_OUTPUT_DIR": "compliance_reports/local",
        "EXPORT_FORMATS": "json,yaml,html",
        "RUN_REAL_TESTS": "true",
        "TEST_TIMEOUT": "300",
        "PARALLEL_TESTS": "1"
    },
    "development": {
        "MCP_SERVER_URL": "ws://dev.dcisionai.com:8080/mcp",
        "MCP_AUTH_TOKEN": "dev-token-here",
        "MCP_TIMEOUT": "60",
        "MCP_MAX_RETRIES": "5",
        "COMPLIANCE_OUTPUT_DIR": "compliance_reports/dev",
        "EXPORT_FORMATS": "json,yaml,html",
        "RUN_REAL_TESTS": "true",
        "TEST_TIMEOUT": "600",
        "PARALLEL_TESTS": "2"
    },
    "staging": {
        "MCP_SERVER_URL": "wss://staging.dcisionai.com/mcp",
        "MCP_AUTH_TOKEN": "staging-token-here",
        "MCP_TIMEOUT": "90",
        "MCP_MAX_RETRIES": "5",
        "COMPLIANCE_OUTPUT_DIR": "compliance_reports/staging",
        "EXPORT_FORMATS": "json,yaml,html",
        "RUN_REAL_TESTS": "true",
        "TEST_TIMEOUT": "900",
        "PARALLEL_TESTS": "3"
    },
    "production": {
        "MCP_SERVER_URL": "wss://api.dcisionai.com/mcp",
        "MCP_AUTH_TOKEN": "production-token-here",
        "MCP_TIMEOUT": "120",
        "MCP_MAX_RETRIES": "5",
        "COMPLIANCE_OUTPUT_DIR": "compliance_reports/production",
        "EXPORT_FORMATS": "json,yaml,html",
        "RUN_REAL_TESTS": "true",
        "TEST_TIMEOUT": "1200",
        "PARALLEL_TESTS": "4"
    }
}


def load_environment_config(env_name: str) -> None:
    """Load configuration for a specific environment."""
    if env_name not in ENVIRONMENTS:
        print(f"❌ Unknown environment: {env_name}")
        print(f"Available environments: {', '.join(ENVIRONMENTS.keys())}")
        return
    
    env_config = ENVIRONMENTS[env_name]
    print(f"🔧 Loading configuration for environment: {env_name}")
    
    for key, value in env_config.items():
        if value is not None:
            os.environ[key] = str(value)
            print(f"   {key} = {value}")
    
    print(f"✅ Environment '{env_name}' configuration loaded")


def get_current_environment() -> Optional[str]:
    """Get current environment name based on server URL."""
    config = MCPComplianceConfig()
    server_url = config.server_url.lower()
    
    if "localhost" in server_url or "127.0.0.1" in server_url:
        return "local"
    elif "dev.dcisionai.com" in server_url:
        return "development"
    elif "staging.dcisionai.com" in server_url:
        return "staging"
    elif "api.dcisionai.com" in server_url:
        return "production"
    else:
        return None


def get_test_config() -> Dict[str, Any]:
    """Get test configuration for the current environment."""
    config = MCPComplianceConfig()
    return {
        "server_url": config.server_url,
        "auth_token": config.auth_token,
        "timeout": config.timeout,
        "max_retries": config.max_retries,
        "parallel_tests": config.parallel_tests,
        "output_dir": config.output_dir,
        "server_config": config.server_config
    }


if __name__ == "__main__":
    # Test configuration loading
    import sys
    
    if len(sys.argv) > 1:
        env_name = sys.argv[1]
        load_environment_config(env_name)
    else:
        print("🔧 Current Configuration:")
        config = MCPComplianceConfig()
        config.print_config()
        
        current_env = get_current_environment()
        if current_env:
            print(f"\n🌍 Current Environment: {current_env}")
        else:
            print("\n🌍 Current Environment: Unknown")
        
        print("\nUsage: python config.py [environment_name]")
        print("Available environments:", ", ".join(ENVIRONMENTS.keys()))
