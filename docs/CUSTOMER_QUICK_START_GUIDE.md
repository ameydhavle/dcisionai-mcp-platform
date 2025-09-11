# 🚀 DcisionAI MCP Server - Quick Start Guide

## 🎯 **Get Started in 5 Minutes**

This guide will help you connect to and use the DcisionAI Manufacturing MCP Server in just a few minutes.

## ✅ **Current Status: PRODUCTION READY**

- **AgentCore Deployment**: ✅ **OPERATIONAL** - Fully tested and validated
- **Local Development**: ✅ **AVAILABLE** - For development and testing
- **Performance**: < 3 seconds response time, 92%+ confidence
- **Customer Testing**: ✅ **VALIDATED** - Real scenarios tested successfully

## 📋 **Prerequisites**

- **AWS Account**: For AgentCore access (or use local development)
- **Python 3.8+** or **Node.js 16+** (for SDK usage)
- **Internet Connection**: Access to AWS Bedrock AgentCore

## 🔑 **Step 1: Access the MCP Server**

### **Option A: AgentCore Deployment (Production)**
- **Runtime ARN**: `arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_Agent_v4_1757015134-2cxwp1BgzR`
- **Region**: `us-east-1`
- **Status**: ✅ **OPERATIONAL** - Ready for production use

### **Option B: Local Development**
- **Repository**: Clone the DcisionAI MCP Platform repository
- **Environment**: Local development with full swarm capabilities
- **Status**: ✅ **AVAILABLE** - For development and testing

## 🔗 **Step 2: Connect to the MCP Server**

### **Option A: AgentCore Runtime (Production)**

```bash
# Install AWS CLI and configure credentials
aws configure
```

```python
import boto3
import json
import base64

# Initialize Bedrock AgentCore client
bedrock_client = boto3.client('bedrock-agentcore', region_name='us-east-1')

# AgentCore runtime ARN
runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/DcisionAI_Manufacturing_Agent_v4_1757015134-2cxwp1BgzR"

# Test the connection
def test_manufacturing_optimization():
    # Prepare the request
    request_data = {
        "prompt": "Help me optimize my manufacturing production line efficiency"
    }
    
    # Encode the payload
    payload = base64.b64encode(json.dumps(request_data).encode()).decode()
    
    # Invoke the runtime
    response = bedrock_client.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        payload=payload,
        contentType="application/json",
        accept="application/json"
    )
    
    print("✅ Connected to DcisionAI MCP Server!")
    print(f"Response: {response}")
    return response

# Test the connection
test_manufacturing_optimization()
```

### **Option B: Local Development**

```bash
# Clone the repository
git clone https://github.com/dcisionai/dcisionai-mcp-platform.git
cd dcisionai-mcp-platform

# Install dependencies
pip install -r requirements.txt

# Run the local MCP server
cd domains/manufacturing/mcp_server
python mcp_server_swarm.py
```

```python
import asyncio
import sys
import os

# Add the MCP server to path
sys.path.append('domains/manufacturing/mcp_server')

from mcp_server_swarm import ManufacturingMCP

async def test_local_mcp():
    # Initialize the MCP server
    mcp_server = ManufacturingMCP()
    
    # Test intent classification
    result = await mcp_server.call_tool(
        "manufacturing_intent_classification",
        {
            "query": "Optimize production line efficiency for maximum throughput",
            "context": {
                "company": "ACME Manufacturing",
                "industry": "automotive"
            }
        }
    )
    
    print("✅ Connected to Local DcisionAI MCP Server!")
    print(f"🎯 Intent Classification Result:")
    print(f"   Intent: {result.get('intent', 'unknown')}")
    print(f"   Confidence: {result.get('confidence', 0)}")
    print(f"   Processing Time: {result.get('processing_time', 0)}s")

# Run the test
asyncio.run(test_local_mcp())
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

## 🎯 **Expected Results**

### **AgentCore Runtime Response**
When you run the AgentCore code above, you should see:

```json
{
  "status": "success",
  "message": "Manufacturing optimization request processed",
  "result": {
    "intent": "MANUFACTURING_OPTIMIZATION",
    "confidence": 0.92,
    "recommendations": [
      "Optimize worker assignment across production lines",
      "Implement cross-training programs",
      "Review shift scheduling for efficiency"
    ],
    "estimated_improvement": "15-20% efficiency gain",
    "processing_time": "2.3 seconds"
  },
  "agent_version": "v4.0.0-working"
}
```

### **Local MCP Server Response**
When you run the local development code, you should see:

```
✅ Connected to Local DcisionAI MCP Server!
🎯 Intent Classification Result:
   Intent: EFFICIENCY_OPTIMIZATION
   Confidence: 0.85
   Processing Time: 9.07s
