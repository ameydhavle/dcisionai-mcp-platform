# DcisionAI SaaS Platform

## 🌐 **Overview**

The DcisionAI SaaS Platform provides a comprehensive web-based interface for mathematical optimization, hosted at `platform.dcisionai.com`. It combines a modern React frontend with a Flask backend API gateway, all integrated with AWS Bedrock AgentCore Runtime for enterprise-grade performance and scalability.

---

## 🏗️ **Architecture**

### **Frontend (React SPA)**
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI)
- **State Management**: Redux Toolkit
- **Build Tool**: Vite
- **Deployment**: Static hosting with CDN

### **Backend (Flask API Gateway)**
- **Framework**: Flask with Gunicorn
- **Authentication**: AWS IAM integration
- **Caching**: Redis for response caching
- **Monitoring**: CloudWatch integration
- **Deployment**: Docker containers on ECS

### **Integration Layer**
- **AgentCore Runtime**: AWS Bedrock AgentCore for serverless execution
- **MCP Protocol**: Model Context Protocol for tool communication
- **API Gateway**: RESTful API for external integrations

---

## 🚀 **Features**

### **User Interface**
- **Modern Design**: Clean, intuitive interface with dark/light themes
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Real-time Updates**: Live progress tracking and result streaming
- **Accessibility**: WCAG 2.1 AA compliance

### **Optimization Workflow**
- **Guided Process**: Step-by-step optimization workflow
- **Problem Input**: Rich text editor with syntax highlighting
- **Results Visualization**: Interactive charts and graphs
- **Export Options**: PDF reports, Excel files, and API responses

### **Advanced Features**
- **Simulation Analysis**: Monte Carlo and scenario planning
- **Risk Assessment**: Value at Risk (VaR) and sensitivity analysis
- **Business Explanations**: Plain-English result interpretations
- **Workflow Templates**: 21 industry-specific optimization templates

---

## 🛠️ **Development Setup**

### **Prerequisites**
- **Node.js**: 18 or higher
- **Python**: 3.10 or higher
- **AWS CLI**: Latest version
- **Docker**: 20.10 or higher (optional)

### **Frontend Development**
```bash
# Navigate to frontend directory
cd saas-platform/frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

### **Backend Development**
```bash
# Navigate to backend directory
cd saas-platform/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server
python app.py
```

### **Full Stack Development**
```bash
# Start both frontend and backend
cd saas-platform
npm run dev  # Starts both frontend and backend concurrently
```

---

## 🔧 **Configuration**

### **Environment Variables**

#### **Backend (.env)**
```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key

# AWS Configuration
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# AgentCore Configuration
MCP_SERVER_URL=https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/mcp_server-IkOAiK3aOz/invocations

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0
```

#### **Frontend (.env)**
```bash
# API Configuration
REACT_APP_API_URL=http://localhost:5001/api
REACT_APP_WS_URL=ws://localhost:5001/ws

# Feature Flags
REACT_APP_ENABLE_SIMULATION=true
REACT_APP_ENABLE_EXPORT=true
REACT_APP_ENABLE_TEMPLATES=true
```

---

## 📡 **API Endpoints**

### **Health Check**
```http
GET /api/health
```

### **Optimization Workflow**
```http
POST /api/mcp/classify-intent
POST /api/mcp/analyze-data
POST /api/mcp/select-solver
POST /api/mcp/build-model
POST /api/mcp/solve-optimization
POST /api/mcp/explain-optimization
POST /api/mcp/simulate-scenarios
```

### **Workflow Templates**
```http
POST /api/mcp/get-workflow-templates
POST /api/mcp/execute-workflow
```

### **Authentication**
```http
POST /api/auth/login
POST /api/auth/logout
GET /api/auth/status
```

---

## 🎨 **UI Components**

### **Core Components**
```
src/components/
├── OptimizationWorkflow/     # Main workflow interface
│   ├── ProblemInput/         # Problem description input
│   ├── WorkflowSteps/        # Step-by-step workflow
│   ├── ResultsDisplay/       # Solution visualization
│   └── SimulationPanel/      # Risk analysis interface
├── Layout/                   # Application layout
│   ├── Header/              # Navigation header
│   ├── Sidebar/             # Navigation sidebar
│   └── Footer/              # Application footer
├── Common/                   # Shared components
│   ├── LoadingSpinner/      # Loading indicators
│   ├── ErrorBoundary/       # Error handling
│   └── Modal/               # Modal dialogs
└── Charts/                   # Data visualization
    ├── LineChart/           # Line charts
    ├── BarChart/            # Bar charts
    └── PieChart/            # Pie charts
