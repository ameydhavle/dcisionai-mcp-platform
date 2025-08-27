#!/usr/bin/env python3
"""
DcisionAI MCP Server - Production Entry Point
=============================================

Production entry point for the DcisionAI MCP server.
Configured for AWS Bedrock AgentCore deployment.

Usage:
    python run_mcp_server.py
"""

import sys
import os
import logging
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def setup_environment():
    """Setup environment for production deployment."""
    # Set default environment variables if not present
    if not os.getenv("MCP_SERVER_HOST"):
        os.environ["MCP_SERVER_HOST"] = "0.0.0.0"
    
    if not os.getenv("MCP_SERVER_PORT"):
        os.environ["MCP_SERVER_PORT"] = "8000"
    
    if not os.getenv("LOG_LEVEL"):
        os.environ["LOG_LEVEL"] = "INFO"
    
    # AWS AgentCore specific settings
    os.environ["STATELESS_HTTP"] = "true"
    os.environ["TRANSPORT"] = "streamable-http"

def setup_logging():
    """Setup production logging."""
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.StreamHandler(sys.stderr)
        ]
    )

def main():
    """Main entry point for production deployment."""
    try:
        # Setup environment
        setup_environment()
        
        # Setup logging
        setup_logging()
        
        # Import and create server
        from mcp_server.fastmcp_server import create_fastmcp_server
        
        # Create server instance
        server = create_fastmcp_server()
        
        # Run server
        server.run()
        
    except KeyboardInterrupt:
        print("\nShutting down gracefully...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Failed to start MCP server: {e}", file=sys.stderr)
        logging.exception("Server startup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
