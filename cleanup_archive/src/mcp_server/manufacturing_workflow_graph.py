#!/usr/bin/env python3
"""
DcisionAI Manufacturing Workflow Graph with Memory Management
===========================================================

Graph-based workflow for manufacturing optimization using Strands Graph pattern.
Implements a sequential pipeline: Intent → Data → Model → Solver
Includes memory management for context preservation and performance optimization.

Based on Strands Graph documentation:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import logging
import time
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import asdict, dataclass, field
from datetime import datetime

# Import Strands Graph components
try:
    from strands import Agent
    from strands.multiagent import GraphBuilder
    from strands_tools import memory, retrieve
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False
    logging.warning("Strands not available - falling back to direct tool calls")

# Import manufacturing tools
from .tools.manufacturing.intent.DcisionAI_Intent_Tool import create_intent_tool
from .tools.manufacturing.data.DcisionAI_Data_Tool import create_data_tool
from .tools.manufacturing.model.DcisionAI_Model_Builder import create_model_builder_tool
from .tools.manufacturing.solver.DcisionAI_Solver_Tool import create_solver_tool

logger = logging.getLogger(__name__)

@dataclass
class WorkflowContext:
    """Shared context across all workflow stages with memory optimization"""
    workflow_id: str
    user_query: str
    customer_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Stage results with memory optimization
    intent_result: Optional[Dict[str, Any]] = None
    data_result: Optional[Dict[str, Any]] = None
    model_result: Optional[Dict[str, Any]] = None
    solver_result: Optional[Dict[str, Any]] = None
    
    # Performance metrics
    stage_timings: Dict[str, float] = field(default_factory=dict)
    memory_usage: Dict[str, int] = field(default_factory=dict)
    
    # Cached computations to avoid redundant processing
    cached_entities: Dict[str, Any] = field(default_factory=dict)
    cached_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Memory optimization flags
    context_optimized: bool = False
    redundant_data_removed: bool = False

class WorkflowMemoryManager:
    """Memory manager integrated into the manufacturing workflow graph"""
    
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
    
    def store_stage_result(self, workflow_id: str, stage: str, result: Dict[str, Any], execution_time: float):
        """Store stage result with memory optimization"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        context = self.active_workflows[workflow_id]
        
        # Store stage result
        setattr(context, f"{stage}_result", result)
        context.stage_timings[stage] = execution_time
        
        # Cache key data for reuse
        if stage == "intent" and "entities" in result:
            context.cached_entities["intent_entities"] = result["entities"]
        elif stage == "data" and "extracted_data_entities" in result:
            context.cached_entities["data_entities"] = result["extracted_data_entities"]
        elif stage == "model" and "decision_variables" in result:
            context.cached_analysis["model_variables"] = result["decision_variables"]
        
        self.performance_metrics[f"{stage}_times"].append(execution_time)
        logger.info(f"🧠 Stored {stage} result for {workflow_id} in {execution_time:.2f}s")
    
    def get_cached_data(self, workflow_id: str) -> Dict[str, Any]:
        """Get cached data to avoid redundant processing"""
        if workflow_id not in self.active_workflows:
            return {}
        
        context = self.active_workflows[workflow_id]
        return {
            "entities": context.cached_entities,
            "analysis": context.cached_analysis
        }
    
    def optimize_memory_usage(self, workflow_id: str):
        """Optimize memory usage for a workflow"""
        if workflow_id not in self.active_workflows:
            return
        
        context = self.active_workflows[workflow_id]
        
        # Remove redundant data
        for stage in ["intent", "data", "model", "solver"]:
            result = getattr(context, f"{stage}_result")
            if result and "raw_response" in result:
                del result["raw_response"]
        
        # Compress large objects
        if context.model_result and "generation_metadata" in context.model_result:
            metadata = context.model_result["generation_metadata"]
            if "agent_response" in metadata and len(str(metadata["agent_response"])) > 1000:
                metadata["agent_response"] = "compressed"
        
        context.context_optimized = True
        logger.info(f"🧠 Optimized memory for workflow {workflow_id}")
    
    def cleanup_workflow(self, workflow_id: str):
        """Clean up workflow context and free memory"""
        if workflow_id in self.active_workflows:
            self.optimize_memory_usage(workflow_id)
            
            context = self.active_workflows[workflow_id]
            total_time = sum(context.stage_timings.values())
            self.performance_metrics["total_times"].append(total_time)
            
            del self.active_workflows[workflow_id]
            logger.info(f"🧠 Cleaned up workflow {workflow_id} (total time: {total_time:.2f}s)")

