# DcisionAI Platform - Quick Start Guide

## Get Started in 5 Minutes

Welcome to DcisionAI! This guide will help you get up and running with the platform in just a few minutes.

## Access the Platform

### Web Interface (Recommended)
1. **Visit**: https://platform.dcisionai.com
2. **No Registration Required**: Start optimizing immediately
3. **Free to Use**: No credit card or signup needed

### API Access
- **AgentCore Gateway**: `https://dcisionai-gateway-0de1a655-ja1rhlcqjx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp`
- **Documentation**: See [API Reference](./API_REFERENCE.md)
- **Authentication**: JWT Bearer token required

## Your First Optimization

### Step 1: Choose a Workflow
Select from 21 predefined workflows across 7 industries:

**Manufacturing:**
- Advanced Production Planning
- Supply Chain Optimization
- Quality Control Optimization

**Healthcare:**
- Resource Allocation Optimization
- Patient Flow Optimization
- Pharmaceutical Supply Chain

**Retail:**
- Inventory Optimization
- Pricing Strategy Optimization
- Store Layout Optimization

### Step 2: Watch the Magic Happen
DcisionAI will automatically:
1. **Analyze** your problem and classify the intent
2. **Assess** data requirements and readiness
3. **Build** a mathematical optimization model
4. **Solve** the problem using advanced algorithms
5. **Generate** comprehensive results and analysis

### **Step 3: Explore Results**
You'll get access to:
- **📊 Overview**: Summary of the optimization results
- **🧮 Mathematical Proof**: Detailed model and solution
- **🎨 3D Visualization**: Interactive 3D decision landscape
- **📈 Business Impact**: Financial and operational metrics
- **⚙️ Implementation Guide**: Clear next steps

## 🎨 **Interactive Features**

### **3D Decision Landscape**
- **Navigate**: Use mouse to rotate and zoom the 3D landscape
- **Explore**: See constraints as walls and optimal point as beacon
- **Understand**: Visualize the optimization space in 3D

### **Sensitivity Analysis**
- **Adjust Parameters**: Use sliders to modify variables
- **See Impact**: Real-time analysis of parameter changes
- **Risk Assessment**: Understand feasibility and risk levels

### **Enhanced Results**
- **Multiple Views**: Switch between different analysis perspectives
- **Export Data**: Download results in various formats
- **Share Results**: Generate shareable links for collaboration

## 🔧 **API Quick Start**

### **Health Check**
```bash
curl https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod/health
```

### **Simple Optimization**
```bash
curl -X POST https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod/intent \
  -H "Content-Type: application/json" \
  -d '{"problem_description": "Optimize production for 3 products"}'
```

### **JavaScript Example**
```javascript
const response = await fetch('https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod/intent', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    problem_description: 'Optimize production for 3 products'
  })
});

const result = await response.json();
console.log(result);
```

### **Python Example**
```python
import requests

response = requests.post(
    'https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod/intent',
    json={'problem_description': 'Optimize production for 3 products'}
)

result = response.json()
print(result)
```

## 🎯 **Common Use Cases**

### **Manufacturing Optimization**
**Problem**: "Optimize production scheduling for 5 products with different demand patterns and capacity constraints"

**What You Get**:
- Optimal production quantities for each product
- Resource allocation recommendations
- Cost savings analysis
- Risk assessment for demand variations

### **Supply Chain Optimization**
**Problem**: "Minimize transportation costs for delivering products to 10 locations from 3 warehouses"

**What You Get**:
- Optimal shipping routes and quantities
- Warehouse utilization analysis
- Cost reduction opportunities
- Delivery time optimization

### **Resource Allocation**
**Problem**: "Optimize staff allocation across 4 departments to maximize productivity while meeting demand"

**What You Get**:
- Optimal staff distribution
- Productivity impact analysis
- Cost-benefit assessment
- Implementation timeline

