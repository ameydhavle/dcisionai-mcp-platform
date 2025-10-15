# DcisionAI Platform - API Reference

## **Base URLs**

### **Primary API Gateway**
```
https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod
```

### **AgentCore Gateway (Future)**
```
https://dcisionai-optimization-gateway.execute-api.us-east-1.amazonaws.com/prod
```

### **Async Optimization API**
```
https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod/async
```

## **Authentication**

### **Current System**
- **Public Access**: No authentication required for optimization endpoints
- **Rate Limiting**: Built-in AWS API Gateway throttling
- **Usage Tracking**: CloudWatch monitoring and logging

### **AgentCore Gateway (Future)**
- **JWT Authentication**: Amazon Cognito-based authentication
- **OAuth 2.0**: Standard OAuth flow for enterprise integration
- **API Keys**: Optional API key authentication for programmatic access

## **Available Endpoints**

### **Async Optimization Endpoints**

#### **1. Start Async Optimization**
**POST** `/async-optimization`

Start an asynchronous optimization process for long-running workflows.

**Request Body:**
```json
{
  "optimization_id": "opt_1704067200_abc123",
  "workflow_data": {
    "optimization_id": "opt_1704067200_abc123",
    "workflow_type": "production_planning",
    "problem_description": "Optimize production for 5 products across 3 production lines...",
    "custom_parameters": {},
    "industry": "manufacturing",
    "title": "Advanced Production Planning"
  }
}
```

**Response:**
```json
{
  "statusCode": 200,
  "body": {
    "status": "success",
    "optimization_id": "opt_1704067200_abc123",
    "message": "Optimization started successfully",
    "estimated_completion_time": "5-10 minutes"
  }
}
```

#### **2. Check Optimization Status**
**GET** `/optimization-status/{optimization_id}`

Check the current status of an async optimization.

**Response:**
```json
{
  "optimization_id": "opt_1704067200_abc123",
  "status": "running",
  "message": "Step 3/4: Model Building",
  "progress": 75,
  "started_at": "2025-10-14T19:13:25.507123",
  "updated_at": "2025-10-14T19:15:30.123456"
}
```

**Status Values:**
- `started`: Optimization has been initiated
- `running`: Optimization is in progress
- `completed`: Optimization completed successfully
- `failed`: Optimization failed with error
- `timeout`: Optimization exceeded maximum time limit

#### **3. Get Optimization Results**
**GET** `/optimization-results/{optimization_id}`

Retrieve the complete results of a completed optimization.

**Response:**
```json
{
  "optimization_id": "opt_1704067200_abc123",
  "status": "completed",
  "result": {
    "status": "success",
    "timestamp": "2025-10-14T19:18:45.123456",
    "workflow": {
      "workflow_type": "production_planning",
      "industry": "manufacturing",
      "title": "Advanced Production Planning"
    },
    "optimization_pipeline": {
      "intent_classification": {
        "result": {
          "intent": "production_optimization",
          "confidence": 0.95,
          "entities": ["products", "production_lines", "capacity"]
        }
      },
      "data_analysis": {
        "result": {
          "readiness_score": 0.92,
          "data_quality": "high",
          "recommendations": ["Consider demand variability", "Include setup costs"]
        }
      },
      "model_building": {
        "result": {
          "model_type": "linear_programming",
          "variables": 15,
          "constraints": 8,
          "objective": "maximize_profit"
        }
      },
      "optimization_solution": {
        "result": {
          "status": "optimal",
          "objective_value": 125000,
          "solve_time": 2.3,
          "solution": {
            "Product_A": 1200,
            "Product_B": 800,
            "Product_C": 600,
            "Product_D": 400,
            "Product_E": 300
          }
        }
      }
    },
    "execution_summary": {
      "total_steps": 4,
      "completed_steps": 4,
      "success": true,
      "workflow_type": "async_optimization",
      "real_optimization": true
    }
  }
}
```

### **🏭 Workflow Endpoints**

#### **4. List All Industries**
**GET** `/workflows`

Get a list of all available industries and their workflow counts.

