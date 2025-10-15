#!/usr/bin/env python3
"""
Individual Tools Test for DcisionAI MCP Server
==============================================

This script tests individual tools with detailed output to see actual responses.
"""

import asyncio
import os
import json
from dcisionai_mcp_server.tools import (
    classify_intent,
    analyze_data,
    build_model,
    solve_optimization,
    get_workflow_templates
)

# Set up environment variables
os.environ["DCISIONAI_ACCESS_TOKEN"] = "eyJraWQiOiJLMWZEMFwvXC9qaGtJSHlZd2IyM2NsMkRSK0dEQ2tFaHVWZVd0djdFMERkOUk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI1cjdyaXJqdmI0OTZpam1rMDNtanNrNTNtOCIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiRGNpc2lvbkFJLUdhdGV3YXktMGRlMWE2NTVcL2ludm9rZSIsImF1dGhfdGltZSI6MTc2MDU0NzgwOCwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfdjlDSmJRMWVKIiwiZXhwIjoxNzYwNTUxNDA4LCJpYXQiOjE3NjA1NDc4MDgsInZlcnNpb24iOjIsImp0aSI6IjIzMDAwOTBmLWZjNzYtNDI1NC1hZjQ3LTY2ZDA5MGVkNzRiMiIsImNsaWVudF9pZCI6IjVyN3Jpcmp2YjQ5NmlqbWswM21qc2s1M204In0.nOgW15NAgzd-fB3Vn8fx0030rmX3_h9nKRkIM_JK3mXdATw-K0rCrinzll9XrN1m4pAOmVJFdoq0YbH7SOI6bMIl840TnN9hSxnKVy1zx5nOPn98btAKzP41UbLVJ8PGE3zAfrkOPtMaqvoMDzgCZP0fFF_FiCPFUWUvSs-OmbR2TnuVmdnuFCXLAQ_CMTJVpwVMk13P3mfJgkSPY33ly3GbtaVN9LDq11ZzVCAvsRbA7DvEWdSc9GVpHYmRwfEJYZZW4KNeOFZZRqZuryY57mBgcUaZ06deesl_ySN72a2CgJ1xnVCeK5VYcwdlUmQrSvEYxAJJGvF-ZacgQC6qUA"
os.environ["DCISIONAI_GATEWAY_URL"] = "https://dcisionai-gateway-0de1a655-ja1rhlcqjx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
os.environ["DCISIONAI_GATEWAY_TARGET"] = "DcisionAI-Optimization-Tools-Fixed"

async def test_classify_intent():
    """Test intent classification with detailed output"""
    print("🔍 TESTING: classify_intent")
    print("=" * 50)
    
    user_input = "I need to optimize my supply chain costs for 5 warehouses across different regions"
    context = "logistics"
    
    result = await classify_intent(user_input, context)
    print(f"Input: {user_input}")
    print(f"Context: {context}")
    print(f"Result: {json.dumps(result, indent=2)}")
    print()

async def test_analyze_data():
    """Test data analysis with detailed output"""
    print("📊 TESTING: analyze_data")
    print("=" * 50)
    
    data_description = "Supply chain data with 5 warehouses, 100 products, demand forecasts, and transportation costs"
    data_type = "tabular"
    constraints = "Warehouse capacity limits, transportation time windows, inventory holding costs"
    
    result = await analyze_data(data_description, data_type, constraints)
    print(f"Data Description: {data_description}")
    print(f"Data Type: {data_type}")
    print(f"Constraints: {constraints}")
    print(f"Result: {json.dumps(result, indent=2)}")
    print()

async def test_build_model():
    """Test model building with detailed output"""
    print("🧮 TESTING: build_model")
    print("=" * 50)
    
    problem_description = "Minimize total supply chain costs including transportation, inventory, and warehouse operations across 5 warehouses and 100 products"
    data_analysis = {"data_quality": "high", "features": ["demand", "costs", "capacity"]}
    model_type = "mixed_integer_programming"
    
    result = await build_model(problem_description, data_analysis, model_type)
    print(f"Problem Description: {problem_description}")
    print(f"Data Analysis: {data_analysis}")
    print(f"Model Type: {model_type}")
    print(f"Result: {json.dumps(result, indent=2)}")
    print()

async def test_solve_optimization():
    """Test optimization solving with detailed output"""
    print("⚡ TESTING: solve_optimization")
    print("=" * 50)
    
    model_specification = {
        "model_type": "mixed_integer_programming",
        "variables": 500,
        "constraints": 200,
        "objective": "minimize_total_cost"
    }
    solver_config = {"time_limit": 300, "solver": "CBC"}
    
    result = await solve_optimization(model_specification, solver_config)
    print(f"Model Specification: {model_specification}")
    print(f"Solver Config: {solver_config}")
    print(f"Result: {json.dumps(result, indent=2)}")
    print()

async def test_get_workflow_templates():
    """Test workflow templates with detailed output"""
    print("📋 TESTING: get_workflow_templates")
    print("=" * 50)
    
    result = await get_workflow_templates()
    print(f"Result: {json.dumps(result, indent=2)}")
    print()

async def main():
    """Run all individual tool tests"""
    print("🛠️ DcisionAI MCP Server - Individual Tools Test")
    print("=" * 60)
    print()
    
    try:
        await test_classify_intent()
        await test_analyze_data()
        await test_build_model()
        await test_solve_optimization()
        await test_get_workflow_templates()
        
        print("✅ All individual tool tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
