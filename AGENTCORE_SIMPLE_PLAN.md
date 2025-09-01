# DcisionAI AgentCore Deployment - Simple Plan

## **🔍 What We Were Doing Wrong**

After reviewing the [official Strands AgentCore documentation](https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_bedrock_agentcore/), I identified several critical issues with our current approach:

### **1. Wrong Deployment Approach**
- **❌ Current**: Custom FastAPI agent with manual `/invocations` and `/ping` endpoints
- **✅ Correct**: Use **AgentCore SDK Integration** (Option A) - much simpler

### **2. Overcomplicated Architecture**
- **❌ Current**: Complex FastMCP server + custom FastAPI wrapper + manual endpoint handling
- **✅ Correct**: Simple agent function with `@app.entrypoint` decorator

### **3. Missing AgentCore SDK Integration**
- **❌ Current**: Manual HTTP server implementation
- **✅ Correct**: Use `bedrock-agentcore` SDK with automatic server setup

### **4. Unnecessary Complexity**
- **❌ Current**: Multiple layers of abstraction, custom protocol handling
- **✅ Correct**: Direct function calls with SDK wrapper

## **🚀 The Simple Solution**

The official documentation provides **two approaches**:

### **Option A: SDK Integration (RECOMMENDED)**
- **Use when**: You want to quickly deploy existing agent functions
- **Best for**: Simple agents, prototyping, minimal setup
- **Benefits**: Automatic HTTP server setup, built-in deployment tools
- **Trade-offs**: Less control over server configuration

### **Option B: Custom Implementation**
- **Use when**: You need full control over your agent's HTTP interface
- **Best for**: Complex agents, custom middleware, production systems
- **Benefits**: Complete FastAPI control, custom routing, advanced features
- **Trade-offs**: More setup required, manual server configuration

## **📋 Implementation Plan**

### **Step 1: Create Simple AgentCore Agent**

I've created `src/mcp_server/agentcore_simple_agent.py` that follows the **Option A: SDK Integration** approach:

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    # Your existing code remains unchanged
    return payload

if __name__ == "__main__":
    app.run()
```

### **Step 2: Simple Dockerfile**

I've created `Dockerfile.agentcore_simple` that:
- Uses ARM64 platform (AgentCore requirement)
- Exposes port 8080 (AgentCore requirement)
- Runs the simple agent directly

### **Step 3: Simple Deployment Script**

I've created `scripts/deployment/deploy_agentcore_simple.py` that:
- Builds and pushes to ECR
- Deploys to AgentCore using the control API
- Provides clear logging and error handling

### **Step 4: Test Script**

I've created `scripts/deployment/test_agentcore_simple.py` that:
- Lists available agent runtimes
- Tests the deployed agent
- Provides troubleshooting guidance

## **🔧 Key Differences**

| Aspect | Old Approach | New Simple Approach |
|--------|-------------|-------------------|
| **Server Setup** | Manual FastAPI with custom endpoints | Automatic via AgentCore SDK |
| **Entry Point** | Custom `/invocations` handler | `@app.entrypoint` decorator |
| **Dependencies** | Complex FastMCP + FastAPI | Simple AgentCore SDK |
| **Deployment** | Manual container configuration | SDK handles most configuration |
| **Testing** | Complex HTTP client setup | Simple SDK client |
| **Maintenance** | High - multiple layers | Low - single layer |

## **🚀 Quick Start Guide**

### **1. Deploy the Simple Agent**

```bash
# Deploy using the simple approach
python scripts/deployment/deploy_agentcore_simple.py
```

### **2. Test the Deployment**

```bash
# List available runtimes
python scripts/deployment/test_agentcore_simple.py

# Update the ARN in the test script and run
# python scripts/deployment/test_agentcore_simple.py
```

### **3. Monitor and Debug**

```bash
# Check agent status
aws bedrock-agentcore-control list-agent-runtimes --region us-east-1

# Monitor logs
aws logs tail /aws/bedrock-agentcore/runtimes/DcisionAI_Manufacturing_Simple_* --follow
```

## **📊 Expected Results**

With the simple approach, you should see:

1. **Faster Deployment**: ~5 minutes vs 15+ minutes
2. **Simpler Debugging**: Clear error messages and logs
3. **Better Reliability**: Fewer points of failure
4. **Easier Maintenance**: Single codebase to maintain

## **🔍 Why This Works Better**

### **1. Follows Official Documentation**
- Uses the recommended "Option A: SDK Integration"
- Leverages built-in AgentCore features
- Reduces custom code and complexity

### **2. Eliminates Common Issues**
- No manual HTTP endpoint management
- No custom protocol handling
- No complex container configuration

### **3. Better Error Handling**
- SDK provides built-in error handling
- Clear error messages and logging
- Automatic retry mechanisms

### **4. Easier Testing**
- Simple function testing
- Built-in SDK testing tools
- Clear success/failure indicators

## **📚 References**

- [Strands AgentCore Deployment Guide](https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_bedrock_agentcore/)
- [AWS AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [AgentCore Runtime Requirements](https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_bedrock_agentcore/#agentcore-runtime-requirements-summary)

## **🎯 Next Steps**

1. **Deploy the simple agent** using the new approach
2. **Test thoroughly** to ensure all functionality works
3. **Compare performance** with the old approach
4. **Document lessons learned** for future deployments
5. **Consider migrating** other agents to this simpler approach

---

**Bottom Line**: The official documentation is right - AgentCore deployment should be simple. We were overcomplicating it with custom implementations when the SDK integration approach is much easier and more reliable.
