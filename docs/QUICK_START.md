# DcisionAI Quick Start Guide

## 🚀 **Get Started in 5 Minutes**

This guide will help you get up and running with DcisionAI in just a few minutes, whether you want to use the web platform, integrate with your IDE, or build custom applications.

---

## 🎯 **Choose Your Path**

### **🌐 Web Platform (Recommended for Most Users)**
Use the hosted SaaS platform at `platform.dcisionai.com` - no installation required!

### **💻 IDE Integration (For Developers)**
Integrate DcisionAI directly into Cursor IDE or Claude Desktop for seamless optimization workflows.

### **🔧 API Integration (For Custom Applications)**
Use the REST API to integrate optimization capabilities into your own applications.

---

## 🌐 **Option 1: Web Platform (Fastest)**

### **Step 1: Visit the Platform**
Open your browser and go to: **`https://platform.dcisionai.com`**

### **Step 2: Describe Your Problem**
In the text area, describe your optimization problem. For example:

```
I need to optimize my production schedule. I have 2 production lines that can produce 100 and 90 units per hour respectively, at costs of $50 and $60 per hour. I need to produce at least 500 units. Minimize total cost.
```

### **Step 3: Follow the Workflow**
The platform will guide you through:
1. **Intent Classification** - Understanding your problem type
2. **Data Analysis** - Assessing your data requirements  
3. **Model Building** - Creating the mathematical model
4. **Optimization** - Finding the optimal solution
5. **Explanation** - Understanding the results in business terms

### **Step 4: Get Your Results**
You'll receive:
- ✅ **Optimal solution** with specific recommendations
- 📊 **Business explanation** in plain English
- 🔍 **Risk analysis** and sensitivity insights
- 💡 **Implementation guidance** for your team

**That's it! You're optimizing! 🎉**

---

## 💻 **Option 2: IDE Integration**

### **For Cursor IDE Users**

#### **Step 1: Install DcisionAI MCP Server**
```bash
# Install via uvx (recommended)
uvx dcisionai-mcp-server

# Or install via pip
pip install dcisionai-mcp-server
```

#### **Step 2: Configure Cursor IDE**
Create or update your MCP configuration file:

**Location**: `~/.cursor/mcp.json` (macOS/Linux) or `%APPDATA%\Cursor\User\mcp.json` (Windows)

```json
{
    "mcpServers": {
        "dcisionai-mcp-server": {
            "command": "uvx",
            "args": ["dcisionai-mcp-server"],
            "env": {
                "AWS_DEFAULT_REGION": "us-east-1"
            }
        }
    }
}
```

#### **Step 3: Restart Cursor IDE**
Close and reopen Cursor IDE to load the new MCP server.

#### **Step 4: Test the Integration**
In a new chat, try:
```
Classify this optimization problem: I need to optimize my production schedule. I have 2 production lines that can produce 100 and 90 units per hour respectively, at costs of $50 and $60 per hour. I need to produce at least 500 units. Minimize total cost.
```

You should see the DcisionAI tools available in the chat interface!

### **For Claude Desktop Users**

#### **Step 1: Install DcisionAI MCP Server**
```bash
uvx dcisionai-mcp-server
```

#### **Step 2: Configure Claude Desktop**
Edit your Claude Desktop configuration:

**Location**: 
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
    "mcpServers": {
        "dcisionai-mcp-server": {
            "command": "uvx",
            "args": ["dcisionai-mcp-server"]
        }
    }
}
```

#### **Step 3: Restart Claude Desktop**
Close and reopen Claude Desktop to load the MCP server.

---

## 🔧 **Option 3: API Integration**

### **Step 1: Set Up AWS Credentials**
```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region: us-east-1
# Enter default output format: json
```

### **Step 2: Test the API**
```bash
# Test health endpoint
curl -X GET https://platform.dcisionai.com/api/health

# Test intent classification
curl -X POST https://platform.dcisionai.com/api/mcp/classify-intent \
  -H "Content-Type: application/json" \
  -d '{
    "problem_description": "I need to optimize my production schedule. I have 2 production lines that can produce 100 and 90 units per hour respectively, at costs of $50 and $60 per hour. I need to produce at least 500 units. Minimize total cost."
  }'
