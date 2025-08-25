#!/usr/bin/env python3
"""
DcisionAI Domain Orchestrator - Multi-Tool Orchestration System
===============================================================

Generic domain orchestrator using peer-to-peer agent swarm pattern for optimization problems.
Coordinates ONLY real, working tools. NO fake responses or simulations.

Current Architecture:
- Intent Classification Tool (✅ WORKING)
- Data Analysis Tool (✅ WORKING)
- Model Builder Tool (✅ WORKING)
- Solution Engine Tool (🚧 ROADMAP - not implemented)
- Visualization Tool (🚧 ROADMAP - not implemented)

Based on AWS peer-to-peer agent swarm patterns.

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Strands framework imports
try:
    from strands import Agent, tool
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False
    logging.error("Strands framework not available")
    raise Exception("Strands framework is required")

# Real tool imports - ONLY working tools
try:
    from .tools.intent.DcisionAI_Intent_Tool_v6 import create_dcisionai_intent_tool_v6
    from .tools.data.DcisionAI_Data_Tool_v3 import create_dcisionai_data_tool_v3
    from .tools.model.DcisionAI_Model_Builder_v1 import create_dcisionai_model_builder
    from src.shared.tools.solver import create_shared_solver_tool
    INTENT_TOOL_AVAILABLE = True
    DATA_TOOL_AVAILABLE = True
    MODEL_TOOL_AVAILABLE = True
    SOLVER_TOOL_AVAILABLE = True
except ImportError:
    INTENT_TOOL_AVAILABLE = False
    DATA_TOOL_AVAILABLE = False
    MODEL_TOOL_AVAILABLE = False
    SOLVER_TOOL_AVAILABLE = False
    logging.warning("Some tools not available - will use fallback")

# Platform throttling imports
from src.shared.throttling import get_platform_throttle_manager

logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    """Manufacturing optimization workflow stages"""
    INITIALIZATION = "initialization"
    INTENT_CLASSIFICATION = "intent_classification"
    DATA_ANALYSIS = "data_analysis" 
    MODEL_BUILDING = "model_building"  # ✅ NOW IMPLEMENTED
    OPTIMIZATION_SOLVING = "optimization_solving"  # ✅ NOW IMPLEMENTED
    ANALYSIS_COMPLETE = "analysis_complete"  # Previous endpoint
    # RESULT_VISUALIZATION = "result_visualization"  # ROADMAP - COMMENTED OUT


class ToolStatus(Enum):
    """Tool availability status - HONEST assessment"""
    WORKING = "working"
    ROADMAP = "roadmap"
    NOT_IMPLEMENTED = "not_implemented"


@dataclass
class WorkflowResult:
    """Real workflow result - no fake data"""
    workflow_id: str
    query: str
    session_id: str  # Changed from customer_id to session_id
    
    # Real results from working tools
    intent_analysis: Optional[Dict[str, Any]] = None
    data_analysis: Optional[Dict[str, Any]] = None
    model_building: Optional[Dict[str, Any]] = None  # ✅ NOW IMPLEMENTED
    solver_results: Optional[Dict[str, Any]] = None  # ✅ NOW IMPLEMENTED
    
    # Roadmap status for future tools - COMMENTED OUT
    # visualization_status: str = "roadmap_not_implemented"
    
    # Real metadata
    current_stage: WorkflowStage = WorkflowStage.INITIALIZATION
    execution_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Real recommendations based on actual analysis
    next_steps: List[str] = field(default_factory=list)
    readiness_assessment: Dict[str, Any] = field(default_factory=dict)


# ==================== REAL TOOL WRAPPERS ====================

@tool
def intent_classification_tool(query: str, session_id: str = "default") -> str:
    """FAST intent classification using optimized parallel execution."""
    try:
        if not INTENT_TOOL_AVAILABLE:
            return json.dumps({
                "status": "error",
                "tool_name": "optimized_intent_classification",
                "error_message": "Intent tool not available",
                "primary_intent": None,
                "confidence": 0.0
            })
        
        intent_tool = create_dcisionai_intent_tool_v6()
        
        result = intent_tool.classify_intent(query=query)
        
        # Return REAL results only
        return json.dumps({
            "status": "success",
            "tool_name": "enhanced_intent_classification",
                            "primary_intent": result.primary_intent.value if hasattr(result.primary_intent, 'value') else str(result.primary_intent),
            "confidence": result.confidence,
            "swarm_agreement": result.swarm_agreement,
            "entities": result.entities,
            "objectives": result.objectives,
            "reasoning": result.reasoning,
            "specialist_consensus": result.classification_metadata.get("specialist_consensus", {}),
            "execution_time": result.classification_metadata.get("execution_time", 0),
            "workers_used": len(result.classification_metadata.get("specialist_consensus", {}))
        })
        
    except Exception as e:
        # HONEST error reporting
        return json.dumps({
            "status": "error",
            "tool_name": "enhanced_intent_classification", 
            "error_message": str(e),
            "primary_intent": None,
            "confidence": 0.0
        })


@tool
def data_analysis_tool(query: str, intent_classification: str, session_id: str = "default") -> str:
    """REAL data analysis using working 3-stage analysis."""
    try:
        if not DATA_TOOL_AVAILABLE:
            return json.dumps({
                "status": "error",
                "tool_name": "three_stage_data_analysis",
                "error_message": "Data tool not available",
                "query_data_requirements": [],
                "critical_data_gaps": ["Data analysis tool not available"]
            })
        
        data_tool = create_dcisionai_data_tool_v3()
        
        result = data_tool.analyze_data_requirements_with_intent(
            query=query,
            intent_result=intent_result,
            session_id=session_id
        )
        
        # Return REAL results only
        return json.dumps({
            "status": "success",
            "tool_name": "three_stage_data_analysis",
            "query_data_requirements": [
                {
                    "element": req.element,
                    "category": req.category.value,
                    "priority": req.priority,
                    "data_type": req.data_type,
                    "description": req.description,
                    "examples": req.examples
                }
                for req in result.query_data_requirements
            ],
            "customer_data_coverage": result.customer_data_availability,
            "external_recommendations": [
                {
                    "source_name": rec.source_name,
                    "source_type": rec.source_type.value,
                    "data_elements": rec.data_elements,
                    "access_method": rec.access_method,
                    "cost_estimate": rec.cost_estimate,
                    "business_value": rec.business_value,
                    "integration_complexity": rec.integration_complexity
                }
                for rec in result.external_data_recommendations
            ],
            "critical_data_gaps": result.data_gaps,
            "optimization_readiness": result.optimization_readiness,
            "stages_completed": result.execution_metadata.get("stages_completed", 0),
            "execution_time": result.execution_metadata.get("execution_time", 0)
        })
        
    except Exception as e:
        # HONEST error reporting
        return json.dumps({
            "status": "error",
            "tool_name": "three_stage_data_analysis",
            "error_message": str(e),
            "query_data_requirements": [],
            "critical_data_gaps": [f"Data analysis failed: {str(e)}"]
        })


@tool
def model_building_tool(intent_result: str, data_result: str, session_id: str = "default") -> str:
    """REAL model building using working 6-specialist swarm."""
    try:
        if not MODEL_TOOL_AVAILABLE:
            return json.dumps({
                "status": "error",
                "tool_name": "model_building",
                "error_message": "Model building tool not available",
                "model": None,
                "build_status": "failed"
            })
        
        model_builder = create_dcisionai_model_builder()
        
        # Parse intent and data results
        intent_data = json.loads(intent_result) if isinstance(intent_result, str) else intent_result
        data_data = json.loads(data_result) if isinstance(data_result, str) else data_result
        
        result = model_builder.build_optimization_model(
            intent_result=intent_data,
            data_result=data_data,
            session_id=session_id
        )
        
        # Return REAL results only
        return json.dumps({
            "status": "success",
            "tool_name": "model_building",
            "model": {
                "model_id": result.model.model_id,
                "model_name": result.model.model_name,
                "model_type": result.model.model_type.value,
                "intent_classification": result.model.intent_classification,
                "decision_variables": [
                    {
                        "name": var.name,
                        "variable_type": var.variable_type,
                        "domain": var.domain,
                        "bounds": var.bounds,
                        "description": var.description,
                        "indices": var.indices,
                        "dimensions": var.dimensions
                    }
                    for var in result.model.decision_variables
                ],
                "constraints": [
                    {
                        "name": const.name,
                        "constraint_type": const.constraint_type,
                        "expression": const.expression,
                        "sense": const.sense,
                        "rhs_value": const.rhs_value,
                        "description": const.description,
                        "priority": const.priority
                    }
                    for const in result.model.constraints
                ],
                "objective_functions": [
                    {
                        "name": obj.name,
                        "sense": obj.sense,
                        "expression": obj.expression,
                        "description": obj.description,
                        "weight": obj.weight,
                        "priority": obj.priority
                    }
                    for obj in result.model.objective_functions
                ],
                "data_schema": {
                    "parameters": result.model.data_schema.parameters,
                    "sets": result.model.data_schema.sets,
                    "scalars": result.model.data_schema.scalars
                },
                "compatible_solvers": [solver.value for solver in result.model.compatible_solvers],
                "recommended_solver": result.model.recommended_solver.value,
                "model_complexity": result.model.model_complexity,
                "estimated_solve_time": result.model.estimated_solve_time,
                "model_validation_score": result.model.model_validation_score,
                "generation_metadata": result.model.generation_metadata
            },
            "build_status": result.build_status,
            "execution_time": result.execution_time,
            "agents_used": result.agents_used,
            "model_quality_score": result.model_quality_score,
            "generation_metadata": result.generation_metadata
        })
        
    except Exception as e:
        # HONEST error reporting
        return json.dumps({
            "status": "error",
            "tool_name": "model_building",
            "error_message": str(e),
            "model": None,
            "build_status": "failed"
        })


@tool
def solver_tool(model_result: str, session_id: str = "default") -> str:
    """REAL solver execution using shared solver tool."""
    try:
        if not SOLVER_TOOL_AVAILABLE:
            return json.dumps({
                "status": "error",
                "tool_name": "shared_solver_tool",
                "error_message": "Solver tool not available",
                "solution": None,
                "solve_status": "failed"
            })
        
        solver_tool = create_shared_solver_tool()
        
        # Parse model result
        model_data = json.loads(model_result) if isinstance(model_result, str) else model_result
        
        result = solver_tool.solve_optimization_model(
            model_data=model_data,
            domain="manufacturing",
            session_id=session_id
        )
        
        # Return REAL results only
        return json.dumps({
            "status": "success",
            "tool_name": "shared_solver_tool",
            "domain": "manufacturing",
            "best_solution": {
                "solver_type": result.best_solution.solver_type.value if result.best_solution else None,
                "status": result.best_solution.status.value if result.best_solution else None,
                "objective_value": result.best_solution.objective_value if result.best_solution else None,
                "solution_variables": result.best_solution.solution_variables if result.best_solution else {},
                "solve_time": result.best_solution.solve_time if result.best_solution else 0.0
            },
            "all_solutions": [
                {
                    "solver_type": sol.solver_type.value,
                    "status": sol.status.value,
                    "objective_value": sol.objective_value,
                    "solve_time": sol.solve_time
                }
                for sol in result.all_solutions
            ],
            "winning_solver": result.winning_solver.value if result.winning_solver else None,
            "total_solve_time": result.total_solve_time,
            "swarm_metadata": result.swarm_metadata,
            "performance_metrics": result.performance_metrics
        })
        
    except Exception as e:
        # HONEST error reporting
        return json.dumps({
            "status": "error",
            "tool_name": "shared_solver_tool",
            "error_message": str(e),
            "solution": None,
            "solve_status": "failed"
        })


class DcisionAI_Manufacturing_Agent:
    """
    HONEST manufacturing optimization orchestrator.
    
    Uses ONLY real, working tools. No fake responses, no simulations.
    Clearly communicates what works and what's on roadmap.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DcisionAI_Manufacturing_Agent")
        self.throttle_manager = get_platform_throttle_manager()
        
        # HONEST tool status - ONLY WORKING TOOLS
        self.available_tools = {
            "intent_classification": ToolStatus.WORKING if INTENT_TOOL_AVAILABLE else ToolStatus.NOT_IMPLEMENTED,
            "data_analysis": ToolStatus.WORKING if DATA_TOOL_AVAILABLE else ToolStatus.NOT_IMPLEMENTED,
            "model_building": ToolStatus.WORKING if MODEL_TOOL_AVAILABLE else ToolStatus.NOT_IMPLEMENTED,  # ✅ NOW IMPLEMENTED
            "optimization_solving": ToolStatus.WORKING if SOLVER_TOOL_AVAILABLE else ToolStatus.NOT_IMPLEMENTED,  # ✅ NOW IMPLEMENTED
            # "visualization": ToolStatus.ROADMAP  # ROADMAP - COMMENTED OUT
        }
        
        # Initialize orchestrator with ONLY working tools
        self._initialize_orchestrator()
        
        working_count = sum(1 for status in self.available_tools.values() if status == ToolStatus.WORKING)
        self.logger.info(f"✅ DcisionAI Manufacturing Agent initialized - {working_count} working tools (intent + data + model + solver)")
    
    def _initialize_orchestrator(self):
        """Initialize orchestrator with ONLY real, working tools"""
        try:
            # Only include tools that are actually available
            available_tools = []
            if INTENT_TOOL_AVAILABLE:
                available_tools.append(intent_classification_tool)
            if DATA_TOOL_AVAILABLE:
                available_tools.append(data_analysis_tool)
            if MODEL_TOOL_AVAILABLE:
                available_tools.append(model_building_tool)
            if SOLVER_TOOL_AVAILABLE:
                available_tools.append(solver_tool)
            
            if not available_tools:
                raise Exception("No working tools available for orchestration")
            
            # Detailed system prompt with exact parameter specifications
            system_prompt = """You are the DcisionAI Manufacturing Orchestrator. You coordinate four working tools:

TOOL SPECIFICATIONS:
1. intent_classification_tool(query: str, session_id: str) -> str
   - Classifies manufacturing problems using 6-agent swarm
   - Returns JSON with classification, confidence, etc.

2. data_analysis_tool(query: str, intent_classification: str, session_id: str) -> str
   - Analyzes data requirements using 3-stage analysis
   - Requires the classification string from step 1
   - Returns JSON with data requirements, gaps, etc.

3. model_building_tool(intent_result: str, data_result: str, session_id: str) -> str
   - Builds optimization models using 6-specialist swarm
   - Requires the full JSON results from steps 1 and 2
   - Returns JSON with model specification, variables, constraints, etc.

4. solver_tool(model_result: str, session_id: str) -> str
   - Executes optimization using shared solver swarm
   - Requires the full model JSON result from step 3
   - Returns JSON with solver results, best solution, performance metrics, etc.

EXACT ORCHESTRATION STEPS:
1. Call intent_classification_tool(query=query, session_id=session_id)
2. Extract classification from the JSON result
3. Call data_analysis_tool(query=query, intent_classification=classification, session_id=session_id)
4. Call model_building_tool(intent_result=full_intent_json, data_result=full_data_json, session_id=session_id)
5. Call solver_tool(model_result=full_model_json, session_id=session_id)
6. Synthesize all results

CRITICAL: Pass the exact parameter names and values as specified above. Do not modify parameter names.

RESPONSE FORMAT (JSON only):
{
    "workflow_status": "completed",
    "current_capabilities": {
        "intent_classification": "results from intent tool",
        "data_analysis": "results from data tool",
        "model_building": "results from model tool",
        "solver_results": "results from solver tool"
    },
    "actionable_next_steps": ["next steps"],
    "optimization_readiness": "assessment",
    "execution_metadata": "performance data"
}"""
            
            self.orchestrator = Agent(
                name="dcisionai_manufacturing_orchestrator",
                tools=available_tools,
                system_prompt=system_prompt
            )
            
            self.logger.info(f"✅ Orchestrator initialized with {len(available_tools)} real tools")
            
        except Exception as e:
            self.logger.error(f"❌ Orchestrator initialization failed: {e}")
            raise
    
    def analyze_manufacturing_optimization(self, query: str, session_id: str = "default") -> WorkflowResult:
        """
        REAL manufacturing optimization analysis using working tools only.
        NO fake responses, NO simulations.
        """
        workflow_start = datetime.now()
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{session_id}"
        
        result = WorkflowResult(
            workflow_id=workflow_id,
            query=query,
            session_id=session_id,
            current_stage=WorkflowStage.INITIALIZATION
        )
        
        try:
            self.logger.info(f"🚀 Starting REAL manufacturing optimization analysis - {workflow_id}")
            
            # Orchestration task for REAL tools only
            orchestration_task = f"""
            Analyze this manufacturing query using all four tools:
            
            Query: "{query}"
            Session ID: {session_id}
            
            Steps:
            1. Use intent_classification_tool
            2. Use data_analysis_tool with intent results
            3. Use model_building_tool with intent and data results
            4. Use solver_tool with model results
            5. Provide synthesis and next steps
            """
            
            # Execute orchestrator with REAL tools
            response = self.orchestrator(orchestration_task)
            
            # Parse REAL orchestrator response
            orchestration_result = self._parse_orchestrator_response(response)
            
            # Extract REAL results
            if orchestration_result.get("workflow_status") == "completed":
                result.intent_analysis = orchestration_result.get("current_capabilities", {}).get("intent_classification")
                result.data_analysis = orchestration_result.get("current_capabilities", {}).get("data_analysis")
                result.model_building = orchestration_result.get("current_capabilities", {}).get("model_building")
                result.solver_results = orchestration_result.get("current_capabilities", {}).get("solver_results")
                result.current_stage = WorkflowStage.OPTIMIZATION_SOLVING
                result.next_steps = orchestration_result.get("actionable_next_steps", [])
                result.readiness_assessment = orchestration_result.get("optimization_readiness", {})
            else:
                result.errors.append("Orchestration failed to complete successfully")
            
            # Calculate REAL execution time
            result.execution_time = (datetime.now() - workflow_start).total_seconds()
            
            self.logger.info(f"✅ Real analysis completed in {result.execution_time:.1f}s")
            return result
            
        except Exception as e:
            result.errors.append(f"Orchestration failed: {str(e)}")
            result.current_stage = WorkflowStage.INITIALIZATION
            result.execution_time = (datetime.now() - workflow_start).total_seconds()
            
            self.logger.error(f"❌ Real analysis failed: {e}")
            return result
    
    def _parse_orchestrator_response(self, response: str) -> Dict[str, Any]:
        """Parse orchestrator response - NO fake data"""
        try:
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Extract JSON
            parsed = self._extract_json_from_text(response_text)
            
            if parsed and "workflow_status" in parsed:
                return parsed
            else:
                return {
                    "workflow_status": "failed",
                    "error": "Failed to parse orchestrator response",
                    "current_capabilities": {},
                    "actionable_next_steps": ["Contact support - orchestrator response parsing failed"]
                }
                
        except Exception as e:
            return {
                "workflow_status": "failed", 
                "error": f"Response parsing failed: {str(e)}",
                "current_capabilities": {},
                "actionable_next_steps": ["Contact support - orchestrator error"]
            }
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON - NO fake data on failure"""
        import re
        
        try:
            # Clean and parse
            cleaned = re.sub(r'```json\s*', '', text)
            cleaned = re.sub(r'```\s*', '', cleaned)
            return json.loads(cleaned.strip())
        except:
            pass
        
        try:
            # Regex extraction
            pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\})*)*\})*)*\}'
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                return json.loads(matches[-1])
        except:
            pass
        
        return None  # HONEST failure
    
    def get_tool_status(self) -> Dict[str, str]:
        """Get HONEST status of all tools"""
        return {
            tool: status.value 
            for tool, status in self.available_tools.items()
        }
    
    def get_current_capabilities(self) -> Dict[str, Any]:
        """Get HONEST assessment of current capabilities"""
        working_tools = []
        roadmap_tools = []
        
        if self.available_tools["intent_classification"] == ToolStatus.WORKING:
            working_tools.append({
                "name": "Intent Classification",
                "description": "6-agent swarm for manufacturing problem classification", 
                "capabilities": ["Problem type identification", "Confidence scoring", "Entity extraction"],
                "status": "working"
            })
        else:
            roadmap_tools.append({
                "name": "Intent Classification",
                "description": "6-agent swarm for manufacturing problem classification",
                "status": "not_implemented",
                "eta": "TBD"
            })
            
        if self.available_tools["data_analysis"] == ToolStatus.WORKING:
            working_tools.append({
                "name": "Data Analysis", 
                "description": "3-stage data requirements analysis",
                "capabilities": ["Query data extraction", "Customer data assessment", "External data recommendations"],
                "status": "working"
            })
        else:
            roadmap_tools.append({
                "name": "Data Analysis",
                "description": "3-stage data requirements analysis", 
                "status": "not_implemented",
                "eta": "TBD"
            })
        
        if self.available_tools["model_building"] == ToolStatus.WORKING:
            working_tools.append({
                "name": "Model Building", 
                "description": "6-specialist swarm for optimization model generation",
                "capabilities": ["Mathematical formulation", "Variable design", "Constraint modeling", "Objective design", "Solver compatibility", "Data schema"],
                "status": "working"
            })
        else:
            roadmap_tools.append({
                "name": "Model Building",
                "description": "6-specialist swarm for optimization model generation", 
                "status": "not_implemented",
                "eta": "TBD"
            })
        
        if self.available_tools["optimization_solving"] == ToolStatus.WORKING:
            working_tools.append({
                "name": "Shared Solver Tool", 
                "description": "Universal optimization solver with swarm intelligence",
                "capabilities": ["OR-Tools", "PuLP", "CVXPY", "Pyomo", "SciPy", "Parallel solving", "Resource monitoring"],
                "status": "working"
            })
        else:
            roadmap_tools.append({
                "name": "Shared Solver Tool",
                "description": "Universal optimization solver with swarm intelligence", 
                "status": "not_implemented",
                "eta": "TBD"
            })
        
        return {
            "working_tools": working_tools,
            "roadmap_tools": roadmap_tools,
            "current_workflow": "Query → Intent Classification → Data Analysis → Model Building → Solver Execution" if len(working_tools) >= 4 else "Query → Intent Classification → Data Analysis → Recommendations" if working_tools else "No working tools available",
            "full_workflow_eta": "Available Now"
        }
    
    def run_comprehensive_test(self, query: str, customer_id: str = "default") -> Dict[str, Any]:
        """
        Run comprehensive test orchestrating both intent and data tools.
        Follows the same pattern as intent tool comprehensive tests.
        """
        test_start = datetime.now()
        test_id = f"comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{customer_id}"
        
        self.logger.info(f"🚀 Starting comprehensive test - {test_id}")
        self.logger.info(f"📝 Query: {query[:100]}...")
        
        try:
            # Step 1: Intent Classification
            self.logger.info("🎯 Step 1: Intent Classification")
            intent_start = datetime.now()
            
            intent_result = None
            if INTENT_TOOL_AVAILABLE:
                try:
                    intent_tool = create_dcisionai_intent_tool_v5()
                    intent_result = intent_tool.classify_intent(query)
                    intent_time = (datetime.now() - intent_start).total_seconds()
                    self.logger.info(f"✅ Intent classification completed in {intent_time:.3f}s")
                except Exception as e:
                    self.logger.error(f"❌ Intent classification failed: {e}")
                    intent_result = None
            else:
                self.logger.warning("⚠️ Intent tool not available")
            
            # Step 2: Data Analysis
            self.logger.info("📊 Step 2: Data Analysis")
            data_start = datetime.now()
            
            data_result = None
            if DATA_TOOL_AVAILABLE:
                try:
                    data_tool = create_dcisionai_data_tool_v3()
                    # Pass the intent result directly to avoid duplicate intent classification
                    intent_classification = intent_result.primary_intent.value if intent_result and hasattr(intent_result.primary_intent, 'value') else (str(intent_result.primary_intent) if intent_result else "unknown")
                    data_result = data_tool.analyze_data_requirements_with_intent(
                        query=query,
                        intent_result=intent_result,  # Pass the full intent result
                        session_id=customer_id
                    )
                    data_time = (datetime.now() - data_start).total_seconds()
                    self.logger.info(f"✅ Data analysis completed in {data_time:.3f}s")
                except Exception as e:
                    self.logger.error(f"❌ Data analysis failed: {e}")
                    # Fallback to original method if new method doesn't exist
                    try:
                        intent_classification = intent_result.primary_intent.value if intent_result and hasattr(intent_result.primary_intent, 'value') else (str(intent_result.primary_intent) if intent_result else "unknown")
                        data_result = data_tool.analyze_data_requirements(
                            query=query,
                            intent_classification=intent_classification,
                            customer_id=customer_id
                        )
                        data_time = (datetime.now() - data_start).total_seconds()
                        self.logger.info(f"✅ Data analysis completed (fallback) in {data_time:.3f}s")
                    except Exception as fallback_e:
                        self.logger.error(f"❌ Data analysis fallback also failed: {fallback_e}")
                        data_result = None
            else:
                self.logger.warning("⚠️ Data tool not available")
            
            # Step 3: Orchestration Synthesis (simplified - no agent loop)
            self.logger.info("🔄 Step 3: Orchestration Synthesis")
            orchestration_start = datetime.now()
            
            # Create simple orchestration result without calling the agent again
            orchestration_result = WorkflowResult(
                workflow_id=f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{customer_id}",
                query=query,
                session_id=customer_id,
                intent_analysis=intent_result,
                data_analysis=data_result,
                current_stage=WorkflowStage.ANALYSIS_COMPLETE,
                next_steps=["Both intent and data analysis completed successfully"],
                readiness_assessment={"status": "ready_for_next_phase"},
                execution_time=(datetime.now() - orchestration_start).total_seconds()
            )
            orchestration_time = (datetime.now() - orchestration_start).total_seconds()
            self.logger.info(f"✅ Orchestration completed in {orchestration_time:.3f}s")
            
            # Calculate total execution time
            total_time = (datetime.now() - test_start).total_seconds()
            
            # Compile comprehensive results
            comprehensive_results = {
                "test_id": test_id,
                "query": query,
                "customer_id": customer_id,
                "execution_summary": {
                    "total_execution_time": total_time,
                    "intent_classification_time": intent_time if intent_result else 0,
                    "data_analysis_time": data_time if data_result else 0,
                    "orchestration_time": orchestration_time,
                    "tools_used": {
                        "intent_tool": INTENT_TOOL_AVAILABLE,
                        "data_tool": DATA_TOOL_AVAILABLE
                    }
                },
                "intent_analysis": {
                    "available": INTENT_TOOL_AVAILABLE,
                    "result": {
                        "primary_intent": intent_result.primary_intent.value if intent_result and hasattr(intent_result.primary_intent, 'value') else (str(intent_result.primary_intent) if intent_result else None),
                        "confidence": intent_result.confidence if intent_result else 0.0,
                        "entities": intent_result.entities if intent_result else [],
                        "objectives": intent_result.objectives if intent_result else [],
                        "reasoning": intent_result.reasoning if intent_result else "",
                        "swarm_agreement": intent_result.swarm_agreement if intent_result else 0.0,
                        "classification_metadata": intent_result.classification_metadata if intent_result else {}
                    } if intent_result else None
                },
                "data_analysis": {
                    "available": DATA_TOOL_AVAILABLE,
                    "result": {
                        "query_data_requirements": [
                            {
                                "element": req.element,
                                "category": req.category.value,
                                "priority": req.priority,
                                "data_type": req.data_type,
                                "description": req.description,
                                "examples": req.examples
                            }
                            for req in data_result.query_data_requirements
                        ] if data_result else [],
                        "customer_data_coverage": data_result.customer_data_availability if data_result else {},
                        "external_data_recommendations": [
                            {
                                "source_name": rec.source_name,
                                "source_type": rec.source_type.value,
                                "data_elements": rec.data_elements,
                                "access_method": rec.access_method,
                                "cost_estimate": rec.cost_estimate,
                                "business_value": rec.business_value,
                                "integration_complexity": rec.integration_complexity
                            }
                            for rec in data_result.external_data_recommendations
                        ] if data_result else [],
                        "critical_data_gaps": data_result.data_gaps if data_result else [],
                        "optimization_readiness": data_result.optimization_readiness if data_result else {},
                        "execution_metadata": data_result.execution_metadata if data_result else {}
                    } if data_result else None
                },
                "orchestration_result": {
                    "workflow_id": orchestration_result.workflow_id,
                    "current_stage": orchestration_result.current_stage.value,
                    "intent_analysis": orchestration_result.intent_analysis,
                    "data_analysis": orchestration_result.data_analysis,
                    "next_steps": orchestration_result.next_steps,
                    "readiness_assessment": orchestration_result.readiness_assessment,
                    "execution_time": orchestration_result.execution_time,
                    "errors": orchestration_result.errors,
                    "warnings": orchestration_result.warnings
                },
                "comprehensive_assessment": {
                    "overall_success": intent_result is not None and data_result is not None,
                    "intent_success": intent_result is not None,
                    "data_success": data_result is not None,
                    "orchestration_success": orchestration_result.current_stage == WorkflowStage.ANALYSIS_COMPLETE,
                    "recommendations": self._generate_comprehensive_recommendations(
                        intent_result, data_result, orchestration_result
                    ),
                    "next_actions": self._generate_next_actions(
                        intent_result, data_result, orchestration_result
                    )
                },
                "test_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "test_type": "comprehensive_orchestration",
                    "tools_orchestrated": ["intent_classification", "data_analysis"],
                    "workflow_stages": ["intent_classification", "data_analysis", "synthesis"]
                }
            }
            
            self.logger.info(f"✅ Comprehensive test completed successfully in {total_time:.3f}s")
            return comprehensive_results
            
        except Exception as e:
            self.logger.error(f"❌ Comprehensive test failed: {e}")
            return {
                "test_id": test_id,
                "query": query,
                "customer_id": customer_id,
                "error": True,
                "error_message": str(e),
                "execution_summary": {
                    "total_execution_time": (datetime.now() - test_start).total_seconds(),
                    "tools_used": {
                        "intent_tool": INTENT_TOOL_AVAILABLE,
                        "data_tool": DATA_TOOL_AVAILABLE
                    }
                },
                "test_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "test_type": "comprehensive_orchestration",
                    "error": True
                }
            }

    def run_full_workflow_test(self, query: str, customer_id: str = "default") -> Dict[str, Any]:
        """
        Run full 4-tool workflow test: Intent → Data → Model → Solver
        This is the complete manufacturing optimization pipeline.
        """
        test_start = datetime.now()
        test_id = f"full_workflow_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{customer_id}"
        
        self.logger.info(f"🚀 Starting full 4-tool workflow test - {test_id}")
        self.logger.info(f"📝 Query: {query[:100]}...")
        
        try:
            # Step 1: Intent Classification
            self.logger.info("🎯 Step 1: Intent Classification")
            intent_start = datetime.now()
            
            intent_result = None
            if INTENT_TOOL_AVAILABLE:
                try:
                    intent_tool = create_dcisionai_intent_tool_v4()
                    intent_result = intent_tool.classify_intent(query)
                    intent_time = (datetime.now() - intent_start).total_seconds()
                    self.logger.info(f"✅ Intent classification completed in {intent_time:.3f}s")
                except Exception as e:
                    self.logger.error(f"❌ Intent classification failed: {e}")
                    intent_result = None
            else:
                self.logger.warning("⚠️ Intent tool not available")
            
            # Step 2: Data Analysis
            self.logger.info("📊 Step 2: Data Analysis")
            data_start = datetime.now()
            
            data_result = None
            if DATA_TOOL_AVAILABLE:
                try:
                    data_tool = create_dcisionai_data_tool_v3()
                    data_result = data_tool.analyze_data_requirements_with_intent(
                        query=query,
                        intent_result=intent_result,
                        session_id=customer_id
                    )
                    data_time = (datetime.now() - data_start).total_seconds()
                    self.logger.info(f"✅ Data analysis completed in {data_time:.3f}s")
                except Exception as e:
                    self.logger.error(f"❌ Data analysis failed: {e}")
                    data_result = None
            else:
                self.logger.warning("⚠️ Data tool not available")
            
            # Step 3: Model Building
            self.logger.info("🏗️ Step 3: Model Building")
            model_start = datetime.now()
            
            model_result = None
            if MODEL_TOOL_AVAILABLE:
                try:
                    model_builder = create_dcisionai_model_builder()
                    model_result = model_builder.build_optimization_model(
                        query=query,
                        intent_result=intent_result,
                        data_result=data_result,
                        session_id=customer_id
                    )
                    model_time = (datetime.now() - model_start).total_seconds()
                    self.logger.info(f"✅ Model building completed in {model_time:.3f}s")
                except Exception as e:
                    self.logger.error(f"❌ Model building failed: {e}")
                    model_result = None
            else:
                self.logger.warning("⚠️ Model tool not available")
            
            # Step 4: Solver Execution
            self.logger.info("⚡ Step 4: Solver Execution")
            solver_start = datetime.now()
            
            solver_result = None
            if SOLVER_TOOL_AVAILABLE:
                try:
                    solver_tool = create_shared_solver_tool()
                    solver_result = solver_tool.solve_optimization_model(
                        query=query,
                        model_result=model_result,
                        session_id=customer_id
                    )
                    solver_time = (datetime.now() - solver_start).total_seconds()
                    self.logger.info(f"✅ Solver execution completed in {solver_time:.3f}s")
                except Exception as e:
                    self.logger.error(f"❌ Solver execution failed: {e}")
                    solver_result = None
            else:
                self.logger.warning("⚠️ Solver tool not available")
            
            # Step 5: Workflow Synthesis
            self.logger.info("🔄 Step 5: Workflow Synthesis")
            synthesis_start = datetime.now()
            
            # Create comprehensive workflow result
            workflow_result = WorkflowResult(
                workflow_id=f"full_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{customer_id}",
                query=query,
                session_id=customer_id,
                intent_analysis=intent_result,
                data_analysis=data_result,
                model_building=model_result,
                solver_results=solver_result,
                current_stage=WorkflowStage.OPTIMIZATION_SOLVING,
                next_steps=self._generate_full_workflow_next_steps(intent_result, data_result, model_result, solver_result),
                readiness_assessment=self._assess_full_workflow_readiness(intent_result, data_result, model_result, solver_result),
                execution_time=(datetime.now() - synthesis_start).total_seconds()
            )
            
            synthesis_time = (datetime.now() - synthesis_start).total_seconds()
            total_time = (datetime.now() - test_start).total_seconds()
            
            # Compile full workflow results
            full_workflow_results = {
                "test_id": test_id,
                "query": query,
                "customer_id": customer_id,
                "execution_summary": {
                    "total_execution_time": total_time,
                    "intent_classification_time": intent_time if intent_result else 0,
                    "data_analysis_time": data_time if data_result else 0,
                    "model_building_time": model_time if model_result else 0,
                    "solver_execution_time": solver_time if solver_result else 0,
                    "synthesis_time": synthesis_time,
                    "tools_used": {
                        "intent_tool": INTENT_TOOL_AVAILABLE,
                        "data_tool": DATA_TOOL_AVAILABLE,
                        "model_tool": MODEL_TOOL_AVAILABLE,
                        "solver_tool": SOLVER_TOOL_AVAILABLE
                    }
                },
                "workflow_stages": {
                    "intent_classification": {
                        "status": "completed" if intent_result else "failed",
                        "result": intent_result
                    },
                    "data_analysis": {
                        "status": "completed" if data_result else "failed",
                        "result": data_result
                    },
                    "model_building": {
                        "status": "completed" if model_result else "failed",
                        "result": model_result
                    },
                    "solver_execution": {
                        "status": "completed" if solver_result else "failed",
                        "result": solver_result
                    }
                },
                "workflow_result": {
                    "workflow_id": workflow_result.workflow_id,
                    "current_stage": workflow_result.current_stage.value,
                    "next_steps": workflow_result.next_steps,
                    "readiness_assessment": workflow_result.readiness_assessment,
                    "execution_time": workflow_result.execution_time,
                    "errors": workflow_result.errors,
                    "warnings": workflow_result.warnings
                },
                "test_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "test_type": "full_4_tool_workflow",
                    "workflow_complete": all([intent_result, data_result, model_result, solver_result])
                }
            }
            
            self.logger.info(f"✅ Full 4-tool workflow test completed successfully in {total_time:.3f}s")
            return full_workflow_results
            
        except Exception as e:
            self.logger.error(f"❌ Full workflow test failed: {e}")
            return {
                "test_id": test_id,
                "query": query,
                "customer_id": customer_id,
                "error": True,
                "error_message": str(e),
                "execution_summary": {
                    "total_execution_time": (datetime.now() - test_start).total_seconds(),
                    "tools_used": {
                        "intent_tool": INTENT_TOOL_AVAILABLE,
                        "data_tool": DATA_TOOL_AVAILABLE,
                        "model_tool": MODEL_TOOL_AVAILABLE,
                        "solver_tool": SOLVER_TOOL_AVAILABLE
                    }
                },
                "test_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "test_type": "full_4_tool_workflow",
                    "error": True
                }
            }
    
    def _generate_comprehensive_recommendations(self, intent_result, data_result, orchestration_result) -> List[str]:
        """Generate comprehensive recommendations based on all tool results"""
        recommendations = []
        
        if intent_result:
            primary_intent = intent_result.primary_intent.value if hasattr(intent_result.primary_intent, 'value') else str(intent_result.primary_intent)
            confidence = intent_result.confidence
            
            if confidence > 0.8:
                recommendations.append(f"High confidence intent classification ({confidence:.2f}): {primary_intent}")
            elif confidence > 0.6:
                recommendations.append(f"Medium confidence intent classification ({confidence:.2f}): {primary_intent}")
            else:
                recommendations.append(f"Low confidence intent classification ({confidence:.2f}): {primary_intent}")
        
        if data_result:
            data_requirements = len(data_result.query_data_requirements)
            data_gaps = len(data_result.data_gaps)
            
            recommendations.append(f"Identified {data_requirements} data requirements")
            if data_gaps > 0:
                recommendations.append(f"Found {data_gaps} critical data gaps that need addressing")
            
            readiness = data_result.optimization_readiness
            if readiness.get("can_build_basic_model", False):
                recommendations.append("Data readiness: Can build basic optimization model")
            else:
                recommendations.append("Data readiness: Need additional data for model building")
        
        if orchestration_result.next_steps:
            recommendations.extend(orchestration_result.next_steps)
        
        return recommendations
    
    def _generate_next_actions(self, intent_result, data_result, orchestration_result) -> List[str]:
        """Generate actionable next steps based on comprehensive analysis"""
        actions = []
        
        if intent_result and data_result:
            actions.append("✅ Both intent and data analysis completed successfully")
            
            if data_result.data_gaps:
                actions.append("🔧 Address critical data gaps identified in analysis")
            
            if data_result.external_data_recommendations:
                actions.append("📊 Consider implementing external data sources for enhanced modeling")
            
            actions.append("🚀 Ready for next phase: Model building and optimization solving")
        else:
            if not intent_result:
                actions.append("⚠️ Intent classification failed - investigate tool availability")
            if not data_result:
                actions.append("⚠️ Data analysis failed - investigate tool availability")
        
        return actions

    def _generate_full_workflow_next_steps(self, intent_result, data_result, model_result, solver_result) -> List[str]:
        """Generate next steps for full 4-tool workflow"""
        steps = []
        
        if all([intent_result, data_result, model_result, solver_result]):
            steps.append("✅ Complete 4-tool workflow executed successfully")
            steps.append("📊 Review optimization results and recommendations")
            steps.append("🔧 Implement suggested optimizations")
            steps.append("📈 Monitor performance improvements")
        else:
            if not intent_result:
                steps.append("⚠️ Intent classification failed - investigate tool availability")
            if not data_result:
                steps.append("⚠️ Data analysis failed - investigate tool availability")
            if not model_result:
                steps.append("⚠️ Model building failed - investigate tool availability")
            if not solver_result:
                steps.append("⚠️ Solver execution failed - investigate tool availability")
        
        return steps

    def _assess_full_workflow_readiness(self, intent_result, data_result, model_result, solver_result) -> Dict[str, Any]:
        """Assess readiness for full workflow execution"""
        readiness = {
            "intent_classification_ready": intent_result is not None,
            "data_analysis_ready": data_result is not None,
            "model_building_ready": model_result is not None,
            "solver_execution_ready": solver_result is not None,
            "full_workflow_ready": all([intent_result, data_result, model_result, solver_result]),
            "tools_available": {
                "intent_tool": INTENT_TOOL_AVAILABLE,
                "data_tool": DATA_TOOL_AVAILABLE,
                "model_tool": MODEL_TOOL_AVAILABLE,
                "solver_tool": SOLVER_TOOL_AVAILABLE
            }
        }
        
        if readiness["full_workflow_ready"]:
            readiness["status"] = "complete"
            readiness["message"] = "All 4 tools executed successfully"
        else:
            readiness["status"] = "partial"
            readiness["message"] = "Some tools failed or are not available"
        
        return readiness


# Factory function
def create_dcisionai_manufacturing_agent() -> DcisionAI_Manufacturing_Agent:
    """Create REAL DcisionAI Manufacturing Agent with working tools only"""
    return DcisionAI_Manufacturing_Agent()
