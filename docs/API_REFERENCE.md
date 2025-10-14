# 🔌 DcisionAI Platform - API Reference

## 🌐 **Base URL**
```
https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod
```

## 🔧 **Authentication**
All API endpoints require no authentication for public access. Enterprise customers can request API keys for rate limiting and usage tracking.

## 📋 **Available Endpoints**

### **1. Health Check**
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

## 📞 **Support**

- **Documentation**: https://docs.dcisionai.com
- **API Status**: https://status.dcisionai.com
- **Support**: support@dcisionai.com
- **Enterprise**: enterprise@dcisionai.com

---

*DcisionAI Platform API - Version 5.0.0-enhanced-with-new-tools*
