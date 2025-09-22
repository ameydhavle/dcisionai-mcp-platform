# 🚀 DcisionAI MCP Server - Quick Start Guide

## 🎯 **Get Started in 5 Minutes**

This guide will help you connect to and use the DcisionAI Manufacturing MCP Server in just a few minutes.

## 📋 **Prerequisites**

- **API Key**: Get your API key from the [DcisionAI Customer Portal](https://portal.dcisionai.com)
- **Python 3.8+** or **Node.js 16+** (for SDK usage)
- **Internet Connection**: Access to the DcisionAI MCP Server

## 🔑 **Step 1: Get Your API Key**

1. **Visit the Customer Portal**: Go to [portal.dcisionai.com](https://portal.dcisionai.com)
2. **Sign Up**: Create your account with email verification
3. **Generate API Key**: Navigate to "API Keys" and create a new key
4. **Copy Your Key**: Save your API key securely (format: `dai_xxxxxxxxxxxxxxxx`)

## 🔗 **Step 2: Connect to the MCP Server**

### **Option A: Using Python SDK (Recommended)**

```bash
# Install the DcisionAI MCP SDK
pip install dcisionai-mcp
```

```python
import asyncio
from dcisionai_mcp import DcisionAIClient

async def main():
    # Initialize the client with your API key
    client = DcisionAIClient(api_key="dai_your_api_key_here")
    
    # Test the connection
    print("🔗 Connecting to DcisionAI MCP Server...")
    
    # List available tools
    tools = await client.list_tools()
    print(f"✅ Connected! Found {len(tools)} tools:")
    for tool in tools:
        print(f"   - {tool.name}: {tool.description}")
    
    # Test a manufacturing tool
    result = await client.manufacturing_intent_classification(
        query="Optimize production line efficiency for maximum throughput"
    )
    
    print(f"🎯 Intent Classification Result:")
    print(f"   Intent: {result.intent}")
    print(f"   Confidence: {result.confidence}")
    print(f"   Entities: {result.entities}")

# Run the example
asyncio.run(main())
```

### **Option B: Using TypeScript/JavaScript SDK**

```bash
# Install the DcisionAI MCP SDK
npm install @dcisionai/mcp-client
```

```typescript
import { DcisionAIClient } from '@dcisionai/mcp-client';

async function main() {
    // Initialize the client with your API key
    const client = new DcisionAIClient({
        apiKey: 'dai_your_api_key_here'
    });
    
    // Test the connection
    console.log('🔗 Connecting to DcisionAI MCP Server...');
    
    // List available tools
    const tools = await client.listTools();
    console.log(`✅ Connected! Found ${tools.length} tools:`);
    tools.forEach(tool => {
        console.log(`   - ${tool.name}: ${tool.description}`);
    });
    
    // Test a manufacturing tool
    const result = await client.manufacturingIntentClassification({
        query: 'Optimize production line efficiency for maximum throughput'
    });
    
    console.log('🎯 Intent Classification Result:');
    console.log(`   Intent: ${result.intent}`);
    console.log(`   Confidence: ${result.confidence}`);
    console.log(`   Entities: ${result.entities}`);
}

// Run the example
main().catch(console.error);
```

### **Option C: Using cURL (Direct API)**

```bash
# Test connection and list tools
curl -X POST "https://agentcore.dcisionai.com/mcp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dai_your_api_key_here" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# Test manufacturing intent classification
curl -X POST "https://agentcore.dcisionai.com/mcp" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dai_your_api_key_here" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "manufacturing_intent_classification",
      "arguments": {
        "query": "Optimize production line efficiency for maximum throughput"
      }
    }
  }'
```

## 🛠️ **Step 3: Available Tools**

The DcisionAI Manufacturing MCP Server provides 4 powerful tools:

### **1. Manufacturing Intent Classification**
```python
result = await client.manufacturing_intent_classification(
    query="We need to optimize our production schedule to minimize costs"
)
# Returns: intent, confidence, entities, objectives, reasoning
```

### **2. Manufacturing Data Analysis**
```python
result = await client.manufacturing_data_analysis(
    data={
        "total_workers": 50,
        "production_lines": 3,
        "max_hours_per_week": 48
    },
    intent_result=intent_result
)
# Returns: data_requirements, insights, optimization_readiness_score
```

### **3. Manufacturing Model Builder**
```python
result = await client.manufacturing_model_builder(
    intent_result=intent_result,
    data_result=data_result
)
# Returns: model_type, variables, constraints, objectives
```

### **4. Manufacturing Optimization Solver**
```python
result = await client.manufacturing_optimization_solver(
    model_result=model_result
)
# Returns: solution, optimal_values, performance_metrics
```

## 🔄 **Step 4: Complete Workflow Example**

Here's a complete example that uses all tools in sequence:

```python
import asyncio
from dcisionai_mcp import DcisionAIClient

async def complete_manufacturing_optimization():
    client = DcisionAIClient(api_key="dai_your_api_key_here")
    
    # Step 1: Classify the intent
    print("🎯 Step 1: Classifying manufacturing intent...")
    intent_result = await client.manufacturing_intent_classification(
        query="Optimize worker assignment across production lines to maximize efficiency while minimizing costs"
    )
    print(f"   Intent: {intent_result.intent} (confidence: {intent_result.confidence})")
    
    # Step 2: Analyze the data
    print("\n📊 Step 2: Analyzing manufacturing data...")
    data_result = await client.manufacturing_data_analysis(
        data={
            "total_workers": 50,
            "production_lines": 3,
            "max_hours_per_week": 48,
            "worker_skills": ["assembly", "quality_control", "packaging"],
            "line_capacities": [100, 120, 80]
        },
        intent_result=intent_result
    )
    print(f"   Readiness Score: {data_result.optimization_readiness_score}")
    
    # Step 3: Build the optimization model
    print("\n🏗️ Step 3: Building optimization model...")
    model_result = await client.manufacturing_model_builder(
        intent_result=intent_result,
        data_result=data_result
    )
    print(f"   Model Type: {model_result.model_type}")
    print(f"   Variables: {len(model_result.variables)}")
    print(f"   Constraints: {len(model_result.constraints)}")
    
    # Step 4: Solve the optimization
    print("\n🔧 Step 4: Solving optimization...")
    solution_result = await client.manufacturing_optimization_solver(
        model_result=model_result
    )
    print(f"   Solution Status: {solution_result.status}")
    print(f"   Optimal Value: {solution_result.optimal_value}")
    
    return {
        "intent": intent_result,
        "data_analysis": data_result,
        "model": model_result,
        "solution": solution_result
    }

# Run the complete workflow
result = asyncio.run(complete_manufacturing_optimization())
print("\n🎉 Manufacturing optimization completed successfully!")
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Authentication Error**
```
Error: Invalid API key
```
**Solution**: 
- Verify your API key is correct
- Check that your account is active
- Ensure you're using the correct format: `dai_xxxxxxxxxxxxxxxx`

#### **2. Connection Timeout**
```
Error: Connection timeout
```
**Solution**:
- Check your internet connection
- Verify the MCP server is operational at [status.dcisionai.com](https://status.dcisionai.com)
- Try again in a few minutes

#### **3. Rate Limit Exceeded**
```
Error: Rate limit exceeded
```
**Solution**:
- Wait for the rate limit to reset (usually 1 hour)
- Consider upgrading your plan for higher limits
- Implement request throttling in your application

#### **4. Tool Not Found**
```
Error: Tool 'manufacturing_intent_classification' not found
```
**Solution**:
- Check the tool name spelling
- Verify the tool is available by calling `list_tools()`
- Ensure you're using the latest SDK version

### **Getting Help**

- **Documentation**: [docs.dcisionai.com](https://docs.dcisionai.com)
- **Support**: [support.dcisionai.com](https://support.dcisionai.com)
- **Status Page**: [status.dcisionai.com](https://status.dcisionai.com)
- **Community**: [community.dcisionai.com](https://community.dcisionai.com)

## 📊 **Rate Limits & Quotas**

| Plan | Requests/Hour | Requests/Day | Support |
|------|---------------|--------------|---------|
| **Free** | 100 | 1,000 | Community |
| **Pro** | 1,000 | 10,000 | Email |
| **Enterprise** | 10,000 | 100,000 | Priority |

## 🔒 **Security Best Practices**

1. **Keep Your API Key Secure**:
   - Never commit API keys to version control
   - Use environment variables: `export DcisionAI_API_KEY="dai_your_key"`
   - Rotate keys regularly

2. **Use HTTPS**:
   - All connections are encrypted by default
   - Never send API keys over unencrypted connections

3. **Monitor Usage**:
   - Check your usage dashboard regularly
   - Set up alerts for unusual activity
   - Review API logs for security issues

## 🎯 **Next Steps**

1. **Explore More Tools**: Try all 4 manufacturing tools
2. **Read the Full Documentation**: [docs.dcisionai.com](https://docs.dcisionai.com)
3. **Join the Community**: [community.dcisionai.com](https://community.dcisionai.com)
4. **Upgrade Your Plan**: Get higher limits and priority support
5. **Build Your Application**: Integrate DcisionAI into your manufacturing systems

## 📞 **Support**

- **Email**: support@dcisionai.com
- **Live Chat**: Available in the customer portal
- **Documentation**: [docs.dcisionai.com](https://docs.dcisionai.com)
- **Status**: [status.dcisionai.com](https://status.dcisionai.com)

---

**Welcome to DcisionAI!** 🚀

Start building intelligent manufacturing solutions with our advanced MCP server and 18-agent swarm architecture.