**Response:**
```json
{
  "status": "success",
  "industries": [
    "manufacturing",
    "marketing", 
    "healthcare",
    "retail",
    "financial",
    "logistics",
    "energy"
  ],
  "summary": {
    "total_industries": 7,
    "total_workflows": 21,
    "workflows_by_industry": {
      "manufacturing": 3,
      "marketing": 3,
      "healthcare": 3,
      "retail": 3,
      "financial": 3,
      "logistics": 3,
      "energy": 3
    }
  }
}
```

#### **5. Get Industry Workflows**
**GET** `/workflows/{industry}`

Get all workflows for a specific industry.

**Response:**
```json
{
  "status": "success",
  "industry": "manufacturing",
  "workflows": [
    {
      "id": "production_planning",
      "title": "Advanced Production Planning",
      "description": "Optimize multi-product production with capacity, labor, and material constraints",
      "category": "production_planning",
      "difficulty": "advanced",
      "estimated_time": "4-5 minutes"
    },
    {
      "id": "supply_chain_optimization",
      "title": "Supply Chain Optimization",
      "description": "Optimize supply chain network design and inventory management",
      "category": "supply_chain",
      "difficulty": "intermediate",
      "estimated_time": "3-4 minutes"
    },
    {
      "id": "quality_control_optimization",
      "title": "Quality Control Optimization",
      "description": "Optimize quality control processes and defect detection",
      "category": "quality_control",
      "difficulty": "intermediate",
      "estimated_time": "3-4 minutes"
    }
  ]
}
```

#### **6. Execute Workflow (Synchronous)**
**POST** `/workflows/{industry}/{workflow_id}/execute`

Execute a workflow synchronously (may timeout for complex optimizations).

**Request Body:**
```json
{
  "custom_parameters": {}
}
```

**Response:**
```json
{
  "status": "success",
  "timestamp": "2025-10-14T19:13:25.507123",
  "workflow": {
    "id": "production_planning",
    "title": "Advanced Production Planning",
    "industry": "manufacturing"
  },
  "optimization_pipeline": {
    "intent_classification": { /* ... */ },
    "data_analysis": { /* ... */ },
    "model_building": { /* ... */ },
    "optimization_solution": { /* ... */ }
  },
  "execution_summary": {
    "total_steps": 4,
    "completed_steps": 4,
    "success": true,
    "workflow_type": "synchronous_optimization"
  }
}
```

### **🔧 Core Optimization Endpoints**

### **7. Health Check**
**GET** `/health`

