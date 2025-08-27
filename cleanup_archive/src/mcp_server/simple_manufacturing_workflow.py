#!/usr/bin/env python3
"""
DcisionAI Simple Manufacturing Workflow
======================================

Simple sequential workflow for manufacturing optimization without Strands Graph.
Implements a sequential pipeline: Intent → Data → Model → Solver

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from dataclasses import asdict
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleManufacturingWorkflow:
    """Simple sequential workflow for manufacturing optimization."""
    
    def __init__(self, mcp_server):
        self.logger = logging.getLogger(__name__)
        self.mcp_server = mcp_server
        self.logger.info("Simple Manufacturing Workflow initialized")
    
    async def process_manufacturing_request(self, query: str) -> Dict[str, Any]:
        """
        Process a manufacturing optimization request through simple sequential workflow.
        
        Args:
            query: Manufacturing optimization query
            
        Returns:
            Dictionary with workflow results and recommendations
        """
        try:
            self.logger.info(f"Processing manufacturing request: {query[:100]}...")
            start_time = datetime.now()
            
            workflow_results = {
                "status": "processing",
                "execution_order": [],
                "node_results": {},
                "errors": []
            }
            
            # Step 1: Intent Classification
            try:
                self.logger.info("Step 1: Intent Classification")
                intent_result = self.mcp_server.intent_tool.classify_intent(query)
                intent_data = asdict(intent_result)
                workflow_results["node_results"]["intent_classification"] = {
                    "content": intent_data,
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                }
                workflow_results["execution_order"].append("intent_classification")
                self.logger.info(f"✅ Intent classified: {intent_data.get('primary_intent', 'unknown')}")
            except Exception as e:
                error_msg = f"Intent classification failed: {e}"
                self.logger.error(error_msg)
                workflow_results["node_results"]["intent_classification"] = {
                    "content": {"error": str(e)},
                    "status": "failed",
                    "timestamp": datetime.now().isoformat()
                }
                workflow_results["errors"].append(error_msg)
            
            # Step 2: Data Requirements Analysis
            try:
                self.logger.info("Step 2: Data Requirements Analysis")
                intent_classification = workflow_results["node_results"].get("intent_classification", {}).get("content", {})
                primary_intent = intent_classification.get("primary_intent", "unknown") if isinstance(intent_classification, dict) else "unknown"
                
                data_result = self.mcp_server.data_tool.analyze_data_requirements(query, str(primary_intent))
                data_data = asdict(data_result)
                workflow_results["node_results"]["data_requirements"] = {
                    "content": data_data,
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                }
                workflow_results["execution_order"].append("data_requirements")
                self.logger.info("✅ Data requirements analyzed")
            except Exception as e:
                error_msg = f"Data analysis failed: {e}"
                self.logger.error(error_msg)
                workflow_results["node_results"]["data_requirements"] = {
                    "content": {"error": str(e)},
                    "status": "failed",
                    "timestamp": datetime.now().isoformat()
                }
                workflow_results["errors"].append(error_msg)
            
            # Step 3: Model Building
            try:
                self.logger.info("Step 3: Model Building (SKIPPED FOR DEBUGGING)")
                # Skip model building for now to isolate the hanging issue
                workflow_results["node_results"]["model_building"] = {
                    "content": {"status": "skipped_for_debugging", "message": "Model building temporarily disabled to isolate hanging issue"},
                    "status": "skipped",
                    "timestamp": datetime.now().isoformat()
                }
                workflow_results["execution_order"].append("model_building")
                self.logger.info("⏭️ Model building skipped for debugging")
            except Exception as e:
                error_msg = f"Model building failed: {e}"
                self.logger.error(error_msg)
                workflow_results["node_results"]["model_building"] = {
                    "content": {"error": str(e)},
                    "status": "failed",
                    "timestamp": datetime.now().isoformat()
                }
                workflow_results["errors"].append(error_msg)
            
            # Step 4: Problem Solving
            try:
                self.logger.info("Step 4: Problem Solving (SKIPPED FOR DEBUGGING)")
                # Skip problem solving for now to isolate the hanging issue
                workflow_results["node_results"]["optimization_solving"] = {
                    "content": {"status": "skipped_for_debugging", "message": "Problem solving temporarily disabled to isolate hanging issue"},
                    "status": "skipped",
                    "timestamp": datetime.now().isoformat()
                }
                workflow_results["execution_order"].append("optimization_solving")
                self.logger.info("⏭️ Problem solving skipped for debugging")
            except Exception as e:
                error_msg = f"Problem solving failed: {e}"
                self.logger.error(error_msg)
                workflow_results["node_results"]["optimization_solving"] = {
                    "content": {"error": str(e)},
                    "status": "failed",
                    "timestamp": datetime.now().isoformat()
                }
                workflow_results["errors"].append(error_msg)
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
            
            # Update workflow status
            successful_steps = len([r for r in workflow_results["node_results"].values() if r.get("status") == "success"])
            total_steps = len(workflow_results["node_results"])
            
            if successful_steps == total_steps:
                workflow_results["status"] = "completed"
            elif successful_steps > 0:
                workflow_results["status"] = "partial"
            else:
                workflow_results["status"] = "failed"
            
            workflow_results["total_execution_time"] = execution_time
            workflow_results["successful_steps"] = successful_steps
            workflow_results["total_steps"] = total_steps
            
            # Create response
            response = {
                "message": f"Manufacturing optimization workflow completed. {successful_steps}/{total_steps} steps successful in {execution_time:.0f}ms",
                "workflow_results": workflow_results,
                "tools_used": workflow_results["execution_order"],
                "tools_available": [
                    "classify_manufacturing_intent",
                    "analyze_data_requirements", 
                    "build_optimization_model",
                    "solve_optimization_problem"
                ],
                "server_ready": True,
                "workflow_type": "simple_sequential_pipeline"
            }
            
            self.logger.info(f"✅ Workflow completed. Steps executed: {workflow_results['execution_order']}")
            return response
            
        except Exception as e:
            self.logger.exception(f"Workflow execution failed: {e}")
            return {
                "message": f"Manufacturing workflow failed: {str(e)}",
                "error": str(e),
                "tools_used": [],
                "tools_available": [
                    "classify_manufacturing_intent",
                    "analyze_data_requirements", 
                    "build_optimization_model",
                    "solve_optimization_problem"
                ],
                "server_ready": False,
                "workflow_type": "simple_sequential_pipeline"
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get the current status of the workflow."""
        return {
            "workflow_type": "simple_sequential_pipeline",
            "nodes": ["intent_classification", "data_requirements", "model_building", "optimization_solving"],
            "status": "ready"
        }


def create_simple_manufacturing_workflow(mcp_server):
    """Create and return a simple manufacturing workflow instance."""
    return SimpleManufacturingWorkflow(mcp_server)
