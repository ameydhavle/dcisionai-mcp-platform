# DcisionAI Quick Start Guide

## 🚀 **Get Started in 5 Minutes**

This guide will help you get up and running with DcisionAI in just 5 minutes. Choose your preferred integration method and start optimizing!

## 🎯 **Integration Options**

### **Option 1: Cursor IDE Integration** (Recommended for Developers)
### **Option 2: SaaS Platform** (Recommended for Business Users)
### **Option 3: Python SDK** (Recommended for Custom Applications)
### **Option 4: REST API** (Recommended for Web Integration)

---

## 🎯 **Option 1: Cursor IDE Integration**

### **Step 1: Install MCP Server**
```bash
# Install using uvx (recommended)
uvx dcisionai-mcp-server@latest

# Or install using pip
pip install dcisionai-mcp-server
```

### **Step 2: Configure Cursor**
Add to your `~/.cursor/mcp.json`:
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
        "select_solver",
        "build_model",
        "solve_optimization",
        "simulate_scenarios",
        "explain_optimization",
        "get_workflow_templates",
        "execute_workflow"
      ]
    }
  }
}
```

### **Step 3: Restart Cursor**
Restart Cursor IDE to load the MCP server.

### **Step 4: Test Integration**
In Cursor, you can now use the DcisionAI tools directly:

```
@dcisionai-mcp-server classify_intent "Optimize my investment portfolio for maximum returns with moderate risk"
```

**Expected Result**: The MCP server will classify your intent and provide optimization recommendations.

### **Step 5: Test Simulation Analysis**
Try the new simulation tool for risk analysis:

```
@dcisionai-mcp-server simulate_scenarios "Quantitative trading execution optimization" --simulation_type monte_carlo --num_trials 10000
```

**Expected Result**: You'll get comprehensive simulation analysis including:
- **Risk Metrics**: Mean, standard deviation, VaR (95%)
- **Scenario Analysis**: Multiple what-if scenarios
- **Stress Testing**: Worst-case scenario analysis
- **Business Recommendations**: Actionable risk mitigation strategies

---

## 🌐 **Option 2: SaaS Platform**

### **Step 1: Visit Platform**
Go to [platform.dcisionai.com](https://platform.dcisionai.com)

### **Step 2: Sign Up**
Create a free account with your email address.

### **Step 3: Choose Workflow**
Select from 21 pre-built industry workflows:
- **Financial**: Portfolio optimization, risk assessment
- **Manufacturing**: Production planning, inventory optimization
- **Healthcare**: Staff scheduling, patient flow
- **Retail**: Demand forecasting, pricing optimization
- **Marketing**: Campaign optimization, budget allocation
- **Logistics**: Route optimization, warehouse management
- **Energy**: Grid optimization, renewable integration

### **Step 4: Upload Data**
Upload your data or use sample data to get started.

### **Step 5: Get Results**
Click "Optimize" and get your results in seconds!

**Expected Result**: You'll receive optimized solutions with business explanations and implementation guidance.

---

## 🐍 **Option 3: Python SDK**

### **Step 1: Install Package**
```bash
pip install dcisionai-mcp-server
```

### **Step 2: Basic Usage**
```python
from dcisionai_mcp_server.tools import DcisionAITools
import asyncio

async def optimize_portfolio():
    tools = DcisionAITools()
    
    # Step 1: Classify intent
    intent = await tools.classify_intent(
        "Optimize my investment portfolio for maximum returns with moderate risk"
    )
    print(f"Intent: {intent['result']['intent']}")
    
    # Step 2: Analyze data
    data = await tools.analyze_data("Portfolio optimization", intent['result'])
    print(f"Data readiness: {data['result']['readiness_score']*100:.1f}%")
    
    # Step 3: Build model
    model = await tools.build_model("Portfolio optimization", intent['result'], data['result'])
    print("Model built successfully")
    
    # Step 4: Solve optimization
    solution = await tools.solve_optimization("Portfolio optimization", intent['result'], data['result'], model['result'])
    print(f"Solution: {solution['result']['optimal_values']}")
    
    # Step 5: Get explanation
    explanation = await tools.explain_optimization("Portfolio optimization", intent['result'], data['result'], model['result'], solution['result'])
    print(f"Business impact: {explanation['result']['executive_summary']['business_impact']}")

# Run optimization
asyncio.run(optimize_portfolio())
```

### **Step 3: Advanced Usage**
```python
# Execute complete workflow
async def execute_workflow():
    tools = DcisionAITools()
    
    result = await tools.execute_workflow(
        industry="financial",
        workflow_id="portfolio_optimization",
        user_input={
            "portfolio_size": 1000000,
            "risk_tolerance": "moderate"
        }
    )
    
    print(f"Workflow result: {result['result']['final_results']}")

asyncio.run(execute_workflow())
```

**Expected Result**: You'll get a complete optimization solution with business explanations.

---

## 🌐 **Option 4: REST API**

### **Step 1: Get API Access**
1. Sign up at [platform.dcisionai.com](https://platform.dcisionai.com)
2. Generate API key in dashboard
3. Note your base URL: `https://platform.dcisionai.com/api`

### **Step 2: Test Connection**
```bash
curl -X GET "https://platform.dcisionai.com/api/mcp/health-check" \
  -H "Authorization: Bearer your-api-key"
```

### **Step 3: Classify Intent**
```bash
curl -X POST "https://platform.dcisionai.com/api/mcp/classify-intent" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_description": "Optimize my investment portfolio for maximum returns with moderate risk"
  }'
```

