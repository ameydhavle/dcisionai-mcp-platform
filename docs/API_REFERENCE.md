# DcisionAI API Reference

## 🚀 **Complete API Documentation**

This document provides comprehensive API reference for the DcisionAI platform, including MCP server tools, REST API endpoints, and integration examples.

## 🎯 **MCP Server Tools**

The DcisionAI MCP server provides 9 core tools for mathematical optimization. Each tool is designed to work independently or as part of a complete optimization workflow.

### **Tool 1: classify_intent**

**Purpose**: Classify user intent for optimization requests using Claude 3 Haiku

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "problem_description": {
      "type": "string",
      "description": "The user's optimization request or problem description"
    },
    "context": {
      "type": "string",
      "description": "Optional context about the business domain"
    }
  },
  "required": ["problem_description"]
}
```

**Example Request**:
```json
{
  "problem_description": "Optimize my investment portfolio for maximum returns with moderate risk",
  "context": "Financial services, $2M portfolio"
}
```

**Example Response**:
```json
{
  "status": "success",
  "step": "intent_classification",
  "timestamp": "2025-10-17T07:34:47.400Z",
  "result": {
    "intent": "portfolio_optimization",
    "industry": "finance",
    "complexity": "medium",
    "confidence": 0.8,
    "entities": ["investment_portfolio", "returns", "risk"],
    "optimization_type": "linear_programming",
    "time_horizon": "medium_term",
    "solver_requirements": {
      "primary": ["PDLP", "GLOP"],
      "fallback": ["GLOP"],
      "capabilities": ["linear_constraints", "continuous_variables"]
    }
  },
  "message": "Intent classified using Claude 3 Haiku with optimization type detection"
}
```

### **Tool 2: analyze_data**

**Purpose**: Analyze and preprocess data for optimization

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "problem_description": {
      "type": "string",
      "description": "Description of the optimization problem"
    },
    "intent_data": {
      "type": "object",
      "description": "Intent classification results from classify_intent"
    }
  },
  "required": ["problem_description"]
}
```

**Example Response**:
```json
{
  "status": "success",
  "step": "data_analysis",
  "timestamp": "2025-10-17T07:34:47.400Z",
  "result": {
    "readiness_score": 0.92,
    "entities": 15,
    "data_quality": "high",
    "missing_data": [],
    "data_sources": ["ERP_system", "production_logs", "demand_forecast", "capacity_planning"],
    "variables_identified": ["x1", "x2", "x3", "x4", "x5", "y1", "y2", "y3", "z1", "z2", "z3", "z4"],
    "constraints_identified": ["capacity", "demand", "labor", "material", "quality"],
    "recommendations": [
      "Ensure all production capacity data is up-to-date",
      "Validate demand forecast accuracy",
      "Include setup costs in optimization model"
    ]
  },
  "message": "Data analysis completed successfully"
}
```

### **Tool 3: build_model**

**Purpose**: Build mathematical optimization model using Claude 3 Haiku

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "problem_description": {
      "type": "string",
      "description": "Detailed problem description"
    },
    "intent_data": {
      "type": "object",
      "description": "Intent classification results"
    },
    "data_analysis": {
      "type": "object",
      "description": "Results from data analysis step"
    }
  },
  "required": ["problem_description"]
}
```

**Example Response**:
```json
{
  "status": "success",
  "step": "model_building",
  "timestamp": "2025-10-17T07:34:47.400Z",
  "result": {
    "raw_response": "{\n  \"model_type\": \"linear_programming\",\n  \"variables\": [\n    {\n      \"name\": \"w1\",\n      \"type\": \"continuous\",\n      \"bounds\": \"0 to 1\",\n      \"description\": \"Allocation weight for asset 1\"\n    }\n  ],\n  \"objective\": {\n    \"type\": \"maximize\",\n    \"expression\": \"w1 * r1 + w2 * r2 + w3 * r3\",\n    \"description\": \"Maximize portfolio expected return\"\n  },\n  \"constraints\": [\n    {\n      \"expression\": \"w1 + w2 + w3 = 1\",\n      \"description\": \"Sum of allocation weights must be 1\"\n    }\n  ]\n}"
  },
  "message": "Model built using Claude 3 Haiku"
}
```

### **Tool 4: solve_optimization**

**Purpose**: Solve the optimization problem and generate results

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "problem_description": {
      "type": "string",
      "description": "Problem description"
    },
    "intent_data": {
      "type": "object",
      "description": "Intent classification results"
    },
    "data_analysis": {
      "type": "object",
      "description": "Data analysis results"
    },
    "model_building": {
      "type": "object",
      "description": "Model building results"
    }
  },
  "required": ["problem_description"]
}
```

