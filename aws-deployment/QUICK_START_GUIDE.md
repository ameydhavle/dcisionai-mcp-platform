# 🚀 DcisionAI Manufacturing Optimizer - Quick Start Guide

## ⚡ **Get Up and Running in 15 Minutes**

This guide will help you deploy and start using the DcisionAI Manufacturing Optimizer quickly.

---

## 🎯 **What You'll Get**

- ✅ **AI-Powered Manufacturing Optimization** in minutes
- ✅ **Real Mathematical Optimization** using PuLP CBC solver
- ✅ **Production-Ready AWS Deployment**
- ✅ **Modern Web Interface** for easy interaction
- ✅ **Complete API** for integration

---

## 📋 **Prerequisites**

- AWS Account with admin permissions
- AWS CLI v2 installed and configured
- Docker installed and running
- Basic understanding of manufacturing operations

---

## 🚀 **Step 1: Deploy to AWS (5 minutes)**

### **Option A: One-Click Deployment**
```bash
# Clone the repository
git clone <repository-url>
cd dcisionai-mcp-platform/aws-deployment

# Deploy everything
./deploy.sh
```

### **Option B: Manual Deployment**
```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name dcisionai-manufacturing-dcisionai --region us-east-1

# 2. Build and push images
cd backend && docker build -t dcisionai-backend . && docker tag dcisionai-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-dcisionai:backend-latest && docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-dcisionai:backend-latest

cd ../frontend && docker build -f Dockerfile.simple -t dcisionai-frontend . && docker tag dcisionai-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-dcisionai:frontend-latest && docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/dcisionai-manufacturing-dcisionai:frontend-latest

# 3. Deploy infrastructure
aws cloudformation deploy --template-file infrastructure/cloudformation-template.yaml --stack-name dcisionai-manufacturing --capabilities CAPABILITY_IAM --region us-east-1
```

---

## 🌐 **Step 2: Access Your Application (2 minutes)**

After deployment, you'll get URLs like:
- **Frontend**: `http://your-alb-dns-name`
- **Backend API**: `http://your-alb-dns-name/api`

### **Test the Deployment**
```bash
# Check backend health
curl http://your-deployment-url:8000/health

# Expected response:
{
  "status": "healthy",
  "architecture": "4-agent simplified",
  "bedrock_connected": true,
  "tools_available": 2,
  "version": "1.0.0-simplified"
}
```

---

## 🎯 **Step 3: Your First Optimization (3 minutes)**

### **Using the Web Interface**

1. **Open the Frontend**: Navigate to your frontend URL
2. **Type Your Problem**: In the chat interface, enter:
   ```
   Optimize production line efficiency with 50 workers across 3 manufacturing lines
   ```
3. **Get Results**: You'll see:
   - Intent classification
   - Data analysis
   - Mathematical model
   - Optimization solution

### **Using the API**

```bash
curl -X POST http://your-deployment-url:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "manufacturing_optimize",
      "arguments": {
        "problem_description": "Optimize production line efficiency with 50 workers across 3 manufacturing lines",
        "constraints": {},
        "optimization_goals": []
      }
    }
  }'
```

### **Expected Results**
```json
{
  "status": "success",
  "intent_classification": {
    "intent": "production_optimization",
    "confidence": 0.9
  },
  "optimization_solution": {
    "status": "optimal",
    "objective_value": 350.0,
    "solution": {
      "worker_productivity": 100.0,
      "line_throughput": 150.0,
      "downtime": 0.0
    },
    "solve_time": 0.025,
    "solver_used": "pulp_cbc"
  }
}
```

---

## 🔧 **Step 4: Integration (5 minutes)**

### **Python Integration**

```python
import requests
import json

def optimize_manufacturing(problem_description):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "manufacturing_optimize",
            "arguments": {
                "problem_description": problem_description,
                "constraints": {},
                "optimization_goals": []
            }
        }
    }
    
    response = requests.post("http://your-deployment-url:8000/mcp", json=payload)
    result = response.json()
    return json.loads(result['result']['content'][0]['text'])

# Use it
result = optimize_manufacturing(
    "Minimize supply chain costs for 5 warehouses across different regions"
)
print(f"Objective Value: {result['optimization_solution']['objective_value']}")
```

