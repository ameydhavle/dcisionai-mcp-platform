#!/usr/bin/env python3
"""
DcisionAI MCP Server - Intent + Data Tools (Incremental Testing)
===============================================================

FastMCP implementation with Intent and Data tools enabled.
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

# Import intent and data tools
from .tools.manufacturing.intent.DcisionAI_Intent_Tool import create_dcisionai_intent_tool_v6
from .tools.manufacturing.data.DcisionAI_Data_Tool import create_data_tool


class DcisionAIFastMCPServerIntentData:
    """FastMCP server with Intent and Data tools enabled for incremental testing."""
    
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
        
        # Initialize tools
        self._initialize_tools()
        
        # Register tools
        self._register_tools()
        
        self.logger.info("DcisionAI FastMCP Server (Intent + Data) initialized successfully")
    
    def _initialize_tools(self):
        """Initialize intent and data classification tools."""
        try:
            self.logger.info("Initializing intent classification tool...")
            self.intent_tool = create_dcisionai_intent_tool_v6()
            self.logger.info("✅ Intent classification tool initialized")
            
            self.logger.info("Initializing data analysis tool...")
            self.data_tool = create_data_tool()
            self.logger.info("✅ Data analysis tool initialized")
            
        except Exception as e:
            self.logger.exception(f"Failed to initialize tools: {e}")
            raise
    
    def _register_tools(self):
        """Register intent and data tools with FastMCP."""
        try:
            self.logger.info("Registering tools with FastMCP...")
            
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
            
            # Register data analysis tool
            @self.mcp.tool()
            def analyze_manufacturing_data(
                query: str,
                intent_analysis: Optional[Dict[str, Any]] = None,
                include_sample_data: bool = True,
                include_assumptions: bool = True
            ) -> Dict[str, Any]:
                """
                Analyze manufacturing data requirements and generate sample data.
                
                Args:
                    query: Natural language query describing manufacturing optimization need
                    intent_analysis: Optional intent classification result
                    include_sample_data: Include generated sample data
                    include_assumptions: Include data assumptions and reasoning
                
                Returns:
                    Data analysis result with requirements, sample data, and assumptions
                """
                try:
                    self.logger.info(f"Processing data analysis for query: {query[:100]}...")
                    
                    # Process data analysis
                    result = self.data_tool.analyze_data_requirements(query, intent_analysis)
                    
                    # Convert to dictionary
                    result_dict = asdict(result)
                    
                    self.logger.info(f"Data analysis completed: {result.analysis_id}")
                    return result_dict
                    
                except Exception as e:
                    self.logger.exception(f"Data analysis failed: {e}")
                    return {
                        "error": str(e),
                        "success": False
                    }
            
            self.logger.info("✅ Tools registered successfully")
            
        except Exception as e:
            self.logger.exception(f"Failed to register tools: {e}")
            raise
    
    async def process_message(self, user_message: str) -> Dict[str, Any]:
        """
        Process user message with intent + data workflow.
        
        Args:
            user_message: User's natural language query
        
        Returns:
            Intent + data analysis result
        """
        try:
            self.logger.info(f"Processing message: {user_message[:100]}...")
            
            # Stage 1: Intent Analysis
            self.logger.info("🧠 STAGE 1: Intent Analysis")
            intent_result = self.intent_tool.classify_intent(user_message)
            intent_dict = asdict(intent_result)
            
            # Stage 2: Data Analysis
            self.logger.info("📊 STAGE 2: Data Analysis")
            data_result = self.data_tool.analyze_data_requirements(user_message, intent_dict)
            data_dict = asdict(data_result)
            
            # Create workflow result
            workflow_result = {
                "workflow_type": "intent_data",
                "stages": {
                    "intent": {
                        "success": True,
                        "result": intent_dict
                    },
                    "data": {
                        "success": True,
                        "result": data_dict
                    }
                },
                "overall_success": True,
                "message": "Intent and data analysis completed successfully"
            }
            
            self.logger.info(f"Intent + Data workflow completed successfully")
            return workflow_result
            
        except Exception as e:
            self.logger.exception(f"Intent + Data workflow failed: {e}")
            return {
                "workflow_type": "intent_data",
                "overall_success": False,
                "error": str(e),
                "message": "Intent and data analysis failed"
            }
    
    def get_app(self):
        """Get the FastAPI app for AgentCore deployment."""
        return self.mcp.get_app()


# Global server instance
_server_instance = None

def get_server() -> DcisionAIFastMCPServerIntentData:
    """Get or create the FastMCP server instance."""
    global _server_instance
    if _server_instance is None:
        _server_instance = DcisionAIFastMCPServerIntentData()
    return _server_instance

def get_app():
    """Get the FastAPI app for AgentCore deployment."""
    return get_server().get_app()