**Example Response**:
```json
{
  "status": "success",
  "step": "optimization_solution",
  "timestamp": "2025-10-17T07:34:47.400Z",
  "result": {
    "status": "optimal",
    "objective_value": 1.22,
    "optimal_values": {
      "x1": 0.10,
      "x2": 0.20,
      "x3": 0.10,
      "x4": 0.60
    },
    "solve_time": 0.0034,
    "solution_quality": "optimal",
    "constraints_satisfied": true,
    "business_impact": {
      "total_profit": 1.22,
      "profit_increase": "12.2%",
      "cost_savings": 244000,
      "capacity_utilization": "85.0%"
    },
    "recommendations": [
      "Focus on x4 with optimal value 0.60",
      "Monitor key performance indicators regularly",
      "Consider capacity expansion for high-demand products"
    ],
    "sensitivity_analysis": {
      "demand_sensitivity": "Solution is moderately sensitive to demand changes",
      "cost_sensitivity": "Solution is robust to cost variations up to 10%",
      "capacity_sensitivity": "Solution can handle capacity changes within 15%"
    }
  },
  "message": "Optimization solved successfully using OR-Tools"
}
```

### **Tool 5: select_solver**

**Purpose**: Select the best available solver for optimization problems

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "optimization_type": {
      "type": "string",
      "description": "Type of optimization problem (linear_programming, quadratic_programming, mixed_integer_linear_programming, etc.)"
    },
    "problem_size": {
      "type": "object",
      "description": "Problem size information (num_variables, num_constraints, etc.)",
      "default": {}
    },
    "performance_requirement": {
      "type": "string",
      "description": "Performance requirement: speed, accuracy, or balanced",
      "default": "balanced"
    }
  },
  "required": ["optimization_type"]
}
```

**Example Response**:
```json
{
  "status": "success",
  "step": "solver_selection",
  "timestamp": "2025-10-17T07:34:47.400Z",
  "result": {
    "selected_solver": "PDLP",
    "performance_rating": "9/10",
    "reasoning": "PDLP selected for large-scale linear programming problems",
    "available_solvers": ["GLOP", "PDLP", "CBC", "SCIP", "HIGHS", "OSQP", "SCS", "CVXPY"],
    "solver_capabilities": {
      "linear_constraints": true,
      "continuous_variables": true,
      "large_scale": true,
      "performance": "high"
    }
  },
  "message": "Solver selected based on problem characteristics"
}
```

### **Tool 6: simulate_scenarios**

**Purpose**: Run simulation analysis on optimization scenarios using Monte Carlo and OSS simulation engines

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "problem_description": {
      "type": "string",
      "description": "Original problem description"
    },
    "optimization_solution": {
      "type": "object",
      "description": "Results from optimization solving"
    },
    "scenario_parameters": {
      "type": "object",
      "description": "Parameters for scenario analysis"
    },
    "simulation_type": {
      "type": "string",
      "description": "Type of simulation (monte_carlo, sensitivity, what_if)",
      "default": "monte_carlo"
    },
    "num_trials": {
      "type": "integer",
      "description": "Number of simulation trials",
      "default": 10000
    }
  },
  "required": ["problem_description"]
}
```

**Example Request**:
```json
{
  "problem_description": "Quantitative trading execution optimization",
  "optimization_solution": {
    "status": "optimal",
    "objective_value": 5000,
    "optimal_values": {"x1": 100000, "x2": 200000}
  },
  "simulation_type": "monte_carlo",
  "num_trials": 10000
}
```

