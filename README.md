# DcisionAI Manufacturing MCP Platform

## 🚀 Overview

DcisionAI Manufacturing MCP Platform is a production-ready multi-agent system for manufacturing optimization using AWS Bedrock inference profiles and the Model Context Protocol (MCP).

## 🏗️ Architecture

### Core Components

- **Manufacturing Domain**: 18 specialized agents across 4 swarms
- **Intent Classification**: 5-agent swarm for understanding manufacturing queries
- **Data Analysis**: 3-agent swarm for manufacturing data processing
- **Model Building**: 4-agent swarm for mathematical optimization models
- **Solver Optimization**: 6-agent swarm for real optimization solving

### Key Features

- ✅ **Real AWS Bedrock Integration**: No mock responses, all real inference profiles
- ✅ **Cross-Region Execution**: Agents distributed across multiple AWS regions
- ✅ **Consensus Mechanisms**: Confidence aggregation and agreement scoring
- ✅ **Production Ready**: AgentCore deployment with swarm architecture
- ✅ **Multi-Tenant Support**: Platform manager with tenant orchestration

## 📁 Repository Structure

```
dcisionai-mcp-platform/
├── main.py                          # Main platform entry point
├── runtime_config.json              # Runtime configuration
├── requirements.txt                 # Main requirements
├── domains/                         # Core domains
│   ├── manufacturing/               # Manufacturing domain
│   │   ├── agents/                  # AgentCore agents
│   │   │   └── DcisionAI_Manufacturing_Agent_v4.py
│   │   ├── mcp_server/              # MCP server components
│   │   │   ├── manufacturing_*_swarm.py  # Swarm implementations
│   │   │   ├── swarm_inference_profile.py
│   │   │   ├── consensus_mechanism.py
│   │   │   └── inference_profile_enhanced_swarm.py
│   │   └── tools/                   # Core manufacturing tools
│   │       ├── intent/              # Intent classification
│   │       ├── data/                # Data analysis
│   │       ├── model/               # Model building
│   │       └── solver/              # Optimization solving
│   ├── finance/                     # Finance domain
│   └── pharma/                      # Pharma domain
├── platform_core/                   # Platform management
├── shared/                          # Shared framework
├── tests/                           # Test suite
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   └── workflow/                    # Workflow tests
├── docs/                            # Documentation
│   ├── Architecture.md              # System architecture
│   ├── CUSTOMER_QUICK_START_GUIDE.md # Quick start guide
│   ├── index.md                     # Documentation index
│   └── openapi_specification.yaml   # API specification
└── archive/                         # Archived content
    ├── cleanup_archive/             # Previous cleanup
    ├── old_tests/                   # Archived test files
    ├── old_deployment/              # Archived deployment files
    ├── old_infrastructure/          # Archived infrastructure
    ├── old_documentation/           # Archived documentation
    ├── old_playground/              # Archived playground
    └── old_customer_portal/         # Archived customer portal
```

## 🚀 Quick Start

### 1. Run Customer Showcase (Recommended)

```bash
python3 run_customer_showcase.py
```

This will run a comprehensive customer demonstration with:
- Real AWS Bedrock inference profiles
- 18-agent swarm architecture
- 4 real-world manufacturing scenarios
- Complete optimization workflow
- Performance metrics and health monitoring
- No mock responses

**Quick Mode**: `python3 run_customer_showcase.py --quick` (2 scenarios, ~6-10 minutes)

### 2. Run End-to-End Test

```bash
python3 test_customer_scenario_e2e.py
```

This will run a complete E2E test with:
- Real AWS Bedrock inference profiles
- 18-agent swarm architecture
- ACME Manufacturing scenario
- No mock responses

### 3. Run Platform Demo

```bash
python3 main.py
```

This will demonstrate the platform architecture and domain management.

### 4. Deploy to AgentCore

```bash
cd domains/manufacturing/agents
python3 DcisionAI_Manufacturing_Agent_v4.py
```

## 🧪 Testing

