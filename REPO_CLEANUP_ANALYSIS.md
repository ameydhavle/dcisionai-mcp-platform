# DcisionAI Repository Cleanup Analysis

## 🎯 Core Components (KEEP)

### 1. Main Entry Points
- `main.py` - Platform demonstration entry point
- `domains/manufacturing/agents/DcisionAI_Manufacturing_Agent_v4.py` - Main AgentCore agent
- `domains/manufacturing/mcp_server/mcp_server.py` - Main MCP server
- `domains/manufacturing/mcp_server/agentcore_agent.py` - AgentCore wrapper

### 2. Core Manufacturing Domain
- `domains/manufacturing/mcp_server/` - Active MCP server components
  - `manufacturing_intent_swarm.py` - 5-agent intent classification
  - `manufacturing_data_swarm.py` - 3-agent data analysis  
  - `manufacturing_model_swarm.py` - 4-agent model building
  - `manufacturing_solver_swarm.py` - 6-agent optimization solving
  - `swarm_inference_profile.py` - AWS Bedrock inference profiles
  - `consensus_mechanism.py` - Swarm consensus algorithms
  - `inference_profile_enhanced_swarm.py` - Swarm framework
  - `parallel_execution_strategy.py` - Execution strategies

### 3. Core Tools (Active)
- `domains/manufacturing/tools/intent/DcisionAI_Intent_Tool.py`
- `domains/manufacturing/tools/data/DcisionAI_Data_Tool.py`
- `domains/manufacturing/tools/model/DcisionAI_Model_Builder.py`
- `domains/manufacturing/tools/solver/DcisionAI_Solver_Tool.py`

### 4. Platform Core
- `platform_core/` - Platform management
- `shared/` - Shared framework components
- `domains/__init__.py` - Domain management

### 5. Essential Configuration
- `requirements.txt` files (active ones only)
- `runtime_config.json`
- `mkdocs.yml`

### 6. Active Tests
- `test_customer_scenario_e2e.py` - Main E2E test
- `tests/` directory (organized test suite)

## 📦 Archive Candidates (MOVE TO ARCHIVE)

### 1. Redundant Agent Versions
- `domains/manufacturing/agents/archive/` - Already archived
- `domains/manufacturing/agents/DcisionAI_Manufacturing_Agent_v4_Simple.py`
- `domains/manufacturing/agents/DcisionAI_Manufacturing_Agent_v4_Working.py`

### 2. Redundant MCP Server Versions
- `cleanup_archive/` - Already exists, contains old versions
- Multiple Dockerfile versions
- Multiple requirements files

### 3. Redundant Tools
- `domains/manufacturing/tools/archive/` - Already archived
- `domains/manufacturing/tools/critique/` - Not core functionality
- `domains/manufacturing/tools/explain/` - Not core functionality
- `domains/manufacturing/tools/swarm/` - Redundant with mcp_server swarms

### 4. Test Files (Root Level)
- `test_customer_local.py`
- `test_customer_mcp_direct.py` 
- `test_customer_scenario.py`
- `test_inference_profiles.py`
- `workflow_test_results_*.json`
- `deployed_mcp_test_results_*.json`

### 5. Deployment Scripts (Redundant)
- `deploy_agentcore_v4_fix.sh`
- `deploy_new_agentcore_v4.sh`
- Multiple Dockerfile versions

### 6. Documentation (Redundant)
- `docs/` - Keep only essential docs
- `customer_portal/` - Move to archive
- `playground/` - Move to archive

### 7. Infrastructure (Archive)
- `infrastructure/` - Move to archive
- `scripts/` - Move to archive

## 🗂️ Proposed Clean Structure

```
dcisionai-mcp-platform/
├── main.py                          # Main entry point
├── runtime_config.json              # Runtime configuration
├── mkdocs.yml                       # Documentation config
├── README.md                        # Main documentation
├── requirements.txt                 # Main requirements
├── domains/                         # Core domains
│   ├── __init__.py
│   ├── manufacturing/               # Manufacturing domain
│   │   ├── agents/
│   │   │   ├── DcisionAI_Manufacturing_Agent_v4.py
│   │   │   └── archive/             # Archived versions
│   │   ├── mcp_server/              # Active MCP server
│   │   │   ├── *.py                 # Core swarm files
│   │   │   ├── requirements.txt
│   │   │   └── Dockerfile
│   │   └── tools/                   # Core tools only
│   │       ├── intent/
│   │       ├── data/
│   │       ├── model/
│   │       └── solver/
│   ├── finance/                     # Other domains
│   └── pharma/
├── platform_core/                   # Platform management
├── shared/                          # Shared framework
├── tests/                           # Organized test suite
├── docs/                            # Essential documentation only
└── archive/                         # All archived content
    ├── cleanup_archive/             # Existing archive
    ├── old_tests/                   # Root level test files
    ├── old_deployment/              # Deployment scripts
    ├── old_infrastructure/          # Infrastructure files
    ├── old_documentation/           # Extra documentation
    └── old_playground/              # Playground files
```

## 🚀 Cleanup Actions

1. **Create archive structure**
2. **Move redundant files to archive**
3. **Keep only core functionality**
4. **Update documentation**
5. **Clean up imports and dependencies**