**Example Response**:
```json
{
  "status": "success",
  "step": "simulation_analysis",
  "timestamp": "2025-10-17T12:43:00.442019",
  "result": {
    "simulation_summary": {
      "analysis_type": "risk_assessment",
      "simulation_type": "monte_carlo",
      "num_trials": 10000,
      "status": "completed",
      "execution_time": "2.3 seconds"
    },
    "scenario_analysis": {
      "scenarios_tested": [
        {
          "scenario_name": "Scenario A: Relax Volume Limit",
          "parameter_changes": {"volume_limit": "5% to 7%"},
          "feasibility": "feasible",
          "expected_outcome": 5250,
          "risk_metrics": {
            "mean": 5250,
            "std_dev": 420,
            "percentile_5": 4600,
            "percentile_95": 6100,
            "var_95": 4600
          }
        }
      ]
    },
    "risk_analysis": {
      "uncertainty_factors": [
        {
          "factor": "Market Impact",
          "contribution_to_variance": 0.45,
          "sensitivity": "High",
          "recommendation": "Monitor volume carefully"
        }
      ],
      "stress_testing": {
        "worst_case_scenario": {
          "description": "High volatility + market impact",
          "probability": 0.05,
          "outcome": 6100,
          "mitigation": "Implement circuit breakers"
        }
      }
    },
    "recommendations": {
      "primary_recommendation": {
        "scenario": "Scenario B: Extend Deadline",
        "expected_benefit": 450,
        "risk_reduction": 0.23,
        "confidence": 0.92
      },
      "implementation_guidance": [
        "Extend trading deadline to 2:00pm",
        "Maintain 5% volume limit for market stability"
      ]
    },
    "mathematical_simulation": {
      "simulation_type": "monte_carlo",
      "num_trials": 10000,
      "risk_metrics": {
        "mean": 1006.44,
        "std_dev": 153.12,
        "percentile_5": 749.71,
        "percentile_95": 1273.33,
        "var_95": 749.71
      },
      "convergence": true
    }
  },
  "message": "Simulation analysis completed using monte_carlo with 10000 trials",
  "simulation_engine": "hybrid"
}
```

**Supported Simulation Types**:
- **monte_carlo**: Risk analysis using NumPy/SciPy
- **discrete_event**: Process simulation using SimPy
- **agent_based**: Complex systems using Mesa
- **system_dynamics**: Causal modeling using PySD
- **stochastic_optimization**: Parameter sensitivity using SALib/PyMC

### **Tool 7: explain_optimization**

**Purpose**: Provide business-facing explainability for optimization results

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "problem_description": {
      "type": "string",
      "description": "Original problem description"
    },
    "intent_data": {
      "type": "object",
      "description": "Results from intent classification",
      "default": {}
      },
      "data_analysis": {
      "type": "object",
      "description": "Results from data analysis",
      "default": {}
      },
      "model_building": {
      "type": "object",
      "description": "Results from model building",
      "default": {}
      },
      "optimization_solution": {
      "type": "object",
      "description": "Results from optimization solving",
      "default": {}
    }
  },
  "required": ["problem_description"]
}
```

**Example Response**:
```json
{
  "status": "success",
  "step": "explainability",
  "timestamp": "2025-10-17T07:34:47.400Z",
  "result": {
    "executive_summary": {
      "problem_statement": "The business is looking to optimize its investment portfolio to maximize returns while minimizing risk.",
      "solution_approach": "We used a linear programming optimization model to analyze the company's investment data and identify the most efficient portfolio allocation.",
      "key_findings": [
        "The current portfolio is not well-diversified, with a heavy concentration in a few high-risk investments.",
        "Reallocating a portion of the funds to lower-risk, more stable investments can significantly improve the overall risk-return profile of the portfolio."
      ],
      "business_impact": "Implementing the recommended portfolio optimization will help the company achieve its financial goals more effectively. It is expected to increase returns by 12.2% while reducing the overall portfolio risk."
    },
    "analysis_breakdown": {
      "data_assessment": {
        "data_quality": "The available investment data is generally of good quality, with some minor gaps in historical performance information for certain asset classes.",
        "missing_data": ["Detailed historical returns for emerging market investments"],
        "assumptions_made": ["Future market conditions will be similar to historical trends"]
      },
      "model_design": {
        "approach_justification": "Linear programming is a well-established optimization technique that is particularly well-suited for portfolio optimization problems.",
        "trade_offs": ["Increasing exposure to higher-risk, higher-return investments can improve overall portfolio performance but also raises the level of risk."]
      }
    },
    "implementation_guidance": {
      "next_steps": [
        "Communicate the optimization findings and recommendations to the investment committee for review and approval.",
        "Develop a detailed implementation plan to gradually transition the current portfolio to the recommended allocation."
      ],
      "monitoring_metrics": ["Portfolio returns (absolute and risk-adjusted)", "Portfolio risk (e.g., standard deviation, Value-at-Risk)"],
      "risk_considerations": ["Potential market volatility and its impact on the portfolio's performance"]
    },
    "technical_details": {
      "optimization_type": "linear_programming",
      "solver_used": "PDLP",
      "computational_efficiency": "The optimization model was able to find the optimal solution in a matter of seconds, demonstrating its computational efficiency.",
      "scalability": "The linear programming approach used in this analysis is highly scalable and can handle large-scale portfolio optimization problems with a large number of assets and constraints."
    }
  },
  "message": "Business explainability generated successfully"
}
```

### **Tool 8: get_workflow_templates**

**Purpose**: Get available industry workflow templates

**Input Schema**:
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Response**:
```json
{
  "status": "success",
  "workflow_templates": {
    "industries": ["manufacturing", "healthcare", "retail", "marketing", "financial", "logistics", "energy"],
    "workflows": {
      "manufacturing": {
        "production_planning": {
          "name": "Production Planning Optimization",
          "description": "Optimize production schedules, resource allocation, and capacity planning",
          "complexity": "high",
          "estimated_time": "15-30 minutes",
          "workflows": 3
        },
        "inventory_optimization": {
          "name": "Inventory Optimization",
          "description": "Minimize inventory costs while maintaining service levels",
          "complexity": "medium",
          "estimated_time": "10-20 minutes",
          "workflows": 3
        }
      },
      "financial": {
        "portfolio_optimization": {
          "name": "Portfolio Optimization",
          "description": "Optimize investment portfolio allocation and risk management",
          "complexity": "high",
          "estimated_time": "20-40 minutes",
          "workflows": 3
        }
      }
    },
    "total_workflows": 21,
    "total_industries": 7
  },
  "total_workflows": 21,
  "industries": 7
}
```

### **Tool 9: execute_workflow**

**Purpose**: Execute a complete optimization workflow

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "industry": {
      "type": "string",
      "description": "Target industry (manufacturing, healthcare, retail, marketing, financial, logistics, energy)"
    },
    "workflow_id": {
      "type": "string",
      "description": "Specific workflow to execute"
    },
    "user_input": {
      "type": "object",
      "description": "User input parameters"
    }
  },
  "required": ["industry", "workflow_id"]
}
```

