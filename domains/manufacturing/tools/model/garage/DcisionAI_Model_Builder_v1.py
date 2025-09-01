#!/usr/bin/env python3
"""
DcisionAI Model Builder Tool - Manufacturing Optimization
========================================================

High-quality optimization model generation using the same patterns as intent and data tools.
Outputs structured models ready for the solver tool to consume.

Uses manager-worker pattern with 6 specialized modeling agents.
Compatible with the existing domain orchestrator.

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import logging
import json
import uuid
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Strands framework imports
try:
    from strands import Agent, tool
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False
    logging.error("Strands framework not available - model builder requires Strands")
    raise Exception("Strands framework is required but not available")

# Platform throttling imports
from shared.throttling import get_platform_throttle_manager

logger = logging.getLogger(__name__)

# ==================== CORE DATA STRUCTURES ====================

class ModelType(Enum):
    """Optimization model types for solver compatibility"""
    LINEAR_PROGRAMMING = "linear_programming"
    INTEGER_PROGRAMMING = "integer_programming"
    MIXED_INTEGER_PROGRAMMING = "mixed_integer_programming"
    QUADRATIC_PROGRAMMING = "quadratic_programming"
    NONLINEAR_PROGRAMMING = "nonlinear_programming"
    CONSTRAINT_PROGRAMMING = "constraint_programming"

class SolverType(Enum):
    """Supported solver types"""
    GUROBI = "gurobi"
    CPLEX = "cplex"
    OR_TOOLS = "or_tools"
    PULP = "pulp"
    CVXPY = "cvxpy"
    PYOMO = "pyomo"

@dataclass
class DecisionVariable:
    """Decision variable specification for solver"""
    name: str
    variable_type: str  # "continuous", "integer", "binary"
    domain: str  # "real", "integer", "binary"
    bounds: Tuple[Optional[float], Optional[float]]
    description: str
    indices: Optional[List[str]] = None
    dimensions: Optional[Dict[str, List[str]]] = None

@dataclass
class OptimizationConstraint:
    """Constraint specification for solver"""
    name: str
    constraint_type: str  # "equality", "inequality", "bound"
    expression: str  # Mathematical expression
    sense: str  # "<=", ">=", "=="
    rhs_value: Union[float, str]
    description: str
    priority: str = "normal"  # "critical", "important", "normal"
    constraint_data: Optional[Dict[str, Any]] = None

@dataclass
class ObjectiveFunction:
    """Objective function specification for solver"""
    name: str
    sense: str  # "minimize", "maximize"
    expression: str
    description: str
    weight: float = 1.0
    priority: int = 1

@dataclass
class ModelDataSchema:
    """Data schema specification for solver"""
    parameters: Dict[str, Dict[str, Any]]  # parameter_name -> {type, description, sample_data}
    sets: Dict[str, List[str]]  # set_name -> sample_values
    scalars: Dict[str, float]  # scalar_name -> sample_value

@dataclass
class OptimizationModel:
    """Complete optimization model for solver consumption"""
    model_id: str
    model_name: str
    model_type: ModelType
    intent_classification: str
    
    # Core model components for solver
    decision_variables: List[DecisionVariable]
    constraints: List[OptimizationConstraint]
    objective_functions: List[ObjectiveFunction]
    data_schema: ModelDataSchema
    
    # Solver compatibility
    compatible_solvers: List[SolverType]
    recommended_solver: SolverType
    
    # Model metadata
    model_complexity: str
    estimated_solve_time: str
    model_validation_score: float
    generation_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelBuildingResult:
    """Model building result with metadata"""
    model: OptimizationModel
    build_status: str
    execution_time: float
    agents_used: int
    model_quality_score: float
    generation_metadata: Dict[str, Any]

# ==================== WORKER AGENT TOOLS ====================

@tool
def mathematical_formulation_agent(intent_result: str, data_result: str, session_id: str = "default") -> str:
    """Mathematical formulation specialist for model type and structure."""
    try:
        agent = Agent(
            name="mathematical_formulation_specialist",
            system_prompt="""You are a Mathematical Formulation specialist for optimization model building.

EXPERTISE: Mathematical optimization, model type selection, problem structure analysis
FOCUS: Determine optimal model type and mathematical structure

