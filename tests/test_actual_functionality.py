#!/usr/bin/env python3
"""
Test script to verify actual functionality vs. warnings.
This provides a clear picture of what's working and what needs fixing.
"""

import sys
import json
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_dependencies():
    """Test which dependencies are actually available."""
    
    print("🔍 Testing Dependencies")
    print("=" * 50)
    
    dependencies = [
        ("strands", "Strands framework for agent orchestration"),
        ("ortools", "OR-Tools for optimization"),
        ("pulp", "PuLP for linear programming"),
        ("cvxpy", "CVXPY for convex optimization"),
        ("pyomo", "Pyomo for mathematical modeling"),
        ("fastapi", "FastAPI for HTTP server"),
        ("uvicorn", "ASGI server"),
    ]
    
    available_deps = []
    missing_deps = []
    
    for dep, description in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}: Available - {description}")
            available_deps.append(dep)
        except ImportError:
            print(f"❌ {dep}: Not available - {description}")
            missing_deps.append(dep)
    
    return available_deps, missing_deps

def test_manufacturing_tools():
    """Test the actual manufacturing tools."""
    
    print("\n🔍 Testing Manufacturing Tools")
    print("=" * 50)
    
    tools = [
        ("Intent Tool v6", "src.models.manufacturing.tools.intent.DcisionAI_Intent_Tool_v6", "create_dcisionai_intent_tool_v6"),
        ("Data Tool v3", "src.models.manufacturing.tools.data.DcisionAI_Data_Tool_v3", "create_dcisionai_data_tool_v3"),
        ("Model Builder v1", "src.models.manufacturing.tools.model.DcisionAI_Model_Builder_v1", "create_dcisionai_model_builder"),
        ("Solver Tool", "src.shared.tools.solver", "create_shared_solver_tool"),
    ]
    
    working_tools = []
    failed_tools = []
    
    for name, module, function in tools:
        try:
            module_obj = __import__(module, fromlist=[function])
            tool_func = getattr(module_obj, function)
            tool_instance = tool_func()
            print(f"✅ {name}: Available and instantiable")
            working_tools.append(name)
        except Exception as e:
            print(f"❌ {name}: Failed - {str(e)}")
            failed_tools.append((name, str(e)))
    
    return working_tools, failed_tools

def test_manufacturing_agent():
    """Test the manufacturing agent functionality."""
    
    print("\n🔍 Testing Manufacturing Agent")
    print("=" * 50)
    
    try:
        from src.models.manufacturing.DcisionAI_Manufacturing_Agent import DcisionAI_Manufacturing_Agent
        agent = DcisionAI_Manufacturing_Agent()
        
        print("✅ Manufacturing agent: Initialized successfully")
        print(f"📊 Available tools: {agent.available_tools}")
        
        # Test actual functionality
        print("\n🧪 Testing Agent Functionality:")
        print("-" * 40)
        
        start_time = time.time()
        result = agent.analyze_manufacturing_optimization(
            "optimize production line efficiency", 
            "test-session"
        )
        execution_time = time.time() - start_time
        
        print(f"✅ Agent.analyze_manufacturing_optimization() - SUCCESS")
        print(f"   Workflow ID: {result.workflow_id}")
        print(f"   Current Stage: {result.current_stage.value}")
        print(f"   Execution Time: {execution_time:.2f}s")
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
        
        return True, result
        
    except Exception as e:
        print(f"❌ Manufacturing agent failed: {e}")
        return False, str(e)

def test_mcp_server():
    """Test the MCP server functionality."""
    
    print("\n🔍 Testing MCP Server")
    print("=" * 50)
    
    try:
        from src.DcisionAI_MCP_Server_v1 import DcisionAI_MCP_Server_v1
        server = DcisionAI_MCP_Server_v1()
        
        print("✅ MCP Server: Initialized successfully")
        print(f"📋 Available tools: {list(server.tools.keys())}")
        print(f"🏭 Manufacturing agent: {'Available' if server.manufacturing_agent else 'Not available'}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP Server failed: {e}")
        return False

def main():
    """Main test function."""
    
    print("🧪 ACTUAL FUNCTIONALITY ASSESSMENT")
    print("=" * 60)
    print("This test verifies what's actually working vs. what's just showing warnings.")
    print("=" * 60)
    
    # Test dependencies
    available_deps, missing_deps = test_dependencies()
    
    # Test manufacturing tools
    working_tools, failed_tools = test_manufacturing_tools()
    
    # Test manufacturing agent
    agent_works, agent_result = test_manufacturing_agent()
    
    # Test MCP server
    server_works = test_mcp_server()
    
    # Summary
    print("\n📊 ACTUAL FUNCTIONALITY SUMMARY")
    print("=" * 60)
    
    print(f"📦 Dependencies: {len(available_deps)}/{len(available_deps) + len(missing_deps)} available")
    print(f"🔧 Manufacturing Tools: {len(working_tools)}/{len(working_tools) + len(failed_tools)} working")
    print(f"🏭 Manufacturing Agent: {'Working' if agent_works else 'Failed'}")
    print(f"🌐 MCP Server: {'Working' if server_works else 'Failed'}")
    
    print("\n🎯 HONEST ASSESSMENT:")
    print("-" * 30)
    
    if len(missing_deps) == 0 and len(failed_tools) == 0 and agent_works and server_works:
        print("✅ FULLY FUNCTIONAL: All components working")
        print("🚀 Ready for production use")
    elif len(missing_deps) == 0 and agent_works and server_works:
        print("✅ MOSTLY FUNCTIONAL: Core components working")
        print("🔧 Some tools have issues but core functionality works")
    elif agent_works and server_works:
        print("⚠️  PARTIALLY FUNCTIONAL: Core functionality works")
        print("🔧 Missing dependencies need to be installed")
    elif agent_works:
        print("⚠️  BASIC FUNCTIONALITY: Agent works but server issues")
        print("🔧 MCP server needs fixing")
    else:
        print("❌ NOT FUNCTIONAL: Core components failing")
        print("🔧 Needs significant fixes")
    
    print("\n📝 SPECIFIC ISSUES:")
    print("-" * 20)
    
    if missing_deps:
        print("Missing Dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
    
    if failed_tools:
        print("Failed Tools:")
        for tool, error in failed_tools:
            print(f"  - {tool}: {error}")
    
    print("\n✅ Assessment complete - Honest evaluation provided!")

if __name__ == "__main__":
    main()
