"""
DcisionAI Platform - Critique Tool
==================================

Advanced multi-tool supervision with constructive criticism and human-in-the-loop capabilities.
Implements swarm intelligence for comprehensive quality assurance across all manufacturing tools.

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
from .critique_swarm_orchestrator import (
    CritiqueSwarmOrchestrator,
    SwarmStrategy,
    WorkflowCritique,
    ToolCritique,
    CritiqueType,
    ConfidenceLevel
)

logger = logging.getLogger(__name__)


class CritiqueTool(BaseTool):
    """
    Advanced Critique Tool with Multi-Tool Supervision Swarm Intelligence
    
    Features:
    - Multi-tool supervision with specialized agents
    - Constructive criticism with token optimization
    - Correctness validation and performance analysis
    - Human-in-the-loop coordination (roadmap)
    - A2A coordination with other tools
    - Quality assessment and improvement recommendations
    """
    
    def __init__(self):
        super().__init__(
            name="critique_tool",
            description="Advanced multi-tool supervision with constructive criticism and human-in-the-loop capabilities"
        )
        self.logger = logging.getLogger(f"{__name__}.CritiqueTool")
        self.swarm_orchestrator = None
        self.strands_tools = {}
        self.deployment = None
        self.critique_history = []
        self.performance_metrics = {}
        
        # A2A coordination state
        self.shared_memory = None
        self.knowledge_graph = None
    
    async def initialize(self) -> bool:
        """Initialize the critique tool with swarm intelligence"""
        try:
            self.logger.info("Initializing Critique Tool with swarm intelligence")
            
            # Initialize swarm orchestrator
            self.swarm_orchestrator = CritiqueSwarmOrchestrator()
            
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
                self.logger.info("AgentCore deployment initialized for critique supervision")
            
            self.logger.info("Critique Tool initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Critique Tool: {e}")
            return False
    
    async def execute(self, input_data: Dict[str, Any]) -> Any:
        """
        Execute critique workflow with multi-tool supervision
        
        Args:
            workflow_results: Results from all tools in the workflow
            workflow_metadata: Metadata about the workflow execution
            strategy: Swarm strategy to use (consensus, competitive, collaborative, validation, hierarchical)
            target_tools: Specific tools to critique (optional)
            critique_focus: Focus areas for critique (token_optimization, correctness_validation, etc.)
            human_review_threshold: Confidence threshold for human review (roadmap)
        
        Returns:
            Dict containing critique results, recommendations, and performance metrics
        """
        try:
            self.logger.info("Executing critique workflow with swarm intelligence")
            
            # Extract parameters
            workflow_results = kwargs.get("workflow_results", {})
            workflow_metadata = kwargs.get("workflow_metadata", {})
            strategy_str = kwargs.get("strategy", "consensus")
            target_tools = kwargs.get("target_tools", [])
            critique_focus = kwargs.get("critique_focus", [])
            human_review_threshold = kwargs.get("human_review_threshold", 0.7)
            
            # Validate inputs
            if not workflow_results:
                raise ValueError("workflow_results is required")
            
            # Convert strategy string to enum
            strategy = self._get_swarm_strategy(strategy_str)
            
            # Execute critique using swarm orchestrator
            if strategy:
                critique_result = await self.swarm_orchestrator.critique_workflow(
                    workflow_results=workflow_results,
                    workflow_metadata=workflow_metadata,
                    strategy=strategy
                )
            else:
                # Use adaptive critique
                critique_result = await self.swarm_orchestrator.adaptive_critique(
                    workflow_results=workflow_results,
                    workflow_metadata=workflow_metadata
                )
            
            # Process critique results
            processed_result = self._process_critique_result(
                critique_result, target_tools, critique_focus, human_review_threshold
            )
            
            # Store in critique history
            self.critique_history.append({
                "timestamp": datetime.now().isoformat(),
                "workflow_metadata": workflow_metadata,
                "strategy": strategy_str,
                "result": processed_result
            })
            
            # Update performance metrics
            self._update_performance_metrics(critique_result)
            
            # A2A coordination: Share critique insights with other tools
            await self._share_critique_insights(processed_result)
            
            self.logger.info("Critique workflow completed successfully")
            return processed_result
            
        except Exception as e:
            self.logger.error(f"Critique workflow failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "critique_result": None,
                "recommendations": [],
                "human_review_points": [],
                "performance_metrics": {}
            }
    
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
    
    def _process_critique_result(self, critique_result: WorkflowCritique, 
                               target_tools: List[str], 
                               critique_focus: List[str],
                               human_review_threshold: float) -> Dict[str, Any]:
        """Process critique result into actionable insights"""
        
        # Filter tool critiques if target tools specified
        tool_critiques = critique_result.tool_critiques
        if target_tools:
            tool_critiques = [
                tc for tc in tool_critiques 
                if tc.tool_type.value in target_tools
            ]
        
        # Filter by critique focus if specified
        if critique_focus:
            tool_critiques = [
                tc for tc in tool_critiques 
                if tc.critique_type.value in critique_focus
            ]
        
        # Identify critical issues requiring human review
        critical_issues = []
        for critique in tool_critiques:
            if (critique.confidence_level in [ConfidenceLevel.LOW, ConfidenceLevel.CRITICAL] or
                critique.quality_score < human_review_threshold):
                critical_issues.append({
                    "tool": critique.tool_type.value,
                    "issue": critique.issue_description,
                    "severity": critique.severity,
                    "confidence": critique.confidence_level.value,
                    "suggestion": critique.constructive_suggestion
                })
        
        # Compile improvement recommendations
        recommendations = []
        for critique in tool_critiques:
            if critique.constructive_suggestion:
                recommendations.append({
                    "tool": critique.tool_type.value,
                    "type": critique.critique_type.value,
                    "suggestion": critique.constructive_suggestion,
                    "impact": critique.performance_impact,
                    "priority": "high" if critique.severity in ["high", "critical"] else "medium"
                })
        
        # Calculate overall quality metrics
        quality_metrics = {
            "overall_quality_score": critique_result.overall_quality_score,
            "workflow_coherence_score": critique_result.workflow_coherence_score,
            "token_efficiency_score": critique_result.token_efficiency_score,
            "correctness_score": critique_result.correctness_score,
            "performance_score": critique_result.performance_score,
            "business_logic_score": critique_result.business_logic_score,
            "swarm_agreement": critique_result.swarm_agreement
        }
        
        return {
            "success": True,
            "critique_result": {
                "tool_critiques": [
                    {
                        "tool_type": tc.tool_type.value,
                        "critique_type": tc.critique_type.value,
                        "severity": tc.severity,
                        "issue_description": tc.issue_description,
                        "constructive_suggestion": tc.constructive_suggestion,
                        "token_optimization": tc.token_optimization,
                        "correctness_issues": tc.correctness_issues,
                        "performance_impact": tc.performance_impact,
                        "quality_score": tc.quality_score,
                        "confidence_level": tc.confidence_level.value,
                        "human_review_needed": tc.human_review_needed
                    }
                    for tc in tool_critiques
                ],
                "quality_metrics": quality_metrics,
                "human_review_points": critique_result.human_review_points,
                "improvement_recommendations": critique_result.improvement_recommendations,
                "consensus_metrics": critique_result.consensus_metrics,
                "critique_metadata": critique_result.critique_metadata
            },
            "critical_issues": critical_issues,
            "recommendations": recommendations,
            "human_review_needed": len(critical_issues) > 0,
            "performance_metrics": {
                "execution_time": critique_result.execution_time,
                "swarm_agreement": critique_result.swarm_agreement,
                "total_critiques": len(tool_critiques)
            }
        }
    
    def _update_performance_metrics(self, critique_result: WorkflowCritique):
        """Update performance metrics based on critique result"""
        self.performance_metrics = {
            "last_execution": datetime.now().isoformat(),
            "total_critiques": len(self.critique_history),
            "average_quality_score": critique_result.overall_quality_score,
            "average_swarm_agreement": critique_result.swarm_agreement,
            "execution_time": critique_result.execution_time,
            "strategy_performance": self.swarm_orchestrator.get_performance_metrics() if self.swarm_orchestrator else {}
        }
    
    async def _share_critique_insights(self, processed_result: Dict[str, Any]):
        """Share critique insights with other tools via A2A coordination"""
        try:
            if self.shared_memory:
                # Store critique insights in shared memory
                await self.shared_memory.store(
                    key=f"critique_insights_{datetime.now().timestamp()}",
                    value={
                        "critical_issues": processed_result.get("critical_issues", []),
                        "recommendations": processed_result.get("recommendations", []),
                        "quality_metrics": processed_result.get("critique_result", {}).get("quality_metrics", {}),
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                self.logger.info("Critique insights shared via A2A coordination")
            
            if self.knowledge_graph:
                # Update knowledge graph with critique insights
                # This would typically involve adding nodes and relationships
                # representing the critique findings and recommendations
                pass
                
        except Exception as e:
            self.logger.warning(f"Failed to share critique insights: {e}")
    
    async def get_critique_history(self) -> List[Dict[str, Any]]:
        """Get critique history for analysis and learning"""
        return self.critique_history
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring and optimization"""
        return self.performance_metrics
    
    async def get_swarm_performance(self) -> Dict[str, Any]:
        """Get swarm performance metrics"""
        if self.swarm_orchestrator:
            return self.swarm_orchestrator.get_performance_metrics()
        return {}
    
    async def analyze_tool_performance(self, tool_name: str) -> Dict[str, Any]:
        """Analyze performance of a specific tool based on critique history"""
        tool_critiques = []
        
        for critique_record in self.critique_history:
            for tool_critique in critique_record.get("result", {}).get("critique_result", {}).get("tool_critiques", []):
                if tool_critique.get("tool_type") == tool_name:
                    tool_critiques.append(tool_critique)
        
        if not tool_critiques:
            return {"error": f"No critique data found for tool: {tool_name}"}
        
        # Calculate performance metrics
        quality_scores = [tc.get("quality_score", 0.0) for tc in tool_critiques]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        critical_issues = [tc for tc in tool_critiques if tc.get("severity") in ["high", "critical"]]
        
        return {
            "tool_name": tool_name,
            "total_critiques": len(tool_critiques),
            "average_quality_score": avg_quality,
            "critical_issues_count": len(critical_issues),
            "common_issues": self._get_common_issues(tool_critiques),
            "improvement_trend": self._calculate_improvement_trend(tool_critiques)
        }
    
    def _get_common_issues(self, tool_critiques: List[Dict[str, Any]]) -> List[str]:
        """Extract common issues from tool critiques"""
        issues = {}
        for critique in tool_critiques:
            issue = critique.get("issue_description", "")
            if issue:
                issues[issue] = issues.get(issue, 0) + 1
        
        # Return top 5 most common issues
        return sorted(issues.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _calculate_improvement_trend(self, tool_critiques: List[Dict[str, Any]]) -> str:
        """Calculate improvement trend based on quality scores over time"""
        if len(tool_critiques) < 2:
            return "insufficient_data"
        
        # This is a simplified trend calculation
        # In a real implementation, you'd use time-series analysis
        quality_scores = [tc.get("quality_score", 0.0) for tc in tool_critiques]
        
        if quality_scores[-1] > quality_scores[0]:
            return "improving"
        elif quality_scores[-1] < quality_scores[0]:
            return "declining"
        else:
            return "stable"