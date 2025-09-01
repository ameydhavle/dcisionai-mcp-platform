#!/usr/bin/env python3
"""
DcisionAI Manufacturing Agent - AgentCore SDK Integration (Intent Only)
======================================================================

Simple AgentCore deployment using the official bedrock-agentcore SDK.
This version only does intent classification to avoid timeout issues.

Based on: https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_bedrock_agentcore/

Usage:
    python src/mcp_server/agentcore_simple_agent_intent_only.py

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

# Import the tools
from mcp_server.tools.manufacturing.intent.DcisionAI_Intent_Tool import create_dcisionai_intent_tool_v6

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | DcisionAI Intent Only | %(message)s"
)
logger = logging.getLogger(__name__)

# Import AgentCore SDK
try:
    from bedrock_agentcore import AgentCoreApp
    app = AgentCoreApp()
except ImportError:
    logger.error("bedrock-agentcore package not found. Install with: pip install bedrock-agentcore")
    sys.exit(1)

# Initialize tools
try:
    intent_tool = create_dcisionai_intent_tool_v6()
    logger.info("✅ Intent tool initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize intent tool: {e}")
    sys.exit(1)

@app.entrypoint
def manufacturing_intent_classification(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    DcisionAI Manufacturing Intent Classification
    
    This endpoint classifies manufacturing optimization intents from natural language queries.
    """
    try:
        # Extract user message from payload
        user_message = payload.get("prompt", "")
        if not user_message:
            return {
                "error": "No prompt provided. Please include a 'prompt' key in your request.",
                "available_tools": ["classify_intent"]
            }
        
        logger.info(f"Processing manufacturing intent classification: {user_message}")
        
        # Step 1: Intent Classification
        logger.info("🔍 Classifying manufacturing intent...")
        intent_result = intent_tool.classify_intent(query=user_message)
        
        # Compile response
        response = {
            "message": "DcisionAI Manufacturing Intent Classification completed successfully",
            "timestamp": str(Path(__file__).stat().st_mtime),
            "model": "dcisionai-manufacturing-agent-intent-only",
            "intent_classification": {
                "primary_intent": intent_result.primary_intent.value if hasattr(intent_result, 'primary_intent') else "Unknown",
                "confidence": intent_result.confidence if hasattr(intent_result, 'confidence') else 0.0,
                "objectives": intent_result.objectives if hasattr(intent_result, 'objectives') else [],
                "reasoning": intent_result.reasoning if hasattr(intent_result, 'reasoning') else "",
                "entities": intent_result.entities if hasattr(intent_result, 'entities') else [],
                "swarm_agreement": intent_result.swarm_agreement if hasattr(intent_result, 'swarm_agreement') else 0.0
            },
            "summary": {
                "intent": intent_result.primary_intent.value if hasattr(intent_result, 'primary_intent') else "Unknown",
                "confidence": intent_result.confidence if hasattr(intent_result, 'confidence') else 0.0,
                "objectives_count": len(intent_result.objectives) if hasattr(intent_result, 'objectives') else 0,
                "entities_count": len(intent_result.entities) if hasattr(intent_result, 'entities') else 0
            },
            "available_tools": ["classify_intent"]
        }
        
        logger.info("✅ Manufacturing intent classification completed successfully")
        return response
        
    except Exception as e:
        logger.exception(f"❌ Error in manufacturing intent classification: {e}")
        return {
            "error": f"Manufacturing intent classification failed: {str(e)}",
            "available_tools": ["classify_intent"]
        }

if __name__ == "__main__":
    logger.info("🚀 Starting DcisionAI Manufacturing Agent (Intent Only - AgentCore SDK)")
    logger.info("📋 Available tools:")
    logger.info("   • Intent Classification")
    logger.info("🔗 AgentCore SDK Integration: Ready")
    
    # Run the AgentCore app
    app.run()
