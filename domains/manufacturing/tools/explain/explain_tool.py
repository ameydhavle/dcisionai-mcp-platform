"""
DcisionAI Platform - Explain Tool
=================================

Advanced customer-facing explanation tool with business-friendly language and UI-friendly output.
Implements swarm intelligence for explaining each tool's results to customers in an accessible way.

Copyright (c) 2025 DcisionAI. All rights reserved.
Production-ready implementation with enterprise-grade performance.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import base tool class
try:
    from src.shared.utils.base import BaseTool
except ImportError:
    from src.models.manufacturing.tools.shared.base import BaseTool

# Import swarm orchestrator
from .explain_swarm_orchestrator import (
    ExplainSwarmOrchestrator,
    SwarmStrategy,
    WorkflowExplanation,
    ToolExplanation,
    ExplanationType,
    AudienceType
)

logger = logging.getLogger(__name__)


class ExplainTool(BaseTool):
    """
    Advanced Explain Tool with Customer-Facing Business Communication
    
    Features:
    - Business-friendly language for different audience types
    - UI-friendly output formats (JSON, XML, structured data)
    - Executive summaries and actionable insights
    - Risk assessment and recommendations
    - Visualization hints and interactive elements
    - Progressive disclosure of information
    - A2A coordination with other tools
    """
    
    def __init__(self):
        super().__init__(
            name="explain_tool",
            description="Advanced customer-facing explanation with business-friendly language and UI-friendly output"
        )
        self.logger = logging.getLogger(f"{__name__}.ExplainTool")
        self.swarm_orchestrator = None
        self.strands_tools = {}
        self.deployment = None
        self.explanation_history = []
        self.performance_metrics = {}
        
        # A2A coordination state
        self.shared_memory = None
        self.knowledge_graph = None
    
    async def initialize(self) -> bool:
        """Initialize the explain tool with swarm intelligence"""
        try:
            self.logger.info("Initializing Explain Tool with swarm intelligence")
            
            # Initialize swarm orchestrator
            self.swarm_orchestrator = ExplainSwarmOrchestrator()
            
            # Initialize Strands tools for A2A coordination
            try:
                
                self.logger.info("Strands tools initialized for A2A coordination")
            except ImportError:
                self.logger.warning("Strands tools not available - A2A coordination limited")
            
            # Initialize shared memory and knowledge graph for A2A coordination
            try:
                
                self.shared_memory = SharedMemory()
                self.knowledge_graph = KnowledgeGraph()
                self.logger.info("Shared memory and knowledge graph initialized for A2A coordination")
            except ImportError:
                self.logger.warning("Strands memory/knowledge not available - using local state")
            
            # Initialize AgentCore deployment if available
            if hasattr(self.swarm_orchestrator, 'deployment') and self.swarm_orchestrator.deployment:
                self.deployment = self.swarm_orchestrator.deployment
                self.logger.info("AgentCore deployment initialized for customer explanations")
            
            self.logger.info("Explain Tool initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Explain Tool: {e}")
            return False
    
    async def execute(self, input_data: Dict[str, Any]) -> Any:
        """
        Execute explanation workflow with customer-facing communication
        
        Args:
            workflow_results: Results from all tools in the workflow
            workflow_metadata: Metadata about the workflow execution
            target_audience: Target audience type (executive, manager, analyst, technical, general)
            strategy: Swarm strategy to use (consensus, competitive, collaborative, validation, hierarchical)
            explanation_focus: Focus areas for explanation (executive_summary, business_insights, etc.)
            ui_format: Preferred UI output format (json, xml, structured)
            include_visualizations: Whether to include visualization hints
        
        Returns:
            Dict containing explanation results, UI components, and audience-specific outputs
        """
        try:
            self.logger.info("Executing explanation workflow with swarm intelligence")
            
            # Extract parameters
            workflow_results = kwargs.get("workflow_results", {})
            workflow_metadata = kwargs.get("workflow_metadata", {})
            target_audience_str = kwargs.get("target_audience", "executive")
            strategy_str = kwargs.get("strategy", "consensus")
            explanation_focus = kwargs.get("explanation_focus", [])
            ui_format = kwargs.get("ui_format", "json")
            include_visualizations = kwargs.get("include_visualizations", True)
            
            # Validate inputs
            if not workflow_results:
                raise ValueError("workflow_results is required")
            
            # Convert parameters to enums
            target_audience = self._get_audience_type(target_audience_str)
            strategy = self._get_swarm_strategy(strategy_str)
            
            # Execute explanation using swarm orchestrator
            if strategy:
                explanation_result = await self.swarm_orchestrator.explain_workflow(
                    workflow_results=workflow_results,
                    workflow_metadata=workflow_metadata,
                    target_audience=target_audience,
                    strategy=strategy
                )
            else:
                # Use adaptive explanation
                explanation_result = await self.swarm_orchestrator.adaptive_explanation(
                    workflow_results=workflow_results,
                    workflow_metadata=workflow_metadata,
                    target_audience=target_audience
                )
            
            # Process explanation results
            processed_result = self._process_explanation_result(
                explanation_result, target_audience, explanation_focus, ui_format, include_visualizations
            )
            
            # Store in explanation history
            self.explanation_history.append({
                "timestamp": datetime.now().isoformat(),
                "workflow_metadata": workflow_metadata,
                "target_audience": target_audience_str,
                "strategy": strategy_str,
                "result": processed_result
            })
            
            # Update performance metrics
            self._update_performance_metrics(explanation_result)
            
            # A2A coordination: Share explanation insights with other tools
            await self._share_explanation_insights(processed_result)
            
            self.logger.info("Explanation workflow completed successfully")
            return processed_result
            
        except Exception as e:
            self.logger.error(f"Explanation workflow failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "explanation_result": None,
                "ui_components": [],
                "audience_specific_outputs": {},
                "performance_metrics": {}
            }
    
    def _get_audience_type(self, audience_str: str) -> AudienceType:
        """Convert audience string to AudienceType enum"""
        audience_map = {
            "executive": AudienceType.EXECUTIVE,
            "manager": AudienceType.MANAGER,
            "analyst": AudienceType.ANALYST,
            "technical": AudienceType.TECHNICAL,
            "general": AudienceType.GENERAL
        }
        return audience_map.get(audience_str.lower(), AudienceType.EXECUTIVE)
    
    def _get_swarm_strategy(self, strategy_str: str) -> Optional[SwarmStrategy]:
        """Convert strategy string to SwarmStrategy enum"""
        strategy_map = {
            "consensus": SwarmStrategy.CONSENSUS,
            "competitive": SwarmStrategy.COMPETITIVE,
            "collaborative": SwarmStrategy.COLLABORATIVE,
            "validation": SwarmStrategy.VALIDATION,
            "hierarchical": SwarmStrategy.HIERARCHICAL
        }
        return strategy_map.get(strategy_str.lower())
    
    def _process_explanation_result(self, explanation_result: WorkflowExplanation, 
                                  target_audience: AudienceType,
                                  explanation_focus: List[str],
                                  ui_format: str,
                                  include_visualizations: bool) -> Dict[str, Any]:
        """Process explanation result into customer-friendly output"""
        
        # Filter tool explanations if focus areas specified
        tool_explanations = explanation_result.tool_explanations
        if explanation_focus:
            tool_explanations = [
                te for te in tool_explanations 
                if te.explanation_type.value in explanation_focus
            ]
        
        # Filter by target audience if specified
        if target_audience != AudienceType.GENERAL:
            tool_explanations = [
                te for te in tool_explanations 
                if te.audience_type == target_audience
            ]
        
        # Compile UI components
        ui_components = []
        if include_visualizations:
            for explanation in tool_explanations:
                for viz_hint in explanation.visualization_hints:
                    ui_components.append({
                        "component_type": "visualization",
                        "chart_type": viz_hint.get("chart_type", "bar"),
                        "data_points": viz_hint.get("data_points", []),
                        "purpose": viz_hint.get("purpose", ""),
                        "tool_source": explanation.tool_type.value
                    })
        
        # Add explanation components
        for explanation in tool_explanations:
            ui_components.append({
                "component_type": "explanation",
                "tool_type": explanation.tool_type.value,
                "explanation_type": explanation.explanation_type.value,
                "content": explanation.executive_summary,
                "business_insights": explanation.business_insights,
                "recommendations": explanation.actionable_recommendations,
                "risk_assessment": explanation.risk_assessment,
                "technical_details": explanation.technical_details,
                "interaction_type": "expandable"
            })
        
        # Create audience-specific outputs
        audience_outputs = {}
        for audience in [AudienceType.EXECUTIVE, AudienceType.MANAGER, AudienceType.ANALYST]:
            audience_outputs[audience.value] = {
                "summary": self._create_audience_summary(explanation_result, audience),
                "focus": self._get_audience_focus(audience),
                "detail_level": self._get_audience_detail_level(audience),
                "recommendations": self._filter_recommendations_for_audience(
                    explanation_result.recommendations, audience
                )
            }
        
        # Format output based on UI format preference
        formatted_output = self._format_output_for_ui(
            explanation_result, ui_components, audience_outputs, ui_format
        )
        
        return {
            "success": True,
            "explanation_result": {
                "tool_explanations": [
                    {
                        "tool_type": te.tool_type.value,
                        "explanation_type": te.explanation_type.value,
                        "audience_type": te.audience_type.value,
                        "executive_summary": te.executive_summary,
                        "business_insights": te.business_insights,
                        "actionable_recommendations": te.actionable_recommendations,
                        "risk_assessment": te.risk_assessment,
                        "technical_details": te.technical_details,
                        "visualization_hints": te.visualization_hints,
                        "ui_friendly_output": te.ui_friendly_output,
                        "confidence_score": te.confidence_score
                    }
                    for te in tool_explanations
                ],
                "executive_summary": explanation_result.executive_summary,
                "business_impact": explanation_result.business_impact,
                "key_insights": explanation_result.key_insights,
                "recommendations": explanation_result.recommendations,
                "risk_assessment": explanation_result.risk_assessment,
                "next_steps": explanation_result.next_steps,
                "explanation_metadata": explanation_result.explanation_metadata
            },
            "ui_components": ui_components,
            "audience_specific_outputs": audience_outputs,
            "formatted_output": formatted_output,
            "performance_metrics": {
                "execution_time": explanation_result.execution_time,
                "swarm_agreement": explanation_result.swarm_agreement,
                "total_explanations": len(tool_explanations)
            }
        }
    
    def _create_audience_summary(self, explanation_result: WorkflowExplanation, 
                               audience: AudienceType) -> str:
        """Create audience-specific summary"""
        if audience == AudienceType.EXECUTIVE:
            return f"Executive Summary: {explanation_result.executive_summary}"
        elif audience == AudienceType.MANAGER:
            return f"Manager Summary: Focus on operational insights and implementation guidance"
        elif audience == AudienceType.ANALYST:
            return f"Analyst Summary: Detailed technical analysis with data insights"
        else:
            return explanation_result.executive_summary
    
    def _get_audience_focus(self, audience: AudienceType) -> str:
        """Get focus area for specific audience"""
        focus_map = {
            AudienceType.EXECUTIVE: "business_impact",
            AudienceType.MANAGER: "operational_insights",
            AudienceType.ANALYST: "technical_details",
            AudienceType.TECHNICAL: "implementation_details",
            AudienceType.GENERAL: "overview"
        }
        return focus_map.get(audience, "overview")
    
    def _get_audience_detail_level(self, audience: AudienceType) -> str:
        """Get detail level for specific audience"""
        detail_map = {
            AudienceType.EXECUTIVE: "high_level",
            AudienceType.MANAGER: "operational",
            AudienceType.ANALYST: "detailed",
            AudienceType.TECHNICAL: "technical",
            AudienceType.GENERAL: "moderate"
        }
        return detail_map.get(audience, "moderate")
    
    def _filter_recommendations_for_audience(self, recommendations: List[str], 
                                           audience: AudienceType) -> List[str]:
        """Filter recommendations based on audience type"""
        if audience == AudienceType.EXECUTIVE:
            # Return strategic recommendations
            return [rec for rec in recommendations if any(keyword in rec.lower() 
                    for keyword in ["strategy", "business", "impact", "roi"])]
        elif audience == AudienceType.MANAGER:
            # Return operational recommendations
            return [rec for rec in recommendations if any(keyword in rec.lower() 
                    for keyword in ["implement", "process", "operation", "team"])]
        elif audience == AudienceType.ANALYST:
            # Return analytical recommendations
            return [rec for rec in recommendations if any(keyword in rec.lower() 
                    for keyword in ["analyze", "data", "model", "optimize"])]
        else:
            return recommendations
    
    def _format_output_for_ui(self, explanation_result: WorkflowExplanation,
                            ui_components: List[Dict[str, Any]],
                            audience_outputs: Dict[str, Dict[str, Any]],
                            ui_format: str) -> Dict[str, Any]:
        """Format output for UI consumption"""
        if ui_format.lower() == "json":
            return {
                "format": "json",
                "data": {
                    "summary": explanation_result.executive_summary,
                    "components": ui_components,
                    "audience_outputs": audience_outputs,
                    "metadata": explanation_result.explanation_metadata
                }
            }
        elif ui_format.lower() == "xml":
            # Convert to XML-like structure
            return {
                "format": "xml",
                "data": {
                    "explanation": {
                        "summary": explanation_result.executive_summary,
                        "components": {"component": ui_components},
                        "audiences": {"audience": audience_outputs}
                    }
                }
            }
        else:
            # Structured format
            return {
                "format": "structured",
                "data": {
                    "summary": explanation_result.executive_summary,
                    "components": ui_components,
                    "audience_outputs": audience_outputs,
                    "interactive_elements": self._extract_interactive_elements(ui_components)
                }
            }
    
    def _extract_interactive_elements(self, ui_components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract interactive elements from UI components"""
        interactive_elements = []
        for component in ui_components:
            if component.get("interaction_type"):
                interactive_elements.append({
                    "element_id": f"{component.get('component_type', 'unknown')}_{len(interactive_elements)}",
                    "type": component.get("interaction_type"),
                    "component": component
                })
        return interactive_elements
    
    def _update_performance_metrics(self, explanation_result: WorkflowExplanation):
        """Update performance metrics based on explanation result"""
        self.performance_metrics = {
            "last_execution": datetime.now().isoformat(),
            "total_explanations": len(self.explanation_history),
            "average_confidence_score": explanation_result.swarm_agreement,
            "execution_time": explanation_result.execution_time,
            "strategy_performance": self.swarm_orchestrator.get_performance_metrics() if self.swarm_orchestrator else {}
        }
    
    async def _share_explanation_insights(self, processed_result: Dict[str, Any]):
        """Share explanation insights with other tools via A2A coordination"""
        try:
            if self.shared_memory:
                # Store explanation insights in shared memory
                await self.shared_memory.store(
                    key=f"explanation_insights_{datetime.now().timestamp()}",
                    value={
                        "key_insights": processed_result.get("explanation_result", {}).get("key_insights", []),
                        "recommendations": processed_result.get("explanation_result", {}).get("recommendations", []),
                        "business_impact": processed_result.get("explanation_result", {}).get("business_impact", {}),
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                self.logger.info("Explanation insights shared via A2A coordination")
            
            if self.knowledge_graph:
                # Update knowledge graph with explanation insights
                # This would typically involve adding nodes and relationships
                # representing the explanation findings and business insights
                pass
                
        except Exception as e:
            self.logger.warning(f"Failed to share explanation insights: {e}")
    
    async def get_explanation_history(self) -> List[Dict[str, Any]]:
        """Get explanation history for analysis and learning"""
        return self.explanation_history
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring and optimization"""
        return self.performance_metrics
    
    async def get_swarm_performance(self) -> Dict[str, Any]:
        """Get swarm performance metrics"""
        if self.swarm_orchestrator:
            return self.swarm_orchestrator.get_performance_metrics()
        return {}
    
    async def generate_audience_specific_explanation(self, workflow_results: Dict[str, Any],
                                                   workflow_metadata: Dict[str, Any],
                                                   target_audience: str) -> Dict[str, Any]:
        """Generate explanation specifically for a target audience"""
        try:
            audience_type = self._get_audience_type(target_audience)
            
            explanation_result = await self.swarm_orchestrator.explain_workflow(
                workflow_results=workflow_results,
                workflow_metadata=workflow_metadata,
                target_audience=audience_type
            )
            
            return self._process_explanation_result(
                explanation_result, audience_type, [], "json", True
            )
            
        except Exception as e:
            self.logger.error(f"Audience-specific explanation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "audience": target_audience
            }
    
    async def analyze_explanation_effectiveness(self, audience_type: str) -> Dict[str, Any]:
        """Analyze effectiveness of explanations for a specific audience"""
        audience_explanations = []
        
        for explanation_record in self.explanation_history:
            if explanation_record.get("target_audience") == audience_type:
                audience_explanations.append(explanation_record)
        
        if not audience_explanations:
            return {"error": f"No explanation data found for audience: {audience_type}"}
        
        # Calculate effectiveness metrics
        confidence_scores = []
        for record in audience_explanations:
            result = record.get("result", {})
            if result.get("success"):
                confidence_scores.append(
                    result.get("performance_metrics", {}).get("swarm_agreement", 0.0)
                )
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return {
            "audience_type": audience_type,
            "total_explanations": len(audience_explanations),
            "average_confidence": avg_confidence,
            "effectiveness_trend": self._calculate_effectiveness_trend(audience_explanations),
            "common_insights": self._get_common_insights(audience_explanations)
        }
    
    def _calculate_effectiveness_trend(self, audience_explanations: List[Dict[str, Any]]) -> str:
        """Calculate effectiveness trend based on confidence scores over time"""
        if len(audience_explanations) < 2:
            return "insufficient_data"
        
        confidence_scores = []
        for record in audience_explanations:
            result = record.get("result", {})
            if result.get("success"):
                confidence_scores.append(
                    result.get("performance_metrics", {}).get("swarm_agreement", 0.0)
                )
        
        if len(confidence_scores) < 2:
            return "insufficient_data"
        
        if confidence_scores[-1] > confidence_scores[0]:
            return "improving"
        elif confidence_scores[-1] < confidence_scores[0]:
            return "declining"
        else:
            return "stable"
    
    def _get_common_insights(self, audience_explanations: List[Dict[str, Any]]) -> List[str]:
        """Extract common insights from audience explanations"""
        insights = {}
        for record in audience_explanations:
            result = record.get("result", {})
            if result.get("success"):
                explanation_result = result.get("explanation_result", {})
                for insight in explanation_result.get("key_insights", []):
                    insights[insight] = insights.get(insight, 0) + 1
        
        # Return top 5 most common insights
        return sorted(insights.items(), key=lambda x: x[1], reverse=True)[:5]