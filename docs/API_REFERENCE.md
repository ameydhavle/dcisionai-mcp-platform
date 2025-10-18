# DcisionAI API Reference

## 🚀 **Overview**

The DcisionAI API provides programmatic access to advanced mathematical optimization capabilities through a RESTful interface. The API is hosted on AWS Bedrock AgentCore Runtime and provides enterprise-grade performance and scalability.

---

## 🔗 **Base URLs**

### **Production Environment**
- **SaaS Platform**: `https://platform.dcisionai.com`
- **API Gateway**: `https://platform.dcisionai.com/api`
- **AgentCore Runtime**: `https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/mcp_server-IkOAiK3aOz/invocations`

### **Development Environment**
- **Local Backend**: `http://localhost:5001`
- **Local API**: `http://localhost:5001/api`

---

## 🔐 **Authentication**

### **AWS IAM Authentication**
All API requests require AWS IAM credentials with appropriate permissions:

```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### **Required IAM Permissions**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:InvokeAgentRuntime"
            ],
            "Resource": "arn:aws:bedrock-agentcore:us-east-1:*:runtime/mcp_server-*"
        }
    ]
}
```

---

## 📋 **API Endpoints**

### **Health Check**

#### `GET /api/health`
Check the health status of the DcisionAI platform.

**Response:**
```json
{
    "status": "healthy",
    "mcp_server_url": "https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/mcp_server-IkOAiK3aOz/invocations",
    "health_status": "healthy",
    "features": [
        "Claude 3 Haiku model building",
        "OR-Tools optimization with 8+ solvers",
        "Business explainability",
        "21 industry workflows",
        "AWS AgentCore hosting"
    ],
    "timestamp": "2025-01-17T20:58:42.123Z",
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

---

## 🧠 **Core Optimization Workflow**

### **1. Intent Classification**

#### `POST /api/mcp/classify-intent`
Classify the optimization problem and identify the domain, type, and complexity.

**Request:**
```json
{
    "problem_description": "I need to optimize my production schedule. I have 2 production lines that can produce 100 and 90 units per hour respectively, at costs of $50 and $60 per hour. I need to produce at least 500 units. Minimize total cost.",
    "context": "manufacturing"
}
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "optimization_type": "linear_programming",
        "problem_domain": "production_planning",
        "objective": "minimize_cost",
        "complexity": "medium",
        "decision_variables": [
            "production_time",
            "resource_allocation"
        ],
        "constraints": [
            "capacity",
            "demand",
            "budget"
        ],
        "reasoning": "Analyzed problem description to identify key decisions and constraints"
    },
    "message": "Intent classified using hosted MCP server on AWS AgentCore"
}
```

### **2. Data Analysis**

#### `POST /api/mcp/analyze-data`
Analyze data readiness and quality for optimization.

**Request:**
```json
{
    "problem_description": "I need to optimize my production schedule...",
    "intent_data": {
        "optimization_type": "linear_programming",
        "problem_domain": "production_planning",
        "objective": "minimize_cost",
        "complexity": "medium"
    }
}
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "data_quality": "high",
        "missing_data": [],
        "data_sources": [
            "production_capacity",
            "cost_parameters",
            "demand_requirements"
        ],
        "recommendations": [
            "Data is sufficient for optimization",
            "Consider adding demand uncertainty parameters"
        ],
        "complexity_assessment": "medium"
    },
    "message": "Data analyzed using enhanced MCP server"
}
```

### **3. Solver Selection**

#### `POST /api/mcp/select-solver`
Intelligently select the optimal solver for the problem.

**Request:**
```json
{
    "optimization_type": "linear_programming",
    "problem_size": {
        "num_variables": 5,
        "num_constraints": 8
    },
    "performance_requirement": "balanced"
}
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "selected_solver": "OR-Tools PDLP",
        "reasoning": "Linear programming problem with medium size, PDLP provides good balance of speed and accuracy",
        "alternative_solvers": [
            "OR-Tools Simplex",
            "Gurobi LP"
        ],
        "performance_estimate": {
            "solve_time": "< 5 seconds",
            "memory_usage": "low",
            "accuracy": "high"
        }
    },
    "message": "Solver selected using AI reasoning"
}
```

### **4. Model Building**

#### `POST /api/mcp/build-model`
Build mathematical optimization model using AI reasoning.

**Request:**
```json
{
    "problem_description": "I need to optimize my production schedule...",
    "intent_data": {
        "optimization_type": "linear_programming",
        "problem_domain": "production_planning",
        "objective": "minimize_cost"
    },
    "data_analysis": {
        "data_quality": "high",
        "complexity_assessment": "medium"
    }
}
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "variables": [
            {
                "name": "x1",
                "description": "Operating time of production line 1 (hours)",
                "type": "continuous",
                "bounds": [0, 24]
            },
            {
                "name": "x2", 
                "description": "Operating time of production line 2 (hours)",
                "type": "continuous",
                "bounds": [0, 24]
            }
        ],
        "objective": {
            "type": "minimize",
            "expression": "50*x1 + 60*x2",
            "description": "Minimize total production cost"
        },
        "constraints": [
            {
                "name": "demand_constraint",
                "expression": "100*x1 + 90*x2 >= 500",
                "description": "Meet minimum production requirement of 500 units"
            }
        ],
        "reasoning_steps": {
            "step1_decision_analysis": "Identified two key decisions: how long to run each production line",
            "step2_constraint_analysis": "Main constraint is meeting demand requirement",
            "step3_objective_analysis": "Objective is to minimize total cost",
            "step4_variable_design": "Variables represent operating time for each line",
            "step5_constraint_formulation": "Demand constraint ensures minimum production",
            "step6_objective_formulation": "Cost objective sums hourly costs for each line",
            "step7_validation": "All variables used in constraints and objective"
        }
    },
    "message": "Model built using Claude 3 Haiku"
}
```

### **5. Optimization Solving**

#### `POST /api/mcp/solve-optimization`
Solve the optimization problem and generate results.

**Request:**
```json
{
    "problem_description": "I need to optimize my production schedule...",
    "intent_data": {
        "optimization_type": "linear_programming",
        "problem_domain": "production_planning"
    },
    "data_analysis": {
        "data_quality": "high"
    },
    "model_building": {
        "variables": [...],
        "objective": {...},
        "constraints": [...]
    }
}
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "solver_status": "optimal",
        "objective_value": 250.0,
        "optimal_values": {
            "x1": 5.0,
            "x2": 0.0
        },
        "solve_time": 0.15,
        "solver_used": "OR-Tools PDLP",
        "business_impact": {
            "total_cost": 250.0,
            "cost_savings": 0.0,
            "capacity_utilization": "83.3%",
            "recommendations": [
                "Use only production line 1 for 5 hours",
                "Production line 2 not needed for this demand level"
            ]
        },
        "validation": {
            "constraint_satisfaction": "all_satisfied",
            "objective_calculation": "verified",
            "business_logic": "validated"
        }
    },
    "message": "Optimization completed successfully"
}
```

### **6. Result Explanation**

#### `POST /api/mcp/explain-optimization`
Provide business-facing explanation of optimization results.

**Request:**
```json
{
    "problem_description": "I need to optimize my production schedule...",
    "optimization_solution": {
        "solver_status": "optimal",
        "objective_value": 250.0,
        "optimal_values": {
            "x1": 5.0,
            "x2": 0.0
        }
    }
}
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "executive_summary": "Optimal solution found: Use production line 1 for 5 hours to meet demand at minimum cost of $250.",
        "detailed_explanation": {
            "solution_interpretation": "The optimal strategy is to operate production line 1 for 5 hours, producing 500 units at $50/hour, while keeping production line 2 idle.",
            "cost_breakdown": {
                "production_line_1": "$250 (5 hours × $50/hour)",
                "production_line_2": "$0 (0 hours)",
                "total_cost": "$250"
            },
            "constraint_analysis": "Demand constraint satisfied: 100 units/hour × 5 hours = 500 units",
            "alternative_analysis": "Using production line 2 would increase cost: 500 units ÷ 90 units/hour × $60/hour = $333.33"
        },
        "business_recommendations": [
            "Implement the 5-hour production schedule on line 1",
            "Consider using line 2 for future demand increases",
            "Monitor demand patterns for capacity planning"
        ],
        "risk_assessment": {
            "solution_robustness": "high",
            "sensitivity_to_changes": "low",
            "implementation_risks": "minimal"
        }
    },
    "message": "Optimization results explained in business terms"
}
```

### **7. Scenario Simulation**

#### `POST /api/mcp/simulate-scenarios`
Run simulation analysis for strategic planning and risk assessment.

**Request:**
```json
{
    "problem_description": "I need to optimize my production schedule...",
    "optimization_solution": {
        "solver_status": "optimal",
        "objective_value": 250.0,
        "optimal_values": {
            "x1": 5.0,
            "x2": 0.0
        }
    },
    "simulation_type": "monte_carlo",
    "num_trials": 10000
}
```

**Response:**
```json
{
    "status": "success",
    "result": {
        "simulation_type": "monte_carlo",
        "num_trials": 10000,
        "uncertainty_sources": [
            {
                "name": "demand_variability",
                "distribution": "normal",
                "mean": 500,
                "std_dev": 50
            },
            {
                "name": "cost_volatility",
                "distribution": "uniform",
                "min": 45,
                "max": 55
            }
        ],
        "results": {
            "expected_cost": 252.3,
            "cost_std_dev": 12.7,
            "percentile_5": 235.1,
            "percentile_95": 271.8,
            "probability_of_feasibility": 0.98
        },
        "risk_analysis": {
            "value_at_risk_95": 271.8,
            "conditional_var": 275.2,
            "risk_drivers": [
                "Demand variability accounts for 60% of cost variance",
                "Cost volatility contributes 40% of uncertainty"
            ]
        },
        "recommendations": [
            "Solution is robust to demand variations",
            "Consider hedging against cost volatility",
            "Monitor demand patterns for early warning"
        ]
    },
    "message": "Simulation analysis completed"
}
```

---

## 🏭 **Industry Workflows**

### **Workflow Templates**

#### `POST /api/mcp/get-workflow-templates`
Get available industry-specific workflow templates.

**Response:**
```json
{
    "status": "success",
    "result": {
        "workflows": [
            {
                "id": "manufacturing_production_planning",
                "name": "Manufacturing Production Planning",
                "description": "Optimize production schedules, capacity, and resource allocation",
                "industry": "manufacturing",
                "complexity": "medium"
            },
            {
                "id": "financial_portfolio_optimization",
                "name": "Financial Portfolio Optimization", 
                "description": "Optimize investment portfolios with risk constraints",
                "industry": "financial",
                "complexity": "high"
            }
        ]
    }
}
```

#### `POST /api/mcp/execute-workflow`
Execute a complete industry workflow.

**Request:**
```json
{
    "industry": "manufacturing",
    "workflow_id": "manufacturing_production_planning",
    "user_input": {
        "production_lines": 2,
        "demand": 500,
        "cost_per_hour": [50, 60],
        "capacity_per_hour": [100, 90]
    }
}
```

---

## ⚠️ **Error Handling**

### **Common Error Responses**

#### **400 Bad Request**
```json
{
    "error": "Bad Request",
    "message": "Invalid request parameters",
    "details": "Problem description is required"
}
```

#### **401 Unauthorized**
```json
{
    "error": "Unauthorized",
    "message": "Invalid AWS credentials or insufficient permissions"
}
```

#### **500 Internal Server Error**
```json
{
    "error": "Internal Server Error",
    "message": "Optimization failed",
    "details": "Solver encountered numerical issues"
}
```

### **Error Codes**
- `INVALID_INPUT`: Request parameters are invalid
- `AUTHENTICATION_FAILED`: AWS credentials are invalid
- `OPTIMIZATION_FAILED`: Solver could not find solution
- `MODEL_BUILDING_FAILED`: AI could not build valid model
- `RATE_LIMIT_EXCEEDED`: Too many requests

---

## 📊 **Rate Limits**

### **Current Limits**
- **Requests per minute**: 100
- **Concurrent requests**: 10
- **Daily quota**: 10,000 requests

### **Rate Limit Headers**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642454400
```

