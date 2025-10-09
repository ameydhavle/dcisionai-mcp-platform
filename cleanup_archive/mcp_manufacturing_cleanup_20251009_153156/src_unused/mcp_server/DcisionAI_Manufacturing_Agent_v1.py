#!/usr/bin/env python3
"""
DcisionAI Manufacturing Agent v1 - AgentCore SDK Integration
===========================================================

Production-ready AgentCore deployment using the official bedrock-agentcore SDK.
This follows the "Option A: SDK Integration" approach from the Strands documentation.

Based on: https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_bedrock_agentcore/

Usage:
    python src/mcp_server/DcisionAI_Manufacturing_Agent_v1.py

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, Any

# Add the src directory to Python path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import AgentCore SDK
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Import our manufacturing tools from consolidated location
from domains.manufacturing.tools.intent.DcisionAI_Intent_Tool import create_dcisionai_intent_tool_v6
from domains.manufacturing.tools.data.DcisionAI_Data_Tool import create_data_tool
from domains.manufacturing.tools.model.DcisionAI_Model_Builder import create_model_builder_tool
from domains.manufacturing.tools.solver.DcisionAI_Solver_Tool import create_solver_tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | DcisionAI AgentCore | %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize AgentCore app
app = BedrockAgentCoreApp()

# Initialize manufacturing tools
logger.info("Initializing DcisionAI Manufacturing Tools...")

try:
    intent_tool = create_dcisionai_intent_tool_v6()
    data_tool = create_data_tool()
    model_tool = create_model_builder_tool()
    solver_tool = create_solver_tool()
    logger.info("✅ All manufacturing tools initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize tools: {e}")
    raise

@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for AgentCore - processes manufacturing optimization requests.
    
    Args:
        payload: Input payload containing user query
        
    Returns:
        Dict containing the response with manufacturing optimization results
    """
    try:
        # Extract user message
        user_message = payload.get("prompt", "")
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
        
        logger.info(f"Processing manufacturing request: {user_message}")
        
        # Step 1: Intent Classification
        logger.info("🔍 Step 1: Classifying manufacturing intent...")
        intent_result = intent_tool.classify_intent(
            query=user_message
        )
        
        # Step 2: Data Analysis
        logger.info("📊 Step 2: Analyzing data requirements...")
        # Convert IntentClassification object to dictionary
        intent_dict = {
            "primary_intent": intent_result.primary_intent.value if hasattr(intent_result, 'primary_intent') else "Unknown",
            "confidence": intent_result.confidence if hasattr(intent_result, 'confidence') else 0.0,
            "objectives": intent_result.objectives if hasattr(intent_result, 'objectives') else [],
            "reasoning": intent_result.reasoning if hasattr(intent_result, 'reasoning') else ""
        }
        data_result = data_tool.analyze_data_requirements(
            user_query=user_message,
            intent_result=intent_dict,
            customer_id="default"
        )
        
        # Step 3: Model Building
        logger.info("🏗️ Step 3: Building optimization model...")
        # Convert DataAnalysisResult object to dictionary
        data_dict = {
            "data_entities": data_result.data_entities if hasattr(data_result, 'data_entities') else [],
            "missing_data": data_result.missing_data if hasattr(data_result, 'missing_data') else [],
            "sample_data": data_result.sample_data if hasattr(data_result, 'sample_data') else {},
            "analysis_metadata": data_result.analysis_metadata if hasattr(data_result, 'analysis_metadata') else {}
        }
        model_result = model_tool.build_optimization_model(
            intent_result=intent_dict,
            data_result=data_dict,
            customer_id="default"
        )
        
        # Step 4: Optimization Solving
        logger.info("⚡ Step 4: Solving optimization problem...")
        solver_result = solver_tool.solve_optimization_model(
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
        
        logger.info("✅ Manufacturing optimization workflow completed successfully")
        return response
        
    except Exception as e:
        logger.exception(f"❌ Error in manufacturing workflow: {e}")
        return {
            "error": f"Manufacturing optimization failed: {str(e)}",
            "available_tools": [
                "classify_intent",
                "analyze_data_requirements", 
                "build_optimization_model",
                "solve_optimization_model"
            ]
        }

if __name__ == "__main__":
    logger.info("🚀 Starting DcisionAI Manufacturing Agent (AgentCore SDK)")
    logger.info("📋 Available tools:")
    logger.info("   • Intent Classification")
    logger.info("   • Data Analysis")
    logger.info("   • Model Building")
    logger.info("   • Optimization Solving")
    logger.info("🔗 AgentCore SDK Integration: Ready")
    
    # Run the AgentCore app
    app.run()
