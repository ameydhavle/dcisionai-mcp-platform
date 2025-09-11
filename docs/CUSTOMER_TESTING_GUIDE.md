# 🧪 DcisionAI MCP Server - Customer Testing Guide

## 📋 **Overview**

This guide provides step-by-step instructions for customers to test the DcisionAI Manufacturing MCP Server with their own scenarios. The guide includes both automated testing and manual verification steps.

---

## 🚀 **Quick Start Testing**

### **Option 1: Automated Customer Scenario Test**

Run the pre-built customer scenario test that simulates ACME Manufacturing:

```bash
# Navigate to the MCP server directory
cd domains/manufacturing/mcp_server

# Run the customer scenario test
python3 ../../../test_customer_scenario_e2e.py
```

**Expected Output**:
```
🚀 Starting DcisionAI MCP Server Customer Scenario E2E Test
📊 Customer: ACME Manufacturing
🎯 Problem: Production line efficiency optimization
🏭 Industry: Automotive Parts Manufacturing
🔧 Using existing E2E test infrastructure with real swarm agents

📋 Customer Intent Classification: STARTING
✅ Intent classified: CAPACITY_PLANNING (confidence: 0.800)
⏱️ Total workflow time: 9.07s
🎉 Customer scenario E2E test completed successfully!
```

---

## 🔧 **Custom Customer Testing**

### **Step 1: Prepare Your Manufacturing Data**

Create a JSON file with your manufacturing scenario:

```json
{
  "company": "Your Company Name",
  "industry": "Your Industry",
  "problem": "Your optimization problem",
  "data": {
    "total_workers": 100,
    "production_lines": 5,
    "max_hours_per_week": 40,
    "worker_skills": ["skill1", "skill2", "skill3"],
    "line_capacities": [150, 200, 180, 160, 190],
    "worker_efficiency": {
      "skill1": 0.95,
      "skill2": 0.90,
      "skill3": 0.85
    },
    "cost_per_hour": 30.00,
    "overtime_multiplier": 1.5
  }
}
```

### **Step 2: Create Custom Test Script**

Create a file `test_my_company.py`:

```python
#!/usr/bin/env python3
"""
Custom Customer Test for Your Company
"""

import asyncio
import json
import sys
import os

# Add the MCP server path
sys.path.append('domains/manufacturing/mcp_server')

from test_customer_scenario_e2e import CustomerScenarioE2ETester

class MyCompanyTester(CustomerScenarioE2ETester):
    def __init__(self):
        super().__init__()
        
        # Load your custom scenario
        with open('my_company_scenario.json', 'r') as f:
            self.customer_scenario = json.load(f)

async def main():
    tester = MyCompanyTester()
    await tester.run_complete_customer_scenario()

if __name__ == "__main__":
    asyncio.run(main())
```

### **Step 3: Run Your Custom Test**

```bash
python3 test_my_company.py
```

---

## 🎯 **Testing Individual Components**

### **Test 1: Intent Classification Only**

```python
import asyncio
import sys
sys.path.append('domains/manufacturing/mcp_server')

from manufacturing_intent_swarm import ManufacturingIntentSwarm

async def test_intent():
    swarm = ManufacturingIntentSwarm()
    
    result = await swarm.classify_intent(
        query="Optimize our production line efficiency",
        context={"company": "Your Company", "industry": "Manufacturing"}
    )
    
    print(f"Intent: {result}")
    return result

asyncio.run(test_intent())
```

### **Test 2: Data Analysis Only**

```python
import asyncio
import sys
sys.path.append('domains/manufacturing/mcp_server')

from manufacturing_data_swarm import ManufacturingDataSwarm

async def test_data_analysis():
    swarm = ManufacturingDataSwarm()
    
    data = {
        "total_workers": 50,
        "production_lines": 3,
        "line_capacities": [100, 120, 80]
    }
    
    result = await swarm.analyze_data(
        data=data,
        intent_result={"intent": "CAPACITY_PLANNING"},
        context={"company": "Your Company"}
    )
    
    print(f"Analysis: {result}")
    return result

asyncio.run(test_data_analysis())
```

### **Test 3: Model Building Only**

```python
import asyncio
import sys
sys.path.append('domains/manufacturing/mcp_server')

from manufacturing_model_swarm import ManufacturingModelSwarm

async def test_model_building():
    swarm = ManufacturingModelSwarm()
    
    result = await swarm.build_model(
        intent_result={"intent": "CAPACITY_PLANNING"},
        data_result={"data_quality": "good"},
        context={"company": "Your Company"}
    )
    
    print(f"Model: {result}")
    return result

asyncio.run(test_model_building())
```

### **Test 4: Optimization Solver Only**

```python
import asyncio
import sys
sys.path.append('domains/manufacturing/mcp_server')

from manufacturing_solver_swarm import ManufacturingSolverSwarm

async def test_solver():
    swarm = ManufacturingSolverSwarm()
    
    result = await swarm.solve_optimization(
        model_result={"model_type": "MILP"},
        context={"company": "Your Company"}
    )
    
    print(f"Solution: {result}")
    return result

asyncio.run(test_solver())
```

---