---

## 🔧 **SDK Examples**

### **Python**
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
        "problem_description": "Optimize my production schedule..."
    }
)

result = response.json()
print(f"Problem type: {result['result']['optimization_type']}")
```

### **JavaScript**
```javascript
const baseUrl = 'https://platform.dcisionai.com/api';

async function classifyIntent(problemDescription) {
    const response = await fetch(`${baseUrl}/mcp/classify-intent`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            problem_description: problemDescription
        })
    });
    
    const result = await response.json();
    return result.result;
}
```

### **cURL**
```bash
curl -X POST https://platform.dcisionai.com/api/mcp/classify-intent \
  -H "Content-Type: application/json" \
  -d '{
    "problem_description": "I need to optimize my production schedule..."
  }'
```

---

## 📈 **Performance Metrics**

### **Response Times**
- **Intent Classification**: < 2 seconds
- **Data Analysis**: < 3 seconds  
- **Model Building**: < 10 seconds
- **Optimization Solving**: < 30 seconds
- **Result Explanation**: < 5 seconds

### **Availability**
- **Uptime**: 99.9%
- **SLA**: 99.5% availability guarantee
- **Maintenance Windows**: Sundays 2-4 AM UTC

---

## 🔄 **Versioning**

### **Current Version**: v1.7.3
- **API Version**: `/api/v1/`
- **Backward Compatibility**: Maintained for 12 months
- **Deprecation Notice**: 6 months advance notice

### **Changelog**
- **v1.7.3**: AgentCore Runtime integration, enhanced simulation
- **v1.7.2**: Pattern-breaking prompts, improved explainability
- **v1.7.1**: Multi-solver support, business validation
- **v1.7.0**: Initial release with core optimization tools

---

*For additional support and examples, visit our [GitHub repository](https://github.com/dcisionai/dcisionai-mcp-platform) or contact our support team.*