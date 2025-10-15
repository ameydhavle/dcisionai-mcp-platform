# 🚀 DcisionAI Platform - Enhanced Architecture

## 🎯 **Platform Overview**

**DcisionAI is an intelligent decision support platform that bridges the gap between AI chatbots and spreadsheets, providing mathematically proven optimal decisions with full transparency and interactivity.**

### **Core Value Proposition**
- **Decision Intelligence**: Mathematically proven optimal decisions with full transparency
- **Multi-Agent Orchestration**: Specialized AI agents collaborate to solve complex problems
- **Actionable Insights**: Transforms data into concrete, implementable strategies
- **Real-time Analysis**: Interactive 3D visualizations, sensitivity analysis, and risk assessment

## 🏗️ **Enhanced Architecture**

### **Production Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend Layer (React)                      │
│                    platform.dcisionai.com                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Perplexity-   │  │   3D Decision   │  │   Sensitivity   │  │
│  │   Style UI      │  │   Landscape     │  │   Analysis      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Monte Carlo   │  │   Business      │  │   Interactive   │  │
│  │   Risk Analysis │  │   Impact        │  │   Results       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway Layer (AWS)                     │
│                    h5w9r03xkf.execute-api.us-east-1.amazonaws.com │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   /health       │  │   /intent       │  │   /data         │  │
│  │   /model        │  │   /solve        │  │   /3d-landscape │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   /sensitivity  │  │   /monte-carlo  │  │   /business-    │  │
│  │                 │  │                 │  │   impact        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Lambda Layer (AWS)                          │
│                    dcisionai-streaming-mcp-manufacturing        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Intent        │  │   Data          │  │   Model         │  │
│  │   Classification│  │   Analysis      │  │   Building      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Optimization  │  │   3D Landscape  │  │   Sensitivity   │  │
│  │   Solving       │  │   Generation    │  │   Analysis      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │   Monte Carlo   │  │   Business      │                      │
│  │   Risk Analysis │  │   Impact        │                      │
│  └─────────────────┘  └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI Platform Layer (AWS Bedrock)             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Claude 3      │  │   Claude 3.5    │  │   Inference     │  │
│  │   Haiku         │  │   Sonnet        │  │   Profiles      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 **8 Core Tools**

### **Original 4 Tools (Optimization Pipeline)**
1. **Intent Classification** (`/intent`)
   - Analyzes problem descriptions
   - Classifies optimization type and scale
   - Extracts entities and objectives

2. **Data Analysis** (`/data`)
   - Identifies data requirements
   - Assesses data readiness
   - Provides data quality metrics

3. **Model Building** (`/model`)
   - Creates mathematical optimization models
   - Defines variables, constraints, and objectives
   - Determines model complexity and scalability

4. **Optimization Solving** (`/solve`)
   - Solves mathematical optimization problems
   - Uses PuLP CBC solver
   - Provides optimal solutions and sensitivity analysis

### **New 4 Tools (Enhanced Analysis)**
5. **3D Landscape Generation** (`/3d-landscape`)
   - Generates 3D terrain data for visualization
   - Creates constraint walls and optimal points
   - Provides interactive 3D decision landscape

6. **Sensitivity Analysis** (`/sensitivity`)
   - Analyzes parameter impact on solutions
   - Assesses feasibility and risk
   - Provides implementation recommendations

7. **Monte Carlo Risk Analysis** (`/monte-carlo`)
   - Runs risk simulations with parameter uncertainty
   - Calculates Value at Risk (VaR) and Expected Shortfall
   - Provides confidence intervals and scenario analysis

8. **Enhanced Business Impact** (`/business-impact`)
   - Calculates sophisticated financial metrics
   - Provides operational impact assessment
   - Includes competitive advantage analysis

## 🎨 **Frontend Architecture**

### **React Components**
- **App.js**: Main application with state management
- **Sidebar.js**: Navigation and feature access
- **Hero.js**: Landing page with quick actions
- **OptimizationResults.js**: Enhanced results display
- **DecisionLandscape3D.js**: 3D visualization using Three.js
- **SensitivityAnalysis.js**: Interactive sensitivity analysis
- **ModelsPage.js**: Available models showcase
- **AgentsPage.js**: AI agents overview
- **KnowledgeBasePage.js**: Data management interface
- **DataConnectorsPage.js**: External data integration

### **Key Features**
- **Perplexity-style UI**: Clean, modern interface
- **Real-time Updates**: Live optimization progress
- **Interactive 3D**: Three.js-powered visualizations
- **Responsive Design**: Mobile and desktop optimized
- **Professional Styling**: Enterprise-grade appearance

## 🚀 **Deployment Architecture**

### **Production (AWS)**
- **Frontend**: CloudFront + S3 (platform.dcisionai.com)
- **Backend**: API Gateway + Lambda (h5w9r03xkf.execute-api.us-east-1.amazonaws.com)
- **AI**: AWS Bedrock with inference profiles
- **Storage**: S3 for static assets and data
- **CDN**: CloudFront for global distribution

### **Local Development**
- **Frontend**: React dev server (localhost:3000)
- **Backend**: Flask proxy server (localhost:5000)
- **MCP Server**: Local MCP server (localhost:8000)

## 🔄 **Data Flow**

1. **User Input**: Problem description via frontend
2. **Intent Classification**: AI analyzes and classifies the problem
3. **Data Analysis**: AI assesses data requirements and readiness
4. **Model Building**: AI creates mathematical optimization model
5. **Optimization Solving**: Mathematical solver finds optimal solution
6. **Enhanced Analysis**: 3D landscape, sensitivity, risk, and business impact
7. **Results Display**: Interactive frontend with multiple visualization options

## 🛡️ **Security & Performance**

### **Security**
- **CORS**: Properly configured for cross-origin requests
- **Authentication**: API Gateway with proper permissions
- **Data Privacy**: No sensitive data stored permanently
- **HTTPS**: All communications encrypted

### **Performance**
- **Lambda**: Serverless scaling for backend
- **CloudFront**: Global CDN for frontend
- **Caching**: Intelligent caching strategies
- **Optimization**: Efficient algorithms and data structures

## 📊 **Monitoring & Analytics**

- **Health Checks**: Real-time system status monitoring
- **Performance Metrics**: Response times and success rates
- **Usage Analytics**: Tool usage and optimization patterns
- **Error Tracking**: Comprehensive error logging and handling

## 🔮 **Future Enhancements**

- **Multi-tenant Support**: Enterprise customer isolation
- **Advanced Visualizations**: More 3D and interactive features
- **API Rate Limiting**: Usage-based access controls
- **Custom Models**: User-defined optimization models
- **Integration APIs**: Third-party system connections
- **Mobile App**: Native mobile application
- **Voice Interface**: Voice-activated optimization
- **Collaborative Features**: Team-based decision making

---

*This architecture represents the current state of DcisionAI Platform as of October 2025, with all 8 tools operational and the enhanced frontend deployed to production.*