**Example Response**:
```json
{
  "status": "success",
  "step": "workflow_execution",
  "timestamp": "2025-10-17T07:34:47.400Z",
  "result": {
    "workflow_id": "portfolio_optimization",
    "industry": "financial",
    "execution_time": 45.2,
    "steps_completed": [
    "intent_classification",
    "data_analysis", 
    "model_building",
      "solver_selection",
      "optimization_solving",
      "explainability"
    ],
    "final_results": {
      "objective_value": 1.22,
      "optimal_allocation": {
        "stocks": 0.10,
        "bonds": 0.20,
        "real_estate": 0.10,
        "commodities": 0.60
      },
      "business_impact": "$244,000 annual return on $2M investment"
    },
    "recommendations": [
      "Implement the recommended allocation gradually over 3 months",
      "Monitor performance monthly and rebalance quarterly",
      "Consider tax implications of rebalancing"
    ]
  },
  "message": "Workflow executed successfully"
}
```

## 🌐 **REST API Endpoints**

The DcisionAI SaaS platform provides REST API endpoints for web integration.

### **Base URL**
```
https://platform.dcisionai.com/api
```

### **Authentication**
All API requests require authentication using JWT tokens:
```http
Authorization: Bearer <your-jwt-token>
```

### **Health Check**

**Endpoint**: `GET /api/mcp/health-check`

**Response**:
```json
{
  "status": "healthy",
  "message": "DcisionAI MCP server (v1.4.3) is running on AWS AgentCore",
  "mcp_server_url": "https://agentcore.dcisionai.com",
  "health_status": "healthy",
  "features": [
    "Claude 3 Haiku model building",
    "OR-Tools optimization with 8+ solvers",
    "Business explainability",
    "21 industry workflows",
    "AWS AgentCore hosting"
  ],
  "timestamp": "2025-10-17T07:34:47.400Z",
  "endpoints": {
    "classify_intent": "/api/mcp/classify-intent",
    "analyze_data": "/api/mcp/analyze-data",
    "build_model": "/api/mcp/build-model",
    "solve_optimization": "/api/mcp/solve-optimization",
    "select_solver": "/api/mcp/select-solver",
    "explain_optimization": "/api/mcp/explain-optimization",
    "execute_workflow": "/api/mcp/execute-workflow"
  }
}
```

### **Intent Classification**

