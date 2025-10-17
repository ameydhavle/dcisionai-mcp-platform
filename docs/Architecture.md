# DcisionAI Architecture

## 🏗️ **System Architecture Overview**

DcisionAI is built on a modern, scalable architecture that combines AI-powered problem formulation with real mathematical optimization solvers. The system is designed for high performance, reliability, and ease of integration.

## 🎯 **Core Architecture Principles**

### **1. AI-First Design**
- **Claude 3 Haiku** for intelligent problem understanding and model building
- **Natural Language Processing** for business problem translation
- **Automated Model Generation** with mathematical rigor

### **2. Real Optimization Engine**
- **OR-Tools Integration** with 8+ professional solvers
- **Solver Selection** based on problem characteristics
- **Performance Optimization** for large-scale problems

### **3. Microservices Architecture**
- **MCP Server** as the core optimization engine
- **SaaS Platform** for user interface and workflow management
- **Cloud-Native** deployment on AWS infrastructure

### **4. Developer-Friendly**
- **MCP Protocol** for IDE integration
- **REST APIs** for web integration
- **Python SDK** for custom applications

## 🏛️ **System Components**

```
┌─────────────────────────────────────────────────────────────────┐
│                    DcisionAI Platform                          │
├─────────────────────────────────────────────────────────────────┤
│  🎯 MCP Server (Core Engine)                                   │
│  ├── Intent Classification Engine                              │
│  ├── Data Analysis & Preprocessing                             │
│  ├── AI Model Builder                                          │
│  ├── Optimization Engine                                       │
│  ├── Solver Selection System                                   │
│  ├── Business Explainability Engine                            │
│  └── Workflow Automation Engine                                │
├─────────────────────────────────────────────────────────────────┤
│  🌐 SaaS Platform (User Interface)                             │
│  ├── React Frontend (Modern UI/UX)                             │
│  ├── Flask Backend (REST API)                                  │
│  ├── MCP Client (Server Integration)                           │
│  └── Workflow Management System                                │
├─────────────────────────────────────────────────────────────────┤
│  ☁️  Cloud Infrastructure                                       │
│  ├── AWS AgentCore Runtime                                     │
│  ├── PyPI Distribution                                         │
│  ├── Cursor IDE Integration                                    │
│  └── Scalable Deployment                                       │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 **MCP Server Architecture**

### **Core Engine Components**

#### **1. Intent Classification Engine**
```python
class IntentClassifier:
    """AI-powered problem understanding using Claude 3 Haiku"""
    
    def classify_intent(self, problem_description: str) -> Dict[str, Any]:
        """
        Analyzes business problems and determines:
        - Problem type (LP, MILP, QP, NLP)
        - Industry context
        - Complexity level
        - Solver requirements
        """
```

**Key Features:**
- **Natural Language Understanding**: Processes business problem descriptions
- **Industry Classification**: Identifies domain-specific requirements
- **Complexity Assessment**: Determines problem difficulty
- **Solver Recommendations**: Suggests optimal solvers

#### **2. Data Analysis Engine**
```python
class DataAnalyzer:
    """Comprehensive data assessment and preprocessing"""
    
    def analyze_data(self, problem_description: str, intent_data: Dict) -> Dict[str, Any]:
        """
        Performs data quality assessment:
        - Data readiness scoring
        - Variable identification
        - Constraint detection
        - Missing data analysis
        """
```

**Key Features:**
- **Data Quality Scoring**: 0-100% readiness assessment
- **Variable Extraction**: Identifies decision variables
- **Constraint Detection**: Finds business constraints
- **Data Validation**: Checks for completeness and consistency

#### **3. AI Model Builder**
```python
class ModelBuilder:
    """Claude 3 Haiku-powered mathematical model generation"""
    
    def build_model(self, problem_description: str, intent_data: Dict, data_analysis: Dict) -> Dict[str, Any]:
        """
        Generates mathematically rigorous optimization models:
        - Variable definitions
        - Objective functions
        - Constraint formulations
        - Model validation
        """