### **Inventory Management**
**Problem**: "Optimize inventory levels for 20 products to minimize holding costs while meeting service levels"

**What You Get**:
- Optimal stock levels for each product
- Reorder point recommendations
- Cost savings analysis
- Service level optimization

## 🎨 **Advanced Features**

### **3D Visualization**
- **Interactive Landscape**: Explore optimization space in 3D
- **Constraint Visualization**: See constraints as 3D walls
- **Optimal Point**: Visualize the best solution as a beacon
- **Variable Nodes**: Understand variable relationships

### **Sensitivity Analysis**
- **Parameter Sliders**: Adjust variables and see real-time impact
- **Risk Assessment**: Understand solution robustness
- **Feasibility Analysis**: Check constraint violations
- **Recommendations**: Get implementation guidance

### **Monte Carlo Risk Analysis**
- **Uncertainty Modeling**: Account for parameter uncertainty
- **Risk Metrics**: Value at Risk (VaR) and Expected Shortfall
- **Confidence Intervals**: Statistical confidence in results
- **Scenario Analysis**: Best case, worst case, and most likely outcomes

### **Business Impact Analysis**
- **Financial Metrics**: ROI, NPV, payback period
- **Operational Impact**: Efficiency gains, capacity utilization
- **Competitive Advantage**: Market position improvements
- **Implementation Timeline**: Phased rollout recommendations

## 🚀 **Best Practices**

### **Problem Description**
- **Be Specific**: Include numbers, constraints, and objectives
- **Provide Context**: Explain the business situation
- **Include Constraints**: Mention limitations and requirements
- **Define Success**: What does optimal mean for your case?

### **Interpreting Results**
- **Check Feasibility**: Ensure the solution is implementable
- **Validate Assumptions**: Review the model assumptions
- **Consider Sensitivity**: Test parameter variations
- **Plan Implementation**: Use the implementation guide

### **Iterative Optimization**
- **Start Simple**: Begin with basic problems
- **Add Complexity**: Gradually include more constraints
- **Test Variations**: Try different scenarios
- **Refine Models**: Improve based on results

## 🔧 **Troubleshooting**

### **Common Issues**

**Problem**: "No solution found"
- **Solution**: Check if constraints are too restrictive
- **Try**: Relaxing some constraints or adjusting bounds

**Problem**: "Results seem unrealistic"
- **Solution**: Review input data and assumptions
- **Try**: Validating data quality and model parameters

**Problem**: "3D visualization not loading"
- **Solution**: Check browser compatibility (Chrome/Firefox recommended)
- **Try**: Refreshing the page or clearing browser cache

### **Getting Help**
- **Documentation**: Check the [API Reference](./API_REFERENCE.md)
- **Examples**: See the [Platform Overview](./PLATFORM_OVERVIEW.md)
- **Support**: Contact support@dcisionai.com

## 🎯 **Next Steps**

### **Explore More Features**
1. **Try Different Problems**: Experiment with various optimization challenges
2. **Use Advanced Analysis**: Explore sensitivity and risk analysis
3. **Integrate with APIs**: Build custom applications
4. **Share Results**: Collaborate with team members

### **Enterprise Features**
1. **Custom Models**: Define your own optimization models
2. **API Integration**: Connect with existing systems
3. **White-label**: Custom branding and domain
4. **Dedicated Support**: Enterprise-grade support

### **Developer Resources**
1. **SDK Documentation**: JavaScript/TypeScript and Python SDKs
2. **API Examples**: Comprehensive code examples
3. **Integration Guides**: Step-by-step integration tutorials
4. **Community**: Join the developer community

## 🎉 **You're Ready!**

You now have everything you need to start using DcisionAI effectively. The platform is designed to be intuitive and powerful, so don't hesitate to experiment and explore.

**Happy Optimizing!** 🚀

---

*Need more help? Check out our [Platform Overview](./PLATFORM_OVERVIEW.md) or [API Reference](./API_REFERENCE.md) for detailed information.*