```

### **State Management**
```
src/store/
├── slices/
│   ├── optimizationSlice.ts  # Optimization workflow state
│   ├── authSlice.ts         # Authentication state
│   ├── uiSlice.ts           # UI state (modals, themes)
│   └── simulationSlice.ts   # Simulation state
├── middleware/
│   ├── apiMiddleware.ts     # API call middleware
│   └── websocketMiddleware.ts # WebSocket middleware
└── store.ts                 # Store configuration
```

---

## 🔐 **Authentication & Security**

### **AWS IAM Integration**
- **User Authentication**: AWS IAM users and roles
- **Session Management**: JWT tokens with refresh mechanism
- **Permission Control**: Fine-grained access control
- **Audit Logging**: Comprehensive security event logging

### **Security Features**
- **HTTPS Only**: All communications encrypted
- **CORS Configuration**: Cross-origin request security
- **Rate Limiting**: API abuse prevention
- **Input Validation**: Comprehensive input sanitization
- **XSS Protection**: Cross-site scripting prevention

---

## 📊 **Monitoring & Analytics**

### **Application Metrics**
- **User Activity**: Page views, session duration, feature usage
- **Performance**: Response times, error rates, throughput
- **Business Metrics**: Optimization requests, success rates, user satisfaction

### **Technical Monitoring**
- **Infrastructure**: CPU, memory, disk usage
- **Application**: Error rates, response times, API usage
- **Security**: Authentication failures, suspicious activity

### **Dashboard**
- **Real-time Metrics**: Live performance monitoring
- **Historical Data**: Trend analysis and capacity planning
- **Alerting**: Automated alerts for critical issues

---

## 🚀 **Deployment**

### **Production Deployment**

#### **Frontend Deployment**
```bash
# Build for production
npm run build

# Deploy to CDN/static hosting
aws s3 sync build/ s3://dcisionai-frontend --delete
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

#### **Backend Deployment**
```bash
# Build Docker image
docker build -t dcisionai-backend .

# Deploy to ECS
aws ecs update-service --cluster dcisionai-cluster --service dcisionai-backend --force-new-deployment
```

### **Docker Deployment**
```bash
# Build and run with Docker Compose
docker-compose up -d

# Scale services
docker-compose up -d --scale backend=3
```

---

## 🧪 **Testing**

### **Frontend Testing**
```bash
# Unit tests
npm test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e
```

### **Backend Testing**
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# API tests
python -m pytest tests/api/
```

### **Load Testing**
```bash
# Install locust
pip install locust

# Run load tests
locust -f load_tests.py --host=https://platform.dcisionai.com
```

---

## 🔧 **Customization**

### **Themes**
```typescript
// Custom theme configuration
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
});
```

### **Workflow Customization**
```typescript
// Custom workflow steps
const customWorkflow = {
  steps: [
    { id: 'problem-input', component: ProblemInput },
    { id: 'data-analysis', component: DataAnalysis },
    { id: 'model-building', component: ModelBuilding },
    { id: 'optimization', component: Optimization },
    { id: 'results', component: ResultsDisplay },
  ],
};
```

### **API Customization**
```python
# Custom API endpoints
@app.route('/api/custom/endpoint', methods=['POST'])
def custom_endpoint():
    # Custom logic here
    return jsonify({"status": "success"})
```

---

## 📈 **Performance Optimization**

### **Frontend Optimization**
- **Code Splitting**: Lazy loading of components
- **Bundle Optimization**: Tree shaking and minification
- **Caching**: Service worker for offline capabilities
- **CDN**: Static asset delivery optimization

### **Backend Optimization**
- **Caching**: Redis for API response caching
- **Database**: Connection pooling and query optimization
- **Load Balancing**: Multiple backend instances
- **Async Processing**: Non-blocking I/O operations

---

## 🔄 **CI/CD Pipeline**

### **Automated Testing**
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          npm test
          python -m pytest
```

### **Automated Deployment**
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          docker build -t dcisionai-backend .
          aws ecs update-service --cluster dcisionai-cluster --service dcisionai-backend
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Frontend Build Failures**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### **Backend Connection Issues**
```bash
# Check if backend is running
curl http://localhost:5001/api/health

# Check logs
tail -f logs/backend.log
```

#### **AgentCore Integration Issues**
```bash
# Test AgentCore connection
agentcore invoke '{"prompt": "test"}'

# Check AWS credentials
aws sts get-caller-identity
```

### **Debug Mode**
```bash
# Enable debug logging
export FLASK_DEBUG=True
export REACT_APP_DEBUG=true
```

---

## 📚 **Documentation**

- **API Reference**: [Complete API documentation](../API_REFERENCE.md)
- **Deployment Guide**: [Production deployment guide](../DEPLOYMENT_GUIDE.md)
- **Architecture**: [System architecture overview](../Architecture.md)
- **MCP Server**: [MCP server documentation](./mcp-server/README.md)

---

## 📞 **Support**

- **GitHub Issues**: [Report bugs and request features](https://github.com/dcisionai/dcisionai-mcp-platform/issues)
- **Community**: [Join our Discord](https://discord.gg/dcisionai)
- **Email**: support@dcisionai.com
- **Documentation**: [Full documentation](../README.md)

---

*The DcisionAI SaaS Platform provides a complete web-based solution for mathematical optimization with enterprise-grade features and scalability.*
