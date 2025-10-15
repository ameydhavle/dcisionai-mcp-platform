# DcisionAI Platform

## Overview

DcisionAI is the Intelligent Enterprise Decision Layer - a revolutionary platform that bridges the gap between AI chatbots and spreadsheets, providing mathematically proven optimal decisions with full transparency and interactivity.

**Live Platform**: https://platform.dcisionai.com

## Architecture

### Current Architecture (AgentCore Gateway + Qwen 30B + MCP Server)

- **AgentCore Gateway**: Amazon Bedrock AgentCore Gateway for advanced agent orchestration
- **Qwen 30B Model**: Qwen 3B Coder 30B for superior mathematical model generation
- **Enhanced Lambda Functions**: 2GB memory, optimized for Qwen 30B integration
- **Real-time Processing**: Live optimization with progress tracking
- **MCP Protocol**: Model Context Protocol for seamless agent communication
- **MCP Server Distribution**: Production-ready Python package for global distribution

### Key Features

- ✅ **Qwen 30B Integration**: Advanced mathematical model generation with Qwen 3B Coder 30B
- ✅ **Real AWS Bedrock Integration**: No mock responses, all real AI models
- ✅ **AgentCore Gateway**: Next-generation agent platform with extended execution
- ✅ **21 Industry Workflows**: Predefined optimization templates across 7 industries
- ✅ **Production Ready**: AWS-hosted with global CDN distribution
- ✅ **MCP Server Distribution**: `pip install dcisionai-mcp-server` for global access

## MCP Server Distribution

### Quick Installation
```bash
pip install dcisionai-mcp-server
```

### Start Server
```bash
dcisionai-mcp-server start --host 0.0.0.0 --port 8000
```

### Available Tools
- `classify_intent` - Intent classification for optimization requests
- `analyze_data` - Data analysis and preprocessing
- `build_model` - Mathematical model building with Qwen 30B
- `solve_optimization` - Optimization solving and results
- `get_workflow_templates` - Industry workflow templates
- `execute_workflow` - End-to-end workflow execution

### IDE Integration
Works with Cursor, Kiro, Claude Code, VS Code, and other MCP-compatible IDEs.

### Documentation
- **Package Documentation**: [dcisionai-mcp-server README](dcisionai-mcp-server/README.md)
- **API Reference**: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- **Quick Start**: [docs/QUICK_START.md](docs/QUICK_START.md)

## 📁 Repository Structure

```
dcisionai-mcp-platform/
├── main.py                          # Main platform entry point
├── runtime_config.json              # Runtime configuration
├── requirements.txt                 # Main requirements
├── dcisionai-mcp-server/            # MCP Server Distribution Package
│   ├── setup.py                     # PyPI package configuration
│   ├── pyproject.toml               # Modern Python packaging
│   ├── requirements.txt             # Package dependencies
│   ├── README.md                    # Package documentation
│   ├── dcisionai_mcp_server/        # Main package
│   │   ├── __init__.py             # Package initialization
│   │   ├── server.py               # Main MCP server
│   │   ├── tools.py                # 6 core optimization tools
│   │   ├── config.py               # Configuration management
│   │   ├── workflows.py            # Workflow manager
│   │   └── cli.py                  # Command-line interface
│   └── tests/                       # Test suite
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
