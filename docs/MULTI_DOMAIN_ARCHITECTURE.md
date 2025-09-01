# DcisionAI Multi-Domain Platform Architecture

## 🏗️ **Architecture Overview**

The DcisionAI platform has been restructured to support multiple domains (Manufacturing, Finance, Pharma, Retail) with a shared framework that enables:

- **Domain Isolation**: Each domain operates independently with its own agents, tools, and workflows
- **Shared Framework**: Common base classes and utilities reduce code duplication
- **Scalable Design**: Easy to add new domains without affecting existing ones
- **Unified Management**: Central platform manager for cross-domain operations

## 📁 **New Directory Structure**

```
dcisionai-mcp-platform/
├── shared/                           # 🧩 Shared Framework Components
│   ├── core/                         # Core abstractions
│   │   ├── base_agent.py            # Base agent class
│   │   └── domain_manager.py        # Domain registration & management
│   ├── tools/                        # Base tool framework
│   │   └── base_tool.py             # Base tool class
│   ├── deployment/                   # Base deployment framework
│   │   └── base_deployer.py         # Base deployment class
│   ├── config/                       # Shared configuration
│   │   └── settings.py              # Platform-wide settings
│   └── __init__.py                  # Shared components exports
├── domains/                          # 🌐 Domain Implementations
│   ├── manufacturing/                # ✅ Active Manufacturing Domain
│   │   ├── agents/                   # Manufacturing agents
│   │   ├── tools/                    # Manufacturing tools
│   │   ├── deployment/               # Manufacturing deployment
│   │   ├── Dockerfile                # Manufacturing Docker config
│   │   └── requirements.txt          # Manufacturing dependencies
│   ├── finance/                      # 🔄 Planned Finance Domain
│   │   └── __init__.py              # Finance domain placeholder
│   ├── pharma/                       # 🔄 Planned Pharma Domain
│   │   └── __init__.py              # Pharma domain placeholder
│   └── __init__.py                  # Domain registry
├── platform/                         # 🎯 Platform Management
│   ├── orchestrator/                 # Platform orchestration
│   │   └── platform_manager.py      # Central platform manager
│   └── __init__.py                  # Platform components
├── docs/                            # 📚 Documentation
│   └── domains/                     # Domain-specific docs
├── main.py                          # 🚀 Main platform entry point
└── requirements.txt                  # Platform dependencies
```

## 🔧 **Shared Framework Components**

### **1. Base Agent Framework (`shared/core/base_agent.py`)**

Abstract base class that all domain agents inherit from:

```python
class BaseAgent(ABC):
    def __init__(self, domain: str, version: str, description: str):
        # Common initialization logic
        
    @abstractmethod
    def _initialize_tools(self) -> None:
        # Domain-specific tool initialization
        
    @abstractmethod
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # Domain-specific request processing
```

**Features:**
- Automatic metadata management
- Built-in logging and health monitoring
- Tool registration and management
- Request validation and logging

### **2. Base Tool Framework (`shared/tools/base_tool.py`)**

Abstract base class for all domain tools:

```python
class BaseTool(ABC):
    def __init__(self, name: str, domain: str, version: str, description: str):
        # Common tool initialization
        
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        # Domain-specific tool execution
```

**Features:**
- Standardized result structure (`ToolResult`)
- Built-in performance metrics
- Input validation and error handling
- Execution logging and monitoring

### **3. Domain Manager (`shared/core/domain_manager.py`)**

Central registry for all domains:

```python
class DomainManager:
    def register_domain(self, name: str, description: str, version: str) -> bool:
        # Register new domain
        
    def register_agent(self, domain: str, agent_name: str, agent: Any) -> bool:
        # Register agent with domain
        
    def register_tool(self, domain: str, tool_name: str, tool: Any) -> bool:
        # Register tool with domain
```

**Features:**
- Domain registration and discovery
- Agent and tool management per domain
- Health monitoring and status tracking
- Cross-domain capability discovery

### **4. Base Deployment Framework (`shared/deployment/base_deployer.py`)**

Abstract base class for domain deployment:

```python
class BaseDeployer:
    def __init__(self, config: DeploymentConfig):
        # Common deployment setup
        
    def deploy(self) -> DeploymentResult:
        # Standardized deployment process
```

**Features:**
- ECR authentication and Docker operations
- AgentCore runtime creation and management
- Deployment monitoring and status tracking
- Cleanup and resource management

### **5. Shared Configuration (`shared/config/settings.py`)**

Centralized configuration management:

```python
class Settings:
    def get_domain_config(self, domain_name: str) -> Dict[str, Any]:
        # Get domain-specific configuration
        
    def get_ecr_repo(self, domain_name: str) -> str:
        # Get ECR repository for domain
```

**Features:**
- Environment-based configuration
- Domain-specific settings
- AWS configuration management
- Centralized ECR and runtime naming

## 🌐 **Domain Implementations**

### **✅ Manufacturing Domain (Active)**

**Location**: `domains/manufacturing/`

**Components**:
- **Agent**: `DcisionAI_Manufacturing_Agent_v1` - Full E2E workflow
- **Tools**: Intent, Data, Model, Solver tools
- **Workflow**: Intent → Data → Model → Solver
- **Status**: ✅ **ACTIVE** - Fully functional

