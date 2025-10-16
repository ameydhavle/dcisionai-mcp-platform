# DcisionAI SaaS Platform

A complete SaaS platform for mathematical optimization with AI-powered problem formulation, featuring a modern React frontend and Flask backend integrated with our enhanced MCP server.

## 🚀 Features

### Enhanced MCP Server Integration (v1.0.11)
- **Claude 3 Haiku Model Building**: Superior mathematical reasoning for model generation
- **Enhanced Constraint Parser**: Handles quadratic constraints with linear approximations
- **PDLP Solver Integration**: Google's first-order method for large-scale optimization
- **Real OR-Tools Optimization**: Genuine mathematical optimization (no AI hallucinations)

### Modern Web Application
- **Perplexity-style UI**: Professional chat interface for optimization queries
- **Real-time Results**: Live optimization progress and results
- **3D Visualization**: Interactive decision landscape and sensitivity analysis
- **Mobile Responsive**: Works seamlessly on all devices
- **Dark Theme**: Modern monochrome design

### Production-Ready Infrastructure
- **Docker Containerization**: Both frontend and backend containerized
- **AWS Deployment Ready**: Complete CloudFormation templates
- **High Availability**: Multi-AZ deployment with auto-scaling
- **Security**: VPC isolation, IAM roles, and security groups
- **Monitoring**: CloudWatch integration for complete observability

## 📁 Directory Structure

```
saas-platform/
├── frontend/                 # React application
│   ├── src/                 # React source code
│   ├── public/              # Static assets
│   ├── package.json         # Node dependencies
│   ├── Dockerfile           # Frontend container
│   └── nginx.conf           # Web server config
├── backend/                 # Flask API server
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container
├── deployment/             # AWS deployment
│   ├── cloudformation-template.yaml  # AWS infrastructure
│   ├── start_servers.sh    # Local development
│   └── start_demo.sh       # Demo setup
└── README.md               # This file
```

## 🛠️ Local Development

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker (optional)

### Quick Start

1. **Start the Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```

2. **Start the Frontend**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Access the Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001
   - Health Check: http://localhost:5001/health

### Using Docker

1. **Build and Run Backend**:
   ```bash
   cd backend
   docker build -t dcisionai-backend .
   docker run -p 5001:5001 dcisionai-backend
   ```

2. **Build and Run Frontend**:
   ```bash
   cd frontend
   docker build -t dcisionai-frontend .
   docker run -p 3000:3000 dcisionai-frontend
   ```

## 🚀 AWS Deployment

### One-Click Deployment
```bash
cd deployment
./deploy.sh
```

### Manual Deployment
1. **Create ECR Repositories**:
   ```bash
   aws ecr create-repository --repository-name dcisionai-frontend
   aws ecr create-repository --repository-name dcisionai-backend
   ```

2. **Build and Push Images**:
   ```bash
   # Build and push frontend
   cd frontend
   docker build -t dcisionai-frontend .
   docker tag dcisionai-frontend:latest <account>.dkr.ecr.<region>.amazonaws.com/dcisionai-frontend:latest
   docker push <account>.dkr.ecr.<region>.amazonaws.com/dcisionai-frontend:latest

   # Build and push backend
   cd ../backend
   docker build -t dcisionai-backend .
   docker tag dcisionai-backend:latest <account>.dkr.ecr.<region>.amazonaws.com/dcisionai-backend:latest
   docker push <account>.dkr.ecr.<region>.amazonaws.com/dcisionai-backend:latest
   ```

3. **Deploy Infrastructure**:
   ```bash
   cd deployment
   aws cloudformation create-stack \
     --stack-name dcisionai-platform \
     --template-body file://cloudformation-template.yaml \
     --capabilities CAPABILITY_IAM
   ```

## 🔧 Configuration

### Environment Variables
- `AWS_DEFAULT_REGION`: AWS region (default: us-east-1)
- `ENVIRONMENT`: Environment (dev/staging/prod)
- `REACT_APP_API_URL`: Backend API URL

### MCP Server Integration
The backend automatically integrates with our enhanced MCP server (v1.0.11) which provides:
- Claude 3 Haiku for model building
- Enhanced constraint parsing
- PDLP solver for optimization
- Real OR-Tools mathematical optimization

## 📊 API Endpoints

### Health Check
- `GET /health` - Backend health status
- `GET /api/mcp/health-check` - MCP server health

### Optimization Pipeline
- `POST /api/mcp/classify-intent` - Intent classification
- `POST /api/mcp/analyze-data` - Data analysis
- `POST /api/mcp/build-model` - Model building (Claude 3 Haiku)
- `POST /api/mcp/solve-optimization` - Optimization solving (PDLP)

### Workflows
- `POST /api/mcp/execute-workflow` - Execute complete workflow
- `GET /api/mcp/workflow-templates` - Get workflow templates

### Examples
- `GET /api/examples` - Get example optimization queries

## 🎯 Usage Examples

### Portfolio Optimization
```json
{
  "problem_description": "I have $500,000 to invest and need help optimizing my portfolio allocation. I'm 38 years old, planning to retire at 60, and want to balance growth with risk management."
}
```

### Production Planning
```json
{
  "problem_description": "Optimize production line efficiency with 50 workers across 3 manufacturing lines, considering skill sets, line capacities, and cost constraints"
}
```

### Supply Chain Optimization
```json
{
  "problem_description": "Optimize supply chain for 5 warehouses across different regions, considering demand forecasting, inventory costs, and transportation constraints"
}
```

## 🔍 Monitoring

### CloudWatch Logs
- Backend: `/ecs/dcisionai-backend`
- Frontend: `/ecs/dcisionai-frontend`

### Health Checks
- Application Load Balancer health checks
- ECS service health monitoring
- CloudWatch alarms for critical metrics

## 🛡️ Security

- **VPC Isolation**: Private network environment
- **Security Groups**: Restrictive firewall rules
- **IAM Roles**: Least privilege access
- **HTTPS Ready**: SSL certificate support
- **Container Security**: Non-root user execution

## 💰 Cost Optimization

- **Fargate Spot**: 70% cost savings available
- **Auto-scaling**: Scale down during low usage
- **CloudWatch Logs**: 30-day retention
- **ECR**: Automatic image cleanup

## 🧪 Testing

### Local Testing
```bash
# Test backend
curl http://localhost:5001/health

# Test MCP integration
curl -X POST http://localhost:5001/api/mcp/classify-intent \
  -H "Content-Type: application/json" \
  -d '{"problem_description": "Optimize resource allocation"}'
```

### Production Testing
```bash
# Test deployment
./deployment/test-deployment.sh
```

## 🚀 Next Steps

1. **Deploy**: Run the deployment script
2. **Test**: Validate all endpoints
3. **Scale**: Configure auto-scaling
4. **Monitor**: Set up CloudWatch alarms
5. **Customize**: Add SSL certificates and custom domains

## 📞 Support

For issues or questions:
- Check the logs in CloudWatch
- Review the health check endpoints
- Test the MCP server integration
- Validate the optimization results

**Your AI-powered optimization platform is ready for production!** 🎯