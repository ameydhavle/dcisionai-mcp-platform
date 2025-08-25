#!/usr/bin/env python3
"""
DcisionAI MCP Server Entry Point
===============================

Entry point script for running the MCP server.
"""

import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the MCP server
from src.mcp_server.main import main

if __name__ == "__main__":
    asyncio.run(main())