**Endpoint**: `POST /api/mcp/classify-intent`

**Request Body**:
```json
{
  "problem_description": "Optimize my investment portfolio for maximum returns with moderate risk",
  "context": "Financial services, $2M portfolio"
}
```

**Response**: Same as MCP tool response

### **Data Analysis**

**Endpoint**: `POST /api/mcp/analyze-data`

**Request Body**:
```json
{
  "problem_description": "Portfolio optimization problem",
  "intent_data": {
    "intent": "portfolio_optimization",
    "industry": "finance"
  }
}
```

**Response**: Same as MCP tool response

### **Model Building**

**Endpoint**: `POST /api/mcp/build-model`

**Request Body**:
```json
{
  "problem_description": "Portfolio optimization",
  "intent_data": {
    "intent": "portfolio_optimization",
    "industry": "finance"
  },
  "data_analysis": {
    "readiness_score": 0.92,
    "variables_identified": ["x1", "x2", "x3", "x4"]
  }
}
```

**Response**: Same as MCP tool response

### **Optimization Solving**

**Endpoint**: `POST /api/mcp/solve-optimization`

**Request Body**:
```json
{
  "problem_description": "Portfolio optimization",
  "intent_data": {
    "intent": "portfolio_optimization"
  },
  "data_analysis": {
    "readiness_score": 0.92
  },
  "model_building": {
    "model_type": "linear_programming"
  }
}
```

**Response**: Same as MCP tool response

### **Solver Selection**

**Endpoint**: `POST /api/mcp/select-solver`

**Request Body**:
```json
{
  "optimization_type": "linear_programming",
  "problem_size": {
    "num_variables": 4,
    "num_constraints": 6
  },
  "performance_requirement": "balanced"
}
```

**Response**: Same as MCP tool response

### **Explain Optimization**

**Endpoint**: `POST /api/mcp/explain-optimization`

**Request Body**:
```json
{
  "problem_description": "Portfolio optimization",
  "intent_data": {
    "intent": "portfolio_optimization"
  },
  "data_analysis": {
    "readiness_score": 0.92
  },
    "model_building": {
    "model_type": "linear_programming"
    },
    "optimization_solution": {
    "objective_value": 1.22,
    "optimal_values": {
      "x1": 0.10,
      "x2": 0.20,
      "x3": 0.10,
      "x4": 0.60
    }
  }
}
```

**Response**: Same as MCP tool response

### **Execute Workflow**

**Endpoint**: `POST /api/mcp/execute-workflow`

**Request Body**:
```json
{
  "industry": "financial",
  "workflow_id": "portfolio_optimization",
  "user_input": {
    "portfolio_size": 1000000,
    "risk_tolerance": "moderate"
  }
}
```

**Response**: Same as MCP tool response

## 🔧 **Integration Examples**

### **Python SDK**

```python
from dcisionai_mcp_server.tools import DcisionAITools
import asyncio

async def optimize_portfolio():
    tools = DcisionAITools()
    
    # Step 1: Classify intent
    intent_result = await tools.classify_intent(
        "Optimize my investment portfolio for maximum returns with moderate risk"
    )
    
    # Step 2: Analyze data
    data_result = await tools.analyze_data(
        "Portfolio optimization", 
        intent_result['result']
    )
    
    # Step 3: Build model
    model_result = await tools.build_model(
        "Portfolio optimization",
        intent_result['result'],
        data_result['result']
    )
    
    # Step 4: Solve optimization
    solve_result = await tools.solve_optimization(
        "Portfolio optimization",
        intent_result['result'],
        data_result['result'],
        model_result['result']
    )
    
    # Step 5: Get explanation
    explain_result = await tools.explain_optimization(
        "Portfolio optimization",
        intent_result['result'],
        data_result['result'],
        model_result['result'],
        solve_result['result']
    )
    
    return {
        'intent': intent_result,
        'data': data_result,
        'model': model_result,
        'solution': solve_result,
        'explanation': explain_result
    }

# Run optimization
result = asyncio.run(optimize_portfolio())
print(f"Optimal allocation: {result['solution']['result']['optimal_values']}")
```

### **JavaScript/Node.js**

