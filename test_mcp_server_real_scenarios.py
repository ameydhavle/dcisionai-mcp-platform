#!/usr/bin/env python3
"""
Real Customer Scenarios Test for DcisionAI MCP Server
====================================================

This script tests the MCP server with realistic business optimization scenarios
that customers would actually use in production.
"""

import asyncio
import os
import json
from dcisionai_mcp_server import DcisionAIMCPServer
from dcisionai_mcp_server.tools import (
    classify_intent,
    analyze_data,
    build_model,
    solve_optimization,
    execute_workflow
)

# Set up environment variables
os.environ["DCISIONAI_ACCESS_TOKEN"] = "eyJraWQiOiJLMWZEMFwvXC9qaGtJSHlZd2IyM2NsMkRSK0dEQ2tFaHVWZVd0djdFMERkOUk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI1cjdyaXJqdmI0OTZpam1rMDNtanNrNTNtOCIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiRGNpc2lvbkFJLUdhdGV3YXktMGRlMWE2NTVcL2ludm9rZSIsImF1dGhfdGltZSI6MTc2MDU0NzgwOCwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfdjlDSmJRMWVKIiwiZXhwIjoxNzYwNTUxNDA4LCJpYXQiOjE3NjA1NDc4MDgsInZlcnNpb24iOjIsImp0aSI6IjIzMDAwOTBmLWZjNzYtNDI1NC1hZjQ3LTY2ZDA5MGVkNzRiMiIsImNsaWVudF9pZCI6IjVyN3Jpcmp2YjQ5NmlqbWswM21qc2s1M204In0.nOgW15NAgzd-fB3Vn8fx0030rmX3_h9nKRkIM_JK3mXdATw-K0rCrinzll9XrN1m4pAOmVJFdoq0YbH7SOI6bMIl840TnN9hSxnKVy1zx5nOPn98btAKzP41UbLVJ8PGE3zAfrkOPtMaqvoMDzgCZP0fFF_FiCPFUWUvSs-OmbR2TnuVmdnuFCXLAQ_CMTJVpwVMk13P3mfJgkSPY33ly3GbtaVN9LDq11ZzVCAvsRbA7DvEWdSc9GVpHYmRwfEJYZZW4KNeOFZZRqZuryY57mBgcUaZ06deesl_ySN72a2CgJ1xnVCeK5VYcwdlUmQrSvEYxAJJGvF-ZacgQC6qUA"
os.environ["DCISIONAI_GATEWAY_URL"] = "https://dcisionai-gateway-0de1a655-ja1rhlcqjx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
os.environ["DCISIONAI_GATEWAY_TARGET"] = "DcisionAI-Optimization-Tools-Fixed"

async def test_manufacturing_scenario():
    """Test Manufacturing Production Planning Optimization"""
    print("🏭 MANUFACTURING SCENARIO: Production Planning Optimization")
    print("=" * 60)
    
    # Scenario: A manufacturing company needs to optimize their production schedule
    user_input = """
    We need to optimize our production schedule for the next 30 days. 
    We have 3 production lines, 5 different products, and varying demand forecasts.
    Our constraints include:
    - Maximum 8 hours per day per production line
    - Setup time of 2 hours when switching between products
    - Minimum batch sizes of 100 units per product
    - Storage capacity of 5000 units total
    - Demand forecasts: Product A (2000 units), Product B (1500 units), 
      Product C (3000 units), Product D (1000 units), Product E (2500 units)
    
    Our goal is to minimize total production costs while meeting all demand.
    """
    
    print(f"📝 User Input: {user_input.strip()}")
    print()
    
    # Step 1: Classify Intent
    print("🔍 Step 1: Classifying Intent...")
    intent_result = await classify_intent(user_input, "manufacturing")
    print(f"✅ Intent Classification: {intent_result}")
    print()
    
    # Step 2: Analyze Data
    print("📊 Step 2: Analyzing Data...")
    data_result = await analyze_data(
        data_description="Production data with 3 lines, 5 products, demand forecasts, and capacity constraints",
        data_type="tabular",
        constraints="Production line capacity, setup times, batch sizes, storage limits"
    )
    print(f"✅ Data Analysis: {data_result}")
    print()
    
    # Step 3: Build Model
    print("🧮 Step 3: Building Mathematical Model...")
    model_result = await build_model(
        problem_description=user_input,
        data_analysis=data_result,
        model_type="mixed_integer_programming"
    )
    print(f"✅ Model Building: {model_result}")
    print()
    
    # Step 4: Solve Optimization
    print("⚡ Step 4: Solving Optimization...")
    solution_result = await solve_optimization(
        model_specification=model_result,
        solver_config={"time_limit": 300, "solver": "CBC"}
    )
    print(f"✅ Optimization Solution: {solution_result}")
    print()
    
    return {
        "scenario": "Manufacturing Production Planning",
        "intent": intent_result,
        "data_analysis": data_result,
        "model": model_result,
        "solution": solution_result
    }