### Customer Showcase (Recommended)
- **File**: `test_customer_showcase_e2e.py`
- **Runner**: `run_customer_showcase.py`
- **Purpose**: Comprehensive customer demonstration with real-world scenarios
- **Duration**: ~15-20 minutes (full), ~6-10 minutes (quick mode)
- **Coverage**: 4 manufacturing scenarios, complete 18-agent swarm workflow
- **Features**: Performance metrics, health monitoring, detailed reporting

### Main E2E Test
- **File**: `test_customer_scenario_e2e.py`
- **Purpose**: Complete workflow testing with real AWS Bedrock
- **Duration**: ~15 minutes (with timeout considerations)
- **Coverage**: Intent → Data → Model → Solver pipeline

### Test Suite
- **Location**: `tests/` directory
- **Types**: Unit, Integration, Workflow tests
- **Framework**: Organized test structure

## 🔧 Configuration

### Runtime Configuration
- **File**: `runtime_config.json`
- **Purpose**: AgentCore deployment configuration
- **Settings**: Runtime name, image URI, role ARN

### Requirements
- **Main**: `requirements.txt`
- **AgentCore**: `domains/manufacturing/mcp_server/requirements.txt`
- **Dependencies**: AWS Bedrock, optimization solvers, MCP framework

## 📊 Performance

### Recent E2E Test Results
- **Intent Classification**: Variable (5 agents, real AWS Bedrock confidence scores)
- **Data Analysis**: Variable (3 agents, real swarm consensus scores)
- **Model Building**: Variable (4 agents, with timeout handling)
- **Solver Optimization**: Variable (6 agents, with timeout handling)

**Note**: All execution times and confidence scores are real results from AWS Bedrock and swarm consensus. No mock data is used.

### Timeout Configuration
- **Model Building & Solver**: 300 seconds (5 minutes)
- **Other Agents**: 120 seconds (2 minutes)
- **Connection**: 60 seconds
- **Retries**: 3 attempts with 1-second delay

## 🏭 Manufacturing Capabilities

### Supported Industries
- Automotive Parts Manufacturing
- Production Line Optimization
- Capacity Planning
- Quality Control
- Supply Chain Optimization

### Optimization Types
- Linear Programming (OR-Tools GLOP)
- Mixed Integer Programming (OR-Tools SCIP)
- High-Performance LP (OR-Tools HiGHS)
- Python-based Optimization (PuLP)
- Convex Optimization (CVXPY)

## 🔗 Integration

### AWS Services
- **Bedrock**: Real inference profiles
- **AgentCore**: Runtime deployment
- **Cross-Region**: Multi-region execution

### Protocols
- **MCP**: Model Context Protocol
- **FastMCP**: Production MCP framework
- **HTTP**: RESTful API endpoints

## 📚 Documentation

- **Customer Showcase**: `CUSTOMER_SHOWCASE_GUIDE.md` - Complete customer demonstration guide
- **Architecture**: `docs/Architecture.md` - Technical architecture and design
- **Quick Start**: `docs/CUSTOMER_QUICK_START_GUIDE.md` - Get up and running in 5 minutes
- **API Spec**: `docs/openapi_specification.yaml` - Complete API reference
- **Index**: `docs/index.md` - Documentation overview

## 🗂️ Archive

All non-essential files have been moved to the `archive/` directory:
- **cleanup_archive/**: Previous cleanup efforts
- **old_tests/**: Archived test files
- **old_deployment/**: Archived deployment scripts
- **old_infrastructure/**: Archived infrastructure files
- **old_documentation/**: Archived documentation
- **old_playground/**: Archived playground files
- **old_customer_portal/**: Archived customer portal

## 🚨 Known Issues

### Timeout Handling
- Model building and solver tasks may experience timeouts
- Timeout configuration has been increased to 300 seconds
- System continues with consensus even if some agents timeout

### Performance Optimization
- Complex mathematical tasks require longer processing time
- Consider using different models for computationally intensive tasks
- Monitor AWS Bedrock quota and throttling

## 📞 Support

For issues or questions:
1. Check the documentation in `docs/`
2. Review test results in `archive/old_tests/`
3. Examine the cleanup analysis in `REPO_CLEANUP_ANALYSIS.md`

---

**DcisionAI Team** | Copyright (c) 2025 DcisionAI. All rights reserved.