```javascript
const axios = require('axios');

class DcisionAIClient {
    constructor(baseURL = 'https://platform.dcisionai.com/api', token) {
        this.baseURL = baseURL;
        this.token = token;
    }
    
    async classifyIntent(problemDescription, context = null) {
        const response = await axios.post(`${this.baseURL}/mcp/classify-intent`, {
            problem_description: problemDescription,
            context: context
        }, {
            headers: { Authorization: `Bearer ${this.token}` }
        });
        return response.data;
    }
    
    async analyzeData(problemDescription, intentData) {
        const response = await axios.post(`${this.baseURL}/mcp/analyze-data`, {
            problem_description: problemDescription,
            intent_data: intentData
        }, {
            headers: { Authorization: `Bearer ${this.token}` }
        });
        return response.data;
    }
    
    async buildModel(problemDescription, intentData, dataAnalysis) {
        const response = await axios.post(`${this.baseURL}/mcp/build-model`, {
            problem_description: problemDescription,
            intent_data: intentData,
            data_analysis: dataAnalysis
        }, {
            headers: { Authorization: `Bearer ${this.token}` }
        });
        return response.data;
    }
    
    async solveOptimization(problemDescription, intentData, dataAnalysis, modelBuilding) {
        const response = await axios.post(`${this.baseURL}/mcp/solve-optimization`, {
            problem_description: problemDescription,
            intent_data: intentData,
            data_analysis: dataAnalysis,
            model_building: modelBuilding
        }, {
            headers: { Authorization: `Bearer ${this.token}` }
        });
        return response.data;
    }
    
    async explainOptimization(problemDescription, intentData, dataAnalysis, modelBuilding, optimizationSolution) {
        const response = await axios.post(`${this.baseURL}/mcp/explain-optimization`, {
            problem_description: problemDescription,
            intent_data: intentData,
            data_analysis: dataAnalysis,
            model_building: modelBuilding,
            optimization_solution: optimizationSolution
        }, {
            headers: { Authorization: `Bearer ${this.token}` }
        });
        return response.data;
    }
    
    async executeWorkflow(industry, workflowId, userInput) {
        const response = await axios.post(`${this.baseURL}/mcp/execute-workflow`, {
            industry: industry,
            workflow_id: workflowId,
            user_input: userInput
        }, {
            headers: { Authorization: `Bearer ${this.token}` }
        });
        return response.data;
    }
}

// Usage example
async function optimizePortfolio() {
    const client = new DcisionAIClient('https://platform.dcisionai.com/api', 'your-jwt-token');
    
    const intent = await client.classifyIntent(
        'Optimize my investment portfolio for maximum returns with moderate risk'
    );
    
    const data = await client.analyzeData('Portfolio optimization', intent.result);
    const model = await client.buildModel('Portfolio optimization', intent.result, data.result);
    const solution = await client.solveOptimization('Portfolio optimization', intent.result, data.result, model.result);
    const explanation = await client.explainOptimization('Portfolio optimization', intent.result, data.result, model.result, solution.result);
    
    return { intent, data, model, solution, explanation };
}

optimizePortfolio().then(result => {
    console.log('Optimal allocation:', result.solution.result.optimal_values);
});
```

### **cURL Examples**

```bash
# Health check
curl -X GET "https://platform.dcisionai.com/api/mcp/health-check" \
  -H "Authorization: Bearer your-jwt-token"

# Classify intent
curl -X POST "https://platform.dcisionai.com/api/mcp/classify-intent" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_description": "Optimize my investment portfolio for maximum returns with moderate risk",
    "context": "Financial services, $2M portfolio"
  }'

# Execute workflow
curl -X POST "https://platform.dcisionai.com/api/mcp/execute-workflow" \
  -H "Authorization: Bearer your-jwt-token" \
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

## 📊 **Error Handling**

### **Common Error Responses**

```json
{
  "status": "error",
  "step": "optimization_solution",
  "timestamp": "2025-10-17T07:34:47.400Z",
  "error": "No valid model variables found",
  "message": "Model building step required before solving"
}
```

### **HTTP Status Codes**

- **200 OK**: Request successful
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### **Rate Limiting**

- **Free Tier**: 100 requests per hour
- **Pro Tier**: 1000 requests per hour
- **Enterprise**: Custom limits

## 🔒 **Security**

### **Authentication**
- JWT-based authentication
- Token expiration: 24 hours
- Refresh token support

### **Data Protection**
- End-to-end encryption
- Data anonymization
- Secure transmission (HTTPS)

### **API Keys**
- Generate API keys in dashboard
- Key rotation support
- Usage monitoring

---

**DcisionAI API Reference**: *Complete Integration Guide*