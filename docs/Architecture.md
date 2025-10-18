# DcisionAI Architecture

## 🏗️ **System Architecture Overview**

DcisionAI is built on a modern, scalable architecture that combines AI reasoning with mathematical optimization engines, hosted on AWS infrastructure for enterprise-grade performance and reliability.

---

## 🎯 **Architecture Principles**

### **1. AI-First Design**
- **Claude 3 Haiku Integration**: Advanced AI reasoning for model formulation
- **Pattern-Breaking Technology**: Avoids training data biases for fresh analysis
- **Chain-of-Thought Reasoning**: Transparent, auditable decision-making process

### **2. Universal Optimization**
- **Industry-Agnostic**: Works across any domain without hardcoded templates
- **Multi-Solver Support**: OR-Tools, Gurobi, CPLEX, and specialized solvers
- **Automatic Solver Selection**: AI chooses optimal solver based on problem characteristics

### **3. Enterprise Scalability**
- **Serverless Architecture**: AWS Bedrock AgentCore Runtime for infinite scale
- **Microservices Design**: Modular components for independent scaling
- **API-First**: RESTful interfaces for easy integration

### **4. Security & Compliance**
- **AWS IAM Integration**: Enterprise-grade authentication and authorization
- **End-to-End Encryption**: Secure data transmission and storage
- **SOC 2 Compliance**: Enterprise security standards

---

## 🏛️ **High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Client Layer                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Web Browser    │  Cursor IDE    │  Claude Desktop  │  Custom Applications    │
│  (React SPA)    │  (MCP Client)  │  (MCP Client)    │  (REST API Client)      │
└─────────────────┬───────────────┬───────────────────┬─────────────────────────┘
                  │               │                   │
                  ▼               ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            API Gateway Layer                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                    Flask Backend Server (MCP Client)                          │
│  • Request Routing    • Authentication    • Response Formatting               │
│  • Rate Limiting      • Error Handling    • Caching Layer                     │
└─────────────────────────────────┬───────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        AWS Bedrock AgentCore Runtime                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                    Hosted MCP Server (Serverless)                             │
│  • Auto-scaling      • Health Monitoring    • Session Management              │
│  • Resource Limits   • Observability        • Security Isolation              │
└─────────────────────────────────┬───────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          DcisionAI MCP Server                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│  • Intent Classification    • Model Building      • Optimization Solving       │
│  • Data Analysis           • Solver Selection    • Result Explanation          │
│  • Simulation Engine       • Business Validation • Workflow Templates          │
└─────────────────────────────────┬───────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Optimization Engine Layer                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  OR-Tools    │  Gurobi    │  CPLEX    │  SCIP    │  OSQP    │  Custom Solvers  │
│  (Primary)   │  (MIP)     │  (LP)     │  (MIP)   │  (QP)    │  (Specialized)   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 **Component Architecture**

### **Frontend Layer (React SPA)**

#### **Technology Stack**
- **Framework**: React 18 with TypeScript
- **State Management**: Redux Toolkit
- **UI Components**: Material-UI (MUI)
- **Build Tool**: Vite
- **Deployment**: Static hosting with CDN

#### **Key Components**
```
src/
├── components/
│   ├── OptimizationWorkflow/     # Main workflow interface
│   ├── ProblemInput/             # Problem description input
│   ├── ResultsDisplay/           # Solution visualization
│   └── SimulationPanel/          # Risk analysis interface
├── services/
│   ├── api.ts                    # API client
│   └── websocket.ts              # Real-time updates
└── utils/
    ├── validation.ts             # Input validation
    └── formatting.ts             # Data formatting
```

#### **Features**
- **Responsive Design**: Mobile-first approach
- **Real-time Updates**: WebSocket integration for live results
- **Progressive Web App**: Offline capabilities
- **Accessibility**: WCAG 2.1 AA compliance

### **Backend Layer (Flask API Gateway)**

#### **Technology Stack**
- **Framework**: Flask with Gunicorn
- **Authentication**: AWS IAM integration
- **Caching**: Redis for response caching
- **Monitoring**: CloudWatch integration
- **Deployment**: Docker containers on ECS

#### **Key Components**
```
backend/
├── app.py                        # Main Flask application
├── routes/
│   ├── mcp_routes.py            # MCP tool endpoints
│   ├── health_routes.py         # Health check endpoints
│   └── auth_routes.py           # Authentication endpoints
├── services/
│   ├── agentcore_client.py      # AgentCore Runtime client
│   ├── cache_service.py         # Redis caching
│   └── monitoring_service.py    # CloudWatch metrics
└── middleware/
    ├── auth_middleware.py       # Authentication
    ├── rate_limit.py            # Rate limiting
    └── error_handler.py         # Error handling
```