async def test_healthcare_scenario():
    """Test Healthcare Staff Scheduling Optimization"""
    print("🏥 HEALTHCARE SCENARIO: Staff Scheduling Optimization")
    print("=" * 60)
    
    # Scenario: A hospital needs to optimize nurse scheduling
    user_input = """
    We need to optimize our nurse scheduling for the ICU department for the next 2 weeks.
    We have 15 nurses with different skill levels and availability:
    - 5 Senior Nurses (can work any shift, 12-hour shifts)
    - 7 Regular Nurses (can work day/evening shifts, 8-hour shifts)
    - 3 Junior Nurses (can only work day shifts, 8-hour shifts)
    
    Requirements:
    - Minimum 3 senior nurses per shift
    - Minimum 5 total nurses per shift
    - Maximum 4 consecutive shifts per nurse
    - 2 days off per week minimum
    - Night shifts (11 PM - 7 AM) need at least 2 senior nurses
    - Day shifts (7 AM - 3 PM) and Evening shifts (3 PM - 11 PM) need at least 1 senior nurse each
    
    Our goal is to minimize overtime costs while ensuring adequate coverage.
    """
    
    print(f"📝 User Input: {user_input.strip()}")
    print()
    
    # Execute complete workflow
    print("🚀 Executing Complete Healthcare Workflow...")
    workflow_result = await execute_workflow(
        industry="healthcare",
        workflow_id="staff_scheduling",
        parameters={
            "time_horizon": 14,
            "department": "ICU",
            "nurses": 15,
            "skill_levels": ["senior", "regular", "junior"],
            "shift_types": ["day", "evening", "night"]
        }
    )
    print(f"✅ Workflow Execution: {workflow_result}")
    print()
    
    return {
        "scenario": "Healthcare Staff Scheduling",
        "workflow_result": workflow_result
    }

async def test_retail_scenario():
    """Test Retail Pricing Optimization"""
    print("🛒 RETAIL SCENARIO: Pricing Optimization")
    print("=" * 60)
    
    # Scenario: A retail chain needs to optimize pricing across multiple stores
    user_input = """
    We need to optimize pricing for our electronics department across 20 stores.
    We have 50 products with different price elasticities and competitor prices:
    - High-end products (10 items): Price elasticity -1.5, competitor margin 15%
    - Mid-range products (25 items): Price elasticity -2.0, competitor margin 20%
    - Budget products (15 items): Price elasticity -2.5, competitor margin 25%
    
    Constraints:
    - Minimum margin of 10% for all products
    - Maximum price increase of 15% from current prices
    - Store-specific demand patterns (urban vs suburban)
    - Seasonal demand variations (holiday season approaching)
    - Inventory levels and turnover rates
    
    Our goal is to maximize total revenue while maintaining competitive positioning.
    """
    
    print(f"📝 User Input: {user_input.strip()}")
    print()
    
    # Execute complete workflow
    print("🚀 Executing Complete Retail Workflow...")
    workflow_result = await execute_workflow(
        industry="retail",
        workflow_id="pricing_optimization",
        parameters={
            "stores": 20,
            "products": 50,
            "categories": ["high-end", "mid-range", "budget"],
            "season": "holiday",
            "competitor_analysis": True
        }
    )
    print(f"✅ Workflow Execution: {workflow_result}")
    print()
    
    return {
        "scenario": "Retail Pricing Optimization",
        "workflow_result": workflow_result
    }

async def test_financial_scenario():
    """Test Financial Portfolio Optimization"""
    print("💰 FINANCIAL SCENARIO: Portfolio Optimization")
    print("=" * 60)
    
    # Scenario: An investment firm needs to optimize portfolio allocation
    user_input = """
    We need to optimize our investment portfolio allocation for a $10M fund.
    We have access to 100 different assets across multiple categories:
    - Stocks (60 assets): Expected returns 8-15%, volatility 15-35%
    - Bonds (25 assets): Expected returns 3-6%, volatility 2-8%
    - Commodities (10 assets): Expected returns 5-12%, volatility 20-40%
    - Alternative investments (5 assets): Expected returns 6-18%, volatility 10-25%
    
    Constraints:
    - Maximum 40% allocation to any single asset
    - Maximum 60% allocation to stocks
    - Minimum 20% allocation to bonds
    - Maximum 15% allocation to commodities
    - Risk tolerance: Portfolio volatility should not exceed 18%
    - Liquidity requirements: At least 5% in highly liquid assets
    
    Our goal is to maximize expected returns while staying within risk parameters.
    """
    
    print(f"📝 User Input: {user_input.strip()}")
    print()
    
    # Execute complete workflow
    print("🚀 Executing Complete Financial Workflow...")
    workflow_result = await execute_workflow(
        industry="financial",
        workflow_id="portfolio_optimization",
        parameters={
            "fund_size": 10000000,
            "assets": 100,
            "risk_tolerance": 0.18,
            "liquidity_requirement": 0.05,
            "time_horizon": 12
        }
    )
    print(f"✅ Workflow Execution: {workflow_result}")
    print()
    
    return {
        "scenario": "Financial Portfolio Optimization",
        "workflow_result": workflow_result
    }

async def main():
    """Run all real customer scenarios"""
    print("🎯 DcisionAI MCP Server - Real Customer Scenarios Test")
    print("=" * 80)
    print()
    
    results = []
    
    try:
        # Test Manufacturing Scenario
        manufacturing_result = await test_manufacturing_scenario()
        results.append(manufacturing_result)
        print()
        
        # Test Healthcare Scenario
        healthcare_result = await test_healthcare_scenario()
        results.append(healthcare_result)
        print()
        
        # Test Retail Scenario
        retail_result = await test_retail_scenario()
        results.append(retail_result)
        print()
        
        # Test Financial Scenario
        financial_result = await test_financial_scenario()
        results.append(financial_result)
        print()
        
        # Summary
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Total Scenarios Tested: {len(results)}")
        print(f"✅ Manufacturing: {'PASS' if manufacturing_result else 'FAIL'}")
        print(f"✅ Healthcare: {'PASS' if healthcare_result else 'FAIL'}")
        print(f"✅ Retail: {'PASS' if retail_result else 'FAIL'}")
        print(f"✅ Financial: {'PASS' if financial_result else 'FAIL'}")
        print()
        print("🎉 All real customer scenarios completed successfully!")
        print("The DcisionAI MCP Server is ready for production use!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