## 📊 **Performance Testing**

### **Load Testing**

Create a load test script:

```python
import asyncio
import time
import statistics

async def load_test():
    from manufacturing_intent_swarm import ManufacturingIntentSwarm
    
    swarm = ManufacturingIntentSwarm()
    times = []
    
    # Run 10 tests
    for i in range(10):
        start = time.time()
        await swarm.classify_intent(
            query=f"Test query {i}",
            context={"company": "Load Test"}
        )
        end = time.time()
        times.append(end - start)
        print(f"Test {i+1}: {end - start:.2f}s")
    
    print(f"Average: {statistics.mean(times):.2f}s")
    print(f"Min: {min(times):.2f}s")
    print(f"Max: {max(times):.2f}s")

asyncio.run(load_test())
```

### **Concurrent Testing**

```python
import asyncio

async def concurrent_test():
    from manufacturing_intent_swarm import ManufacturingIntentSwarm
    
    swarm = ManufacturingIntentSwarm()
    
    # Run 5 concurrent tests
    tasks = []
    for i in range(5):
        task = swarm.classify_intent(
            query=f"Concurrent test {i}",
            context={"company": "Concurrent Test"}
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    print(f"Completed {len(results)} concurrent tests")

asyncio.run(concurrent_test())
```

---

## 🔍 **Verification Steps**

### **Step 1: Verify Agent Swarm Initialization**

Look for these log messages:
```
✅ All 5 intent classification agents initialized
🎯 ManufacturingIntentSwarm initialized with 5 specialized agents
```

### **Step 2: Verify Cross-Region Execution**

Look for these log messages:
```
🚀 Executing 5 agents using 'Cross-Region Parallel' strategy
✅ Agent ops_research_agent completed (5/5)
✅ Agent production_systems_agent completed (2/5)
✅ Agent supply_chain_agent completed (1/5)
✅ Agent quality_agent completed (4/5)
✅ Agent sustainability_agent completed (3/5)
```

### **Step 3: Verify Consensus Mechanism**

Look for these log messages:
```
🔄 Executing consensus with 5 agents using confidence_aggregation
✅ Consensus completed: confidence=0.800, agreement=1.000
```

### **Step 4: Verify Real AWS Integration**

Look for these log messages:
```
🚀 Executing inference for intent_classifier in us-east-1
✅ Inference completed for intent_classifier in us-east-1
```

---

## 📈 **Expected Performance Metrics**

### **Intent Classification**
- **Time**: 8-12 seconds
- **Confidence**: 0.7-0.9
- **Agreement**: 0.8-1.0

### **Data Analysis**
- **Time**: 6-10 seconds
- **Data Points**: All provided data processed
- **Quality Score**: 0.8-1.0

### **Model Building**
- **Time**: 8-15 seconds
- **Model Type**: MILP, LP, or IP
- **Complexity**: Medium to High

### **Optimization Solver**
- **Time**: 10-20 seconds
- **Solution**: Optimal or near-optimal
- **Solver Used**: OR-Tools, PuLP, or CVXPY

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Issue 1: Import Errors**
```
ModuleNotFoundError: No module named 'manufacturing_intent_swarm'
```

**Solution**:
```bash
cd domains/manufacturing/mcp_server
python3 ../../../test_customer_scenario_e2e.py
```

#### **Issue 2: AWS Credentials**
```
NoCredentialsError: Unable to locate credentials
```

**Solution**:
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

#### **Issue 3: Timeout Errors**
```
TimeoutError: Request timed out
```

**Solution**: Increase timeout in test script or check AWS region availability.

### **Debug Mode**

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📋 **Test Checklist**

### **Pre-Test Setup**
- [ ] AWS credentials configured
- [ ] Python dependencies installed
- [ ] MCP server directory accessible
- [ ] Test data prepared

### **During Test**
- [ ] Agent swarm initializes successfully
- [ ] Cross-region execution works
- [ ] Consensus mechanism operates
- [ ] Real AWS Bedrock calls made
- [ ] Performance within expected range

### **Post-Test Verification**
- [ ] Results saved to JSON file
- [ ] Performance metrics recorded
- [ ] Customer context preserved
- [ ] No mock responses detected

---

## 🎯 **Success Criteria**

### **✅ Test Passes If**:
1. All 4 workflow steps complete successfully
2. Performance within expected time ranges
3. Real AWS Bedrock calls made (no mocks)
4. Consensus mechanism produces results
5. Customer data properly processed
6. Results saved to file

### **❌ Test Fails If**:
1. Any step times out or errors
2. Mock responses detected
3. Performance significantly below expectations
4. Consensus mechanism fails
5. Customer data not processed correctly

---

## 📞 **Support**

### **Getting Help**
- **Documentation**: Check `docs/` directory
- **Examples**: See `test_customer_scenario_e2e.py`
- **Logs**: Check console output for detailed information

### **Reporting Issues**
Include in your report:
1. Test script used
2. Customer scenario data
3. Error messages
4. Performance metrics
5. AWS region and credentials status

---

**Guide Version**: 1.0  
**Last Updated**: January 10, 2025  
**Compatible With**: DcisionAI MCP Server v4.0.0
