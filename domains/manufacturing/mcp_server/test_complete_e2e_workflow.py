#!/usr/bin/env python3
"""
Complete E2E Workflow Test for Manufacturing Swarm Architecture

This script tests the complete workflow:
Intent Classification → Data Analysis → Model Building → Solver Optimization

NO MOCK RESPONSES: All tests use real AWS Bedrock inference profiles.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | E2E Test | %(message)s"
)
logger = logging.getLogger(__name__)

# Import the swarm tools
from manufacturing_intent_swarm import ManufacturingIntentSwarm
from manufacturing_data_swarm import ManufacturingDataSwarm
from manufacturing_model_swarm import ManufacturingModelSwarm
from manufacturing_solver_swarm import ManufacturingSolverSwarm

class CompleteE2ETester:
    """Test the complete E2E workflow with real swarm execution."""
    
    def __init__(self):
        logger.info("🚀 Initializing Complete E2E Workflow Tester")
        
        # Initialize all swarms
        self.intent_swarm = ManufacturingIntentSwarm()
        self.data_swarm = ManufacturingDataSwarm()
        self.model_swarm = ManufacturingModelSwarm()
        self.solver_swarm = ManufacturingSolverSwarm()
        
        logger.info("✅ All swarms initialized successfully")
    
    def test_complete_workflow(self, query: str) -> Dict[str, Any]:
        """Test the complete E2E workflow with a manufacturing query."""
        logger.info(f"🎯 Starting complete E2E workflow test")
        logger.info(f"   Query: {query}")
        
        start_time = time.time()
        results = {}
        
        try:
            # Step 1: Intent Classification
            logger.info("📋 Step 1: Intent Classification (5-agent swarm)")
            intent_start = time.time()
            intent_result = self.intent_swarm.classify_intent(query)
            intent_time = time.time() - intent_start
            
            results["intent_classification"] = {
                "result": intent_result,
                "execution_time": intent_time,
                "status": "success" if intent_result.get("status") != "error" else "error"
            }
            
            logger.info(f"✅ Intent Classification completed in {intent_time:.2f}s")
            logger.info(f"   Intent: {intent_result.get('intent', 'unknown')}")
            logger.info(f"   Confidence: {intent_result.get('confidence', 0)}")
            
            # Step 2: Data Analysis
            logger.info("📊 Step 2: Data Analysis (3-agent swarm)")
            data_start = time.time()
            data_result = self.data_swarm.analyze_data_requirements(
                user_query=query,
                intent_result=intent_result
            )
            data_time = time.time() - data_start
            
            results["data_analysis"] = {
                "result": data_result,
                "execution_time": data_time,
                "status": "success" if data_result.get("status") != "error" else "error"
            }
            
            logger.info(f"✅ Data Analysis completed in {data_time:.2f}s")
            logger.info(f"   Extracted entities: {len(data_result.get('extracted_data_entities', []))}")
            
            # Step 3: Model Building
            logger.info("🏗️ Step 3: Model Building (4-agent swarm)")
            model_start = time.time()
            model_result = self.model_swarm.build_optimization_model(
                intent_result=intent_result,
                data_result=data_result
            )
            model_time = time.time() - model_start
            
            results["model_building"] = {
                "result": model_result,
                "execution_time": model_time,
                "status": "success" if model_result.get("status") != "error" else "error"
            }
            
            logger.info(f"✅ Model Building completed in {model_time:.2f}s")
            logger.info(f"   Model type: {model_result.get('model_type', 'unknown')}")
            logger.info(f"   Variables: {len(model_result.get('decision_variables', []))}")
            
            # Step 4: Solver Optimization
            logger.info("🔧 Step 4: Solver Optimization (6-agent swarm)")
            solver_start = time.time()
            solver_result = self.solver_swarm.solve_optimization_model(
                model_result=model_result
            )
            solver_time = time.time() - solver_start
            
            results["solver_optimization"] = {
                "result": solver_result,
                "execution_time": solver_time,
                "status": "success" if solver_result.get("status") != "error" else "error"
            }
            
            logger.info(f"✅ Solver Optimization completed in {solver_time:.2f}s")
            logger.info(f"   Solver recommendations: {len(solver_result.get('solver_recommendations', []))}")
            
            # Calculate total execution time
            total_time = time.time() - start_time
            
            results["summary"] = {
                "total_execution_time": total_time,
                "intent_time": intent_time,
                "data_time": data_time,
                "model_time": model_time,
                "solver_time": solver_time,
                "success": all([
                    results["intent_classification"]["status"] == "success",
                    results["data_analysis"]["status"] == "success",
                    results["model_building"]["status"] == "success",
                    results["solver_optimization"]["status"] == "success"
                ])
            }
            
            logger.info(f"🎉 Complete E2E workflow completed in {total_time:.2f}s")
            logger.info(f"   Intent: {intent_time:.2f}s")
            logger.info(f"   Data: {data_time:.2f}s")
            logger.info(f"   Model: {model_time:.2f}s")
            logger.info(f"   Solver: {solver_time:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ E2E workflow failed: {str(e)}")
            results["error"] = str(e)
            results["summary"] = {
                "total_execution_time": time.time() - start_time,
                "success": False
            }
            return results

def main():
    """Run the complete E2E workflow test."""
    logger.info("🚀 Starting Complete E2E Workflow Test")
    
    # Initialize tester
    tester = CompleteE2ETester()
    
    # Test queries
    test_queries = [
        "Assign shifts for 45 workers across 3 lines, ensuring no one works more than 48 hours per week.",
        "Optimize inventory levels for seasonal demand fluctuations",
        "Schedule production for 5 products with setup times and capacity constraints"
    ]
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"🧪 Test {i}: {query}")
        logger.info(f"{'='*80}")
        
        # Run the complete workflow
        results = tester.test_complete_workflow(query)
        
        # Log summary
        if results.get("summary", {}).get("success"):
            logger.info(f"✅ Test {i} PASSED - Total time: {results['summary']['total_execution_time']:.2f}s")
        else:
            logger.error(f"❌ Test {i} FAILED")
        
        # Save results
        with open(f"e2e_test_results_{i}.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📄 Results saved to e2e_test_results_{i}.json")
        
        # Wait between tests to avoid throttling
        if i < len(test_queries):
            logger.info("⏳ Waiting 30 seconds before next test...")
            time.sleep(30)

if __name__ == "__main__":
    main()
