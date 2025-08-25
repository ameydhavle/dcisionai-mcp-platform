"""
MCP Intent Classification Tool
=============================

MCP wrapper for the DcisionAI Intent Classification Tool.
"""

import asyncio
from typing import Dict, Any, Optional

from .base import DcisionAITool, ToolResult
from ...models.manufacturing.tools.intent.DcisionAI_Intent_Tool_v6 import create_dcisionai_intent_tool_v6


class IntentClassificationTool(DcisionAITool):
    """MCP wrapper for Intent Classification Tool."""
    
    def __init__(self, tenant_id: str = "default"):
        super().__init__(tenant_id)
        # Initialize the underlying manufacturing tool
        try:
            self.intent_tool = create_dcisionai_intent_tool_v6()
            self.logger.info("Intent classification tool initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize intent tool: {e}")
            raise
    
    @property
    def name(self) -> str:
        return "manufacturing_intent_classification"
    
    @property
    def description(self) -> str:
        return "Classify manufacturing optimization queries using 6-agent swarm system"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Manufacturing optimization query to classify"
                },
                "include_confidence": {
                    "type": "boolean",
                    "description": "Include confidence scores in response",
                    "default": True
                },
                "include_reasoning": {
                    "type": "boolean", 
                    "description": "Include reasoning in response",
                    "default": True
                }
            },
            "required": ["query"]
        }
    
    async def _execute(self, **kwargs) -> ToolResult:
        """Execute intent classification."""
        try:
            query = kwargs.get("query")
            if not query:
                return ToolResult(
                    success=False,
                    error="Query is required"
                )
            
            # Execute the underlying manufacturing tool
            result = await asyncio.to_thread(
                self.intent_tool.classify_intent,
                query
            )
            
            # Format the result for MCP
            mcp_result = {
                "primary_intent": result.primary_intent.value if result.primary_intent else None,
                "confidence": result.confidence,
                "entities": result.entities,
                "objectives": result.objectives,
                "swarm_agreement": result.swarm_agreement
            }
            
            # Add optional fields based on input parameters
            if kwargs.get("include_reasoning", True):
                mcp_result["reasoning"] = result.reasoning
            
            if kwargs.get("include_confidence", True):
                mcp_result["classification_metadata"] = result.classification_metadata
            
            self.logger.info(
                "Intent classification completed",
                query=query,
                primary_intent=mcp_result["primary_intent"],
                confidence=mcp_result["confidence"]
            )
            
            return ToolResult(
                success=True,
                data=mcp_result,
                metadata={
                    "tool_version": "v6",
                    "swarm_agents": 6,
                    "execution_time_ms": result.classification_metadata.get("execution_time_ms", 0)
                }
            )
            
        except Exception as e:
            self.logger.exception(f"Intent classification failed: {e}")
            return ToolResult(
                success=False,
                error=f"Intent classification failed: {str(e)}"
            )
