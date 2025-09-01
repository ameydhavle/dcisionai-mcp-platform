#!/usr/bin/env python3
"""
Performance Optimization for Manufacturing Optimization Workflow
=============================================================

Fine-tune response times and identify bottlenecks in the 4-tool workflow.
Optimize for production deployment with minimal latency.

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import sys
import os
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class PerformanceOptimizer:
    """Optimize performance of manufacturing optimization workflow"""
    
    def __init__(self):
        self.performance_data = {}
        self.optimization_results = {}
        
    def benchmark_tool_performance(self, tool_name: str, iterations: int = 5):
        """Benchmark individual tool performance"""
        print(f"\n⚡ BENCHMARKING {tool_name.upper()}")
        print("=" * 60)
        
        execution_times = []
        success_count = 0
        
        for i in range(iterations):
            print(f"   Iteration {i+1}/{iterations}...")
            
            try:
                start_time = time.time()
                
                if tool_name == "intent":
                    result = self._benchmark_intent_tool()
                elif tool_name == "data":
                    result = self._benchmark_data_tool()
                elif tool_name == "model":
                    result = self._benchmark_model_tool()
                elif tool_name == "solver":
                    result = self._benchmark_solver_tool()
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                execution_time = time.time() - start_time
                execution_times.append(execution_time)
                success_count += 1
                
                print(f"   ✅ Success: {execution_time:.2f}s")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        # Calculate statistics
        if execution_times:
            stats = {
                "tool_name": tool_name,
                "iterations": iterations,
                "success_count": success_count,
                "success_rate": success_count / iterations,
                "execution_times": execution_times,
                "mean_time": statistics.mean(execution_times),
                "median_time": statistics.median(execution_times),
                "min_time": min(execution_times),
                "max_time": max(execution_times),
                "std_dev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            }
            
            print(f"\n📊 {tool_name.upper()} PERFORMANCE STATS:")
            print(f"   Success Rate: {stats['success_rate']:.1%}")
            print(f"   Mean Time: {stats['mean_time']:.2f}s")
            print(f"   Median Time: {stats['median_time']:.2f}s")
            print(f"   Min Time: {stats['min_time']:.2f}s")
            print(f"   Max Time: {stats['max_time']:.2f}s")
            print(f"   Std Dev: {stats['std_dev']:.2f}s")
            
            self.performance_data[tool_name] = stats
            return stats
        else:
            print(f"\n❌ {tool_name.upper()} BENCHMARK FAILED")
            return None
    
    def _benchmark_intent_tool(self):
        """Benchmark intent tool"""
        from mcp_server.tools.manufacturing.intent.DcisionAI_Intent_Tool import create_intent_tool
        
        intent_tool = create_intent_tool()
        return intent_tool.analyze_intent(
            "I need to optimize my production schedule to minimize costs while meeting customer demand",
            "perf_test"
        )
    
    def _benchmark_data_tool(self):
        """Benchmark data tool"""
        from mcp_server.tools.manufacturing.data.DcisionAI_Data_Tool import create_data_tool
        
        data_tool = create_data_tool()
        return data_tool.analyze_data_requirements(
            "I need to optimize my production schedule to minimize costs while meeting customer demand",
            {
                "primary_intent": "production_optimization",
                "confidence": 0.9,
                "objectives": ["minimize_costs", "meet_demand"]
            },
            "perf_test"
        )
    
    def _benchmark_model_tool(self):
        """Benchmark model tool"""
        from mcp_server.tools.manufacturing.model.DcisionAI_Model_Builder import create_model_builder_tool
        
        model_builder = create_model_builder_tool()
        return model_builder.build_optimization_model(
            {
                "primary_intent": "production_optimization",
                "confidence": 0.9,
                "objectives": ["minimize_costs", "meet_demand"]
            },
            {
                "extracted_data_entities": ["production_capacity", "demand_forecast"],
                "missing_data_entities": ["unit_costs"],
                "sample_data_generated": {
                    "production_capacity": {"Line_A": 100, "Line_B": 150},
                    "demand_forecast": {"Product_A": 500, "Product_B": 300}
                },
                "industry_context": "Automotive manufacturing"
            },
            "perf_test"
        )
    
    def _benchmark_solver_tool(self):
        """Benchmark solver tool"""
        from mcp_server.tools.manufacturing.solver.DcisionAI_Solver_Tool import create_solver_tool
        
        # Create a simple test model
        from mcp_server.tools.manufacturing.solver.DcisionAI_Solver_Tool import OptimizationModel
        
        test_model = OptimizationModel(
            model_id="perf_test_model",
            model_name="Performance Test Model",
            model_type="linear_programming",
            decision_variables=[
                {"name": "x1", "variable_type": "continuous", "bounds": (0, None)},
                {"name": "x2", "variable_type": "continuous", "bounds": (0, None)}
            ],
            constraints=[
                {"name": "capacity", "expression": "x1 + x2 <= 100", "sense": "<=", "rhs_value": 100}
            ],
            objective_functions=[
                {"name": "minimize_cost", "sense": "minimize", "expression": "10*x1 + 8*x2"}
            ],
            data_schema={},
            compatible_solvers=["or_tools_glop"],
            recommended_solver="or_tools_glop"
        )
        
        solver_tool = create_solver_tool()
        return solver_tool.solve_optimization_model(test_model, max_solve_time=30.0)
    
    def benchmark_workflow_performance(self, iterations: int = 3):
        """Benchmark complete workflow performance"""
        print(f"\n🚀 BENCHMARKING COMPLETE WORKFLOW")
        print("=" * 60)
        
        workflow_times = []
        stage_times = {
            "intent": [],
            "data": [],
            "model": [],
            "solver": []
        }
        
        for i in range(iterations):
            print(f"   Workflow Iteration {i+1}/{iterations}...")
            
            try:
                workflow_start = time.time()
                
                # Stage 1: Intent
                stage_start = time.time()
                intent_result = self._benchmark_intent_tool()
                intent_time = time.time() - stage_start
                stage_times["intent"].append(intent_time)
                
                # Stage 2: Data
                stage_start = time.time()
                data_result = self._benchmark_data_tool()
                data_time = time.time() - stage_start
                stage_times["data"].append(data_time)
                
                # Stage 3: Model
                stage_start = time.time()
                model_result = self._benchmark_model_tool()
                model_time = time.time() - stage_start
                stage_times["model"].append(model_time)
                
                # Stage 4: Solver
                stage_start = time.time()
                solver_result = self._benchmark_solver_tool()
                solver_time = time.time() - stage_start
                stage_times["solver"].append(solver_time)
                
                workflow_time = time.time() - workflow_start
                workflow_times.append(workflow_time)
                
                print(f"   ✅ Workflow Success: {workflow_time:.2f}s")
                print(f"      Intent: {intent_time:.2f}s | Data: {data_time:.2f}s | Model: {model_time:.2f}s | Solver: {solver_time:.2f}s")
                
            except Exception as e:
                print(f"   ❌ Workflow Failed: {e}")
        
        # Calculate workflow statistics
        if workflow_times:
            workflow_stats = {
                "iterations": iterations,
                "workflow_times": workflow_times,
                "mean_workflow_time": statistics.mean(workflow_times),
                "median_workflow_time": statistics.median(workflow_times),
                "min_workflow_time": min(workflow_times),
                "max_workflow_time": max(workflow_times),
                "stage_times": stage_times,
                "stage_averages": {
                    stage: statistics.mean(times) if times else 0
                    for stage, times in stage_times.items()
                }
            }
            
            print(f"\n📊 WORKFLOW PERFORMANCE STATS:")
            print(f"   Mean Workflow Time: {workflow_stats['mean_workflow_time']:.2f}s")
            print(f"   Median Workflow Time: {workflow_stats['median_workflow_time']:.2f}s")
            print(f"   Min Workflow Time: {workflow_stats['min_workflow_time']:.2f}s")
            print(f"   Max Workflow Time: {workflow_stats['max_workflow_time']:.2f}s")
            
            print(f"\n📊 STAGE AVERAGES:")
            for stage, avg_time in workflow_stats["stage_averages"].items():
                print(f"   {stage.title()}: {avg_time:.2f}s")
            
            self.performance_data["workflow"] = workflow_stats
            return workflow_stats
        else:
            print(f"\n❌ WORKFLOW BENCHMARK FAILED")
            return None
    
    def identify_bottlenecks(self):
        """Identify performance bottlenecks"""
        print(f"\n🔍 IDENTIFYING PERFORMANCE BOTTLENECKS")
        print("=" * 60)
        
        if "workflow" not in self.performance_data:
            print("❌ No workflow performance data available")
            return
        
        workflow_data = self.performance_data["workflow"]
        stage_averages = workflow_data["stage_averages"]
        
        # Find slowest stage
        slowest_stage = max(stage_averages.items(), key=lambda x: x[1])
        fastest_stage = min(stage_averages.items(), key=lambda x: x[1])
        
        print(f"🐌 Slowest Stage: {slowest_stage[0]} ({slowest_stage[1]:.2f}s)")
        print(f"⚡ Fastest Stage: {fastest_stage[0]} ({fastest_stage[1]:.2f}s)")
        
        # Calculate bottlenecks
        total_time = sum(stage_averages.values())
        bottlenecks = []
        
        for stage, time in stage_averages.items():
            percentage = (time / total_time) * 100
            bottlenecks.append((stage, time, percentage))
        
        bottlenecks.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n📊 STAGE CONTRIBUTION TO TOTAL TIME:")
        for stage, time, percentage in bottlenecks:
            print(f"   {stage.title()}: {time:.2f}s ({percentage:.1f}%)")
        
        # Optimization recommendations
        print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
        
        if slowest_stage[1] > 30:  # More than 30 seconds
            print(f"   ⚠️ {slowest_stage[0].title()} stage is very slow ({slowest_stage[1]:.2f}s)")
            print(f"      Consider caching or parallel processing")
        
        if workflow_data["mean_workflow_time"] > 120:  # More than 2 minutes
            print(f"   ⚠️ Total workflow time is high ({workflow_data['mean_workflow_time']:.2f}s)")
            print(f"      Consider optimizing slowest stages")
        
        # Check for high variability
        workflow_times = workflow_data["workflow_times"]
        if len(workflow_times) > 1:
            cv = statistics.stdev(workflow_times) / statistics.mean(workflow_times)
            if cv > 0.3:  # Coefficient of variation > 30%
                print(f"   ⚠️ High variability in workflow times (CV: {cv:.2f})")
                print(f"      Consider investigating inconsistent performance")
        
        return bottlenecks
    
    def generate_optimization_report(self):
        """Generate comprehensive optimization report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_optimization_report_{timestamp}.json"
        
        # Prepare report data
        report = {
            "timestamp": timestamp,
            "performance_data": self.performance_data,
            "summary": {
                "total_tools_tested": len(self.performance_data),
                "workflow_available": "workflow" in self.performance_data
            }
        }
        
        if "workflow" in self.performance_data:
            workflow_data = self.performance_data["workflow"]
            report["summary"]["mean_workflow_time"] = workflow_data["mean_workflow_time"]
            report["summary"]["slowest_stage"] = max(
                workflow_data["stage_averages"].items(), 
                key=lambda x: x[1]
            )[0]
        
        # Save report
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Performance optimization report saved to: {filename}")
        return filename
    
    def run_full_optimization(self):
        """Run complete performance optimization analysis"""
        print("🚀 PERFORMANCE OPTIMIZATION ANALYSIS")
        print("=" * 80)
        print("⚡ Individual Tool Benchmarks | 🔍 Bottleneck Analysis | 📊 Optimization Report")
        print("=" * 80)
        
        # Benchmark individual tools
        tools = ["intent", "data", "model", "solver"]
        for tool in tools:
            self.benchmark_tool_performance(tool, iterations=3)
        
        # Benchmark complete workflow
        self.benchmark_workflow_performance(iterations=3)
        
        # Identify bottlenecks
        bottlenecks = self.identify_bottlenecks()
        
        # Generate report
        report_file = self.generate_optimization_report()
        
        print(f"\n🎯 PERFORMANCE OPTIMIZATION COMPLETE!")
        print(f"📊 Report generated: {report_file}")
        
        return {
            "performance_data": self.performance_data,
            "bottlenecks": bottlenecks,
            "report_file": report_file
        }

def main():
    """Main optimization function"""
    optimizer = PerformanceOptimizer()
    
    try:
        results = optimizer.run_full_optimization()
        print(f"\n✅ Performance optimization analysis completed successfully!")
    except KeyboardInterrupt:
        print("\n👋 Performance optimization interrupted")
    except Exception as e:
        print(f"\n❌ Performance optimization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