CLASSIFICATION RULES:
- LINEAR_PROGRAMMING: Linear objective and constraints, continuous variables
- INTEGER_PROGRAMMING: Linear with integer variables, no continuous variables
- MIXED_INTEGER_PROGRAMMING: Linear with both integer and continuous variables
- QUADRATIC_PROGRAMMING: Quadratic objective or constraints
- NONLINEAR_PROGRAMMING: Nonlinear objective or constraints
- CONSTRAINT_PROGRAMMING: Complex logical constraints, discrete variables

RESPONSE FORMAT (JSON only):
{
    "model_type": "LINEAR_PROGRAMMING|INTEGER_PROGRAMMING|MIXED_INTEGER_PROGRAMMING|QUADRATIC_PROGRAMMING|NONLINEAR_PROGRAMMING|CONSTRAINT_PROGRAMMING",
    "model_structure": "detailed description of mathematical structure",
    "complexity_assessment": "low|medium|high",
    "reasoning": "Clear explanation of model type selection",
    "key_characteristics": ["characteristic1", "characteristic2"],
    "estimated_solve_time": "fast|medium|slow"
}"""
        )
        
        prompt = f"""
        Analyze the intent and data results to determine the optimal mathematical formulation:
        
        Intent Result: {intent_result}
        Data Result: {data_result}
        Session ID: {session_id}
        
        Determine the best model type and mathematical structure for this optimization problem.
        """
        
        response = agent(prompt)
        return response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        return json.dumps({
            "model_type": "MIXED_INTEGER_PROGRAMMING",
            "model_structure": "Standard MIP formulation",
            "complexity_assessment": "medium",
            "reasoning": f"Error in formulation analysis: {str(e)}",
            "key_characteristics": ["mixed_variables", "linear_constraints"],
            "estimated_solve_time": "medium"
        })

@tool
def variable_design_agent(intent_result: str, data_result: str, session_id: str = "default") -> str:
    """Variable design specialist for decision variable architecture."""
    try:
        agent = Agent(
            name="variable_design_specialist",
            system_prompt="""You are a Variable Design specialist for optimization model building.

EXPERTISE: Decision variable design, indexing, bounds, variable types
FOCUS: Design optimal decision variable structure for the problem

VARIABLE DESIGN RULES:
- Binary variables: Yes/No decisions, assignment problems
- Integer variables: Countable quantities, discrete decisions
- Continuous variables: Measurable quantities, resource allocation
- Indexed variables: Multiple entities, time periods, resources
- Bounds: Physical constraints, logical limits, business rules

RESPONSE FORMAT (JSON only):
{
    "decision_variables": [
        {
            "name": "variable_name",
            "variable_type": "binary|integer|continuous",
            "domain": "real|integer|binary",
            "bounds": [lower_bound, upper_bound],
            "description": "Variable description",
            "indices": ["index1", "index2"],
            "dimensions": {"dimension1": ["value1", "value2"]}
        }
    ],
    "variable_structure": "description of variable architecture",
    "indexing_scheme": "description of indexing approach"
}"""
        )
        
        prompt = f"""
        Design decision variables for the optimization problem:
        
        Intent Result: {intent_result}
        Data Result: {data_result}
        Session ID: {session_id}
        
        Create appropriate decision variables with proper indexing and bounds.
        """
        
        response = agent(prompt)
        return response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        return json.dumps({
            "decision_variables": [
                {
                    "name": "x",
                    "variable_type": "continuous",
                    "domain": "real",
                    "bounds": [0, None],
                    "description": "Default continuous variable",
                    "indices": [],
                    "dimensions": {}
                }
            ],
            "variable_structure": "Basic continuous variable structure",
            "indexing_scheme": "Simple single variable"
        })

@tool
def constraint_modeling_agent(intent_result: str, data_result: str, session_id: str = "default") -> str:
    """Constraint modeling specialist for constraint system design."""
    try:
        agent = Agent(
            name="constraint_modeling_specialist",
            system_prompt="""You are a Constraint Modeling specialist for optimization model building.

EXPERTISE: Constraint formulation, mathematical expressions, constraint systems
FOCUS: Design comprehensive constraint system for the problem

CONSTRAINT TYPES:
- Resource constraints: Capacity limits, resource availability
- Logical constraints: If-then, either-or, mutual exclusivity
- Balance constraints: Flow conservation, inventory balance
- Time constraints: Sequencing, deadlines, precedence
- Business constraints: Policy rules, operational limits

