#!/usr/bin/env python3
"""
Complete Manufacturing Optimization Workflow Test
===============================================

Test the complete 4-tool workflow: Intent → Data → Model → Solver
Simulates real-world manufacturing optimization scenarios.

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import sys
import os
import time
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

class WorkflowTester:
    """Test the complete manufacturing optimization workflow"""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        
    def test_scenario(self, scenario_name: str, user_query: str):
        """Test a complete workflow scenario"""
        print(f"\n{'='*80}")
        print(f"🧪 TESTING SCENARIO: {scenario_name}")
        print(f"{'='*80}")
        print(f"📝 User Query: {user_query}")
        
        scenario_start = time.time()
        scenario_results = {
            "scenario_name": scenario_name,
            "user_query": user_query,
            "stages": {},
            "overall_success": True,
            "total_time": 0
        }
        
        try:
            # Stage 1: Intent Analysis
            print(f"\n🧠 STAGE 1: Intent Analysis")
            intent_result = self._test_intent_stage(user_query)
            if intent_result:
                scenario_results["stages"]["intent"] = {
                    "success": True,
                    "primary_intent": intent_result.primary_intent,
                    "confidence": intent_result.confidence,
                    "objectives": intent_result.objectives
                }
            else:
                scenario_results["stages"]["intent"] = {"success": False}
                scenario_results["overall_success"] = False
                return scenario_results
            
            # Stage 2: Data Analysis
            print(f"\n📊 STAGE 2: Data Analysis")
            data_result = self._test_data_stage(user_query, intent_result)
            if data_result:
                scenario_results["stages"]["data"] = {
                    "success": True,
                    "analysis_id": data_result.analysis_id,
                    "extracted_entities": len(data_result.extracted_data_entities),
                    "missing_entities": len(data_result.missing_data_entities),
                    "industry_context": data_result.industry_context
                }
            else:
                scenario_results["stages"]["data"] = {"success": False}
                scenario_results["overall_success"] = False
                return scenario_results
            
            # Stage 3: Model Building
            print(f"\n🔧 STAGE 3: Model Building")
            model_result = self._test_model_stage(intent_result, data_result)
            if model_result:
                scenario_results["stages"]["model"] = {
                    "success": True,
                    "model_id": model_result.model_id,
                    "model_type": model_result.model_type.value,
                    "variables": len(model_result.decision_variables),
                    "constraints": len(model_result.constraints),
                    "objectives": len(model_result.objective_functions)
                }
            else:
                scenario_results["stages"]["model"] = {"success": False}
                scenario_results["overall_success"] = False
                return scenario_results
            
            # Stage 4: Solver Execution
            print(f"\n🏁 STAGE 4: Solver Execution")
            solver_result = self._test_solver_stage(model_result)
            if solver_result:
                scenario_results["stages"]["solver"] = {
                    "success": True,
                    "solver_used": solver_result.solver_type.value,
                    "status": solver_result.status.value,
                    "objective_value": solver_result.objective_value,
                    "solve_time": solver_result.solve_time
                }
            else:
                scenario_results["stages"]["solver"] = {"success": False}
                scenario_results["overall_success"] = False
                return scenario_results
            
            scenario_results["total_time"] = time.time() - scenario_start
            print(f"\n✅ SCENARIO COMPLETED: {scenario_name}")
            print(f"⏱️ Total Time: {scenario_results['total_time']:.2f}s")
            
            return scenario_results
            
        except Exception as e:
            print(f"\n❌ SCENARIO FAILED: {scenario_name}")
            print(f"Error: {e}")
            scenario_results["overall_success"] = False
            scenario_results["error"] = str(e)
            scenario_results["total_time"] = time.time() - scenario_start
            return scenario_results
    
    def _test_intent_stage(self, user_query: str):
        """Test intent analysis stage"""
        try:
            from mcp_server.tools.manufacturing.intent.DcisionAI_Intent_Tool import create_intent_tool
            
            start_time = time.time()
            intent_tool = create_intent_tool()
            intent_result = intent_tool.classify_intent(user_query)
            execution_time = time.time() - start_time
            
            print(f"   ✅ Intent: {intent_result.primary_intent}")
            print(f"   📊 Confidence: {intent_result.confidence:.2f}")
            print(f"   🎯 Objectives: {intent_result.objectives}")
            print(f"   ⏱️ Time: {execution_time:.2f}s")
            
            return intent_result
            
        except Exception as e:
            print(f"   ❌ Intent Stage Failed: {e}")
            return None
    
    def _test_data_stage(self, user_query: str, intent_result):
        """Test data analysis stage"""
        try:
            from mcp_server.tools.manufacturing.data.DcisionAI_Data_Tool import create_data_tool
            
            start_time = time.time()
            data_tool = create_data_tool()
            data_result = data_tool.analyze_data_requirements(user_query, {
                "primary_intent": intent_result.primary_intent,
                "confidence": intent_result.confidence,
                "objectives": intent_result.objectives
            }, "workflow_test")
            execution_time = time.time() - start_time
            
            print(f"   ✅ Analysis ID: {data_result.analysis_id}")
            print(f"   🏭 Industry: {data_result.industry_context}")
            print(f"   📋 Extracted: {len(data_result.extracted_data_entities)} entities")
            print(f"   ❌ Missing: {len(data_result.missing_data_entities)} entities")
            print(f"   ⏱️ Time: {execution_time:.2f}s")
            
            return data_result
            
        except Exception as e:
            print(f"   ❌ Data Stage Failed: {e}")
            return None
    
    def _test_model_stage(self, intent_result, data_result):
        """Test model building stage"""
        try:
            from mcp_server.tools.manufacturing.model.DcisionAI_Model_Builder import create_model_builder_tool
            
            start_time = time.time()
            model_builder = create_model_builder_tool()
            model_result = model_builder.build_optimization_model({
                "primary_intent": intent_result.primary_intent.value,
                "confidence": intent_result.confidence,
                "objectives": intent_result.objectives
            }, {
                "extracted_data_entities": data_result.extracted_data_entities,
                "missing_data_entities": [missing.entity_name for missing in data_result.missing_data_entities],
                "sample_data_generated": data_result.sample_data_generated,
                "industry_context": data_result.industry_context
            }, "workflow_test")
            execution_time = time.time() - start_time
            
            print(f"   ✅ Model ID: {model_result.model_id}")
            print(f"   📛 Type: {model_result.model_type.value}")
            print(f"   🔢 Variables: {len(model_result.decision_variables)}")
            print(f"   ⚖️ Constraints: {len(model_result.constraints)}")
            print(f"   ⏱️ Time: {execution_time:.2f}s")
            
            return model_result
            
        except Exception as e:
            print(f"   ❌ Model Stage Failed: {e}")
            return None
    
    def _test_solver_stage(self, model_result):
        """Test solver execution stage"""
        try:
            from mcp_server.tools.manufacturing.solver.DcisionAI_Solver_Tool import create_solver_tool
            
            start_time = time.time()
            solver_tool = create_solver_tool()
            solver_result = solver_tool.solve_optimization_model(model_result, max_solve_time=60.0)
            execution_time = time.time() - start_time
            
            print(f"   ✅ Solver: {solver_result.solver_type.value}")
            print(f"   📈 Objective: {solver_result.objective_value}")
            print(f"   ✅ Status: {solver_result.status.value}")
            print(f"   ⏱️ Time: {execution_time:.2f}s")
            
            return solver_result
            
        except Exception as e:
            print(f"   ❌ Solver Stage Failed: {e}")
            return None
    
    def run_single_scenario(self):
        """Run single test scenario for consensus intent"""
        print("🚀 COMPLETE MANUFACTURING OPTIMIZATION WORKFLOW TEST")
        print("=" * 80)
        print("🧠 Intent → 📊 Data → 🔧 Model → 🏁 Solver")
        print("=" * 80)
        
        self.start_time = time.time()
        
        # Single test scenario for consensus intent
        scenario = {
            "name": "Production Optimization",
            "query": "I need to optimize my production schedule to minimize costs while meeting customer demand for our automotive parts manufacturing"
        }
        
        # Run single scenario
        result = self.test_scenario(scenario["name"], scenario["query"])
        self.results[scenario["name"]] = result
        
        # Generate summary report
        self._generate_summary_report()
    
    def _generate_summary_report(self):
        """Generate comprehensive summary report"""
        total_time = time.time() - self.start_time
        
        print(f"\n{'='*80}")
        print("📊 WORKFLOW TEST SUMMARY REPORT")
        print(f"{'='*80}")
        
        successful_scenarios = 0
        total_scenarios = len(self.results)
        
        for scenario_name, result in self.results.items():
            if result["overall_success"]:
                successful_scenarios += 1
                print(f"✅ {scenario_name}: SUCCESS ({result['total_time']:.2f}s)")
            else:
                print(f"❌ {scenario_name}: FAILED ({result['total_time']:.2f}s)")
                if "error" in result:
                    print(f"   Error: {result['error']}")
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Scenarios: {total_scenarios}")
        print(f"   Successful: {successful_scenarios}")
        print(f"   Failed: {total_scenarios - successful_scenarios}")
        print(f"   Success Rate: {(successful_scenarios/total_scenarios)*100:.1f}%")
        print(f"   Total Test Time: {total_time:.2f}s")
        
        if successful_scenarios == total_scenarios:
            print(f"\n🎉 WORKFLOW TEST PASSED!")
            print(f"🚀 Manufacturing optimization workflow is production-ready!")
        else:
            print(f"\n⚠️ Workflow test failed - review errors above")
        
        # Save detailed results
        self._save_detailed_results()
    
    def _save_detailed_results(self):
        """Save detailed test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"workflow_test_results_{timestamp}.json"
        
        # Convert results to serializable format
        serializable_results = {}
        for scenario_name, result in self.results.items():
            serializable_results[scenario_name] = {
                "scenario_name": result["scenario_name"],
                "user_query": result["user_query"],
                "overall_success": result["overall_success"],
                "total_time": result["total_time"],
                "stages": result["stages"]
            }
            if "error" in result:
                serializable_results[scenario_name]["error"] = result["error"]
        
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: {filename}")

def main():
    """Main test function"""
    tester = WorkflowTester()
    
    try:
        tester.run_single_scenario()
    except KeyboardInterrupt:
        print("\n👋 Workflow test interrupted")
    except Exception as e:
        print(f"\n❌ Workflow test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