class ManufacturingWorkflowGraph:
    """Graph-based workflow for manufacturing optimization with Strands memory."""
    
    def __init__(self):
        if not STRANDS_AVAILABLE:
            raise ImportError("Strands is required for Graph-based workflow")
        
        self.logger = logging.getLogger(__name__)
        self.graph = None
        self.memory_agent = None
        self._initialize_memory()
        self._build_workflow_graph()
    
    def _initialize_memory(self):
        """Initialize Strands memory for workflow context management"""
        try:
            # Create memory agent with Strands memory tools
            self.memory_agent = Agent(tools=[memory, retrieve])
            self.logger.info("✅ Strands memory initialized for workflow context management")
        except Exception as e:
            self.logger.warning(f"Strands memory not available: {e}")
            self.memory_agent = None
    
    def _build_workflow_graph(self):
        """Build the manufacturing optimization workflow graph."""
        
        self.logger.info("Building manufacturing optimization workflow graph...")
        
        # Create specialized agents for each step
        intent_agent = Agent(
            name="intent_classifier",
            system_prompt="""You are a manufacturing intent classification specialist. 
            Analyze manufacturing optimization queries and classify them into specific intent categories.
            Focus on production scheduling, capacity planning, inventory optimization, quality control, 
            supply chain, maintenance, cost optimization, demand forecasting, and environmental optimization."""
        )
        
        data_agent = Agent(
            name="data_analyst", 
            system_prompt="""You are a manufacturing data requirements specialist.
            Analyze manufacturing optimization queries and determine what specific data is needed.
            Consider production metrics, quality data, inventory levels, demand forecasts, 
            cost structures, and operational constraints."""
        )
        
        model_agent = Agent(
            name="model_builder",
            system_prompt="""You are a mathematical optimization model builder specialist.
            Build mathematical optimization models based on intent classification and data requirements.
            Create objective functions, constraints, and decision variables for manufacturing optimization problems."""
        )
        
        solver_agent = Agent(
            name="optimization_solver",
            system_prompt="""You are a manufacturing optimization solver specialist.
            Solve mathematical optimization models to find optimal manufacturing configurations.
            Provide specific recommendations for production planning, resource allocation, and operational improvements."""
        )
        
        # Build the graph using GraphBuilder
        builder = GraphBuilder()
        
        # Add nodes (agents)
        builder.add_node(intent_agent, "intent_classification")
        builder.add_node(data_agent, "data_requirements")
        builder.add_node(model_agent, "model_building")
        builder.add_node(solver_agent, "optimization_solving")
        
        # Add edges (dependencies) - sequential pipeline
        builder.add_edge("intent_classification", "data_requirements")
        builder.add_edge("data_requirements", "model_building")
        builder.add_edge("model_building", "optimization_solving")
        
        # Set entry point
        builder.set_entry_point("intent_classification")
        
        # Build the graph
        self.graph = builder.build()
        
        self.logger.info("✅ Manufacturing workflow graph built successfully")
        self.logger.info("📊 Graph structure: Intent → Data → Model → Solver")
    
    def store_workflow_context(self, workflow_id: str, stage: str, data: Dict[str, Any]):
        """Store workflow context in Strands memory"""
        if not self.memory_agent:
            self.logger.warning("Strands memory not available - skipping context storage")
            return
        
        try:
            # Store context in Strands memory
            self.memory_agent.tool.memory(
                action="store",
                content=json.dumps(data, default=str),
                metadata={
                    "workflow_id": workflow_id,
                    "stage": stage,
                    "timestamp": datetime.now().isoformat(),
                    "type": "workflow_context"
                }
            )
            self.logger.info(f"🧠 Stored {stage} context for workflow {workflow_id}")
        except Exception as e:
            self.logger.warning(f"Failed to store context in memory: {e}")
    
    def retrieve_workflow_context(self, workflow_id: str, stage: str) -> Optional[Dict[str, Any]]:
        """Retrieve workflow context from Strands memory"""
        if not self.memory_agent:
            self.logger.warning("Strands memory not available - cannot retrieve context")
            return None
        
        try:
            # Retrieve context from Strands memory
            result = self.memory_agent.tool.retrieve(
                query=f"workflow_id:{workflow_id} stage:{stage}",
                metadata_filter={
                    "workflow_id": workflow_id,
                    "stage": stage,
                    "type": "workflow_context"
                }
            )
            
            if result and result.get("content"):
                return json.loads(result["content"])
            return None
        except Exception as e:
            self.logger.warning(f"Failed to retrieve context from memory: {e}")
            return None
    
    def execute_workflow_with_memory(self, user_query: str, customer_id: str = "default") -> Dict[str, Any]:
        """Execute workflow with memory management using Strands"""
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(user_query.encode()).hexdigest()[:8]}"
        
        self.logger.info(f"🚀 Starting workflow execution with memory management: {workflow_id}")
        
        # Store initial context
        self.store_workflow_context(workflow_id, "start", {
            "user_query": user_query,
            "customer_id": customer_id,
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            # Execute workflow using Strands Graph
            if self.graph:
                result = self.graph.run(user_query)
                
                # Store final result
                self.store_workflow_context(workflow_id, "complete", {
                    "result": result,
                    "workflow_id": workflow_id,
                    "execution_time": time.time()
                })
                
                return {
                    "workflow_id": workflow_id,
                    "result": result,
                    "memory_used": True,
                    "status": "success"
                }
            else:
                raise Exception("Workflow graph not initialized")
                
        except Exception as e:
            self.logger.error(f"❌ Workflow execution failed: {e}")
            
            # Store error context
            self.store_workflow_context(workflow_id, "error", {
                "error": str(e),
                "workflow_id": workflow_id,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "workflow_id": workflow_id,
                "error": str(e),
                "memory_used": True,
                "status": "error"
            }
    
    async def process_manufacturing_request(self, query: str) -> Dict[str, Any]:
        """
        Process a manufacturing optimization request through the graph workflow.
        
        Args:
            query: Manufacturing optimization query
            
        Returns:
            Dictionary with workflow results and recommendations
        """
        try:
            self.logger.info(f"Processing manufacturing request: {query[:100]}...")
            
            # Execute the graph workflow
            result = await self.graph.invoke_async(query)
            
            # Extract results from each node
            workflow_results = {
                "status": result.status.value if hasattr(result.status, 'value') else str(result.status),
                "execution_order": [node.node_id for node in result.execution_order],
                "total_execution_time": result.execution_time,
                "node_results": {}
            }
            
            # Process results from each node
            for node_id, node_result in result.results.items():
                if node_result and node_result.result:
                    # Extract the content from the agent result
                    content = node_result.result.message.content[0].text if hasattr(node_result.result, 'message') else str(node_result.result)
                    
                    workflow_results["node_results"][node_id] = {
                        "content": content,
                        "execution_time": node_result.execution_time,
                        "status": node_result.status.value if hasattr(node_result.status, 'value') else str(node_result.status)
                    }
            
            # Create a comprehensive response
            response = {
                "message": f"Manufacturing optimization workflow completed successfully in {result.execution_time}ms",
                "workflow_results": workflow_results,
                "tools_used": ["intent_classification", "data_requirements", "model_building", "optimization_solving"],
                "tools_available": [
                    "classify_manufacturing_intent",
                    "analyze_data_requirements", 
                    "build_optimization_model",
                    "solve_optimization_problem"
                ],
                "server_ready": True,
                "workflow_type": "strands_graph_sequential_pipeline"
            }
            
            self.logger.info(f"✅ Workflow completed. Nodes executed: {workflow_results['execution_order']}")
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
                "workflow_type": "strands_graph_sequential_pipeline"
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get the current status of the workflow graph."""
        return {
            "workflow_type": "strands_graph_sequential_pipeline",
            "nodes": ["intent_classification", "data_requirements", "model_building", "optimization_solving"],
            "edges": [
                ("intent_classification", "data_requirements"),
                ("data_requirements", "model_building"),
                ("model_building", "optimization_solving")
            ],
            "entry_point": "intent_classification",
            "status": "ready" if self.graph else "not_initialized"
        }


def create_manufacturing_workflow():
    """Create and return a manufacturing workflow graph instance."""
    try:
        return ManufacturingWorkflowGraph()
    except ImportError as e:
        logger.warning(f"Strands not available: {e}")
        return None