**Capabilities**:
- Manufacturing intent classification
- Data requirement analysis
- Optimization model building
- Production scheduling optimization

### **🔄 Finance Domain (Planned)**

**Location**: `domains/finance/`

**Planned Components**:
- **Agents**: Risk assessment, portfolio optimization, fraud detection
- **Tools**: Financial analysis, compliance checking, market analysis
- **Workflow**: Risk → Portfolio → Fraud → Compliance
- **Status**: 🔄 **PLANNED** - Architecture ready

**Planned Capabilities**:
- Financial risk assessment
- Portfolio optimization
- Fraud detection algorithms
- Regulatory compliance checking

### **🔄 Pharma Domain (Planned)**

**Location**: `domains/pharma/`

**Planned Components**:
- **Agents**: Drug discovery, clinical trial optimization, supply chain management
- **Tools**: Research optimization, regulatory compliance, data analysis
- **Workflow**: Discovery → Trials → Supply Chain → Compliance
- **Status**: 🔄 **PLANNED** - Architecture ready

**Planned Capabilities**:
- Drug discovery optimization
- Clinical trial planning
- Supply chain optimization
- Regulatory compliance management

## 🎯 **Platform Management**

### **Platform Manager (`platform/orchestrator/platform_manager.py`)**

Central orchestrator for the entire platform:

```python
class PlatformManager:
    def get_platform_summary(self) -> Dict[str, Any]:
        # Comprehensive platform overview
        
    def get_cross_domain_capabilities(self) -> Dict[str, Any]:
        # Cross-domain feature discovery
        
    def get_all_domains_health(self) -> Dict[str, Any]:
        # Platform-wide health monitoring
```

**Features**:
- Unified domain management
- Cross-domain capability discovery
- Platform health monitoring
- Configuration export and management

## 🚀 **Getting Started**

### **1. Run the Platform Demo**

```bash
python main.py
```

This will:
- Initialize all platform components
- Display domain information and status
- Show cross-domain capabilities
- Export platform configuration

### **2. Access Domain-Specific Components**

```python
from domains.manufacturing import DcisionAI_Manufacturing_Agent_v1
from platform import platform_manager

# Get platform summary
summary = platform_manager.get_platform_summary()

# Get domain information
manufacturing_info = platform_manager.get_domain_info("manufacturing")
```

### **3. Deploy a Domain**

```python
from domains.manufacturing.deployment import deploy_dcisionai_manufacturing_agent_v1

# Deploy manufacturing domain
deploy_dcisionai_manufacturing_agent_v1()
```

## 🔄 **Adding New Domains**

### **Step 1: Create Domain Structure**

```bash
mkdir -p domains/newdomain/{agents,tools,deployment}
```

### **Step 2: Implement Domain Components**

1. **Create Agent** (inherit from `BaseAgent`)
2. **Create Tools** (inherit from `BaseTool`)
3. **Create Deployment Script** (inherit from `BaseDeployer`)

### **Step 3: Register Domain**

```python
from shared.core.domain_manager import DomainManager

domain_manager = DomainManager()
domain_manager.register_domain(
    name="newdomain",
    description="New domain description",
    version="1.0.0"
)
```

### **Step 4: Update Configuration**

Add domain configuration to `shared/config/settings.py`:

```python
def _get_newdomain_config(self) -> Dict[str, Any]:
    return {
        "name": "newdomain",
        "description": "New domain description",
        "version": "1.0.0",
        "ecr_repo": f"{self.aws.ecr_base_url}/dcisionai-newdomain-v1",
        # ... other configuration
    }
```

## 📊 **Benefits of New Architecture**

### **✅ Code Reusability**
- Shared base classes reduce duplication
- Common utilities across all domains
- Standardized interfaces and patterns

### **✅ Maintainability**
- Clear separation of concerns
- Domain isolation prevents conflicts
- Centralized configuration management

### **✅ Scalability**
- Easy to add new domains
- Independent domain development
- Shared infrastructure and tools

### **✅ Consistency**
- Standardized deployment process
- Unified monitoring and health checks
- Consistent error handling and logging

### **✅ Developer Experience**
- Clear project structure
- Intuitive domain organization
- Comprehensive documentation

## 🔮 **Future Enhancements**

### **Phase 2: Enhanced Domains**
- Finance domain implementation
- Pharma domain implementation
- Retail domain implementation

### **Phase 3: Cross-Domain Features**
- Cross-domain workflows
- Shared data models
- Unified analytics dashboard

### **Phase 4: Advanced Features**
- Multi-tenant support
- Advanced monitoring and alerting
- Automated scaling and optimization

## 📚 **Additional Resources**

- **Platform Demo**: Run `python main.py` to see the architecture in action
- **Domain Examples**: See `domains/manufacturing/` for a complete domain implementation
- **Shared Framework**: Explore `shared/` for reusable components
- **Configuration**: Check `shared/config/settings.py` for platform settings

---

**🎉 The DcisionAI platform is now ready for multi-domain expansion!**