#### **Features**
- **MCP Client**: Communicates with AgentCore Runtime
- **API Gateway**: Routes requests to appropriate services
- **Authentication**: AWS IAM and session management
- **Rate Limiting**: Prevents abuse and ensures fair usage
- **Caching**: Improves response times for common requests

### **AgentCore Runtime Layer**

#### **Technology Stack**
- **Platform**: AWS Bedrock AgentCore Runtime
- **Runtime**: Python 3.10 with asyncio
- **Deployment**: Serverless with auto-scaling
- **Monitoring**: CloudWatch Logs and Metrics
- **Security**: IAM roles and VPC isolation

#### **Key Components**
```
agentcore/
├── dcisionai_agentcore_standalone.py  # Main entry point
├── requirements_standalone.txt        # Dependencies
└── deployment/
    ├── deploy_to_agentcore_noninteractive.sh
    └── gateway_config.json
```

#### **Features**
- **Serverless Execution**: Automatic scaling based on demand
- **Session Management**: Persistent sessions for multi-step workflows
- **Health Monitoring**: Automatic health checks and recovery
- **Resource Limits**: CPU and memory limits for security
- **Observability**: Comprehensive logging and metrics

### **MCP Server Layer**

#### **Technology Stack**
- **Protocol**: Model Context Protocol (MCP)
- **AI Models**: Claude 3 Haiku, Qwen 30B
- **Optimization**: OR-Tools, Gurobi, CPLEX
- **Simulation**: NumPy, SciPy, SimPy
- **Deployment**: PyPI package distribution

#### **Key Components**
```
dcisionai_mcp_server/
├── tools.py                       # Core optimization tools
├── optimization_engine.py         # Solver integration
├── ai_reasoning.py               # AI model interactions
├── simulation_engine.py          # Monte Carlo and other simulations
└── business_validation.py        # Business logic validation
```

#### **Core Tools**
1. **`classify_intent`** - Problem classification using AI reasoning
2. **`analyze_data`** - Data quality assessment and requirements analysis
3. **`select_solver`** - Intelligent solver selection based on problem characteristics
4. **`build_model`** - Mathematical model formulation with AI assistance
5. **`solve_optimization`** - Execute optimization using selected solver
6. **`explain_optimization`** - Business-friendly result explanation
7. **`simulate_scenarios`** - Risk analysis and scenario planning

### **Optimization Engine Layer**

#### **Supported Solvers**
- **Linear Programming**: OR-Tools PDLP, Gurobi LP, CPLEX LP
- **Mixed Integer**: OR-Tools CP-SAT, Gurobi MIP, SCIP
- **Quadratic Programming**: OSQP, Gurobi QP
- **Constraint Programming**: OR-Tools CP-SAT
- **Specialized Solvers**: Custom implementations for specific problem types

#### **Solver Selection Logic**
```python
def select_optimal_solver(problem_characteristics):
    if problem_characteristics.type == "linear_programming":
        if problem_characteristics.size == "small":
            return "OR-Tools Simplex"
        elif problem_characteristics.size == "large":
            return "OR-Tools PDLP"
    elif problem_characteristics.type == "mixed_integer":
        return "OR-Tools CP-SAT"
    # ... additional logic
```

---

## 🔄 **Data Flow Architecture**

### **Request Flow**
```
1. Client Request → 2. API Gateway → 3. AgentCore Runtime → 4. MCP Server → 5. Optimization Engine
                                                                                    ↓
6. Results ← 5. Response Processing ← 4. MCP Response ← 3. Runtime Response ← 2. API Response
```

### **Detailed Flow**
1. **Client Request**: User submits optimization problem via web UI, IDE, or API
2. **API Gateway**: Flask backend validates request, authenticates user, applies rate limits
3. **AgentCore Runtime**: AWS-hosted MCP server receives request, manages session
4. **MCP Server**: DcisionAI tools process request, classify intent, build model
5. **Optimization Engine**: Selected solver executes optimization, returns results
6. **Response Processing**: Results formatted, validated, and explained
7. **Client Response**: Formatted results returned to client with business explanations

### **Session Management**
```
Client Session → API Gateway Session → AgentCore Runtime Session → MCP Server Context
```

