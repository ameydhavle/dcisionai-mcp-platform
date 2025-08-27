"""
DcisionAI Platform - Manufacturing Tools Package
===============================================

Advanced manufacturing optimization tools with swarm intelligence and A2A coordination.
"""

# Enhanced DcisionAI Tools (Production Ready)
try:
    from .intent.DcisionAI_Intent_Tool import (
        DcisionAI_Intent_Tool,
        IntentClassification,
        SwarmPerformanceMetrics,
        create_dcisionai_intent_tool
    )
    INTENT_TOOL_AVAILABLE = True
except ImportError:
    DcisionAI_Intent_Tool = None
    IntentClassification = None
    SwarmPerformanceMetrics = None
    create_dcisionai_intent_tool = None
    INTENT_TOOL_AVAILABLE = False

try:
    from .data.DcisionAI_Data_Tool import (
        DcisionAI_Data_Tool,
        DataAnalysisResult,
        DataRequirement,
        DataSourceRecommendation,
        DataCategory,
        DataSource,
        create_dcisionai_data_tool
    )
    DATA_TOOL_AVAILABLE = True
except ImportError:
    DcisionAI_Data_Tool = None
    DataAnalysisResult = None
    DataRequirement = None
    DataSourceRecommendation = None
    DataCategory = None
    DataSource = None
    create_dcisionai_data_tool = None
    DATA_TOOL_AVAILABLE = False

# Main Manufacturing Agent
try:
    from .DcisionAI_Manufacturing_Agent import (
        DcisionAI_Manufacturing_Agent,
        WorkflowResult,
        WorkflowStage,
        ToolStatus,
        create_dcisionai_manufacturing_agent
    )
    MANUFACTURING_AGENT_AVAILABLE = True
except ImportError:
    DcisionAI_Manufacturing_Agent = None
    WorkflowResult = None
    WorkflowStage = None
    ToolStatus = None
    create_dcisionai_manufacturing_agent = None
    MANUFACTURING_AGENT_AVAILABLE = False

# Legacy tools (for backward compatibility)
try:
    from .model.model_builder_optimized import OptimizedModelBuilder
    ModelBuilderStrandsSwarmOrchestrator = OptimizedModelBuilder  # Alias for compatibility
except ImportError:
    ModelBuilderStrandsSwarmOrchestrator = None

# Solver tools
try:
    from .solver.solver_tool import SolverTool
    from .solver.solver_swarm_orchestrator import SolverSwarmOrchestrator
except ImportError:
    SolverTool = None
    SolverSwarmOrchestrator = None

# Legacy data tools
try:
    from .data.data_tool import DataTool
    DataSwarmOrchestrator = None  # Not implemented yet
except ImportError:
    DataTool = None
    DataSwarmOrchestrator = None

# Legacy intent tools
try:
    from .intent.intent_tool import IntentTool
    IntentSwarmOrchestrator = None  # Not implemented yet
except ImportError:
    IntentTool = None
    IntentSwarmOrchestrator = None

# Critique tools
try:
    from .critique.critique_tool import CritiqueTool
    from .critique.critique_swarm_orchestrator import CritiqueSwarmOrchestrator
except ImportError:
    CritiqueTool = None
    CritiqueSwarmOrchestrator = None

# Explain tools
try:
    from .explain.explain_tool import ExplainTool
    from .explain.explain_swarm_orchestrator import ExplainSwarmOrchestrator
except ImportError:
    ExplainTool = None
    ExplainSwarmOrchestrator = None

# Swarm tools
try:
    from .swarm.adaptive_manufacturing_swarms import AdaptiveManufacturingSwarms
    from .swarm.swarm_tool import SwarmTool
    from .swarm.manufacturing_domain_optimizer import ManufacturingDomainOptimizer
    from .swarm.strands_optimization_solver import StrandsOptimizationSolver
except ImportError:
    AdaptiveManufacturingSwarms = None
    SwarmTool = None
    ManufacturingDomainOptimizer = None
    StrandsOptimizationSolver = None

__all__ = [
    # Enhanced DcisionAI Tools (Production Ready)
    "DcisionAI_Intent_Tool",
    "IntentClassification", 
    "SwarmPerformanceMetrics",
    "create_dcisionai_intent_tool",
    "DcisionAI_Data_Tool",
    "DataAnalysisResult",
    "DataRequirement",
    "DataSourceRecommendation", 
    "DataCategory",
    "DataSource",
    "create_dcisionai_data_tool",
    "DcisionAI_Manufacturing_Agent",
    "WorkflowResult",
    "WorkflowStage",
    "ToolStatus",
    "create_dcisionai_manufacturing_agent",
    
    # Tool availability flags
    "INTENT_TOOL_AVAILABLE",
    "DATA_TOOL_AVAILABLE", 
    "MANUFACTURING_AGENT_AVAILABLE",
    
    # Legacy tools (for backward compatibility)
    "ModelBuilderStrandsSwarmOrchestrator",
    "SolverTool",
    "SolverSwarmOrchestrator",
    "DataTool",
    "DataSwarmOrchestrator",
    "IntentTool",
    "IntentSwarmOrchestrator",
    "CritiqueTool",
    "CritiqueSwarmOrchestrator",
    "ExplainTool",
    "ExplainSwarmOrchestrator",
    "AdaptiveManufacturingSwarms",
    "SwarmTool",
    "ManufacturingDomainOptimizer",
    "StrandsOptimizationSolver"
]
