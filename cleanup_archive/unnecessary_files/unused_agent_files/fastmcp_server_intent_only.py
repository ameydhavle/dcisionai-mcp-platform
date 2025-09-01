#!/usr/bin/env python3
"""
DcisionAI MCP Server - Intent Tool Only (Incremental Testing)
============================================================

Simplified FastMCP implementation with only Intent tool enabled.
Used for incremental testing of AgentCore deployment.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import asdict

# Import FastMCP for AWS AgentCore compatibility
try:
    from mcp.server.fastmcp import FastMCP
    from starlette.responses import JSONResponse
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    print("Error: FastMCP not available. Please install with: pip install mcp")

# Import configuration and utilities
from .config.settings import settings
from .utils.logging import get_logger

# Import only intent tool
from .tools.manufacturing.intent.DcisionAI_Intent_Tool import create_dcisionai_intent_tool_v6


class DcisionAIFastMCPServerIntentOnly:
    """FastMCP server with only Intent tool enabled for incremental testing."""
    
    def __init__(self):
        if not FASTMCP_AVAILABLE:
            raise ImportError("FastMCP is required for AWS AgentCore deployment")
        
        # Initialize FastMCP with production settings
        self.mcp = FastMCP(
            host=settings.server_host,
            stateless_http=True
        )
        
        # Setup logging
        self.logger = get_logger(__name__)
        
        # Initialize only intent tool
        self._initialize_intent_tool()
        
        # Register intent tool
        self._register_intent_tool()
        
        self.logger.info("DcisionAI FastMCP Server (Intent Only) initialized successfully")
    
    def _initialize_intent_tool(self):
        """Initialize only the intent classification tool."""
        try:
            self.logger.info("Initializing intent classification tool...")
            
            # Initialize intent classification tool
            self.intent_tool = create_dcisionai_intent_tool_v6()
            self.logger.info("✅ Intent classification tool initialized")
            
        except Exception as e:
            self.logger.exception(f"Failed to initialize intent tool: {e}")
            raise
    
    def _register_intent_tool(self):
        """Register only the intent tool with FastMCP."""
        try:
            self.logger.info("Registering intent tool with FastMCP...")
            
            # Register intent classification tool
            @self.mcp.tool()
            def classify_manufacturing_intent(
                query: str,
                include_confidence: bool = True,
                include_reasoning: bool = True
            ) -> Dict[str, Any]:
                """
                Classify manufacturing optimization intent from natural language query.
                
                Args:
                    query: Natural language query describing manufacturing optimization need
                    include_confidence: Include confidence scores in response
                    include_reasoning: Include reasoning for classification
                
                Returns:
                    Intent classification result with primary intent, confidence, and objectives
                """
                try:
                    self.logger.info(f"Processing intent classification for query: {query[:100]}...")
                    
                    # Process intent classification
                    result = self.intent_tool.classify_intent(query)
                    
                    # Convert to dictionary
                    result_dict = asdict(result)
                    
                    self.logger.info(f"Intent classification completed: {result.primary_intent.value}")
                    return result_dict
                    
                except Exception as e:
                    self.logger.exception(f"Intent classification failed: {e}")
                    return {
                        "error": str(e),
                        "success": False
                    }
            
            self.logger.info("✅ Intent tool registered successfully")
            
        except Exception as e:
            self.logger.exception(f"Failed to register intent tool: {e}")
            raise
    
    async def process_message(self, user_message: str) -> Dict[str, Any]:
        """
        Process user message with intent-only workflow.
        
        Args:
            user_message: User's natural language query
        
        Returns:
            Intent classification result
        """
        try:
            self.logger.info(f"Processing message: {user_message[:100]}...")
            
            # Stage 1: Intent Analysis Only
            self.logger.info("🧠 STAGE 1: Intent Analysis")
            intent_result = self.intent_tool.classify_intent(user_message)
            
            # Convert to dictionary
            intent_dict = asdict(intent_result)
            
            # Create simplified workflow result
            workflow_result = {
                "workflow_type": "intent_only",
                "stages": {
                    "intent": {
                        "success": True,
                        "result": intent_dict
                    }
                },
                "overall_success": True,
                "message": "Intent analysis completed successfully"
            }
            
            self.logger.info(f"Intent-only workflow completed successfully")
            return workflow_result
            
        except Exception as e:
            self.logger.exception(f"Intent-only workflow failed: {e}")
            return {
                "workflow_type": "intent_only",
                "overall_success": False,
                "error": str(e),
                "message": "Intent analysis failed"
            }
    
    def get_app(self):
        """Get the FastAPI app for AgentCore deployment."""
        return self.mcp.get_app()


# Global server instance
_server_instance = None

def get_server() -> DcisionAIFastMCPServerIntentOnly:
    """Get or create the FastMCP server instance."""
    global _server_instance
    if _server_instance is None:
        _server_instance = DcisionAIFastMCPServerIntentOnly()
    return _server_instance

def get_app():
    """Get the FastAPI app for AgentCore deployment."""
    return get_server().get_app()