Check the status of the DcisionAI platform and available tools.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-14T19:13:25.507123",
  "tools_available": 8,
  "inference_profiles": [
    "intent_classification",
    "data_analysis", 
    "model_building",
    "optimization_solution"
  ],
  "version": "5.0.0-enhanced-with-new-tools",
  "architecture": "4-agent optimization with inference profiles + 4 new tools",
  "new_tools": [
    "generate_3d_landscape",
    "sensitivity_analysis",
    "monte_carlo_risk_analysis", 
    "enhanced_business_impact"
  ]
}
```

---

### **2. Intent Classification**
**POST** `/intent`

Analyze and classify optimization problems to understand intent and requirements.

**Request Body:**
```json
{
  "problem_description": "Optimize production for 3 products with capacity constraints"
}
```

**Response:**
```json
{
  "status": "success",
  "step": "intent_classification",
  "timestamp": "2025-10-14T19:13:25.507123",
  "result": {
    "intent": "production_optimization",
    "confidence": 0.95,
    "entities": ["products", "capacity"],
    "objectives": ["minimize costs", "maximize efficiency"],
    "constraints": ["capacity limits", "demand requirements"],
    "problem_scale": "small",
    "extracted_quantities": [3],
    "reasoning": "Production optimization problem with capacity constraints"
  },
  "message": "Intent classified as: production_optimization (scale: small)"
}
```

---

### **3. Data Analysis**
**POST** `/data`

Analyze data requirements and assess readiness for optimization.

**Request Body:**
```json
{
  "problem_description": "Optimize production for 3 products",
  "intent_data": {
    "intent": "production_optimization",
    "entities": ["products"],
    "problem_scale": "small"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "step": "data_analysis",
  "timestamp": "2025-10-14T19:13:25.507123",
  "result": {
    "data_entities": [
      {
        "name": "products",
        "attributes": ["product_id", "demand", "capacity"]
      }
    ],
    "readiness_score": 0.85,
    "sample_data": {"products": 3},
    "assumptions": ["Standard capacity metrics available"],
    "data_complexity": "low",
    "estimated_data_points": 100,
    "data_quality_requirements": ["Real-time demand data"]
  },
  "message": "Data analysis complete: 85% readiness"
}
```

---

### **4. Model Building**
**POST** `/model`

Create mathematical optimization models based on problem analysis.

**Request Body:**
```json
{
  "problem_description": "Optimize production for 3 products",
  "intent_data": {
    "intent": "production_optimization",
    "problem_scale": "small"
  },
  "data_analysis": {
    "data_entities": [{"name": "products"}],
    "readiness_score": 0.85
  }
}
```

**Response:**
```json
{
  "status": "success",
  "step": "model_building",
  "timestamp": "2025-10-14T19:13:25.507123",
  "result": {
    "model_type": "linear_programming",
    "variables": [
      {
        "name": "x1",
        "description": "Product A production",
        "type": "continuous",
        "lower_bound": 0,
        "upper_bound": 100
      }
    ],
    "objective": {
      "type": "maximize",
      "expression": "3*x1 + 2*x2 + 4*x3",
      "description": "Total profit maximization"
    },
    "constraints": [
      {
        "expression": "x1 + x2 + x3 <= 100",
        "description": "Total capacity constraint"
      }
    ],
    "model_complexity": "low",
    "estimated_solve_time": 0.5,
    "scalability": "good"
  },
  "message": "Model built: linear_programming with 3 variables"
}
```

---

### **5. Optimization Solving**
**POST** `/solve`

Solve mathematical optimization problems and find optimal solutions.

**Request Body:**
```json
{
  "problem_description": "Optimize production for 3 products",
  "intent_data": {
    "intent": "production_optimization"
  },
  "model_building": {
    "model_type": "linear_programming",
    "variables": [{"name": "x1", "description": "Product A production"}],
    "objective": {"type": "maximize", "expression": "3*x1 + 2*x2 + 4*x3"},
    "constraints": [{"expression": "x1 + x2 + x3 <= 100"}]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "step": "optimization_solution",
  "timestamp": "2025-10-14T19:13:25.507123",
  "result": {
    "status": "optimal",
    "objective_value": 750.0,
    "solution": {"x1": 50, "x2": 30, "x3": 20},
    "solve_time": 0.5,
    "iterations": 15,
    "gap": 0.0,
    "solver_info": {
      "solver": "PuLP CBC",
      "version": "2.7.0",
      "method": "Branch and Cut"
    },
    "sensitivity_analysis": {
      "shadow_prices": {"constraint_1": 2.5},
      "reduced_costs": {"x1": 0.0, "x2": 0.0, "x3": 0.0}
    }
  },
  "message": "Optimization solved: optimal with objective value 750.0"
}
```

---

### **6. 3D Landscape Generation**
**POST** `/3d-landscape`

Generate 3D landscape data for interactive visualization of optimization space.

**Request Body:**
```json
{
  "optimization_result": {
    "model_building": {
      "variables": [
        {"name": "x1", "description": "Product A production"}
      ],
      "constraints": [
        {"expression": "x1 <= 100"}
      ]
    },
    "optimization_solution": {
      "objective_value": 750,
      "solution": {"x1": 50}
    }
  },
  "resolution": 25
}
```

**Response:**
```json
{
  "status": "success",
  "landscape_data": {
    "terrain": {
      "heights": [[0.0, 0.1, 0.2, ...]],
      "bounds": {"x_min": -10, "x_max": 10, "y_min": -10, "y_max": 10},
      "resolution": 25
    },
    "constraints": [
      {
        "id": "constraint_0",
        "position": {"x": 5, "y": 2, "z": 3},
        "rotation": {"x": 0, "y": 0, "z": 0},
        "expression": "x1 <= 100",
        "type": "inequality",
        "color": [0.8, 0.3, 0.3]
      }
    ],
    "optimal_point": {
      "position": {"x": 0, "y": 5, "z": 0},
      "objective_value": 750,
      "solution": {"x1": 50},
      "color": [1.0, 0.8, 0.0],
      "intensity": 0.75
    },
    "variables": [
      {
        "id": "x1",
        "position": {"x": 3, "y": 1, "z": 2},
        "value": 50,
        "description": "Product A production",
        "importance": 0.5,
        "color": [0.2, 0.6, 0.8]
      }
    ],
    "metadata": {
      "resolution": 25,
      "objective_value": 750,
      "variable_count": 1,
      "constraint_count": 1,
      "generated_at": "2025-10-14T19:13:25.507057"
    }
  },
  "timestamp": "2025-10-14T19:13:25.507123"
}
```

---

### **7. Sensitivity Analysis**
**POST** `/sensitivity`

Analyze parameter sensitivity and impact on optimization results.

**Request Body:**
```json
{
  "base_optimization_result": {
    "optimization_solution": {
      "objective_value": 750,
      "solution": {"x1": 50}
    }
  },
  "parameter_changes": {
    "x1": 1.2
  }
}
```

**Response:**
```json
{
  "status": "success",
  "sensitivity_analysis": {
    "parameter_changes": {"x1": 1.2},
    "original_solution": {"x1": 50},
    "modified_solution": {"x1": 60.0},
    "objective_impact": {
      "original_objective": 750,
      "estimated_new_objective": 720.0,
      "change_percent": -4.0,
      "change_factor": 0.96,
      "impact_level": "low"
    },
    "feasibility_impact": {
      "feasibility_risk": "low",
      "constraint_violations": [],
      "recommendation": "Safe to implement"
    },
    "risk_assessment": {
      "risk_level": "low",
      "max_parameter_change": 0.2,
      "number_of_changes": 1,
      "confidence": 0.9
    },
    "recommendations": [
      "x1 change is within safe range"
    ]
  },
  "timestamp": "2025-10-14T19:13:25.507123"
}
```

---

### **8. Monte Carlo Risk Analysis**
**POST** `/monte-carlo`

Run Monte Carlo simulations for risk analysis with parameter uncertainty.

**Request Body:**
```json
{
  "base_optimization_result": {
    "optimization_solution": {
      "objective_value": 750,
      "solution": {"x1": 50}
    }
  },
  "uncertainty_ranges": {
    "x1": [0.8, 1.2]
  },
  "num_simulations": 100
}
```

**Response:**
```json
{
  "status": "success",
  "monte_carlo_analysis": {
    "simulation_count": 100,
    "base_objective": 750,
    "risk_metrics": {
      "success_rate": 1.0,
      "mean_objective": 742.73,
      "std_objective": 42.10,
      "min_objective": 675.50,
      "max_objective": 819.87,
      "value_at_risk_5pct": 681.90,
      "expected_shortfall": 677.09,
      "coefficient_of_variation": 0.034,
      "downside_deviation": 15.0
    },
    "confidence_intervals": {
      "90pct": 681.90,
      "95pct": 676.61,
      "99pct": 675.50
    },
    "scenario_analysis": {
      "best_case": 819.87,
      "worst_case": 675.50,
      "most_likely": 738.83,
      "feasible_scenarios": 100,
      "total_scenarios": 100
    },
    "recommendations": [
      "Low risk - solution is robust to parameter uncertainty",
      "Low variability - solution is stable"
    ]
  },
  "timestamp": "2025-10-14T19:13:25.507123"
}
```

---

### **9. Enhanced Business Impact**
**POST** `/business-impact`

Calculate sophisticated business impact metrics and financial analysis.

**Request Body:**
```json
{
  "optimization_result": {
    "optimization_solution": {
      "objective_value": 750,
      "solution": {"x1": 50}
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "business_impact": {
    "financial_impact": {
      "annual_savings": 9000,
      "roi_percentage": 250.0,
      "payback_period_months": 4.8,
      "npv_5_year": 36000.0,
      "irr_percentage": 45.2
    },
    "operational_impact": {
      "efficiency_gain": 23.5,
      "capacity_utilization": 87.3,
      "throughput_increase": 15.8,
      "quality_improvement": 12.4
    },
    "risk_metrics": {
      "confidence_level": 0.95,
      "risk_adjusted_savings": 675.0,
      "downside_protection": 0.85,
      "volatility_score": 0.12
    },
    "implementation_timeline": {
      "immediate_impact": 225.0,
      "month_1_impact": 450.0,
      "month_3_impact": 600.0,
      "month_6_impact": 750,
      "full_impact_timeline": "6 months"
    },
    "competitive_advantage": {
      "market_position_improvement": "15%",
      "cost_leadership_gap": "$2.3M annually",
      "innovation_capacity": "Enhanced",
      "customer_satisfaction": "+8.5%"
    }
  },
  "timestamp": "2025-10-14T19:13:25.507123"
}
```

---

## 🔧 **Error Handling**

All endpoints return consistent error responses:

```json
{
  "status": "error",
  "error": "Error description",
  "timestamp": "2025-10-14T19:13:25.507123"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (invalid input)
- `500`: Internal Server Error
- `503`: Service Unavailable

## 📊 **Rate Limits**

- **Free Tier**: 100 requests per hour
- **Enterprise**: Custom rate limits available
- **Burst**: Up to 10 requests per second

## 🔗 **SDK Support**

### **JavaScript/TypeScript**
```bash
npm install @dcisionai/sdk
```

```javascript
import { DcisionAI } from '@dcisionai/sdk';

const client = new DcisionAI({
  apiKey: 'your-api-key'
});

const result = await client.optimize({
  problem: 'Optimize production for 3 products'
});
```

### **Python**
```bash
pip install dcisionai
```

```python
from dcisionai import DcisionAI

client = DcisionAI(api_key='your-api-key')
result = client.optimize(problem='Optimize production for 3 products')
```

## 🚀 **AgentCore Gateway Integration (Future)**

### **Overview**
DcisionAI is preparing for integration with Amazon Bedrock AgentCore Gateway, which will provide enhanced capabilities for agent-based optimization workflows.

### **AgentCore Gateway Features**
- **Semantic Tool Discovery**: Intelligent discovery of optimization tools based on natural language queries
- **Extended Execution Time**: No 29-second timeout limitations for complex optimizations
- **Persistent Memory**: Context retention across optimization sessions
- **Enhanced Observability**: Detailed monitoring and debugging capabilities
- **MCP Protocol Support**: Model Context Protocol for seamless agent-tool communication

### **MCP Tools Available**
All DcisionAI workflows are converted to MCP-compatible tools:

```json
{
  "name": "optimize_production_planning",
  "description": "Advanced Production Planning - Optimize multi-product production with capacity, labor, and material constraints",
  "inputSchema": {
    "type": "object",
    "properties": {
      "problem_description": {
        "type": "string",
        "description": "Detailed description of the production planning problem"
      },
      "custom_parameters": {
        "type": "object",
        "description": "Custom parameters for the optimization"
      }
    },
    "required": ["problem_description"]
  },
  "metadata": {
    "industry": "manufacturing",
    "category": "production_planning",
    "difficulty": "advanced",
    "estimated_time": "4-5 minutes"
  }
}
```

### **Semantic Search Examples**
With AgentCore Gateway, users can discover optimization tools using natural language:

- **"Help me optimize my manufacturing production"** → Discovers production planning tools
- **"I need to optimize my marketing budget"** → Finds marketing spend optimization tools
- **"How can I improve my supply chain?"** → Locates supply chain optimization workflows

### **Authentication (AgentCore Gateway)**
```bash
# JWT Token Authentication
curl -H "Authorization: Bearer <jwt-token>" \
     -H "Content-Type: application/json" \
     -X POST https://dcisionai-optimization-gateway.execute-api.us-east-1.amazonaws.com/prod/tools/call \
     -d '{
       "name": "optimize_production_planning",
       "arguments": {
         "problem_description": "Optimize production for 5 products..."
       }
     }'
```

### **Migration Path**
1. **Current System**: Enhanced Lambda + API Gateway with async processing
2. **Transition**: AgentCore Gateway for new features while maintaining backward compatibility
3. **Future**: Full AgentCore Gateway integration with semantic search and extended capabilities

### **Benefits of AgentCore Gateway**
- **No Timeout Issues**: Extended execution time for complex optimizations
- **Intelligent Discovery**: Semantic search for finding relevant optimization tools
- **Better User Experience**: Natural language interaction with optimization workflows
- **Enhanced Monitoring**: Detailed observability and debugging capabilities
- **Scalable Architecture**: Better handling of concurrent optimization requests

## 📞 **Support**

- **Documentation**: https://docs.dcisionai.com
- **API Status**: https://status.dcisionai.com
- **Support**: support@dcisionai.com
- **Enterprise**: enterprise@dcisionai.com

---

*DcisionAI Platform API - Version 6.0.0-with-agentcore-gateway*