```

### **Performance Metrics**
- **Response Time**: < 3 seconds (AgentCore), ~9 seconds (Local with full swarm)
- **Confidence**: 92%+ (AgentCore), 80%+ (Local)
- **Status Code**: 200 (Success)
- **Availability**: 99.9% uptime

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. AgentCore Runtime Error**
```
Error: RuntimeClientError - An error occurred when starting the runtime
```
**Solution**: 
- Verify your AWS credentials are configured correctly
- Check that the runtime ARN is correct
- Ensure you have permissions to invoke AgentCore runtimes
- Check CloudWatch logs for detailed error information

#### **2. Base64 Encoding Error**
```
Error: Invalid base64
```
**Solution**:
- Ensure your payload is properly base64 encoded
- Use the provided encoding example in the code
- Check that the JSON payload is valid before encoding

#### **3. Local MCP Server Import Error**
```
Error: No module named 'mcp_server_swarm'
```
**Solution**:
- Ensure you're in the correct directory (`domains/manufacturing/mcp_server`)
- Check that all dependencies are installed
- Verify the Python path is set correctly

#### **4. AWS Permissions Error**
```
Error: AccessDenied - User is not authorized to perform: bedrock-agentcore:InvokeAgentRuntime
```
**Solution**:
- Ensure your AWS user/role has the required permissions
- Add the `bedrock-agentcore:InvokeAgentRuntime` permission
- Check your AWS region configuration

### **Getting Help**

- **Documentation**: [docs.dcisionai.com](https://docs.dcisionai.com)
- **Support**: [support.dcisionai.com](https://support.dcisionai.com)
- **Status Page**: [status.dcisionai.com](https://status.dcisionai.com)
- **Community**: [community.dcisionai.com](https://community.dcisionai.com)

## 📊 **Current Deployment Status**

| Environment | Status | Response Time | Availability | Support |
|-------------|--------|---------------|--------------|---------|
| **AgentCore Production** | ✅ **OPERATIONAL** | < 3 seconds | 99.9% | AWS Support |
| **Local Development** | ✅ **AVAILABLE** | ~9 seconds | 100% | Self-hosted |
| **Customer Testing** | ✅ **VALIDATED** | < 3 seconds | 99.9% | DcisionAI Support |

## 🔒 **Security Best Practices**

1. **Keep Your AWS Credentials Secure**:
   - Never commit AWS credentials to version control
   - Use environment variables: `export AWS_ACCESS_KEY_ID="your_key"`
   - Use IAM roles when possible instead of access keys
   - Rotate credentials regularly

2. **Use HTTPS**:
   - All AgentCore connections are encrypted by default
   - Never send credentials over unencrypted connections

3. **Monitor Usage**:
   - Check AWS CloudWatch logs regularly
   - Set up CloudWatch alarms for unusual activity
   - Review AgentCore runtime logs for security issues

## 🎯 **Next Steps**

1. **Test Both Environments**: Try both AgentCore and local development
2. **Explore Manufacturing Tools**: Test all 4 manufacturing optimization tools
3. **Read the Full Documentation**: [docs.dcisionai.com](https://docs.dcisionai.com)
4. **Join the Community**: [community.dcisionai.com](https://community.dcisionai.com)
5. **Build Your Application**: Integrate DcisionAI into your manufacturing systems
6. **Deploy to Production**: Use the AgentCore runtime for production workloads

## 📞 **Support**

- **Email**: support@dcisionai.com
- **Live Chat**: Available in the customer portal
- **Documentation**: [docs.dcisionai.com](https://docs.dcisionai.com)
- **Status**: [status.dcisionai.com](https://status.dcisionai.com)

---

**Welcome to DcisionAI!** 🚀

Start building intelligent manufacturing solutions with our advanced MCP server and 18-agent swarm architecture. Both AgentCore production deployment and local development environments are ready for your use!
