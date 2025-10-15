# DcisionAI MCP Server - Customer Installation Guide

## 🎯 **Quick Start (Recommended)**

Since the GitHub repository isn't published yet, here's the **local installation method** that works immediately:

### **Step 1: Download and Install**

```bash
# Clone the repository (when available) or download the source
git clone https://github.com/DcisionAI/dcisionai-mcp-platform.git
cd dcisionai-mcp-platform/dcisionai-mcp-server

# Run the local installer
chmod +x install-local.sh
./install-local.sh
```

### **Step 2: Configure Environment**

The installer will create a `.env` file. Edit it with your credentials:

```bash
# Edit the .env file
nano dcisionai-mcp-server/.env
```

Update these values:
```env
DCISIONAI_ACCESS_TOKEN=your_actual_access_token_here
DCISIONAI_GATEWAY_URL=https://dcisionai-gateway-0de1a655-ja1rhlcqjx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp
DCISIONAI_GATEWAY_TARGET=DcisionAI-Optimization-Tools-Fixed
```

### **Step 3: Configure Cursor IDE**

The installer will create or update your Cursor MCP configuration at `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "dcisionai-optimization": {
      "command": "/path/to/your/venv/bin/python",
      "args": [
        "-m", "dcisionai_mcp_server.cli"
      ],
      "env": {
        "DCISIONAI_ACCESS_TOKEN": "your_access_token_here",
        "DCISIONAI_GATEWAY_URL": "https://dcisionai-gateway-0de1a655-ja1rhlcqjx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp",
        "DCISIONAI_GATEWAY_TARGET": "DcisionAI-Optimization-Tools-Fixed"
      },
      "disabled": false,
      "autoApprove": [
        "classify_intent",
        "analyze_data",
        "build_model",
        "solve_optimization",
        "get_workflow_templates",
        "execute_workflow"
      ]
    }
  }
}
```

### **Step 4: Restart Cursor IDE**

Close and reopen Cursor to activate the MCP integration.

### **Step 5: Verify Installation**

The DcisionAI MCP server should now show as **green** with "6 tools enabled" in Cursor.

## 🧪 **Testing Your Installation**

### **Test 1: CLI Commands**
```bash
# Activate the virtual environment
source venv/bin/activate

# Test the CLI
dcisionai-mcp-server --help

# List available workflows
dcisionai-mcp-server list-workflows

# Test connection
dcisionai-mcp-server test-connection

# Run health check
dcisionai-mcp-server health-check
```

### **Test 2: Cursor Integration**
In Cursor, try these example prompts:

```
"Help me optimize my supply chain costs for 5 warehouses"
"Show me available manufacturing workflows"
"Build a production planning model for 3 lines and 5 products"
"Analyze my inventory management problem"
```

## 🔧 **Manual Installation (Alternative)**

If the auto-installer doesn't work, here's the manual process:

### **Step 1: Set Up Python Environment**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -e dcisionai-mcp-server/
```

### **Step 2: Set Environment Variables**
```bash
export DCISIONAI_ACCESS_TOKEN="your_access_token_here"
export DCISIONAI_GATEWAY_URL="https://dcisionai-gateway-0de1a655-ja1rhlcqjx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
export DCISIONAI_GATEWAY_TARGET="DcisionAI-Optimization-Tools-Fixed"
```

### **Step 3: Configure Cursor MCP**
Create or edit `~/.cursor/mcp.json` with the configuration above.

## 🚀 **Using DcisionAI Tools in Cursor**

Once installed, you can use these optimization tools directly in Cursor:

### **Available Tools:**
1. **classify_intent** - Classify optimization problem intent
2. **analyze_data** - Analyze data requirements for optimization
3. **build_model** - Build mathematical optimization models
4. **solve_optimization** - Solve optimization problems
5. **get_workflow_templates** - Get available workflow templates
6. **execute_workflow** - Execute complete optimization workflows

### **Example Conversations:**
```
User: "I need to optimize my production schedule for 3 lines and 5 products"
Result: ✅ Complete workflow execution with mathematical model and solution

User: "Show me available healthcare workflows"
Result: ✅ List of 3 healthcare workflows (patient_flow, staff_scheduling, equipment_utilization)

User: "Help me optimize my supply chain costs"
Result: ✅ Intent classification, data analysis, model building, and optimization solution
```

## 📊 **Available Workflows**

The DcisionAI MCP Server includes **21 workflows** across **7 industries**:

### **Manufacturing (3 workflows)**
- Supply Chain Optimization
- Quality Control & Process Optimization
- Advanced Production Planning

### **Healthcare (3 workflows)**
- Patient Flow Optimization
- Staff Scheduling Optimization
- Equipment Utilization Optimization

### **Retail (3 workflows)**
- Inventory Management Optimization
- Marketing Campaign Optimization
- Pricing Strategy Optimization

### **Marketing (3 workflows)**
- Customer Acquisition Optimization
- Campaign Management Optimization
- Marketing Spend Optimization

### **Financial (3 workflows)**
- Portfolio Management Optimization
- Fraud Detection Optimization
- Credit Risk Assessment Optimization

### **Logistics (3 workflows)**
- Warehouse Operations Optimization
- Fleet Management Optimization
- Route Planning Optimization

### **Energy (3 workflows)**
- Renewable Energy Optimization
- Maintenance Scheduling Optimization
- Grid Management Optimization

## 🔧 **Troubleshooting**

### **Issue: Still showing red dot in Cursor**
- **Solution**: Ensure the virtual environment path is correct in `~/.cursor/mcp.json`
- **Check**: Run `which python` in your activated venv to get the correct path

### **Issue: "No tools, prompts, or resources"**
- **Solution**: Verify the MCP server is properly installed and configured
- **Check**: Run `dcisionai-mcp-server --help` to verify installation

### **Issue: Authentication errors**
- **Solution**: Check your `DCISIONAI_ACCESS_TOKEN` is valid and not expired
- **Check**: Run `dcisionai-mcp-server test-connection` to verify credentials

### **Issue: Import errors**
- **Solution**: Ensure all dependencies are installed in the virtual environment
- **Check**: Run `pip list` to verify all packages are installed

## 🎯 **Expected Results**

After successful installation, you should see:

- **✅ Green dot** in Cursor MCP servers list
- **✅ "6 tools enabled"** message
- **✅ All optimization tools** available in Cursor chat
- **✅ Real-time optimization** capabilities
- **✅ Professional mathematical models** and business insights

## 🌟 **Customer Benefits**

With the DcisionAI MCP Server, you get:

- **✅ Seamless IDE Integration** - Use optimization tools directly in Cursor
- **✅ Real-time Optimization** - Get instant mathematical models and solutions
- **✅ Industry Expertise** - 21 workflows across 7 industries
- **✅ Professional Results** - Production-grade optimization capabilities
- **✅ Natural Language Interface** - Ask questions in plain English
- **✅ Auto-Approval** - Tools run without manual confirmation

## 📈 **Next Steps**

1. **Install the MCP server** using the guide above
2. **Configure your credentials** in the .env file
3. **Restart Cursor IDE** to activate the integration
4. **Start optimizing** your business problems with AI-powered tools
5. **Explore workflows** across different industries
6. **Get professional insights** for your optimization challenges

**The future of optimization is now at your fingertips!** 🚀

## 📞 **Support**

If you encounter any issues:
1. Check the troubleshooting section above
2. Run the health check: `dcisionai-mcp-server health-check`
3. Verify your environment variables are set correctly
4. Ensure Cursor IDE is restarted after configuration changes

**Happy optimizing!** ✨