---

## 🛡️ **Security Architecture**

### **Authentication & Authorization**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client        │    │   API Gateway   │    │   AgentCore     │
│                 │    │                 │    │   Runtime       │
│ • AWS IAM       │───▶│ • JWT Tokens    │───▶│ • IAM Roles     │
│ • Session Mgmt  │    │ • Rate Limiting │    │ • VPC Isolation │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Data Security**
- **Encryption in Transit**: TLS 1.3 for all communications
- **Encryption at Rest**: AWS KMS for data storage
- **Input Validation**: Comprehensive validation at all layers
- **Output Sanitization**: Safe handling of optimization results

### **Network Security**
- **VPC Isolation**: Private subnets for backend services
- **Security Groups**: Restrictive firewall rules
- **WAF Protection**: Web Application Firewall for API endpoints
- **DDoS Protection**: AWS Shield for DDoS mitigation

---

## 📊 **Monitoring & Observability**

### **Monitoring Stack**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │    │   Infrastructure│    │   Business      │
│   Metrics       │    │   Metrics       │    │   Metrics       │
│                 │    │                 │    │                 │
│ • Response Time │    │ • CPU/Memory    │    │ • API Usage     │
│ • Error Rates   │    │ • Network I/O   │    │ • User Activity │
│ • Throughput    │    │ • Disk Usage    │    │ • Revenue       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   CloudWatch    │
                    │   Dashboard     │
                    └─────────────────┘
```

### **Logging Strategy**
- **Application Logs**: Structured JSON logging with correlation IDs
- **Access Logs**: Request/response logging with performance metrics
- **Error Logs**: Detailed error tracking with stack traces
- **Audit Logs**: Security and compliance event logging

### **Alerting**
- **Performance Alerts**: Response time and throughput thresholds
- **Error Alerts**: Error rate and failure pattern detection
- **Security Alerts**: Authentication failures and suspicious activity
- **Business Alerts**: Usage anomalies and capacity planning

---

## 🚀 **Scalability Architecture**

### **Horizontal Scaling**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   API Gateway   │    │   AgentCore     │
│                 │    │   Instances     │    │   Runtime       │
│ • Auto-scaling  │───▶│ • Auto-scaling  │───▶│ • Serverless    │
│ • Health Checks │    │ • Health Checks │    │ • Auto-scaling  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Caching Strategy**
- **API Response Caching**: Redis for frequently requested data
- **CDN Caching**: CloudFront for static assets
- **Database Caching**: Query result caching
- **Session Caching**: User session data caching

### **Performance Optimization**
- **Connection Pooling**: Database and external service connections
- **Async Processing**: Non-blocking I/O operations
- **Batch Processing**: Bulk operations for efficiency
- **Resource Optimization**: CPU and memory usage optimization

---

## 🔧 **Development Architecture**

### **Development Workflow**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Development   │    │   Testing       │    │   Production    │
│   Environment   │    │   Environment   │    │   Environment   │
│                 │    │                 │    │                 │
│ • Local MCP     │───▶│ • Staging MCP   │───▶│ • AgentCore     │
│ • Mock APIs     │    │ • Test Data     │    │ • Production    │
│ • Hot Reload    │    │ • Integration   │    │ • Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **CI/CD Pipeline**
1. **Code Commit**: Git push triggers CI pipeline
2. **Automated Testing**: Unit tests, integration tests, security scans
3. **Build & Package**: Docker images and deployment packages
4. **Deploy to Staging**: Automated deployment to test environment
5. **Production Deployment**: Manual approval and deployment
6. **Monitoring**: Automated health checks and rollback if needed

---

## 🔮 **Future Architecture**

### **Planned Enhancements**
- **Multi-Region Deployment**: Global availability and disaster recovery
- **Edge Computing**: CDN-based optimization for reduced latency
- **Advanced AI Models**: Integration with latest AI models and techniques
- **Real-time Collaboration**: Multi-user optimization sessions
- **Custom Model Training**: User-specific model fine-tuning

### **Technology Roadmap**
- **Q1 2025**: Multi-region deployment and edge computing
- **Q2 2025**: Advanced AI model integration and real-time collaboration
- **Q3 2025**: Custom model training and advanced analytics
- **Q4 2025**: Mobile applications and IoT integration

---

*This architecture is designed to be scalable, secure, and maintainable while providing the flexibility to adapt to changing requirements and technologies.*