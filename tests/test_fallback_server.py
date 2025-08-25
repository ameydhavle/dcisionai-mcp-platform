#!/usr/bin/env python3
"""
Test script to demonstrate the fallback MCP server with all 6 agent responses.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.mcp_server_fallback import FallbackMCPServer

async def test_fallback_server():
    """Test the fallback MCP server with all 6 agent responses."""
    
    print("🧪 Testing DcisionAI Fallback MCP Server")
    print("=" * 50)
    
    # Initialize the server
    server = FallbackMCPServer()
    
    # Test the complete workflow
    print("\n🚀 Testing Complete Manufacturing Optimization Workflow")
    print("-" * 50)
    
    query = "optimize production line efficiency and reduce cycle time"
    session_id = "test-session-1"
    
    # Call the complete workflow
    result = await server._handle_complete_workflow({
        "query": query,
        "session_id": session_id,
        "include_all_tools": True
    }, "test-1")
    
    # Parse the response
    response_text = result["result"]["content"][0]["text"]
    response_data = json.loads(response_text)
    
    print(f"✅ Workflow completed successfully!")
    print(f"📊 Workflow ID: {response_data['workflow_id']}")
    print(f"⏱️  Execution Time: {response_data['execution_time']:.2f}s")
    print(f"🔧 Total Tools Executed: {response_data['workflow_summary']['total_tools_executed']}")
    
    print("\n📋 All 6 Agent Responses:")
    print("=" * 50)
    
    tool_results = response_data["tool_results"]
    
    # Tool 1: Intent Classification
    print("\n1️⃣ Intent Classification (6-agent swarm):")
    intent = tool_results["intent_classification"]
    print(f"   • Primary Intent: {intent['primary_intent']}")
    print(f"   • Confidence: {intent['confidence']}")
    print(f"   • Agents Used: {', '.join(intent['agents_used'])}")
    print(f"   • Swarm Consensus: {intent['swarm_consensus']}")
    
    # Tool 2: Data Analysis
    print("\n2️⃣ Data Analysis (3-stage analysis):")
    data = tool_results["data_analysis"]
    print(f"   • Data Quality Score: {data['data_quality_score']}")
    print(f"   • Optimization Readiness: {data['optimization_readiness']}")
    print(f"   • Stages Completed: {data['execution_metadata']['stages_completed']}")
    print(f"   • Agents Used: {', '.join(data['execution_metadata']['agents_used'])}")
    
    # Tool 3: Model Building
    print("\n3️⃣ Model Building (6-specialist swarm):")
    model = tool_results["model_building"]
    print(f"   • Model Type: {model['model']['model_type']}")
    print(f"   • Model Complexity: {model['model']['model_complexity']}")
    print(f"   • Recommended Solver: {model['model']['recommended_solver']}")
    print(f"   • Agents Used: {model['agents_used']}")
    
    # Tool 4: Solver Execution
    print("\n4️⃣ Solver Execution (shared solver swarm):")
    solver = tool_results["solver_results"]
    print(f"   • Solver Used: {solver['solver_results']['solver_used']}")
    print(f"   • Solution Status: {solver['solver_results']['solution_status']}")
    print(f"   • Objective Value: {solver['solver_results']['objective_value']}")
    print(f"   • Efficiency Improvement: {solver['solver_results']['best_solution']['efficiency_improvement']}")
    
    # Tool 5: Visualization (roadmap)
    print("\n5️⃣ Visualization (roadmap - not implemented):")
    viz = tool_results["visualization"]
    print(f"   • Status: {viz['status']}")
    print(f"   • Message: {viz['message']}")
    print(f"   • Planned Capabilities: {', '.join(viz['capabilities'])}")
    
    # Tool 6: Swarm Orchestration
    print("\n6️⃣ Swarm Orchestration (coordination):")
    swarm = tool_results["swarm_orchestration"]
    print(f"   • Agents Coordinated: {swarm['agents_coordinated']}")
    print(f"   • Coordination Pattern: {swarm['coordination_pattern']}")
    print(f"   • Optimization Quality: {swarm['performance_metrics']['optimization_quality']}")
    print(f"   • Agent Utilization: {swarm['performance_metrics']['agent_utilization']}")
    
    print("\n🎯 Workflow Summary:")
    print("=" * 50)
    summary = response_data["workflow_summary"]
    print(f"   • Tools Available: {summary['tools_available']}")
    print(f"   • Tools on Roadmap: {summary['tools_roadmap']}")
    print(f"   • Tools for Coordination: {summary['tools_coordination']}")
    print(f"   • Optimization Readiness: {summary['optimization_readiness']}")
    
    print("\n📝 Next Steps:")
    for i, step in enumerate(summary['next_steps'], 1):
        print(f"   {i}. {step}")
    
    print("\n✅ All 6 agent responses successfully demonstrated!")
    print("🔧 The MCP server shows the complete manufacturing optimization workflow")
    print("🎯 Each tool demonstrates its specific capabilities and agent coordination")

if __name__ == "__main__":
    asyncio.run(test_fallback_server())