RESPONSE FORMAT (JSON only):
{
    "constraints": [
        {
            "name": "constraint_name",
            "constraint_type": "equality|inequality|bound",
            "expression": "mathematical_expression",
            "sense": "<=|>=|==",
            "rhs_value": "right_hand_side_value",
            "description": "Constraint description",
            "priority": "critical|important|normal"
        }
    ],
    "constraint_system": "description of constraint architecture",
    "constraint_categories": ["category1", "category2"]
}"""
        )
        
        prompt = f"""
        Design constraints for the optimization problem:
        
        Intent Result: {intent_result}
        Data Result: {data_result}
        Session ID: {session_id}
        
        Create appropriate constraints with mathematical expressions.
        """
        
        response = agent(prompt)
        return response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        return json.dumps({
            "constraints": [
                {
                    "name": "default_constraint",
                    "constraint_type": "inequality",
                    "expression": "x <= 100",
                    "sense": "<=",
                    "rhs_value": 100,
                    "description": "Default upper bound constraint",
                    "priority": "normal"
                }
            ],
            "constraint_system": "Basic constraint system",
            "constraint_categories": ["bounds"]
        })

@tool
def objective_design_agent(intent_result: str, data_result: str, session_id: str = "default") -> str:
    """Objective design specialist for objective function formulation."""
    try:
        agent = Agent(
            name="objective_design_specialist",
            system_prompt="""You are an Objective Design specialist for optimization model building.

EXPERTISE: Objective function formulation, multi-objective optimization, goal programming
FOCUS: Design optimal objective functions for the problem

OBJECTIVE TYPES:
- Cost minimization: Operational costs, production costs
- Profit maximization: Revenue optimization, efficiency
- Time minimization: Makespan, completion time
- Quality maximization: Performance, reliability
- Multi-objective: Weighted combinations, Pareto optimization

RESPONSE FORMAT (JSON only):
{
    "objective_functions": [
        {
            "name": "objective_name",
            "sense": "minimize|maximize",
            "expression": "mathematical_expression",
            "description": "Objective description",
            "weight": 1.0,
            "priority": 1
        }
    ],
    "objective_strategy": "description of objective approach",
    "multi_objective_handling": "description of multi-objective strategy"
}"""
        )
        
        prompt = f"""
        Design objective functions for the optimization problem:
        
        Intent Result: {intent_result}
        Data Result: {data_result}
        Session ID: {session_id}
        
        Create appropriate objective functions with mathematical expressions.
        """
        
        response = agent(prompt)
        return response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        return json.dumps({
            "objective_functions": [
                {
                    "name": "default_objective",
                    "sense": "minimize",
                    "expression": "x",
                    "description": "Default minimization objective",
                    "weight": 1.0,
                    "priority": 1
                }
            ],
            "objective_strategy": "Basic minimization strategy",
            "multi_objective_handling": "Single objective approach"
        })

@tool
def solver_compatibility_agent(intent_result: str, data_result: str, session_id: str = "default") -> str:
    """Solver compatibility specialist for solver selection and code generation."""
    try:
        agent = Agent(
            name="solver_compatibility_specialist",
            system_prompt="""You are a Solver Compatibility specialist for optimization model building.

EXPERTISE: Solver selection, code generation, solver-specific implementations
FOCUS: Determine compatible solvers and generate solver-ready code

SOLVER CAPABILITIES:
- GUROBI: Commercial, high-performance, comprehensive
- CPLEX: Commercial, enterprise-grade, robust
- OR_TOOLS: Google, open-source, constraint programming
- PULP: Python, open-source, linear programming
- CVXPY: Python, convex optimization, academic
- PYOMO: Python, modeling framework, flexible

RESPONSE FORMAT (JSON only):
{
    "compatible_solvers": ["GUROBI", "CPLEX", "OR_TOOLS"],
    "recommended_solver": "GUROBI",
    "solver_implementations": {
        "gurobi": "model.addConstrs(...)",
        "or_tools": "solver.Add(...)",
        "pulp": "prob += pl.lpSum(...)"
    },
    "solver_selection_reasoning": "explanation of solver choice"
}"""
        )
        
        prompt = f"""
        Determine solver compatibility and generate solver code:
        
        Intent Result: {intent_result}
        Data Result: {data_result}
        Session ID: {session_id}
        
        Select compatible solvers and provide solver-specific implementations.
        """
        
        response = agent(prompt)
        return response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        return json.dumps({
            "compatible_solvers": ["GUROBI", "OR_TOOLS", "PULP"],
            "recommended_solver": "GUROBI",
            "solver_implementations": {
                "gurobi": "# Gurobi implementation\nmodel = Model()",
                "or_tools": "# OR-Tools implementation\nsolver = Solver()",
                "pulp": "# PuLP implementation\nprob = LpProblem()"
            },
            "solver_selection_reasoning": "Standard solver selection"
        })

@tool
def data_schema_agent(intent_result: str, data_result: str, session_id: str = "default") -> str:
    """Data schema specialist for model data requirements."""
    try:
        agent = Agent(
            name="data_schema_specialist",
            system_prompt="""You are a Data Schema specialist for optimization model building.