### **JavaScript Integration**

```javascript
async function optimizeManufacturing(problemDescription) {
    const payload = {
        jsonrpc: "2.0",
        id: 1,
        method: "tools/call",
        params: {
            name: "manufacturing_optimize",
            arguments: {
                problem_description: problemDescription,
                constraints: {},
                optimization_goals: []
            }
        }
    };
    
    const response = await fetch("http://your-deployment-url:8000/mcp", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    const result = await response.json();
    return JSON.parse(result.result.content[0].text);
}

// Use it
const result = await optimizeManufacturing(
    "Maximize quality control efficiency while reducing inspection costs"
);
console.log(`Objective Value: ${result.optimization_solution.objective_value}`);
```

---

## 📊 **Step 5: Example Use Cases**

### **Production Optimization**
```
"Optimize production line efficiency with 50 workers across 3 manufacturing lines"
```

### **Supply Chain Management**
```
"Minimize supply chain costs for 8 suppliers across different regions while ensuring 99% on-time delivery"
```

### **Quality Control**
```
"Maximize quality control efficiency while reducing inspection costs by 30%"
```

### **Resource Allocation**
```
"Optimize resource allocation across 5 production lines with varying demand patterns"
```

### **Inventory Management**
```
"Optimize inventory levels to minimize holding costs while preventing stockouts across 200+ SKUs"
```

---

## 🎯 **Best Practices**

### **Query Formulation**
- ✅ **Be Specific**: Include numbers, constraints, and objectives
- ✅ **Provide Context**: Mention industry, scale, and business goals
- ✅ **Include Constraints**: Specify limitations and requirements
- ✅ **Define Success**: What does "optimal" mean for your use case?

### **Integration Tips**
- ✅ **Error Handling**: Always check response status
- ✅ **Caching**: Cache results for similar queries
- ✅ **Monitoring**: Track optimization results and business impact
- ✅ **Iteration**: Start simple and gradually increase complexity

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **"Bedrock Connection Failed"**
- Verify AWS credentials: `aws sts get-caller-identity`
- Check AWS region settings
- Ensure Bedrock access permissions

#### **"Optimization Failed"**
- Check constraint feasibility
- Simplify the problem description
- Verify variable bounds are realistic

#### **"Slow Response Times"**
- Reduce problem complexity
- Check AWS region latency
- Monitor resource utilization

### **Health Checks**
```bash
# Backend health
curl http://your-deployment-url:8000/health

# Frontend health
curl http://your-deployment-url:3000/

# AWS resources
aws ecs describe-services --cluster dcisionai-manufacturing-cluster
```

---

## 📚 **Next Steps**

### **Learn More**
- 📖 [Complete Documentation](./CUSTOMER_DOCUMENTATION.md)
- 🎯 [Customer Examples](./CUSTOMER_EXAMPLES.md)
- 🏗️ [Architecture Details](./README.md)

### **Advanced Features**
- 🔧 Custom optimization models
- 📊 Performance monitoring
- 🔒 Security hardening
- 📈 Auto-scaling configuration

### **Enterprise Features**
- 🏢 Multi-tenant deployment
- 🔐 Advanced authentication
- 📊 Custom dashboards
- 🎓 Training and support

---

## 🎉 **Congratulations!**

You've successfully deployed and started using the DcisionAI Manufacturing Optimizer! 

**What's Next?**
1. **Explore Examples**: Try different optimization scenarios
2. **Integrate**: Connect with your existing systems
3. **Scale**: Optimize more complex problems
4. **Monitor**: Track performance and business impact

**Need Help?**
- 📧 Email: support@dcisionai.com
- 📚 Documentation: [docs.dcisionai.com](https://docs.dcisionai.com)
- 🐛 Issues: [GitHub Issues](https://github.com/dcisionai/issues)

**Ready to transform your manufacturing operations? Let's optimize!** 🚀
