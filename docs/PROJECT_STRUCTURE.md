# DcisionAI MCP Platform - Project Structure

## **📁 Clean Production Structure**

```
dcisionai-mcp-platform/
├── 📄 AGENTCORE_DEPLOYMENT_GUIDE.md    # Complete deployment documentation
├── 📄 PROJECT_STRUCTURE.md             # This file - project structure
├── 📄 Tasks.md                         # Task tracking and progress
├── 📄 README.md                        # Main project documentation
├── 📄 DEPLOYMENT.md                    # General deployment information
├── 📄 PROJECT_SUMMARY.md               # Project overview
├── 📄 HANDOFF_DcisionAI_MCP_Platform.md # Original handoff document
│
├── 🐳 Dockerfile                       # Production ARM64 container
├── 📋 requirements.mcp.txt             # Production dependencies
│
├── 📁 scripts/
│   └── 📁 deployment/                  # Deployment scripts
│       ├── 🚀 dcisionai_manufacturing_build_and_deploy.py      # Complete deployment pipeline
│       ├── 🏭 dcisionai_manufacturing_deploy_agentcore.py      # AgentCore deployment
│       ├── 🧪 dcisionai_manufacturing_invoke_agentcore.py      # AgentCore testing
│       └── 📄 README.md                # Deployment documentation
│
├── 📁 src/
│   └── 📁 mcp_server/                  # Main production architecture
│       ├── 🎯 DcisionAI_Manufacturing_Agent.py  # FastAPI agent (REQUIRED endpoints)
│       ├── ⚡ fastmcp_server.py        # MCP server implementation
│       ├── 🛠️ tools/
│       │   └── 📁 manufacturing/       # Manufacturing tools
│       │       ├── 🎯 intent/          # Intent classification
│       │       ├── 📊 data/            # Data analysis
│       │       ├── 🏗️ model/           # Model building
│       │       ├── 🔧 solver/          # Optimization solving
│       │       ├── 🔄 swarm/           # Swarm orchestration
│       │       ├── 💬 critique/        # Critique tools
│       │       ├── 📝 explain/         # Explanation tools
│       │       └── 🔗 shared/          # Shared components
│       ├── ⚙️ config/                  # Configuration management
│       │   ├── settings.py             # Server settings
│       │   └── aws_credentials.py      # AWS credential management
│       ├── 🔧 utils/                   # Utilities
│       │   ├── logging.py              # Logging configuration
│       │   └── metrics.py              # Metrics collection
│       ├── 🏢 tenants/                 # Multi-tenant management
│       ├── 📡 protocol/                # MCP protocol handling
│       ├── 🌐 gateway/                 # Production gateway service
│       ├── 🖥️ main.py                  # Main server entry point
│       └── 🌍 http_server.py           # HTTP server implementation
│
├── 📁 cleanup_archive/                 # Archived obsolete files
│   ├── agentcore_entry_point.py        # Old entry point
│   ├── Dockerfile.mcp                  # Old Dockerfile
│   ├── run_mcp_server.py              # Old server script
│   ├── requirements.agentcore.txt      # Old requirements
│   ├── test_*.py                       # Old test files
│   ├── *.log                           # Old log files
│   └── src/garage/                     # Old versioned files
│
├── 📁 docs/                            # Documentation
├── 📁 scripts/                         # Utility scripts
├── 📁 cloudformation/                  # AWS infrastructure
├── 📁 monitoring/                      # Monitoring configuration
├── 📁 tests/                           # Test suite
├── 📁 archive/                         # Legacy archive
├── 📁 .github/                         # GitHub configuration
├── 📁 venv/                            # Python virtual environment
│
├── 🐳 .dockerignore                     # Docker ignore rules
├── 📄 .gitignore                       # Git ignore rules
└── 📄 .bedrock_agentcore.yaml          # AgentCore configuration
```

## **🎯 Key Components**

### **Production Core**
- **`src/mcp_server/custom_agent.py`**: FastAPI agent with required `/invocations` and `/ping` endpoints
- **`Dockerfile`**: ARM64 container for AgentCore deployment
- **`requirements.mcp.txt`**: All production dependencies

### **Manufacturing Tools**
- **Intent Classification**: Analyze manufacturing intent
- **Data Analysis**: Process manufacturing data requirements
- **Model Building**: Create optimization models
- **Solver Tools**: Solve optimization problems
- **Swarm Orchestration**: Coordinate multiple agents
- **Critique Tools**: Evaluate and critique solutions
- **Explanation Tools**: Explain results and decisions

### **Infrastructure**
- **Configuration Management**: Settings and AWS credentials
- **Multi-tenancy**: Tenant management system
- **Monitoring**: Logging and metrics
- **Gateway**: Production gateway service
- **Protocol Handling**: MCP protocol implementation

## **🚀 Deployment Architecture**

### **AgentCore Integration**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AWS AgentCore │    │   Custom Agent  │    │  MCP Server     │
│                 │    │                 │    │                 │
│  /invocations   │───▶│  FastAPI Agent  │───▶│  Manufacturing  │
│  /ping          │    │                 │    │  Tools          │
│                 │    │  Port 8080      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Tool Integration**
```
┌─────────────────┐
│  FastAPI Agent  │
│                 │
│  /invocations   │───▶ Intent Tool
│  /ping          │───▶ Data Tool
│                 │───▶ Model Tool
│  Port 8080      │───▶ Solver Tool
│                 │───▶ Swarm Tool
└─────────────────┘───▶ Critique Tool
                      └─▶ Explain Tool
```

## **📊 File Purposes**

### **Core Files**
- **`custom_agent.py`**: Main FastAPI application for AgentCore
- **`fastmcp_server.py`**: MCP server implementation
- **`Dockerfile`**: ARM64 container configuration
- **`requirements.mcp.txt`**: Python dependencies

### **Deployment Files**
- **`deploy_custom_agent.py`**: Deploy to AgentCore
- **`invoke_custom_agent.py`**: Test deployed agent
- **`.bedrock_agentcore.yaml`**: AgentCore configuration

### **Documentation**
- **`AGENTCORE_DEPLOYMENT_GUIDE.md`**: Complete deployment guide
- **`PROJECT_STRUCTURE.md`**: This file
- **`Tasks.md`**: Task tracking
- **`README.md`**: Main documentation

## **🧹 Cleanup Summary**

### **Removed Files**
- ❌ Old versioned MCP server files
- ❌ Obsolete Dockerfiles
- ❌ Old test files
- ❌ Old requirements files
- ❌ Log files
- ❌ Obsolete entry points
- ❌ Unused directories (`src/shared`, `src/platform`)

### **Archived Files**
- 📦 `cleanup_archive/`: Contains all obsolete files for reference

### **Kept Files**
- ✅ Production architecture (`src/mcp_server/`)
- ✅ Working custom agent
- ✅ Production Dockerfile
- ✅ Deployment scripts
- ✅ Documentation
- ✅ Configuration files

## **🎯 Success Metrics**

- ✅ **Clean Structure**: Organized, maintainable codebase
- ✅ **Production Ready**: All components working in AgentCore
- ✅ **Documented**: Complete deployment and structure guides
- ✅ **Archived**: Obsolete files preserved for reference
- ✅ **Deployable**: One-command deployment process

---

**Last Updated**: August 26, 2025  
**Status**: ✅ Clean and Production Ready  
**Version**: 1.0.0