```

### **Step 3: Integrate into Your Application**
```python
import requests
import json

# Set up client
base_url = "https://platform.dcisionai.com/api"
headers = {"Content-Type": "application/json"}

# Classify intent
response = requests.post(
    f"{base_url}/mcp/classify-intent",
    headers=headers,
    json={
        "problem_description": "Your optimization problem here..."
    }
)

result = response.json()
print(f"Problem type: {result['result']['optimization_type']}")
```

---

## 🎯 **Example Workflows**

### **Manufacturing Production Planning**
```
Problem: Optimize production schedule for 2 lines producing 100 and 90 units/hour at $50 and $60/hour. Need 500 units minimum. Minimize cost.

Expected Result: Use line 1 for 5 hours, line 2 for 0 hours. Total cost: $250.
```

### **Financial Portfolio Optimization**
```
Problem: Allocate $100K across 3 stocks with expected returns of 8%, 12%, 15% and risks of 10%, 15%, 20%. Limit total risk to 15%.

Expected Result: Optimal allocation with risk-adjusted returns and diversification strategy.
```

### **Retail Inventory Optimization**
```
Problem: Manage inventory for 500 stores across 3 regions. 1000 SKUs, $5M budget. Maximize profit while meeting demand.

Expected Result: Optimal inventory allocation across regions and SKUs with profit maximization.
```

---

## 🛠️ **Available Tools**

### **Core Optimization Workflow**
1. **`classify_intent`** - Understand your problem type and domain
2. **`analyze_data`** - Assess data quality and requirements
3. **`select_solver`** - Choose the best optimization algorithm
4. **`build_model`** - Create mathematical model using AI reasoning
5. **`solve_optimization`** - Find optimal solution
6. **`explain_optimization`** - Get business-friendly explanations
7. **`simulate_scenarios`** - Analyze risks and alternatives

### **Advanced Features**
- **`get_workflow_templates`** - Access 21 industry-specific workflows
- **`execute_workflow`** - Run complete optimization workflows
- **Pattern-Breaking AI** - Avoid biases from training data
- **Chain-of-Thought Reasoning** - Transparent decision process

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **MCP Server Not Showing in IDE**
```bash
# Check if MCP server is installed
uvx dcisionai-mcp-server --version

# Restart your IDE completely
# Check configuration file syntax
```

#### **API Authentication Errors**
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check IAM permissions
aws iam list-attached-user-policies --user-name your-username
```

#### **Web Platform Not Loading**
- Check your internet connection
- Try refreshing the page
- Clear browser cache
- Try a different browser

### **Getting Help**
- **Documentation**: [Full API Reference](API_REFERENCE.md)
- **GitHub Issues**: [Report bugs](https://github.com/dcisionai/dcisionai-mcp-platform/issues)
- **Community**: [Join our Discord](https://discord.gg/dcisionai)
- **Email**: support@dcisionai.com

---

## 🎓 **Next Steps**

### **Learn More**
- 📖 [Platform Overview](PLATFORM_OVERVIEW.md) - Comprehensive platform capabilities
- 🔧 [API Reference](API_REFERENCE.md) - Complete API documentation
- 🚀 [Deployment Guide](DEPLOYMENT_GUIDE.md) - Advanced deployment options

### **Advanced Usage**
- **Custom Workflows**: Create industry-specific optimization templates
- **API Integration**: Build custom applications with optimization capabilities
- **Enterprise Features**: Advanced security, monitoring, and support

### **Community**
- **GitHub**: [Contribute to the project](https://github.com/dcisionai/dcisionai-mcp-platform)
- **Discord**: [Join developer discussions](https://discord.gg/dcisionai)
- **Blog**: [Read optimization insights](https://blog.dcisionai.com)

---

## 🎉 **You're Ready!**

Congratulations! You now have DcisionAI set up and ready to solve your optimization problems. Whether you're using the web platform, IDE integration, or API, you have access to powerful AI-driven mathematical optimization capabilities.

**Start optimizing today and transform your business decisions! 🚀**

---

*Need help? Check our [troubleshooting guide](#troubleshooting) or contact our support team at support@dcisionai.com.*