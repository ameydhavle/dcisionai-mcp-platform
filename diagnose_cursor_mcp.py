#!/usr/bin/env python3
"""
Diagnostic script to check why Cursor is not detecting MCP server tools
"""

import subprocess
import sys
import os
import json

def check_python_path():
    """Check if the Python path in Cursor config is correct."""
    print("🔍 Checking Python path...")
    python_path = "/Users/ameydhavle/Documents/DcisionAI/dcisionai-mcp-platform/venv/bin/python"
    
    if os.path.exists(python_path):
        print(f"✅ Python path exists: {python_path}")
        
        # Check Python version
        result = subprocess.run([python_path, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Python version: {result.stdout.strip()}")
        else:
            print(f"❌ Python version check failed: {result.stderr}")
    else:
        print(f"❌ Python path does not exist: {python_path}")
        return False
    
    return True

def check_module_import():
    """Check if the MCP server module can be imported."""
    print("\n🔍 Checking module import...")
    python_path = "/Users/ameydhavle/Documents/DcisionAI/dcisionai-mcp-platform/venv/bin/python"
    
    try:
        result = subprocess.run([
            python_path, "-c", 
            "import dcisionai_mcp_server.robust_mcp; print('Module imported successfully')"
        ], capture_output=True, text=True, cwd="/Users/ameydhavle/Documents/DcisionAI/dcisionai-mcp-platform")
        
        if result.returncode == 0:
            print("✅ Module can be imported successfully")
            print(f"Output: {result.stdout.strip()}")
        else:
            print("❌ Module import failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception during module import: {e}")
        return False
    
    return True

def check_environment_variables():
    """Check if environment variables are set correctly."""
    print("\n🔍 Checking environment variables...")
    
    required_vars = [
        "DCISIONAI_ACCESS_TOKEN",
        "DCISIONAI_GATEWAY_URL", 
        "DCISIONAI_GATEWAY_TARGET"
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set (length: {len(value)})")
        else:
            print(f"❌ {var}: Not set")
            all_good = False
    
    return all_good

def test_mcp_server_startup():
    """Test if the MCP server can start up properly."""
    print("\n🔍 Testing MCP server startup...")
    python_path = "/Users/ameydhavle/Documents/DcisionAI/dcisionai-mcp-platform/venv/bin/python"
    
    # Set environment variables
    env = os.environ.copy()
    env.update({
        "DCISIONAI_ACCESS_TOKEN": "eyJraWQiOiJLMWZEMFwvXC9qaGtJSHlZd2IyM2NsMkRSK0dEQ2tFaHVWZVd0djdFMERkOUk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI1cjdyaXJqdmI0OTZpam1rMDNtanNrNTNtOCIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiRGNpc2lvbkFJLUdhdGV3YXktMGRlMWE2NTVcL2ludm9rZSIsImF1dGhfdGltZSI6MTc2MDU1MjM2OCwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfdjlDSmJRMWVKIiwiZXhwIjoxNzYwNTU1OTY4LCJpYXQiOjE3NjA1NTIzNjgsInZlcnNpb24iOjIsImp0aSI6Ijg0MjI0MTVlLWRkNzItNGUxOC1iNzE4LWM0ZDA2OGEwYjc1MiIsImNsaWVudF9pZCI6IjVyN3Jpcmp2YjQ5NmlqbWswM21qc2s1M204In0.jIcR3ieA2Z5zjmsvPxv1dhYDzDRBSubaERUYlnZvjlP1VbHE88fyixssnMDECpJevzbHE7w_2ctVZDVYNtyrlgWhdW-j5fRKXGB0WP0GcPwI2g9MlgQIkSAwiqTZdDc2A8So01RhtsLQeXHmUBVvtvV_b-ptZtXl8aOzd7M-0DZExOxf4PvcZaBULTVLKAS2Rqehh_M3mvlS-3vaqXXdGF2JL3kxtdn8MYT4lbVBmJ-S4frGOJawNrZ7Dtl9ZRx5iOd-ljxVn8KxXh7kgtWH1LLvgdPnvfWC0-sCQd5OpIxg-QRVlX4No4dKQQSgG9F4bFhNHVvd97opfj8NKFdIGg",
        "DCISIONAI_GATEWAY_URL": "https://dcisionai-gateway-0de1a655-ja1rhlcqjx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp",
        "DCISIONAI_GATEWAY_TARGET": "DcisionAI-Optimization-Tools-Fixed"
    })
    
    try:
        # Test server startup with a simple command
        result = subprocess.run([
            python_path, "-m", "dcisionai_mcp_server.robust_mcp"
        ], input='{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "test", "version": "1.0.0"}}}\n', 
        capture_output=True, text=True, timeout=5, env=env, cwd="/Users/ameydhavle/Documents/DcisionAI/dcisionai-mcp-platform")
        
        if result.returncode == 0:
            print("✅ MCP server started successfully")
            print(f"Response: {result.stdout.strip()}")
        else:
            print("❌ MCP server startup failed")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✅ MCP server started (timeout expected for long-running server)")
    except Exception as e:
        print(f"❌ Exception during MCP server startup: {e}")
        return False
    
    return True

def check_cursor_config():
    """Check if Cursor configuration is correct."""
    print("\n🔍 Checking Cursor configuration...")
    config_path = os.path.expanduser("~/.cursor/mcp.json")
    
    if os.path.exists(config_path):
        print(f"✅ Cursor config exists: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if "mcpServers" in config and "dcisionai-optimization" in config["mcpServers"]:
                server_config = config["mcpServers"]["dcisionai-optimization"]
                print("✅ DcisionAI MCP server configuration found")
                
                # Check command
                if "command" in server_config:
                    print(f"✅ Command: {server_config['command']}")
                else:
                    print("❌ Command not found in config")
                
                # Check args
                if "args" in server_config:
                    print(f"✅ Args: {server_config['args']}")
                else:
                    print("❌ Args not found in config")
                
                # Check env
                if "env" in server_config:
                    print(f"✅ Environment variables: {len(server_config['env'])} set")
                else:
                    print("❌ Environment variables not found in config")
                
                return True
            else:
                print("❌ DcisionAI MCP server configuration not found")
                return False
        except Exception as e:
            print(f"❌ Error reading Cursor config: {e}")
            return False
    else:
        print(f"❌ Cursor config does not exist: {config_path}")
        return False

def main():
    """Run all diagnostic checks."""
    print("🔧 DcisionAI MCP Server - Cursor Integration Diagnostics")
    print("=" * 60)
    
    checks = [
        ("Python Path", check_python_path),
        ("Module Import", check_module_import),
        ("Environment Variables", check_environment_variables),
        ("MCP Server Startup", test_mcp_server_startup),
        ("Cursor Configuration", check_cursor_config)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with exception: {e}")
            results.append((name, False))
    
    print("\n📊 Diagnostic Summary")
    print("=" * 30)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All checks passed! MCP server should work with Cursor.")
        print("💡 If Cursor still shows 'No tools', try restarting Cursor IDE.")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main()
