#!/usr/bin/env python3
"""
Workflow Memory Manager - Context & Memory Optimization
====================================================

Optimizes memory usage and context sharing across the 4-tool workflow:
- Intent → Data → Model → Solver

Reduces redundant processing and maintains context throughout the pipeline.

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import json
import time
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class WorkflowContext:
    """Shared context across all workflow stages"""
    workflow_id: str
    user_query: str
    customer_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Stage results
    intent_result: Optional[Dict[str, Any]] = None
    data_result: Optional[Dict[str, Any]] = None
    model_result: Optional[Dict[str, Any]] = None
    solver_result: Optional[Dict[str, Any]] = None
    
    # Performance metrics
    stage_timings: Dict[str, float] = field(default_factory=dict)
    memory_usage: Dict[str, int] = field(default_factory=dict)
    
    # Cached computations
    cached_entities: Dict[str, Any] = field(default_factory=dict)
    cached_analysis: Dict[str, Any] = field(default_factory=dict)

class WorkflowMemoryManager:
    """Manages memory and context across the manufacturing optimization workflow"""
    
    def __init__(self):
        self.active_workflows: Dict[str, WorkflowContext] = {}
        self.global_cache: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, List[float]] = {
            "intent_times": [],
            "data_times": [],
            "model_times": [],
            "solver_times": [],
            "total_times": []
        }
    
    def create_workflow_context(self, user_query: str, customer_id: str) -> WorkflowContext:
        """Create new workflow context with optimized memory allocation"""
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(user_query.encode()).hexdigest()[:8]}"
        
        context = WorkflowContext(
            workflow_id=workflow_id,
            user_query=user_query,
            customer_id=customer_id
        )
        
        self.active_workflows[workflow_id] = context
        logger.info(f"🧠 Created workflow context: {workflow_id}")
        
        return context
    
    def store_intent_result(self, workflow_id: str, intent_result: Dict[str, Any], execution_time: float):
        """Store intent analysis result with context preservation"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        context = self.active_workflows[workflow_id]
        context.intent_result = intent_result
        context.stage_timings["intent"] = execution_time
        
        # Cache key entities for reuse
        if "entities" in intent_result:
            context.cached_entities["intent_entities"] = intent_result["entities"]
        
        # Cache objectives for model building
        if "objectives" in intent_result:
            context.cached_analysis["optimization_objectives"] = intent_result["objectives"]
        
        self.performance_metrics["intent_times"].append(execution_time)
        logger.info(f"🧠 Stored intent result for {workflow_id} in {execution_time:.2f}s")
    
    def store_data_result(self, workflow_id: str, data_result: Dict[str, Any], execution_time: float):
        """Store data analysis result with context preservation"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        context = self.active_workflows[workflow_id]
        context.data_result = data_result
        context.stage_timings["data"] = execution_time
        
        # Cache extracted entities for model building
        if "extracted_data_entities" in data_result:
            context.cached_entities["data_entities"] = data_result["extracted_data_entities"]
        
        # Cache industry context
        if "industry_context" in data_result:
            context.cached_analysis["industry_context"] = data_result["industry_context"]
        
        # Cache sample data for solver
        if "sample_data_generated" in data_result:
            context.cached_analysis["sample_data"] = data_result["sample_data_generated"]
        
        self.performance_metrics["data_times"].append(execution_time)
        logger.info(f"🧠 Stored data result for {workflow_id} in {execution_time:.2f}s")
    
    def store_model_result(self, workflow_id: str, model_result: Dict[str, Any], execution_time: float):
        """Store model building result with context preservation"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        context = self.active_workflows[workflow_id]
        context.model_result = model_result
        context.stage_timings["model"] = execution_time
        
        # Cache model structure for solver
        if "decision_variables" in model_result:
            context.cached_analysis["model_variables"] = model_result["decision_variables"]
        
        if "constraints" in model_result:
            context.cached_analysis["model_constraints"] = model_result["constraints"]
        
        self.performance_metrics["model_times"].append(execution_time)
        logger.info(f"🧠 Stored model result for {workflow_id} in {execution_time:.2f}s")
    
    def store_solver_result(self, workflow_id: str, solver_result: Dict[str, Any], execution_time: float):
        """Store solver result with context preservation"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        context = self.active_workflows[workflow_id]
        context.solver_result = solver_result
        context.stage_timings["solver"] = execution_time
        
        # Cache solution for potential reuse
        if "solution" in solver_result:
            context.cached_analysis["optimal_solution"] = solver_result["solution"]
        
        self.performance_metrics["solver_times"].append(execution_time)
        logger.info(f"🧠 Stored solver result for {workflow_id} in {execution_time:.2f}s")
    
    def get_cached_entities(self, workflow_id: str) -> Dict[str, Any]:
        """Get cached entities to avoid re-extraction"""
        if workflow_id not in self.active_workflows:
            return {}
        
        return self.active_workflows[workflow_id].cached_entities
    
    def get_cached_analysis(self, workflow_id: str) -> Dict[str, Any]:
        """Get cached analysis results to avoid re-computation"""
        if workflow_id not in self.active_workflows:
            return {}
        
        return self.active_workflows[workflow_id].cached_analysis
    
    def get_workflow_context(self, workflow_id: str) -> Optional[WorkflowContext]:
        """Get complete workflow context"""
        return self.active_workflows.get(workflow_id)
    
    def optimize_memory_usage(self, workflow_id: str):
        """Optimize memory usage for a workflow"""
        if workflow_id not in self.active_workflows:
            return
        
        context = self.active_workflows[workflow_id]
        
        # Remove redundant data
        if context.intent_result and "raw_response" in context.intent_result:
            del context.intent_result["raw_response"]
        
        if context.data_result and "raw_response" in context.data_result:
            del context.data_result["raw_response"]
        
        # Compress large objects
        if context.model_result and "generation_metadata" in context.model_result:
            metadata = context.model_result["generation_metadata"]
            if "agent_response" in metadata and len(str(metadata["agent_response"])) > 1000:
                metadata["agent_response"] = "compressed"
        
        logger.info(f"🧠 Optimized memory for workflow {workflow_id}")
    
    def cleanup_workflow(self, workflow_id: str):
        """Clean up workflow context and free memory"""
        if workflow_id in self.active_workflows:
            # Optimize before cleanup
            self.optimize_memory_usage(workflow_id)
            
            # Store final metrics
            context = self.active_workflows[workflow_id]
            total_time = sum(context.stage_timings.values())
            self.performance_metrics["total_times"].append(total_time)
            
            # Remove from active workflows
            del self.active_workflows[workflow_id]
            
            logger.info(f"🧠 Cleaned up workflow {workflow_id} (total time: {total_time:.2f}s)")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary across all workflows"""
        summary = {
            "total_workflows": len(self.performance_metrics["total_times"]),
            "average_times": {},
            "memory_optimization": {
                "active_workflows": len(self.active_workflows),
                "global_cache_size": len(self.global_cache)
            }
        }
        
        for stage, times in self.performance_metrics.items():
            if times:
                summary["average_times"][stage] = sum(times) / len(times)
        
        return summary
    
    def export_workflow_context(self, workflow_id: str) -> Dict[str, Any]:
        """Export workflow context for debugging or analysis"""
        if workflow_id not in self.active_workflows:
            return {}
        
        context = self.active_workflows[workflow_id]
        
        return {
            "workflow_id": context.workflow_id,
            "user_query": context.user_query,
            "customer_id": context.customer_id,
            "timestamp": context.timestamp.isoformat(),
            "stage_timings": context.stage_timings,
            "cached_entities": context.cached_entities,
            "cached_analysis": context.cached_analysis,
            "has_intent_result": context.intent_result is not None,
            "has_data_result": context.data_result is not None,
            "has_model_result": context.model_result is not None,
            "has_solver_result": context.solver_result is not None
        }

# Global memory manager instance
workflow_memory_manager = WorkflowMemoryManager()

def get_memory_manager() -> WorkflowMemoryManager:
    """Get the global workflow memory manager"""
    return workflow_memory_manager
