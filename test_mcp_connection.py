#!/usr/bin/env python3
"""
Test script to simulate Cursor's MCP connection to our server
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any

async def test_mcp_server():
    """Test the MCP server connection like Cursor would."""
    
    print("🧪 Testing DcisionAI MCP Server Connection")
    print("=" * 50)
    
    # Start the MCP server process
    cmd = [
        "/Users/ameydhavle/Documents/DcisionAI/dcisionai-mcp-platform/venv/bin/python",
        "-m", "dcisionai_mcp_server.simple_mcp"
    ]
    
    env = {
        "DCISIONAI_ACCESS_TOKEN": "eyJraWQiOiJLMWZEMFwvXC9qaGtJSHlZd2IyM2NsMkRSK0dEQ2tFaHVWZVd0djdFMERkOUk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI1cjdyaXJqdmI0OTZpam1rMDNtanNrNTNtOCIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiRGNpc2lvbkFJLUdhdGV3YXktMGRlMWE2NTVcL2ludm9rZSIsImF1dGhfdGltZSI6MTc2MDU1MjM2OCwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfdjlDSmJRMWVKIiwiZXhwIjoxNzYwNTU1OTY4LCJpYXQiOjE3NjA1NTIzNjgsInZlcnNpb24iOjIsImp0aSI6Ijg0MjI0MTVlLWRkNzItNGUxOC1iNzE4LWM0ZDA2OGEwYjc1MiIsImNsaWVudF9pZCI6IjVyN3Jpcmp2YjQ5NmlqbWswM21qc2s1M204In0.jIcR3ieA2Z5zjmsvPxv1dhYDzDRBSubaERUYlnZvjlP1VbHE88fyixssnMDECpJevzbHE7w_2ctVZDVYNtyrlgWhdW-j5fRKXGB0WP0GcPwI2g9MlgQIkSAwiqTZdDc2A8So01RhtsLQeXHmUBVvtvV_b-ptZtXl8aOzd7M-0DZExOxf4PvcZaBULTVLKAS2Rqehh_M3mvlS-3vaqXXdGF2JL3kxtdn8MYT4lbVBmJ-S4frGOJawNrZ7Dtl9ZRx5iOd-ljxVn8KxXh7kgtWH1LLvgdPnvfWC0-sCQd5OpIxg-QRVlX4No4dKQQSgG9F4bFhNHVvd97opfj8NKFdIGg",
        "DCISIONAI_GATEWAY_URL": "https://dcisionai-gateway-0de1a655-ja1rhlcqjx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp",
        "DCISIONAI_GATEWAY_TARGET": "DcisionAI-Optimization-Tools-Fixed"
    }
    
    try:
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        print("✅ MCP Server process started")
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialization request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read initialization response
        init_response = process.stdout.readline()
        print(f"📥 Initialization response: {init_response.strip()}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        print("📤 Sending initialized notification...")
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # Send tools list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("📤 Sending tools list request...")
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        # Read tools response
        tools_response = process.stdout.readline()
        print(f"📥 Tools response: {tools_response.strip()}")
        
        # Parse and display tools
        try:
            tools_data = json.loads(tools_response)
            if "result" in tools_data and "tools" in tools_data["result"]:
                tools = tools_data["result"]["tools"]
                print(f"\n🎉 Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  • {tool['name']}: {tool['description']}")
            else:
                print("❌ No tools found in response")
                print(f"Full response: {tools_data}")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse tools response: {e}")
            print(f"Raw response: {tools_response}")
        
        # Clean up
        process.terminate()
        process.wait()
        
        print("\n✅ MCP Server test completed")
        
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
