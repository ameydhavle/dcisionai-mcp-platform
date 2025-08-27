#!/usr/bin/env python3
"""
Test script to check what's actually functional vs. what's not working.
This provides honest assessment of the platform's current state.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_manufacturing_agent_status():
    """Test the actual status of the manufacturing agent."""
    
    print("🔍 Testing Real Manufacturing Agent Status")
    print("=" * 50)
    
    try:
        from src.models.manufacturing.DcisionAI_Manufacturing_Agent import DcisionAI_Manufacturing_Agent
        agent = DcisionAI_Manufacturing_Agent()
        
        print("\n📊 Manufacturing Agent Tool Status:")
        print("-" * 40)
        
        working_count = 0
        for tool, status in agent.available_tools.items():
            status_icon = "✅" if status.value == "working" else "❌"
            print(f"{status_icon} {tool}: {status.value}")
            if status.value == "working":
                working_count += 1
        
        print(f"\n📈 Summary: {working_count}/{len(agent.available_tools)} tools marked as working")
        
        # Test if the agent can actually be used
        print("\n🧪 Testing Agent Functionality:")
        print("-" * 40)
        
        try:
            # Test the analyze_manufacturing_optimization method
            result = agent.analyze_manufacturing_optimization(
                "optimize production line efficiency", 
                "test-session"
            )
            print("✅ Agent.analyze_manufacturing_optimization() - SUCCESS")
            print(f"   Workflow ID: {result.workflow_id}")
            print(f"   Current Stage: {result.current_stage.value}")
            print(f"   Errors: {len(result.errors)}")
            print(f"   Warnings: {len(result.warnings)}")
            
            if result.errors:
                print("   ❌ Errors found:")
                for error in result.errors:
                    print(f"      - {error}")
                    
            if result.warnings:
                print("   ⚠️  Warnings found:")
                for warning in result.warnings:
                    print(f"      - {warning}")
                    
        except Exception as e:
            print(f"❌ Agent.analyze_manufacturing_optimization() - FAILED")
            print(f"   Error: {str(e)}")
            
        return working_count, len(agent.available_tools)
        
    except Exception as e:
        print(f"❌ Failed to initialize manufacturing agent: {e}")
        return 0, 0

def test_mcp_servers():
    """Test which MCP servers are actually functional."""
    
    print("\n🔍 Testing MCP Server Functionality")
    print("=" * 50)
    
    servers = [
        ("Enhanced MCP Server", "src.mcp_server_enhanced", "EnhancedMCPServer"),
        ("HTTP MCP Server", "src.mcp_server_http", "HTTPMCPServer"),
        ("Simple MCP Server", "src.mcp_server_simple", "MCPServer"),
    ]
    
    functional_servers = []
    
    for name, module, class_name in servers:
        try:
            module_obj = __import__(module, fromlist=[class_name])
            server_class = getattr(module_obj, class_name)
            server = server_class()
            print(f"✅ {name}: Available")
            functional_servers.append(name)
        except Exception as e:
            print(f"❌ {name}: Not available - {str(e)}")
    
    return functional_servers

def test_dependencies():
    """Test which dependencies are actually available."""
    
    print("\n🔍 Testing Dependencies")
    print("=" * 50)
    
    dependencies = [
        ("strands", "Strands framework for agent orchestration"),
        ("fastapi", "FastAPI for HTTP server"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("structlog", "Structured logging"),
    ]
    
    available_deps = []
    
    for dep, description in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}: Available - {description}")
            available_deps.append(dep)
        except ImportError:
            print(f"❌ {dep}: Not available - {description}")
    
    return available_deps

def main():
    """Main test function."""
    
    print("🧪 REAL FUNCTIONALITY ASSESSMENT")
    print("=" * 60)
    print("This test provides an honest assessment of what's actually working.")
    print("=" * 60)
    
    # Test manufacturing agent
    working_tools, total_tools = test_manufacturing_agent_status()
    
    # Test MCP servers
    functional_servers = test_mcp_servers()
    
    # Test dependencies
    available_deps = test_dependencies()
    
    # Summary
    print("\n📊 REAL FUNCTIONALITY SUMMARY")
    print("=" * 60)
    
    print(f"🏭 Manufacturing Agent: {working_tools}/{total_tools} tools working")
    print(f"🌐 MCP Servers: {len(functional_servers)} functional")
    print(f"📦 Dependencies: {len(available_deps)} available")
    
    print("\n🎯 HONEST ASSESSMENT:")
    print("-" * 30)
    
    if working_tools == total_tools and len(functional_servers) > 0:
        print("✅ FULLY FUNCTIONAL: All tools working, MCP servers available")
        print("🚀 Ready for production use")
    elif working_tools > 0 and len(functional_servers) > 0:
        print("⚠️  PARTIALLY FUNCTIONAL: Some tools working, MCP servers available")
        print("🔧 Needs dependency fixes for full functionality")
    elif len(functional_servers) > 0:
        print("⚠️  BASIC FUNCTIONALITY: MCP servers available but tools not working")
        print("🔧 Needs manufacturing agent fixes")
    else:
        print("❌ NOT FUNCTIONAL: No working components")
        print("🔧 Needs significant fixes")
    
    print("\n📝 RECOMMENDATIONS:")
    print("-" * 20)
    
    if "strands" not in available_deps:
        print("1. Install strands framework for full agent functionality")
    
    if working_tools < total_tools:
        print("2. Fix manufacturing agent tool dependencies")
    
    if len(functional_servers) == 0:
        print("3. Fix MCP server dependencies")
    
    print("\n✅ Assessment complete - Honest evaluation provided!")

if __name__ == "__main__":
    main()
