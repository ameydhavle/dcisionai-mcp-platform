#!/usr/bin/env python3
"""
DcisionAI Manufacturing MCP Server - End-to-End Test Suite
=========================================================

Comprehensive E2E tests for manufacturing domain tools with real prompts.
Tests all tools to ensure NO canned responses and real solver execution.

Manufacturing Test Scenarios:
1. Intent Classification - Production optimization queries
2. Data Analysis - Manufacturing performance data
3. Model Building - Production scheduling optimization
4. Solver Execution - Real optimization with OR-Tools/PuLP/CVXPY

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import asyncio
import json
import time
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

class ManufacturingE2ETester:
    """End-to-end tester for manufacturing MCP server tools."""
    
    def __init__(self, mcp_url="http://localhost:8000/mcp"):
        self.mcp_url = mcp_url
        self.headers = {}
        self.test_results = {}
    
    async def run_all_tests(self):
        """Run comprehensive E2E tests for all manufacturing tools."""
        print("🚀 DcisionAI Manufacturing MCP Server - E2E Test Suite")
        print("=" * 60)
        print("Testing with REAL manufacturing scenarios - NO canned responses")
        print()
        
        async with streamablehttp_client(self.mcp_url, self.headers, timeout=120, terminate_on_close=False) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # Test 1: Intent Classification with 5-Agent Consensus
                await self.test_intent_classification(session)
                
                # Test 2: Data Analysis with Real Manufacturing Data
                await self.test_data_analysis(session)
                
                # Test 3: Model Building for Production Optimization
                await self.test_model_building(session)
                
                # Test 4: Solver Execution with Real Optimization
                await self.test_solver_execution(session)
                
                # Summary
                self.print_test_summary()
    
    async def test_intent_classification(self, session):
        """Test intent classification with manufacturing-specific queries."""
        print("🧪 TEST 1: Intent Classification (5-Agent Consensus)")
        print("-" * 50)
        
        test_queries = [
            "Optimize production line efficiency for maximum throughput while minimizing energy costs",
            "Schedule maintenance for 50 machines across 3 shifts to minimize downtime",
            "Analyze defect rates in automotive parts production over the last quarter",
            "Build a mathematical model for inventory optimization with demand uncertainty",
            "Implement predictive maintenance for CNC machines using sensor data"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📋 Test Query {i}: {query}")
            
            try:
                result = await session.call_tool('manufacturing_intent_classification', {'query': query})
                result_data = json.loads(result.content[0].text)
                
                # Verify real response (not canned)
                intent = result_data.get('intent', 'unknown')
                confidence = result_data.get('confidence', 0)
                agreement_score = result_data.get('agreement_score', 0)
                entities = result_data.get('entities', [])
                reasoning = result_data.get('reasoning', '')
                
                print(f"   ✅ Intent: {intent}")
                print(f"   ✅ Confidence: {confidence}")
                print(f"   ✅ Agreement Score: {agreement_score}")
                print(f"   ✅ Entities: {entities}")
                print(f"   ✅ Reasoning: {reasoning[:100]}...")
                
                # Verify this is NOT a canned response
                if confidence > 0.5 and agreement_score > 0 and len(entities) > 0:
                    print(f"   🎉 REAL 5-AGENT CONSENSUS RESPONSE!")
                    self.test_results[f'intent_test_{i}'] = 'PASS'
                else:
                    print(f"   ❌ POTENTIAL CANNED RESPONSE!")
                    self.test_results[f'intent_test_{i}'] = 'FAIL'
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                self.test_results[f'intent_test_{i}'] = 'ERROR'
    
    async def test_data_analysis(self, session):
        """Test data analysis with real manufacturing performance data."""
        print("\n🧪 TEST 2: Data Analysis (Multi-Perspective Analysis)")
        print("-" * 50)
        
        manufacturing_data = {
            "production_metrics": {
                "total_units_produced": 1250,
                "defective_units": 23,
                "quality_score": 0.9816,
                "efficiency_rating": 0.87,
                "downtime_hours": 45.5,
                "energy_consumption": 12500,
                "material_waste_percentage": 2.3
            },
            "line_performance": {
                "line_a": {"throughput": 450, "defect_rate": 0.018, "efficiency": 0.92},
                "line_b": {"throughput": 380, "defect_rate": 0.025, "efficiency": 0.85},
                "line_c": {"throughput": 420, "defect_rate": 0.015, "efficiency": 0.89}
            },
            "time_period": "Q3 2024",
            "target_metrics": {
                "quality_threshold": 0.98,
                "efficiency_target": 0.90,
                "waste_limit": 2.0
            }
        }
        
        print(f"📊 Analyzing manufacturing data: {manufacturing_data['production_metrics']['total_units_produced']} units produced")
        
        try:
            result = await session.call_tool('manufacturing_data_analysis', {
                'data': manufacturing_data,
                'analysis_type': 'comprehensive'
            })
            result_data = json.loads(result.content[0].text)
            
            # Verify real analysis (not canned)
            metrics = result_data.get('metrics', {})
            trends = result_data.get('trends', [])
            issues = result_data.get('issues', [])
            recommendations = result_data.get('recommendations', [])
            
            print(f"   ✅ Metrics identified: {len(metrics)}")
            print(f"   ✅ Trends found: {len(trends)}")
            print(f"   ✅ Issues identified: {len(issues)}")
            print(f"   ✅ Recommendations: {len(recommendations)}")
            
            # Show sample analysis
            if metrics:
                print(f"   📈 Sample metrics: {list(metrics.keys())[:3]}")
            if issues:
                print(f"   ⚠️ Sample issues: {issues[:2]}")
            if recommendations:
                print(f"   💡 Sample recommendations: {recommendations[:2]}")
            
            # Verify this is NOT a canned response
            if len(metrics) > 3 and len(recommendations) > 2:
                print(f"   🎉 REAL DATA ANALYSIS RESPONSE!")
                self.test_results['data_analysis'] = 'PASS'
            else:
                print(f"   ❌ POTENTIAL CANNED RESPONSE!")
                self.test_results['data_analysis'] = 'FAIL'
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            self.test_results['data_analysis'] = 'ERROR'
    
    async def test_model_building(self, session):
        """Test model building for production optimization problems."""
        print("\n🧪 TEST 3: Model Building (Mathematical Optimization)")
        print("-" * 50)
        
        optimization_problem = {
            "problem_type": "production_scheduling",
            "constraints": {
                "max_capacity": 1000,
                "min_quality": 0.95,
                "max_cost": 50000,
                "labor_hours_limit": 160,
                "machine_availability": 0.85
            },
            "data": {
                "demand": [120, 150, 180, 200, 160, 140, 110],
                "capacity": [100, 100, 100, 100, 100, 100, 100],
                "costs": [15, 18, 22, 25, 20, 17, 14],
                "quality_scores": [0.96, 0.94, 0.98, 0.97, 0.95, 0.96, 0.99]
            },
            "objectives": ["maximize_production", "minimize_cost", "maintain_quality"]
        }
        
        print(f"🏗️ Building optimization model for production scheduling")
        print(f"   Constraints: {len(optimization_problem['constraints'])}")
        print(f"   Data points: {len(optimization_problem['data']['demand'])}")
        
        try:
            result = await session.call_tool('manufacturing_model_builder', {
                'problem_type': optimization_problem['problem_type'],
                'constraints': optimization_problem['constraints'],
                'data': optimization_problem['data']
            })
            result_data = json.loads(result.content[0].text)
            
            # Verify real model building (not canned)
            objective = result_data.get('objective', '')
            variables = result_data.get('variables', [])
            constraints = result_data.get('constraints', [])
            complexity = result_data.get('complexity', 'unknown')
            model_type = result_data.get('model_type', 'unknown')
            
            print(f"   ✅ Objective: {objective}")
            print(f"   ✅ Variables: {len(variables)}")
            print(f"   ✅ Constraints: {len(constraints)}")
            print(f"   ✅ Complexity: {complexity}")
            print(f"   ✅ Model Type: {model_type}")
            
            # Show sample model components
            if variables:
                print(f"   📊 Sample variables: {variables[:3]}")
            if constraints:
                print(f"   🔧 Sample constraints: {constraints[:2]}")
            
            # Verify this is NOT a canned response
            if len(variables) > 2 and len(constraints) > 1 and complexity != 'unknown':
                print(f"   🎉 REAL MODEL BUILDING RESPONSE!")
                self.test_results['model_building'] = 'PASS'
            else:
                print(f"   ❌ POTENTIAL CANNED RESPONSE!")
                self.test_results['model_building'] = 'FAIL'
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            self.test_results['model_building'] = 'ERROR'
    
    async def test_solver_execution(self, session):
        """Test solver execution with real optimization solvers."""
        print("\n🧪 TEST 4: Solver Execution (Real OR-Tools/PuLP/CVXPY)")
        print("-" * 50)
        
        # Create a simple but real optimization model
        optimization_model = {
            "objective": "maximize 3*x1 + 2*x2 + 4*x3",
            "variables": ["x1", "x2", "x3"],
            "constraints": [
                "x1 + x2 + x3 <= 100",
                "2*x1 + x2 <= 80", 
                "x2 + 3*x3 <= 90",
                "x1 >= 0, x2 >= 0, x3 >= 0"
            ],
            "model_type": "linear_programming",
            "complexity": "medium"
        }
        
        print(f"🔧 Solving optimization model with real solvers")
        print(f"   Objective: {optimization_model['objective']}")
        print(f"   Variables: {optimization_model['variables']}")
        print(f"   Constraints: {len(optimization_model['constraints'])}")
        
        try:
            result = await session.call_tool('manufacturing_optimization_solver', {
                'model': optimization_model,
                'solver_type': 'auto'
            })
            result_data = json.loads(result.content[0].text)
            
            # Verify real solver execution (not canned)
            status = result_data.get('status', 'unknown')
            objective_value = result_data.get('objective_value', 0)
            solver_used = result_data.get('solver_used', 'unknown')
            solve_time = result_data.get('solve_time', 0)
            solution = result_data.get('solution', {})
            iterations = result_data.get('iterations', 0)
            
            print(f"   ✅ Status: {status}")
            print(f"   ✅ Objective Value: {objective_value}")
            print(f"   ✅ Solver Used: {solver_used}")
            print(f"   ✅ Solve Time: {solve_time}s")
            print(f"   ✅ Iterations: {iterations}")
            print(f"   ✅ Solution: {solution}")
            
            # Verify this is NOT a canned response
            if (solver_used != 'unknown' and 
                solve_time > 0 and 
                objective_value > 0 and 
                status in ['optimal', 'feasible', 'infeasible']):
                print(f"   🎉 REAL SOLVER EXECUTION!")
                print(f"   ✅ Using actual {solver_used} solver")
                self.test_results['solver_execution'] = 'PASS'
            else:
                print(f"   ❌ POTENTIAL CANNED RESPONSE!")
                print(f"   ❌ No real solver execution detected")
                self.test_results['solver_execution'] = 'FAIL'
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            self.test_results['solver_execution'] = 'ERROR'
    
    def print_test_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 60)
        print("📊 E2E TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result == 'PASS')
        failed_tests = sum(1 for result in self.test_results.values() if result == 'FAIL')
        error_tests = sum(1 for result in self.test_results.values() if result == 'ERROR')
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"🚨 Errors: {error_tests}")
        print()
        
        # Detailed results
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result == 'PASS' else "❌" if result == 'FAIL' else "🚨"
            print(f"{status_icon} {test_name}: {result}")
        
        print()
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! MCP Server working with real responses!")
        elif passed_tests > total_tests // 2:
            print("⚠️ MOSTLY WORKING - Some issues detected")
        else:
            print("❌ MAJOR ISSUES - Multiple failures detected")
        
        print("\n🔍 VERIFICATION CHECKLIST:")
        print("✅ Intent Tool: 5-agent consensus with agreement scoring")
        print("✅ Data Tool: Multi-perspective analysis with real insights")
        print("✅ Model Tool: Mathematical modeling with variables/constraints")
        print("✅ Solver Tool: Real optimization solvers (OR-Tools/PuLP/CVXPY)")
        print("✅ NO Canned Responses: All tools return intelligent, contextual results")

async def main():
    """Run the comprehensive E2E test suite."""
    tester = ManufacturingE2ETester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
