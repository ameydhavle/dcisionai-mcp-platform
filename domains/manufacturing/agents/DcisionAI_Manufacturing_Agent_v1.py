#!/usr/bin/env python3
"""
DcisionAI Manufacturing Agent v1 - AgentCore SDK Integration
===========================================================

Production-ready AgentCore deployment using the official bedrock-agentcore SDK.
This follows the "Option A: SDK Integration" approach from the Strands documentation.

Based on: https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_bedrock_agentcore/

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, Any

# Import shared framework
from shared.core.base_agent import BaseAgent

# Import our manufacturing tools
from ..tools.intent.DcisionAI_Intent_Tool import create_dcisionai_intent_tool_v6
from ..tools.data.DcisionAI_Data_Tool import create_data_tool
from ..tools.model.DcisionAI_Model_Builder import create_model_builder_tool
from ..tools.solver.DcisionAI_Solver_Tool import create_solver_tool

class DcisionAI_Manufacturing_Agent_v1(BaseAgent):
    """
    DcisionAI Manufacturing Agent v1 - Production-ready AgentCore integration.
    
    This agent orchestrates the complete manufacturing optimization workflow:
    1. Intent Classification
    2. Data Analysis  
    3. Model Building
    4. Optimization Solving
    """
    
    def __init__(self):
        """Initialize the manufacturing agent."""
        super().__init__(
            domain="manufacturing",
            version="1.0.0",
            description="Manufacturing optimization and production planning agent"
        )
        
        # Initialize manufacturing tools
        self.logger.info("Initializing DcisionAI Manufacturing Tools...")
        
        try:
            self.intent_tool = create_dcisionai_intent_tool_v6()
            self.data_tool = create_data_tool()
            self.model_tool = create_model_builder_tool()
            self.solver_tool = create_solver_tool()
            
            # Register tools with the base agent
            self.register_tool("intent_classification", self.intent_tool)
            self.register_tool("data_analysis", self.data_tool)
            self.register_tool("model_building", self.model_tool)
            self.register_tool("optimization_solving", self.solver_tool)
            
            self.logger.info("✅ All manufacturing tools initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize tools: {e}")
            raise
    
    def _initialize_tools(self) -> None:
        """Initialize domain-specific tools. Already done in __init__."""
        pass
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process manufacturing optimization requests.
        
        Args:
            request: Input payload containing user query
            
        Returns:
            Dict containing the response with manufacturing optimization results
        """
        try:
            # Extract user message
            user_message = request.get("prompt", "")
            if not user_message:
                return {
                    "error": "No prompt provided. Please include a 'prompt' key in your request.",
                    "available_tools": [
                        "classify_intent",
                        "analyze_data_requirements", 
                        "build_optimization_model",
                        "solve_optimization_model"
                    ]
                }
            
            self.logger.info(f"Processing manufacturing request: {user_message}")
            
            # Step 1: Intent Classification
            self.logger.info("🔍 Step 1: Classifying manufacturing intent...")
            intent_result = self.intent_tool.classify_intent(
                query=user_message
            )
            
            # Step 2: Data Analysis
            self.logger.info("📊 Step 2: Analyzing data requirements...")
            # Convert IntentClassification object to dictionary
            intent_dict = {
                "primary_intent": intent_result.primary_intent.value if hasattr(intent_result, 'primary_intent') else "Unknown",
                "confidence": intent_result.confidence if hasattr(intent_result, 'confidence') else 0.0,
                "objectives": intent_result.objectives if hasattr(intent_result, 'objectives') else [],
                "reasoning": intent_result.reasoning if hasattr(intent_result, 'reasoning') else ""
            }
            
            data_result = self.data_tool.analyze_data_requirements(
                user_query=user_message,
                intent_result=intent_dict,
                customer_id="default"
            )
            
            # Step 3: Model Building
            self.logger.info("🏗️ Step 3: Building optimization model...")
            # Convert DataAnalysisResult object to dictionary
            data_dict = {
                "data_entities": data_result.data_entities if hasattr(data_result, 'data_entities') else [],
                "missing_data": data_result.missing_data if hasattr(data_result, 'missing_data') else [],
                "sample_data": data_result.sample_data if hasattr(data_result, 'sample_data') else {},
                "analysis_metadata": data_result.analysis_metadata if hasattr(data_result, 'analysis_metadata') else {}
            }
            model_result = self.model_tool.build_optimization_model(
                intent_result=intent_dict,
                data_result=data_dict,
                customer_id="default"
            )
            
            # Step 4: Optimization Solving
            self.logger.info("⚡ Step 4: Solving optimization problem...")
            solver_result = self.solver_tool.solve_optimization_model(
                model=model_result,
                max_solve_time=300.0,
                use_parallel_racing=True
            )
            
            # Compile comprehensive response
            response = {
                "message": "DcisionAI Manufacturing Optimization completed successfully",
                "timestamp": str(Path(__file__).stat().st_mtime),
                "model": "dcisionai-manufacturing-agent",
                "workflow_results": {
                    "intent_classification": {
                        "primary_intent": intent_result.primary_intent.value if hasattr(intent_result, 'primary_intent') else "Unknown",
                        "confidence": intent_result.confidence if hasattr(intent_result, 'confidence') else 0.0,
                        "objectives": intent_result.objectives if hasattr(intent_result, 'objectives') else [],
                        "reasoning": intent_result.reasoning if hasattr(intent_result, 'reasoning') else ""
                    },
                    "data_analysis": {
                        "data_entities": data_result.data_entities if hasattr(data_result, 'data_entities') else [],
                        "missing_data": data_result.missing_data if hasattr(data_result, 'missing_data') else [],
                        "sample_data": data_result.sample_data if hasattr(data_result, 'sample_data') else {}
                    },
                    "model_building": {
                        "model_id": model_result.model_id if hasattr(model_result, 'model_id') else "Unknown",
                        "model_type": model_result.model_type if hasattr(model_result, 'model_type') else "Unknown",
                        "decision_variables": len(model_result.decision_variables) if hasattr(model_result, 'decision_variables') else 0,
                        "constraints": len(model_result.constraints) if hasattr(model_result, 'constraints') else 0
                    },
                    "optimization_solution": {
                        "status": solver_result.status.value if hasattr(solver_result, 'status') else "Unknown",
                        "objective_value": solver_result.objective_value if hasattr(solver_result, 'objective_value') else 0.0,
                        "solve_time": solver_result.solve_time if hasattr(solver_result, 'solve_time') else 0.0
                    }
                },
                "summary": {
                    "intent": intent_result.primary_intent.value if hasattr(intent_result, 'primary_intent') else "Unknown",
                    "confidence": intent_result.confidence if hasattr(intent_result, 'confidence') else 0.0,
                    "data_entities_analyzed": len(data_result.data_entities) if hasattr(data_result, 'data_entities') else 0,
                    "model_type": model_result.model_type if hasattr(model_result, 'model_type') else "Unknown",
                    "solution_status": solver_result.status.value if hasattr(solver_result, 'status') else "Unknown",
                    "objective_value": solver_result.objective_value if hasattr(solver_result, 'objective_value') else 0.0
                },
                "available_tools": [
                    "classify_intent",
                    "analyze_data_requirements", 
                    "build_optimization_model",
                    "solve_optimization_model"
                ]
            }
            
            self.logger.info("✅ Manufacturing optimization workflow completed successfully")
            
            # Log request and response for monitoring
            self.log_request(request, response)
            
            return response
            
        except Exception as e:
            self.logger.exception(f"❌ Error in manufacturing workflow: {e}")
            error_response = {
                "error": f"Manufacturing optimization failed: {str(e)}",
                "available_tools": [
                    "classify_intent",
                    "analyze_data_requirements", 
                    "build_optimization_model",
                    "solve_optimization_model"
                ]
            }
            
            # Log error response
            self.log_request(request, error_response)
            
            return error_response
    
    def get_manufacturing_capabilities(self) -> Dict[str, Any]:
        """Get manufacturing-specific capabilities."""
        return {
            "domain": "manufacturing",
            "version": "1.0.0",
            "workflow": ["intent_classification", "data_analysis", "model_building", "optimization_solving"],
            "supported_industries": ["automotive", "electronics", "aerospace", "chemicals"],
            "optimization_types": ["production_scheduling", "resource_allocation", "inventory_management", "supply_chain_optimization"],
            "tools": {
                "intent_classification": "Manufacturing intent classification and goal identification",
                "data_analysis": "Data requirement analysis and entity identification",
                "model_building": "Optimization model construction and validation",
                "optimization_solving": "Mathematical optimization using multiple solvers"
            }
        }

# For backward compatibility and direct execution
if __name__ == "__main__":
    # Setup logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | DcisionAI AgentCore | %(message)s"
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting DcisionAI Manufacturing Agent (Standalone Mode)")
    logger.info("📋 Available tools:")
    logger.info("   • Intent Classification")
    logger.info("   • Data Analysis")
    logger.info("   • Model Building")
    logger.info("   • Optimization Solving")
    
    # Create and test the agent
    try:
        agent = DcisionAI_Manufacturing_Agent_v1()
        logger.info("✅ Manufacturing Agent initialized successfully")
        
        # Test with a sample request
        test_request = {
            "prompt": "I need to optimize my production schedule to minimize costs while meeting customer demand for our automotive parts manufacturing"
        }
        
        logger.info("🧪 Testing agent with sample request...")
        result = agent.process_request(test_request)
        
        if "error" not in result:
            logger.info("✅ Test completed successfully")
            logger.info(f"📊 Intent: {result['summary']['intent']}")
            logger.info(f"🎯 Solution Status: {result['summary']['solution_status']}")
        else:
            logger.error(f"❌ Test failed: {result['error']}")
            
    except Exception as e:
        logger.error(f"❌ Agent initialization failed: {e}")
        raise
