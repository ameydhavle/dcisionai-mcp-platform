# 🚨 CRITICAL: AI IGNORING TEMPLATES

## 📅 **Analysis Date**: October 17, 2025

## 🔍 **Issue Identified**

The AI is **completely ignoring our ultra-specific manufacturing templates** despite explicit instructions. This indicates a fundamental problem with how the AI processes complex prompts.

### **Evidence:**
1. **Template Provided**: "Variables: z1, z2, z3... (operating time for each line/machine)"
2. **AI Generated**: x1, x2, x3, y1, y2, y3 (production quantities) + z1, z2 (time)
3. **Template Provided**: "Constraints: rate × time >= demand"
4. **AI Generated**: Nonsensical capacity constraints

### **Root Cause:**
The AI is **not following structured templates** in complex prompts. It's generating models based on its training data rather than following explicit instructions.

---

## 🎯 **SOLUTION: HARDCODED TEMPLATE DETECTION**

Instead of relying on the AI to follow templates, we need to **detect the problem type** and **force the correct model** programmatically.

### **Approach 1: Problem Type Detection + Hardcoded Models**

```python
def build_model_with_hardcoded_templates(problem_description, intent_data, data_analysis, solver_selection):
    """
    Build model using hardcoded templates for common problem types
    """
    
    # Detect problem type
    problem_type = detect_problem_type(problem_description, intent_data)
    
    if problem_type == "manufacturing_production_planning":
        return build_manufacturing_model(problem_description)
    elif problem_type == "healthcare_staffing":
        return build_staffing_model(problem_description)
    elif problem_type == "portfolio_optimization":
        return build_portfolio_model(problem_description)
    else:
        # Fallback to AI-generated model
        return build_ai_model(problem_description, intent_data, data_analysis, solver_selection)

def build_manufacturing_model(problem_description):
    """
    Hardcoded manufacturing production planning model
    """
    # Extract parameters from problem description
    lines = extract_production_lines(problem_description)
    products = extract_products(problem_description)
    demands = extract_demands(problem_description)
    costs = extract_costs(problem_description)
    
    # Build correct model
    variables = []
    constraints = []
    
    # Time variables for each line
    for i, line in enumerate(lines):
        variables.append({
            "name": f"z{i+1}",
            "type": "continuous",
            "bounds": "0 to 8",
            "description": f"Operating time for {line['name']} (hours)"
        })
    
    # Demand constraints: rate × time >= demand
    for product in products:
        constraint_expr = " + ".join([
            f"{line['rates'][product]} * z{i+1}" 
            for i, line in enumerate(lines) 
            if product in line['rates']
        ])
        constraints.append({
            "expression": f"{constraint_expr} >= {demands[product]}",
            "description": f"Demand constraint for {product}"
        })
    
    # Objective: minimize total cost
    objective_expr = " + ".join([
        f"{line['cost']} * z{i+1}" 
        for i, line in enumerate(lines)
    ])
    
    return {
        "model_type": "linear_programming",
        "variables": variables,
        "objective": {
            "type": "minimize",
            "expression": objective_expr,
            "description": "Total production cost"
        },
        "constraints": constraints,
        "model_complexity": "medium",
        "estimated_solve_time": 1,
        "mathematical_formulation": "Hardcoded manufacturing model with correct variable definitions and constraints"
    }
```

### **Approach 2: Template Enforcement**

```python
def enforce_manufacturing_template(ai_generated_model, problem_description):
    """
    Take AI-generated model and enforce manufacturing template
    """
    
    # Check if AI followed template
    if not follows_manufacturing_template(ai_generated_model):
        # Force correct template
        return build_manufacturing_model(problem_description)
    
    return ai_generated_model

def follows_manufacturing_template(model):
    """
    Check if model follows manufacturing template
    """
    variables = model.get("variables", [])
    constraints = model.get("constraints", [])
    
    # Check for time variables
    has_time_vars = any("z" in var["name"] for var in variables)
    
    # Check for rate × time constraints
    has_rate_time_constraints = any("*" in constraint["expression"] for constraint in constraints)
    
    # Check for unused production variables
    production_vars = [var for var in variables if "x" in var["name"] or "y" in var["name"]]
    used_production_vars = any(
        var["name"] in constraint["expression"] 
        for var in production_vars 
        for constraint in constraints
    )
    
    return has_time_vars and has_rate_time_constraints and not (production_vars and not used_production_vars)
```

---

## 🚀 **IMMEDIATE IMPLEMENTATION**

### **Step 1: Add Problem Type Detection**
```python
def detect_problem_type(problem_description, intent_data):
    """
    Detect problem type from description and intent
    """
    text = problem_description.lower()
    intent = intent_data.get("intent", "").lower()
    industry = intent_data.get("industry", "").lower()
    
    if "manufacturing" in industry or "production" in intent:
        if "line" in text and "units/hour" in text:
            return "manufacturing_production_planning"
    
    if "healthcare" in industry or "staff" in intent:
        return "healthcare_staffing"
    
    if "portfolio" in intent or "allocation" in text:
        return "portfolio_optimization"
    
    return "unknown"
```

### **Step 2: Add Hardcoded Model Builders**
```python
def extract_production_lines(problem_description):
    """
    Extract production line information from problem description
    """
    # Parse problem description to extract:
    # - Line names
    # - Production rates for each product
    # - Operating costs
    # - Time limits
    
    lines = []
    # Implementation details...
    return lines

def extract_products(problem_description):
    """
    Extract product information from problem description
    """
    # Parse problem description to extract:
    # - Product names
    # - Demand requirements
    
    products = []
    # Implementation details...
    return products
```

### **Step 3: Integrate with Existing Tools**
```python
async def build_model(self, problem_description: str, intent_data: Dict[str, Any], 
                     data_analysis: Dict[str, Any], solver_selection: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build optimization model with hardcoded templates for common problems
    """
    
    # Detect problem type
    problem_type = self.detect_problem_type(problem_description, intent_data)
    
    if problem_type == "manufacturing_production_planning":
        # Use hardcoded manufacturing template
        model = self.build_manufacturing_model(problem_description)
    else:
        # Use AI-generated model
        model = await self.build_ai_model(problem_description, intent_data, data_analysis, solver_selection)
    
    return {
        "status": "success",
        "step": "model_building",
        "timestamp": datetime.now().isoformat(),
        "result": model,
        "message": f"Model built using {'hardcoded template' if problem_type != 'unknown' else 'AI generation'}"
    }
```

---

## 🎯 **CONCLUSION**

The AI is **fundamentally unable to follow complex templates** despite explicit instructions. We need to implement **hardcoded template detection** and **programmatic model generation** for common problem types.

**Next Action**: Implement hardcoded manufacturing template with parameter extraction from problem descriptions.

---

**Status**: 🚨 **CRITICAL - AI IGNORING TEMPLATES** 🚨