EXPERTISE: Data requirements, parameter specification, data validation
FOCUS: Define complete data schema for the optimization model

DATA SCHEMA COMPONENTS:
- Parameters: Model coefficients, costs, capacities
- Sets: Index sets, entities, time periods
- Scalars: Constants, configuration values
- Validation: Data types, ranges, relationships

RESPONSE FORMAT (JSON only):
{
    "data_schema": {
        "parameters": {
            "param_name": {
                "type": "float|int|string",
                "description": "Parameter description",
                "sample_data": "sample_value"
            }
        },
        "sets": {
            "set_name": ["value1", "value2"]
        },
        "scalars": {
            "scalar_name": "scalar_value"
        }
    },
    "data_requirements": "description of data needs",
    "validation_rules": ["rule1", "rule2"]
}"""
        )
        
        prompt = f"""
        Define data schema for the optimization model:
        
        Intent Result: {intent_result}
        Data Result: {data_result}
        Session ID: {session_id}
        
        Create complete data schema with parameters, sets, and scalars.
        """
        
        response = agent(prompt)
        return response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        return json.dumps({
            "data_schema": {
                "parameters": {
                    "cost": {
                        "type": "float",
                        "description": "Default cost parameter",
                        "sample_data": 1.0
                    }
                },
                "sets": {
                    "items": ["item1", "item2"]
                },
                "scalars": {
                    "capacity": 100
                }
            },
            "data_requirements": "Basic data requirements",
            "validation_rules": ["cost >= 0", "capacity > 0"]
        })

# ==================== MODEL BUILDING TOOL ====================

class DcisionAI_Model_Builder:
    """
    DcisionAI Model Builder Tool using manager-worker pattern.
    
    Uses 6 specialized agents to build high-quality optimization models.
    Follows the same patterns as intent and data tools.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DcisionAI_Model_Builder")
        self.throttle_manager = get_platform_throttle_manager()
        
        # Initialize manager agent with all worker tools
        self._initialize_manager_agent()
        
        self.logger.info("✅ DcisionAI Model Builder initialized with 6 specialist agents")
    
    def _initialize_manager_agent(self):
        """Initialize manager agent with all 6 worker tools"""
        try:
            self.manager_agent = Agent(
                name="model_building_manager",
                tools=[
                    mathematical_formulation_agent,
                    variable_design_agent,
                    constraint_modeling_agent,
                    objective_design_agent,
                    solver_compatibility_agent,
                    data_schema_agent
                ],
                system_prompt="""You are a Model Building Manager for manufacturing optimization problems.

You coordinate a team of 6 specialist agents to build high-quality optimization models:
1. mathematical_formulation_agent: Model type selection and mathematical structure
2. variable_design_agent: Decision variable architecture and indexing
3. constraint_modeling_agent: Constraint system design and formulation
4. objective_design_agent: Objective function formulation and strategy
5. solver_compatibility_agent: Solver selection and code generation
6. data_schema_agent: Data requirements and schema definition

DELEGATION STRATEGY:
- Manufacturing optimization problems: All 6 specialists for comprehensive model building
- Complex problems: All specialists with detailed analysis
- Simple problems: Core specialists (formulation, variables, constraints, objectives)

MODEL BUILDING PROCESS:
1. Delegate to mathematical_formulation_agent for model type and structure
2. Delegate to variable_design_agent for decision variable architecture
3. Delegate to constraint_modeling_agent for constraint system design
4. Delegate to objective_design_agent for objective function formulation
5. Delegate to solver_compatibility_agent for solver selection and code
6. Delegate to data_schema_agent for data requirements definition

RESPONSE FORMAT (JSON only):
{
    "model_id": "model_20250101_120000_abc123",
    "model_name": "Manufacturing Optimization Model",
    "model_type": "MIXED_INTEGER_PROGRAMMING",
    "intent_classification": "production_scheduling",
    "decision_variables": [...],
    "constraints": [...],
    "objective_functions": [...],
    "data_schema": {...},
    "compatible_solvers": ["GUROBI", "CPLEX", "OR_TOOLS"],
    "recommended_solver": "GUROBI",
    "model_complexity": "medium",
    "estimated_solve_time": "medium",
    "model_validation_score": 0.85,
    "specialist_consensus": {
        "mathematical_formulation": {...},
        "variable_design": {...},
        "constraint_modeling": {...},
        "objective_design": {...},
        "solver_compatibility": {...},
        "data_schema": {...}
    }
}

CRITICAL RULES:
- ALWAYS delegate to all 6 specialists for comprehensive model building
- Synthesize results into a complete optimization model
- Ensure solver compatibility and code generation
- Provide complete data schema for solver consumption
- Validate model quality and complexity assessment"""
            )
            
            self.logger.info("✅ Model building manager initialized with 6 specialist worker tools")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize model building manager: {e}")
            raise Exception(f"Model building manager initialization failed: {e}")
    
    def build_optimization_model(
        self, 
        intent_result: Dict[str, Any], 
        data_result: Dict[str, Any], 
        session_id: str = "default"
    ) -> ModelBuildingResult:
        """Build optimization model using manager-worker delegation"""
        start_time = datetime.now()
        
        try:
            self.logger.info("🚀 Starting model building with 6-specialist delegation")
            
            # Manager delegates to worker specialists
            model_building_task = f"""
            Build a comprehensive optimization model using your 6-specialist team:
            
            Intent Result: {json.dumps(intent_result, indent=2)}
            Data Result: {json.dumps(data_result, indent=2)}
            Session ID: {session_id}
            
            Delegate to ALL 6 specialists and build a complete optimization model from their analyses.
            Ensure the model is solver-ready with proper mathematical formulation, variables, constraints, objectives, and data schema.
            
            IMPORTANT: Wait for ALL 6 specialists to respond before building the final model.
            """
            
            # Execute manager agent
            response = self.manager_agent(model_building_task)
            
            # Parse manager's synthesized response
            model_result = self._parse_manager_response(response)
            
            # Build optimization model from results
            optimization_model = self._build_optimization_model_from_results(model_result, intent_result, session_id)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ModelBuildingResult(
                model=optimization_model,
                build_status="completed",
                execution_time=execution_time,
                agents_used=6,
                model_quality_score=model_result.get("model_validation_score", 0.8),
                generation_metadata={
                    "strategy": "manager_worker_delegation",
                    "manager_agent": "model_building_manager",
                    "worker_tools": [
                        "mathematical_formulation_agent",
                        "variable_design_agent", 
                        "constraint_modeling_agent",
                        "objective_design_agent",
                        "solver_compatibility_agent",
                        "data_schema_agent"
                    ],
                    "throttle_status": self.throttle_manager.get_status() if self.throttle_manager else None
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"❌ Model building failed: {e}")
            
            # Return error result
            error_model = self._create_error_model(intent_result, session_id)
            return ModelBuildingResult(
                model=error_model,
                build_status="failed",
                execution_time=execution_time,
                agents_used=0,
                model_quality_score=0.0,
                generation_metadata={
                    "strategy": "manager_worker_delegation",
                    "error": True,
                    "error_message": str(e)
                }
            )
    
    def _parse_manager_response(self, response: str) -> Dict[str, Any]:
        """Parse manager response"""
        try:
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Extract JSON
            parsed = self._extract_json_from_text(response_text)
            
            if parsed and "model_id" in parsed:
                return parsed
            else:
                return {
                    "model_id": f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
                    "model_name": "Default Optimization Model",
                    "model_type": "MIXED_INTEGER_PROGRAMMING",
                    "intent_classification": "unknown",
                    "decision_variables": [],
                    "constraints": [],
                    "objective_functions": [],
                    "data_schema": {},
                    "compatible_solvers": ["GUROBI"],
                    "recommended_solver": "GUROBI",
                    "model_complexity": "medium",
                    "estimated_solve_time": "medium",
                    "model_validation_score": 0.5,
                    "specialist_consensus": {}
                }
                
        except Exception as e:
            return {
                "model_id": f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
                "model_name": "Error Model",
                "model_type": "MIXED_INTEGER_PROGRAMMING",
                "intent_classification": "unknown",
                "error": True,
                "error_message": str(e)
            }
    
    def _build_optimization_model_from_results(self, model_result: Dict[str, Any], intent_result: Dict[str, Any], session_id: str) -> OptimizationModel:
        """Build OptimizationModel from manager results"""
        try:
            # Extract model components
            decision_variables = []
            for var_data in model_result.get("decision_variables", []):
                decision_variables.append(DecisionVariable(
                    name=var_data.get("name", "x"),
                    variable_type=var_data.get("variable_type", "continuous"),
                    domain=var_data.get("domain", "real"),
                    bounds=var_data.get("bounds", [0, None]),
                    description=var_data.get("description", ""),
                    indices=var_data.get("indices", []),
                    dimensions=var_data.get("dimensions", {})
                ))
            
            constraints = []
            for const_data in model_result.get("constraints", []):
                constraints.append(OptimizationConstraint(
                    name=const_data.get("name", "constraint"),
                    constraint_type=const_data.get("constraint_type", "inequality"),
                    expression=const_data.get("expression", "x <= 100"),
                    sense=const_data.get("sense", "<="),
                    rhs_value=const_data.get("rhs_value", 100),
                    description=const_data.get("description", ""),
                    priority=const_data.get("priority", "normal")
                ))
            
            objective_functions = []
            for obj_data in model_result.get("objective_functions", []):
                objective_functions.append(ObjectiveFunction(
                    name=obj_data.get("name", "objective"),
                    sense=obj_data.get("sense", "minimize"),
                    expression=obj_data.get("expression", "x"),
                    description=obj_data.get("description", ""),
                    weight=obj_data.get("weight", 1.0),
                    priority=obj_data.get("priority", 1)
                ))
            
            # Build data schema
            data_schema_data = model_result.get("data_schema", {})
            data_schema = ModelDataSchema(
                parameters=data_schema_data.get("parameters", {}),
                sets=data_schema_data.get("sets", {}),
                scalars=data_schema_data.get("scalars", {})
            )
            
            # Determine solver compatibility
            compatible_solvers = []
            for solver_name in model_result.get("compatible_solvers", ["GUROBI"]):
                try:
                    compatible_solvers.append(SolverType(solver_name.lower()))
                except ValueError:
                    pass
            
            if not compatible_solvers:
                compatible_solvers = [SolverType.GUROBI]
            
            recommended_solver = SolverType(model_result.get("recommended_solver", "gurobi").lower())
            
            return OptimizationModel(
                model_id=model_result.get("model_id", f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"),
                model_name=model_result.get("model_name", "Manufacturing Optimization Model"),
                model_type=ModelType(model_result.get("model_type", "mixed_integer_programming").lower()),
                intent_classification=intent_result.get("primary_intent", "unknown"),
                decision_variables=decision_variables,
                constraints=constraints,
                objective_functions=objective_functions,
                data_schema=data_schema,
                compatible_solvers=compatible_solvers,
                recommended_solver=recommended_solver,
                model_complexity=model_result.get("model_complexity", "medium"),
                estimated_solve_time=model_result.get("estimated_solve_time", "medium"),
                model_validation_score=model_result.get("model_validation_score", 0.8),
                generation_metadata={
                    "strategy": "manager_worker_delegation",
                    "session_id": session_id,
                    "intent_classification": intent_result.get("primary_intent", "unknown"),
                    "specialist_consensus": model_result.get("specialist_consensus", {})
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error building optimization model: {e}")
            return self._create_error_model(intent_result, session_id)
    
    def _create_error_model(self, intent_result: Dict[str, Any], session_id: str) -> OptimizationModel:
        """Create error model when building fails"""
        return OptimizationModel(
            model_id=f"error_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
            model_name="Error Model",
            model_type=ModelType.MIXED_INTEGER_PROGRAMMING,
            intent_classification=intent_result.get("primary_intent", "unknown"),
            decision_variables=[],
            constraints=[],
            objective_functions=[],
            data_schema=ModelDataSchema(parameters={}, sets={}, scalars={}),
            compatible_solvers=[SolverType.GUROBI],
            recommended_solver=SolverType.GUROBI,
            model_complexity="unknown",
            estimated_solve_time="unknown",
            model_validation_score=0.0,
            generation_metadata={
                "strategy": "manager_worker_delegation",
                "error": True,
                "session_id": session_id
            }
        )
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from text response"""
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
        
        return None

# Factory function
def create_dcisionai_model_builder() -> DcisionAI_Model_Builder:
    """Create DcisionAI Model Builder Tool"""
    return DcisionAI_Model_Builder()
