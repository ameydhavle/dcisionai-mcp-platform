#!/usr/bin/env python3
"""
DcisionAI MCP Server v6 - AWS Documentation Example
==================================================

Exact implementation from AWS Bedrock AgentCore MCP documentation.
This is a minimal working example to verify AWS AgentCore compatibility
before adapting our manufacturing tools.

Based on: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html
"""

from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

# Create FastMCP server exactly as shown in AWS docs
mcp = FastMCP(host="0.0.0.0", stateless_http=True)

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.tool()
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together"""
    return a * b

@mcp.tool()
def greet_user(name: str) -> str:
    """Greet a user by name"""
    return f"Hello, {name}! Nice to meet you."

if __name__ == "__main__":
    print("🚀 Starting DcisionAI MCP Server v6 - AWS Documentation Example")
    print("✅ AWS AgentCore compliant - stateless HTTP, port 8000, session isolation")
    print("📍 Available at: http://0.0.0.0:8000/mcp")
    print("🛠️  Tools: add_numbers, multiply_numbers, greet_user")
    mcp.run(transport="streamable-http")
