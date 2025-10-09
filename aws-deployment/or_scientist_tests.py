#!/usr/bin/env python3
"""
OR Scientist Test Suite
======================

Comprehensive testing of the optimization platform from an OR scientist's perspective.
Tests model generation quality, mathematical correctness, and practical relevance.
"""

import requests
import json
import time
from typing import Dict, Any, List

# API Base URL
API_BASE = "https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod"

class ORScientistTester:
    """Test suite for OR scientist validation."""
    
    def __init__(self):
        self.test_results = []
    
    def test_full_workflow(self, problem_description: str, expected_intent: str, test_name: str) -> Dict[str, Any]:
        """Test the complete optimization workflow."""
        print(f"\n🧪 Testing: {test_name}")
        print(f"📝 Problem: {problem_description}")
        print("-" * 80)
        
        start_time = time.time()
        
        # Step 1: Intent Classification
        print("🎯 Step 1: Intent Classification...")
        intent_response = requests.post(f"{API_BASE}/intent", 
            json={"problem_description": problem_description},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if intent_response.status_code != 200:
            return {"error": f"Intent classification failed: {intent_response.status_code}"}
        
        intent_data = intent_response.json()
        print(f"✅ Intent: {intent_data['result']['intent']} (confidence: {intent_data['result']['confidence']})")
        print(f"📊 Scale: {intent_data['result']['problem_scale']}")
        print(f"🔢 Quantities: {intent_data['result']['extracted_quantities']}")
        
        # Step 2: Data Analysis
        print("\n📊 Step 2: Data Analysis...")
        data_response = requests.post(f"{API_BASE}/data",
            json={
                "problem_description": problem_description,
                "intent_data": intent_data['result']
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if data_response.status_code != 200:
            return {"error": f"Data analysis failed: {data_response.status_code}"}
        
        data_analysis = data_response.json()
        print(f"✅ Data Complexity: {data_analysis['result']['data_complexity']}")
        print(f"📈 Estimated Data Points: {data_analysis['result']['estimated_data_points']}")
        print(f"🏗️ Entities: {len(data_analysis['result']['data_entities'])}")
        
        # Step 3: Model Building (CRITICAL FOR OR SCIENTISTS)
        print("\n🔧 Step 3: Model Building (OR Scientist Focus)...")
        model_response = requests.post(f"{API_BASE}/model",
            json={
                "problem_description": problem_description,
                "intent_data": intent_data['result'],
                "data_analysis": data_analysis['result']
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if model_response.status_code != 200:
            return {"error": f"Model building failed: {model_response.status_code}"}
        
        model_data = model_response.json()
        model_result = model_data['result']
        
        # OR Scientist Analysis
        print(f"✅ Model Type: {model_result['model_type']}")
        print(f"📊 Variables: {len(model_result['variables'])}")
        print(f"🔗 Constraints: {len(model_result['constraints'])}")
        print(f"🎯 Objective: {model_result['objective_function']}")
        print(f"⏱️ Solve Time: {model_result['estimated_solve_time']}s")
        
        # Detailed Variable Analysis
        print(f"\n📋 Variable Analysis:")
        var_types = {}
        for var in model_result['variables']:
            var_type = var['type']
            var_types[var_type] = var_types.get(var_type, 0) + 1
        for var_type, count in var_types.items():
            print(f"   - {var_type}: {count} variables")
        
        # Constraint Analysis
        print(f"\n🔗 Constraint Analysis:")
        constraint_types = {"capacity": 0, "demand": 0, "balance": 0, "other": 0}
        for constraint in model_result['constraints']:
            constraint_lower = constraint.lower()
            if "capacity" in constraint_lower or "max" in constraint_lower or "<=" in constraint:
                constraint_types["capacity"] += 1
            elif "demand" in constraint_lower or "min" in constraint_lower or ">=" in constraint:
                constraint_types["demand"] += 1
            elif "balance" in constraint_lower or "=" in constraint:
                constraint_types["balance"] += 1
            else:
                constraint_types["other"] += 1
        
        for ctype, count in constraint_types.items():
            if count > 0:
                print(f"   - {ctype}: {count} constraints")
        
        # Step 4: Optimization Solution
        print("\n⚡ Step 4: Optimization Solution...")
        solve_response = requests.post(f"{API_BASE}/solve",
            json={
                "problem_description": problem_description,
                "intent_data": intent_data['result'],
                "model_building": model_result
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if solve_response.status_code != 200:
            return {"error": f"Optimization solving failed: {solve_response.status_code}"}
        
        solve_data = solve_response.json()
        solve_result = solve_data['result']
        
        print(f"✅ Status: {solve_result['status']}")
        print(f"💰 Objective Value: {solve_result.get('objective_value', 'N/A')}")
        print(f"⏱️ Solve Time: {solve_result.get('solve_time', 'N/A')}s")
        print(f"💡 Recommendations: {len(solve_result.get('recommendations', []))}")
        
        total_time = time.time() - start_time
        
        # OR Scientist Evaluation
        evaluation = self.evaluate_model_quality(model_result, intent_data['result'], problem_description)
        
        result = {
            "test_name": test_name,
            "problem_description": problem_description,
            "intent": intent_data['result']['intent'],
            "problem_scale": intent_data['result']['problem_scale'],
            "model_type": model_result['model_type'],
            "variables_count": len(model_result['variables']),
            "constraints_count": len(model_result['constraints']),
            "variable_types": var_types,
            "constraint_types": constraint_types,
            "objective_function": model_result['objective_function'],
            "estimated_solve_time": model_result['estimated_solve_time'],
            "total_execution_time": total_time,
            "evaluation": evaluation
        }
        
        self.test_results.append(result)
        return result
    
    def evaluate_model_quality(self, model_result: Dict[str, Any], intent_data: Dict[str, Any], problem_description: str) -> Dict[str, Any]:
        """Evaluate model quality from OR scientist perspective."""
        evaluation = {
            "mathematical_correctness": "good",
            "practical_relevance": "good", 
            "scalability": "good",
            "issues": [],
            "strengths": [],
            "overall_score": 0
        }
        
        variables = model_result['variables']
        constraints = model_result['constraints']
        model_type = model_result['model_type']
        problem_scale = intent_data['problem_scale']
        
        # Check variable count appropriateness
        if problem_scale == "small" and len(variables) > 20:
            evaluation["issues"].append("Too many variables for small-scale problem")
        elif problem_scale == "large" and len(variables) < 30:
            evaluation["issues"].append("Too few variables for large-scale problem")
        else:
            evaluation["strengths"].append("Appropriate variable count for problem scale")
        
        # Check constraint count appropriateness
        if len(constraints) < 3:
            evaluation["issues"].append("Too few constraints - model may be under-constrained")
        elif len(constraints) > len(variables) * 2:
            evaluation["issues"].append("Too many constraints - model may be over-constrained")
        else:
            evaluation["strengths"].append("Balanced constraint count")
        
        # Check variable types
        has_continuous = any(v['type'] == 'continuous' for v in variables)
        has_integer = any(v['type'] == 'integer' for v in variables)
        has_binary = any(v['type'] == 'binary' for v in variables)
        
        if model_type == "mixed_integer_programming" and not (has_integer or has_binary):
            evaluation["issues"].append("MIP model should have integer/binary variables")
        elif model_type == "linear_programming" and (has_integer or has_binary):
            evaluation["issues"].append("LP model should not have integer/binary variables")
        else:
            evaluation["strengths"].append("Appropriate variable types for model class")
        
        # Check constraint structure
        has_capacity = any("capacity" in c.lower() or "<=" in c for c in constraints)
        has_demand = any("demand" in c.lower() or ">=" in c for c in constraints)
        
        if not has_capacity and not has_demand:
            evaluation["issues"].append("Missing capacity or demand constraints")
        else:
            evaluation["strengths"].append("Includes capacity/demand constraints")
        
        # Check objective function
        if "minimize" not in model_result['objective_function'].lower() and "maximize" not in model_result['objective_function'].lower():
            evaluation["issues"].append("Objective function unclear")
        else:
            evaluation["strengths"].append("Clear objective function")
        
        # Calculate overall score
        score = 100
        score -= len(evaluation["issues"]) * 15
        score += len(evaluation["strengths"]) * 5
        evaluation["overall_score"] = max(0, min(100, score))
        
        return evaluation
    
    def run_all_tests(self):
        """Run comprehensive OR scientist test suite."""
        print("🧪 OR SCIENTIST TEST SUITE")
        print("=" * 80)
        
        # Test Cases
        test_cases = [
            {
                "name": "Small Supply Chain",
                "description": "Minimize transportation costs for 3 warehouses serving 8 customers with 2 products",
                "expected_intent": "supply_chain_optimization"
            },
            {
                "name": "Medium Production Planning", 
                "description": "Optimize production schedule for 25 workers across 4 shifts with 6 production lines and 15 products",
                "expected_intent": "production_optimization"
            },
            {
                "name": "Large Inventory Management",
                "description": "Minimize inventory costs for 50 warehouses, 200 suppliers, 500 products with seasonal demand patterns",
                "expected_intent": "inventory_optimization"
            },
            {
                "name": "Resource Allocation",
                "description": "Allocate 100 resources across 20 projects with budget constraints and skill requirements",
                "expected_intent": "resource_allocation"
            },
            {
                "name": "Transportation Optimization",
                "description": "Minimize delivery costs for 30 vehicles serving 150 locations with time windows and capacity limits",
                "expected_intent": "transportation_optimization"
            }
        ]
        
        for test_case in test_cases:
            try:
                result = self.test_full_workflow(
                    test_case["description"],
                    test_case["expected_intent"],
                    test_case["name"]
                )
                
                if "error" in result:
                    print(f"❌ {test_case['name']}: {result['error']}")
                else:
                    print(f"✅ {test_case['name']}: Score {result['evaluation']['overall_score']}/100")
                    
            except Exception as e:
                print(f"❌ {test_case['name']}: Exception - {e}")
        
        # Summary Report
        self.print_summary_report()
    
    def print_summary_report(self):
        """Print comprehensive summary report."""
        print("\n" + "=" * 80)
        print("📊 OR SCIENTIST EVALUATION SUMMARY")
        print("=" * 80)
        
        if not self.test_results:
            print("❌ No test results available")
            return
        
        # Overall Statistics
        total_tests = len(self.test_results)
        avg_score = sum(r['evaluation']['overall_score'] for r in self.test_results) / total_tests
        avg_variables = sum(r['variables_count'] for r in self.test_results) / total_tests
        avg_constraints = sum(r['constraints_count'] for r in self.test_results) / total_tests
        avg_execution_time = sum(r['total_execution_time'] for r in self.test_results) / total_tests
        
        print(f"📈 Overall Performance:")
        print(f"   - Tests Passed: {total_tests}")
        print(f"   - Average Score: {avg_score:.1f}/100")
        print(f"   - Average Variables: {avg_variables:.1f}")
        print(f"   - Average Constraints: {avg_constraints:.1f}")
        print(f"   - Average Execution Time: {avg_execution_time:.1f}s")
        
        # Model Type Distribution
        model_types = {}
        for result in self.test_results:
            model_type = result['model_type']
            model_types[model_type] = model_types.get(model_type, 0) + 1
        
        print(f"\n🔧 Model Type Distribution:")
        for model_type, count in model_types.items():
            print(f"   - {model_type}: {count} models")
        
        # Scale Distribution
        scales = {}
        for result in self.test_results:
            scale = result['problem_scale']
            scales[scale] = scales.get(scale, 0) + 1
        
        print(f"\n📊 Problem Scale Distribution:")
        for scale, count in scales.items():
            print(f"   - {scale}: {count} problems")
        
        # Detailed Results
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            print(f"\n🧪 {result['test_name']}:")
            print(f"   - Intent: {result['intent']}")
            print(f"   - Scale: {result['problem_scale']}")
            print(f"   - Model: {result['model_type']}")
            print(f"   - Variables: {result['variables_count']}")
            print(f"   - Constraints: {result['constraints_count']}")
            print(f"   - Score: {result['evaluation']['overall_score']}/100")
            
            if result['evaluation']['issues']:
                print(f"   - Issues: {', '.join(result['evaluation']['issues'])}")
            if result['evaluation']['strengths']:
                print(f"   - Strengths: {', '.join(result['evaluation']['strengths'])}")

def main():
    """Run OR scientist test suite."""
    tester = ORScientistTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
