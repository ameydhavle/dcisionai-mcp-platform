#!/usr/bin/env python3
"""
Startup script for DcisionAI Manufacturing MCP Server
====================================================

This script provides easy startup options for different deployment scenarios.
"""

import os
import sys
import argparse
import yaml
from pathlib import Path

def load_config(config_file: str = "config/default.yaml"):
    """Load configuration from YAML file."""
    config_path = Path(config_file)
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

def setup_environment(config: dict):
    """Set up environment variables from config."""
    if 'aws' in config:
        aws_config = config['aws']
        if 'region' in aws_config:
            os.environ['AWS_DEFAULT_REGION'] = aws_config['region']
    
    if 'logging' in config:
        log_config = config['logging']
        if 'level' in log_config:
            os.environ['LOG_LEVEL'] = log_config['level']

def start_server(config_file: str = "config/default.yaml", port: int = None):
    """Start the MCP server with specified configuration."""
    print("🚀 Starting DcisionAI Manufacturing MCP Server")
    print("=" * 50)
    
    # Load configuration
    config = load_config(config_file)
    print(f"📋 Configuration loaded from: {config_file}")
    
    # Set up environment
    setup_environment(config)
    
    # Override port if specified
    if port:
        config['server'] = config.get('server', {})
        config['server']['port'] = port
    
    # Display configuration
    server_config = config.get('server', {})
    print(f"🌐 Host: {server_config.get('host', '0.0.0.0')}")
    print(f"🔌 Port: {server_config.get('port', 8000)}")
    print(f"🐛 Debug: {server_config.get('debug', False)}")
    
    aws_config = config.get('aws', {})
    print(f"☁️  AWS Region: {aws_config.get('region', 'us-east-1')}")
    
    # Check AWS credentials
    if not os.environ.get('AWS_ACCESS_KEY_ID'):
        print("⚠️  Warning: AWS_ACCESS_KEY_ID not set")
    if not os.environ.get('AWS_SECRET_ACCESS_KEY'):
        print("⚠️  Warning: AWS_SECRET_ACCESS_KEY not set")
    
    print("\n✅ Starting server...")
    
    # Import and run the MCP server
    try:
        from mcp_server import mcp
        mcp.run(transport="streamable-http")
    except ImportError as e:
        print(f"❌ Failed to import MCP server: {e}")
        print("Make sure you have installed the requirements: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Start DcisionAI Manufacturing MCP Server")
    parser.add_argument(
        "--config", 
        default="config/default.yaml",
        help="Configuration file path (default: config/default.yaml)"
    )
    parser.add_argument(
        "--port", 
        type=int,
        help="Override port number"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Use production configuration"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode with minimal configuration"
    )
    
    args = parser.parse_args()
    
    # Determine configuration file
    if args.production:
        config_file = "config/production.yaml"
    elif args.test:
        config_file = "config/test.yaml"
    else:
        config_file = args.config
    
    # Start the server
    start_server(config_file, args.port)

if __name__ == "__main__":
    main()