### **Step 4: Execute Workflow**
```bash
curl -X POST "https://platform.dcisionai.com/api/mcp/execute-workflow" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "financial",
    "workflow_id": "portfolio_optimization",
    "user_input": {
      "portfolio_size": 1000000,
      "risk_tolerance": "moderate"
    }
  }'
```

**Expected Result**: You'll receive JSON responses with optimization results.

---

## 🎯 **Common Use Cases**

### **Portfolio Optimization**
```python
# Optimize investment portfolio
result = await tools.execute_workflow(
    industry="financial",
    workflow_id="portfolio_optimization",
    user_input={
        "portfolio_size": 2000000,
        "risk_tolerance": "moderate",
        "time_horizon": "5_years"
    }
)
```

### **Production Planning**
```python
# Optimize production schedule
result = await tools.execute_workflow(
    industry="manufacturing",
    workflow_id="production_planning",
    user_input={
        "production_capacity": 1000,
        "demand_forecast": [100, 120, 110, 130],
        "resource_constraints": ["labor", "materials"]
    }
)
```

### **Staff Scheduling**
```python
# Optimize healthcare staff schedule
result = await tools.execute_workflow(
    industry="healthcare",
    workflow_id="staff_scheduling",
    user_input={
        "staff_count": 50,
        "shift_requirements": [8, 8, 8, 8],
        "skill_requirements": ["nurse", "doctor", "technician"]
    }
)
```

### **Route Optimization**
```python
# Optimize delivery routes
result = await tools.execute_workflow(
    industry="logistics",
    workflow_id="route_optimization",
    user_input={
        "vehicle_count": 10,
        "delivery_locations": 50,
        "capacity_constraints": [1000, 1000, 1000]
    }
)
```

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
# AWS Bedrock (for AI models)
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"

# API Configuration
export DcisionAI_API_KEY="your-api-key"
export DcisionAI_BASE_URL="https://platform.dcisionai.com/api"
```

### **Python Configuration**
```python
import os
from dcisionai_mcp_server.tools import DcisionAITools

# Configure AWS credentials
os.environ['AWS_ACCESS_KEY_ID'] = 'your-access-key'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'your-secret-key'
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

# Initialize tools
tools = DcisionAITools()
```

---

## 📊 **Understanding Results**

### **Optimization Results**
```json
{
  "status": "optimal",
  "objective_value": 1.22,
  "optimal_values": {
    "x1": 0.10,  // 10% allocation to asset 1
    "x2": 0.20,  // 20% allocation to asset 2
    "x3": 0.10,  // 10% allocation to asset 3
    "x4": 0.60   // 60% allocation to asset 4
  },
  "solve_time": 0.0034,
  "business_impact": {
    "total_profit": 1.22,
    "profit_increase": "12.2%",
    "cost_savings": 244000
  }
}
```

### **Business Explanation**
```json
{
  "executive_summary": {
    "problem_statement": "Optimize investment portfolio for maximum returns",
    "solution_approach": "Linear programming optimization model",
    "key_findings": [
      "Current portfolio is not well-diversified",
      "Reallocation can improve risk-return profile"
    ],
    "business_impact": "Expected to increase returns by 12.2%"
  },
  "implementation_guidance": {
    "next_steps": [
      "Communicate findings to investment committee",
      "Develop implementation plan"
    ],
    "monitoring_metrics": [
      "Portfolio returns",
      "Portfolio risk"
    ]
  }
}
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. MCP Server Not Loading**
```bash
# Check if package is installed
pip list | grep dcisionai-mcp-server

# Reinstall if needed
pip install --force-reinstall dcisionai-mcp-server
```

#### **2. AWS Credentials Error**
```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

#### **3. Python Version Compatibility**
```bash
# Check Python version
python --version

# Use Python 3.8-3.12 (OR-Tools compatibility)
pyenv install 3.11.0
pyenv local 3.11.0
```

#### **4. Import Errors**
```bash
# Install dependencies
pip install -r requirements.txt

# Or install with all solvers
pip install dcisionai-mcp-server[all-solvers]
```

### **Getting Help**

1. **Documentation**: [docs.dcisionai.com](https://docs.dcisionai.com)
2. **Support**: [support@dcisionai.com](mailto:support@dcisionai.com)
3. **GitHub Issues**: [github.com/dcisionai/issues](https://github.com/dcisionai/issues)
4. **Community**: [discord.gg/dcisionai](https://discord.gg/dcisionai)

---

## 🎯 **Next Steps**

### **1. Explore Workflows**
- Try different industry workflows
- Experiment with various problem types
- Learn from business explanations

### **2. Integrate with Your Systems**
- Connect to your databases
- Build custom applications
- Automate optimization processes

### **3. Scale Your Usage**
- Upgrade to Pro tier for higher limits
- Deploy on your infrastructure
- Get enterprise support

### **4. Join the Community**
- Share your use cases
- Contribute to open source
- Get expert support

---

## 🎉 **Congratulations!**

You've successfully set up DcisionAI! You now have access to:

- ✅ **8 Core Optimization Tools**
- ✅ **21 Industry Workflows**
- ✅ **Real Mathematical Solvers**
- ✅ **AI-Powered Business Explanations**
- ✅ **Multiple Integration Options**

**Ready to optimize?** Start with a simple problem and watch DcisionAI transform your business challenges into optimal solutions!

---

**DcisionAI Quick Start**: *From Zero to Optimization in 5 Minutes*