```

**Key Features:**
- **Mathematical Formulation**: PhD-level model generation
- **OR-Tools Compatibility**: Ensures solver compatibility
- **Constraint Parsing**: Robust mathematical expression handling
- **Model Validation**: Checks for mathematical correctness

#### **4. Optimization Engine**
```python
class OptimizationEngine:
    """Real mathematical optimization using OR-Tools"""
    
    def solve_optimization(self, model_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solves optimization problems using real solvers:
        - Solver selection
        - Problem solving
        - Solution validation
        - Performance metrics
        """
```

**Key Features:**
- **Real Optimization**: Uses actual mathematical solvers
- **Multiple Solvers**: 8+ professional optimization solvers
- **Performance Optimization**: Sub-second solve times
- **Solution Validation**: Ensures optimality and feasibility

#### **5. Solver Selection System**
```python
class SolverSelector:
    """Intelligent solver selection based on problem characteristics"""
    
    def select_solver(self, optimization_type: str, problem_size: Dict, performance_requirement: str) -> Dict[str, Any]:
        """
        Selects optimal solver based on:
        - Problem type (LP, MILP, QP, NLP)
        - Problem size (variables, constraints)
        - Performance requirements
        - Solver capabilities
        """
```

**Available Solvers:**
| Solver | Type | Best For | Performance |
|--------|------|----------|-------------|
| **PDLP** | LP | Large-scale problems | ⭐⭐⭐⭐⭐ |
| **GLOP** | LP | General purpose | ⭐⭐⭐⭐ |
| **CBC** | MILP | Mixed-integer problems | ⭐⭐⭐⭐ |
| **SCIP** | MILP | Complex MILP | ⭐⭐⭐⭐⭐ |
| **HiGHS** | LP/MILP | High-performance | ⭐⭐⭐⭐⭐ |
| **OSQP** | QP | Quadratic problems | ⭐⭐⭐⭐ |
| **SCS** | Conic | Conic optimization | ⭐⭐⭐⭐ |
| **CVXPY** | General | Research problems | ⭐⭐⭐ |

#### **6. Business Explainability Engine**
```python
class ExplainabilityEngine:
    """AI-generated business communication and insights"""
    
    def explain_optimization(self, problem_description: str, solution_data: Dict) -> Dict[str, Any]:
        """
        Generates comprehensive business reports:
        - Executive summaries
        - Technical details
        - Implementation guidance
        - Risk analysis
        """
```

**Key Features:**
- **Executive Summaries**: C-level business communication
- **Technical Details**: Mathematical and algorithmic insights
- **Implementation Guidance**: Step-by-step deployment plans
- **Risk Analysis**: Sensitivity and scenario analysis

#### **7. Workflow Automation Engine**
```python
class WorkflowEngine:
    """Industry-specific workflow automation"""
    
    def execute_workflow(self, industry: str, workflow_id: str, user_input: Dict) -> Dict[str, Any]:
        """
        Executes complete optimization workflows:
        - Industry-specific templates
        - End-to-end automation
        - Result integration
        - Business reporting
        """
```

**Industry Workflows:**
- **Manufacturing**: Production planning, inventory optimization, quality control
- **Healthcare**: Staff scheduling, patient flow, resource allocation
- **Retail**: Demand forecasting, pricing optimization, supply chain
- **Marketing**: Campaign optimization, budget allocation, customer segmentation
- **Financial**: Portfolio optimization, risk assessment, fraud detection
- **Logistics**: Route optimization, warehouse optimization, fleet management
- **Energy**: Grid optimization, renewable integration, demand response

## 🌐 **SaaS Platform Architecture**

### **Frontend (React)**

#### **Component Architecture**
```
src/
├── components/
│   ├── Dashboard/           # Main dashboard
│   ├── WorkflowBuilder/     # Workflow creation
│   ├── ResultsViewer/       # Optimization results
│   ├── DataUpload/          # Data management
│   └── Settings/            # User preferences
├── services/
│   ├── api.js              # API client
│   ├── mcp.js              # MCP client
│   └── auth.js             # Authentication
└── utils/
    ├── optimization.js     # Optimization utilities
    └── visualization.js    # Chart components
```

#### **Key Features**
- **Modern UI/UX**: Dark monochrome theme with professional design
- **Real-time Updates**: Live optimization results and progress
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Accessibility**: WCAG 2.1 AA compliant

### **Backend (Flask)**

#### **API Architecture**
```python
# REST API Endpoints
@app.route('/api/mcp/health-check', methods=['GET'])
@app.route('/api/mcp/classify-intent', methods=['POST'])
@app.route('/api/mcp/analyze-data', methods=['POST'])
@app.route('/api/mcp/build-model', methods=['POST'])
@app.route('/api/mcp/solve-optimization', methods=['POST'])
@app.route('/api/mcp/select-solver', methods=['POST'])
@app.route('/api/mcp/explain-optimization', methods=['POST'])
@app.route('/api/mcp/execute-workflow', methods=['POST'])
```

#### **Key Features**
- **RESTful Design**: Clean, documented API endpoints
- **MCP Integration**: Seamless connection to MCP server
- **Authentication**: Secure user management
- **Error Handling**: Comprehensive error management
- **Logging**: Detailed request/response logging

## ☁️ **Cloud Infrastructure**

### **AWS AgentCore Runtime**

#### **Deployment Architecture**
```
AWS AgentCore Runtime
├── Lambda Functions
│   ├── MCP Server Handler
│   ├── API Gateway Integration
│   └── CloudWatch Logging
├── ECR Container Registry
│   ├── MCP Server Image
│   └── DcisionAI Tools
├── IAM Roles & Policies
│   ├── Bedrock Access
│   ├── CloudWatch Logs
│   └── ECR Access
└── CloudWatch Monitoring
    ├── Performance Metrics
    ├── Error Tracking
    └── Cost Monitoring
```

#### **Key Features**
- **Serverless Scaling**: Automatic scaling based on demand
- **High Availability**: 99.9% uptime SLA
- **Cost Optimization**: Pay-per-use pricing
- **Security**: Enterprise-grade security

### **PyPI Distribution**

#### **Package Structure**
```
dcisionai-mcp-server/
├── dcisionai_mcp_server/
│   ├── __init__.py
│   ├── tools.py              # Core optimization tools
│   ├── optimization_engine.py # OR-Tools integration
│   ├── solver_selector.py    # Solver selection logic
│   └── working_mcp_server.py # MCP server implementation
├── pyproject.toml            # Package configuration
├── README.md                 # Documentation
└── requirements.txt          # Dependencies
```

#### **Installation Options**
```bash
# Standard installation
pip install dcisionai-mcp-server

# With optional solvers
pip install dcisionai-mcp-server[all-solvers]

# Development installation
pip install -e .
```

### **Cursor IDE Integration**

#### **MCP Configuration**
```json
{
  "mcpServers": {
    "dcisionai-mcp-server": {
      "command": "uvx",
      "args": ["dcisionai-mcp-server@latest"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      },
      "autoApprove": [
        "classify_intent",
        "analyze_data",
        "build_model",
        "solve_optimization",
        "select_solver",
        "explain_optimization",
        "get_workflow_templates",
        "execute_workflow"
      ]
    }
  }
}
```

## 🔄 **Data Flow Architecture**

### **Optimization Pipeline**

```
1. Problem Input
   ↓
2. Intent Classification (Claude 3 Haiku)
   ↓
3. Data Analysis & Preprocessing
   ↓
4. Model Building (AI-Powered)
   ↓
5. Solver Selection (ML-Based)
   ↓
6. Optimization Solving (OR-Tools)
   ↓
7. Business Explainability (AI-Generated)
   ↓
8. Results & Recommendations
```

### **API Request Flow**

```
Client Request
   ↓
Flask Backend
   ↓
MCP Client
   ↓
MCP Server
   ↓
DcisionAI Tools
   ↓
Optimization Engine
   ↓
OR-Tools Solvers
   ↓
Results Processing
   ↓
Response to Client
```

## 🛡️ **Security Architecture**

### **Security Layers**

1. **Authentication & Authorization**
   - JWT-based authentication
   - Role-based access control
   - API key management

2. **Data Protection**
   - End-to-end encryption
   - Data anonymization
   - Secure data transmission

3. **Infrastructure Security**
   - VPC isolation
   - Security groups
   - IAM policies

4. **Compliance**
   - GDPR compliance
   - SOC 2 Type II
   - ISO 27001

## 📊 **Performance Architecture**

### **Performance Metrics**

- **Solve Time**: < 1 second for most problems
- **Throughput**: 1000+ requests per minute
- **Scalability**: Handles 1000+ variables, 1000+ constraints
- **Availability**: 99.9% uptime SLA

### **Optimization Strategies**

1. **Caching**: Redis-based result caching
2. **Load Balancing**: Multiple server instances
3. **Database Optimization**: Indexed queries
4. **CDN**: Global content delivery

## 🔧 **Development Architecture**

### **Development Workflow**

```
1. Local Development
   ├── MCP Server Testing
   ├── Unit Tests
   └── Integration Tests
   ↓
2. Staging Environment
   ├── End-to-End Testing
   ├── Performance Testing
   └── Security Testing
   ↓
3. Production Deployment
   ├── AWS AgentCore
   ├── PyPI Distribution
   └── Monitoring
```

### **Testing Strategy**

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **End-to-End Tests**: Complete workflow testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability assessment

## 🚀 **Deployment Architecture**

### **Deployment Options**

1. **AWS AgentCore Runtime** (Recommended)
   - Serverless deployment
   - Automatic scaling
   - Managed infrastructure

2. **Docker Containers**
   - Containerized deployment
   - Kubernetes orchestration
   - Custom infrastructure

3. **Local Installation**
   - PyPI package installation
   - Development environment
   - Custom configurations

### **Monitoring & Observability**

- **CloudWatch**: AWS-native monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **ELK Stack**: Log aggregation and analysis

---

**DcisionAI Architecture**: *Scalable, Secure, and Developer-Friendly*