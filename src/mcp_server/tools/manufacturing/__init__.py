"""
DcisionAI Platform - Manufacturing Tools Package
===============================================

Advanced manufacturing optimization tools with swarm intelligence and A2A coordination.
This package imports tools from the consolidated domains/manufacturing/tools location.
"""

# Import tools from consolidated location
try:
    from domains.manufacturing.tools.intent.DcisionAI_Intent_Tool import (
        DcisionAI_Intent_Tool,
        IntentClassification,
        SwarmPerformanceMetrics,
        create_dcisionai_intent_tool_v6
    )
    INTENT_TOOL_AVAILABLE = True
except ImportError:
    DcisionAI_Intent_Tool = None
    IntentClassification = None
    SwarmPerformanceMetrics = None
    create_dcisionai_intent_tool_v6 = None
    INTENT_TOOL_AVAILABLE = False

try:
    from domains.manufacturing.tools.data.DcisionAI_Data_Tool import (
        DcisionAI_Data_Tool,
        DataAnalysisResult,
        DataRequirement,
        DataSourceRecommendation,
        DataCategory,
        DataSource,
        create_data_tool
    )
    DATA_TOOL_AVAILABLE = True
except ImportError:
    DcisionAI_Data_Tool = None
    DataAnalysisResult = None
    DataRequirement = None
    DataSourceRecommendation = None
    DataCategory = None
    DataSource = None
    create_data_tool = None
    DATA_TOOL_AVAILABLE = False

try:
    from domains.manufacturing.tools.model.DcisionAI_Model_Builder import (
        DcisionAI_Model_Builder,
        ModelBuildingResult,
        ModelType,
        create_model_builder_tool
    )
    MODEL_TOOL_AVAILABLE = True
except ImportError:
    DcisionAI_Model_Builder = None
    ModelBuildingResult = None
    ModelType = None
    create_model_builder_tool = None
    MODEL_TOOL_AVAILABLE = False

try:
    from domains.manufacturing.tools.solver.DcisionAI_Solver_Tool import (
        DcisionAI_Solver_Tool,
        SolverResult,
        SolverType,
        create_solver_tool
    )
    SOLVER_TOOL_AVAILABLE = True
except ImportError:
    DcisionAI_Solver_Tool = None
    SolverResult = None
    SolverType = None
    create_solver_tool = None
    SOLVER_TOOL_AVAILABLE = False

# Main Manufacturing Agent
try:
    from domains.manufacturing.agents.DcisionAI_Manufacturing_Agent_v1 import (
        DcisionAI_Manufacturing_Agent_v1
    )
    MANUFACTURING_AGENT_AVAILABLE = True
except ImportError:
    DcisionAI_Manufacturing_Agent_v1 = None
    MANUFACTURING_AGENT_AVAILABLE = False

# Export consolidated tools
__all__ = [
    # Intent tools
    "DcisionAI_Intent_Tool",
    "IntentClassification", 
    "SwarmPerformanceMetrics",
    "create_dcisionai_intent_tool_v6",
    
    # Data tools
    "DcisionAI_Data_Tool",
    "DataAnalysisResult",
    "DataRequirement",
    "DataSourceRecommendation",
    "DataCategory",
    "DataSource",
    "create_data_tool",
    
    # Model tools
    "DcisionAI_Model_Builder",
    "ModelBuildingResult",
    "ModelType",
    "create_model_builder_tool",
    
    # Solver tools
    "DcisionAI_Solver_Tool",
    "SolverResult",
    "SolverType",
    "create_solver_tool",
    
    # Agent
    "DcisionAI_Manufacturing_Agent_v1",
    
    # Availability flags
    "INTENT_TOOL_AVAILABLE",
    "DATA_TOOL_AVAILABLE",
    "MODEL_TOOL_AVAILABLE",
    "SOLVER_TOOL_AVAILABLE",
    "MANUFACTURING_AGENT_AVAILABLE"
]
