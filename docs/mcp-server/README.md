# DcisionAI MCP Server

## 🚀 **Overview**

The DcisionAI MCP Server provides advanced mathematical optimization capabilities through the Model Context Protocol (MCP). It integrates AI reasoning with industry-leading optimization engines to solve complex business problems across any domain.

---

## 🛠️ **Installation**

### **Quick Install (Recommended)**
```bash
# Install via uvx (isolated environment)
uvx dcisionai-mcp-server

# Or install via pip
pip install dcisionai-mcp-server
```

### **Development Install**
```bash
# Clone repository
git clone https://github.com/dcisionai/dcisionai-mcp-platform.git
cd dcisionai-mcp-platform/mcp-server

# Install in development mode
pip install -e .
```

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
# AWS Configuration (for AgentCore integration)
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key

# Optional: Custom model configuration
export DcisionAI_MODEL_PROVIDER=claude
export DcisionAI_MODEL_NAME=claude-3-haiku-20240307
```

### **MCP Client Configuration**

#### **Cursor IDE**
```json
// ~/.cursor/mcp.json
{
    "mcpServers": {
        "dcisionai-mcp-server": {
            "command": "uvx",
            "args": ["dcisionai-mcp-server"],
            "env": {
                "AWS_DEFAULT_REGION": "us-east-1"
            }
        }
    }
}
```

#### **Claude Desktop**
```json
// claude_desktop_config.json
{
    "mcpServers": {
        "dcisionai-mcp-server": {
            "command": "uvx",
            "args": ["dcisionai-mcp-server"]
        }
    }
}
```

---

## 🎯 **Available Tools**

### **Core Optimization Workflow**

#### **1. Intent Classification**
```python
# Tool: classify_intent
# Purpose: Classify optimization problems and identify domain, type, and complexity
# Input: problem_description, context (optional)
# Output: optimization_type, problem_domain, objective, complexity, decision_variables, constraints
```

#### **2. Data Analysis**
```python
# Tool: analyze_data
# Purpose: Assess data readiness and quality for optimization
# Input: problem_description, intent_data
# Output: data_quality, missing_data, data_sources, recommendations
```

#### **3. Solver Selection**
```python
# Tool: select_solver
# Purpose: Intelligently select optimal solver for the problem
# Input: optimization_type, problem_size, performance_requirement
# Output: selected_solver, reasoning, alternative_solvers, performance_estimate
```

#### **4. Model Building**
```python
# Tool: build_model
# Purpose: Build mathematical optimization model using AI reasoning
# Input: problem_description, intent_data, data_analysis
# Output: variables, objective, constraints, reasoning_steps
```

#### **5. Optimization Solving**
```python
# Tool: solve_optimization
# Purpose: Execute optimization and generate results
# Input: problem_description, intent_data, data_analysis, model_building
# Output: solver_status, objective_value, optimal_values, business_impact
```

#### **6. Result Explanation**
```python
# Tool: explain_optimization
# Purpose: Provide business-facing explanation of results
# Input: problem_description, optimization_solution
# Output: executive_summary, detailed_explanation, business_recommendations
```

#### **7. Scenario Simulation**
```python
# Tool: simulate_scenarios
# Purpose: Run simulation analysis for strategic planning
# Input: problem_description, optimization_solution, simulation_type, num_trials
# Output: simulation_results, risk_analysis, recommendations
```

### **Advanced Features**

#### **Workflow Templates**
```python
# Tool: get_workflow_templates
# Purpose: Get available industry-specific workflow templates
# Output: List of 21 industry workflows with descriptions

# Tool: execute_workflow
# Purpose: Execute complete industry workflow
# Input: industry, workflow_id, user_input
# Output: Complete optimization workflow results
```

---

## 🧠 **AI Reasoning Features**

### **Pattern-Breaking Technology**
- **Anti-Bias Prompts**: Explicitly avoids learned patterns from training data
- **First-Principles Reasoning**: Forces AI to think from mathematical fundamentals
- **Industry-Agnostic**: Works across any domain without hardcoded templates

### **Chain-of-Thought Reasoning**
- **7-Step Process**: Transparent, auditable decision-making workflow
- **Step-by-Step Analysis**: Shows reasoning for each decision
- **Validation Checks**: Ensures all variables are used and constraints are satisfied

### **Business Validation**
- **AI-Driven Logic**: Uses AI reasoning instead of keyword matching
- **Mathematical Validation**: Verifies objective calculations and constraint satisfaction
- **Business Sense Checks**: Ensures solutions make business sense

---

## 🔧 **Optimization Engines**

### **Supported Solvers**
- **Linear Programming**: OR-Tools PDLP, Gurobi LP, CPLEX LP
- **Mixed Integer**: OR-Tools CP-SAT, Gurobi MIP, SCIP
- **Quadratic Programming**: OSQP, Gurobi QP
- **Constraint Programming**: OR-Tools CP-SAT

### **Solver Selection Logic**
The AI automatically selects the optimal solver based on:
- Problem type (LP, MIP, QP, CP)
- Problem size (variables and constraints)
- Performance requirements (speed vs. accuracy)
- Available solver capabilities

---

## 📊 **Simulation Capabilities**

### **Monte Carlo Simulation**
- **Risk Analysis**: Quantify uncertainty in optimization results
- **Parameter Sampling**: Generate random realizations of uncertain parameters
- **Statistical Analysis**: Mean, standard deviation, percentiles, VaR

### **Discrete Event Simulation**
- **Process Simulation**: Model complex processes and workflows
- **Queuing Theory**: Analyze waiting times and resource utilization
- **System Dynamics**: Understand feedback loops and causal relationships

### **Agent-Based Simulation**
- **Complex Systems**: Model interactions between multiple agents
- **Market Dynamics**: Simulate market behavior and competition
- **Emergent Behavior**: Understand system-level patterns

---

## 🎯 **Use Cases**

### **Manufacturing & Production**
```
Problem: Optimize production schedule for multiple lines with capacity constraints
Tools: classify_intent → analyze_data → build_model → solve_optimization → explain_optimization
Result: Optimal production schedule with cost minimization and capacity utilization
```

### **Financial Portfolio Optimization**
```
Problem: Allocate investments across assets with risk constraints
Tools: classify_intent → analyze_data → build_model → solve_optimization → simulate_scenarios
Result: Risk-adjusted portfolio allocation with Monte Carlo risk analysis
```

### **Retail Inventory Management**
```
Problem: Optimize inventory across multiple locations and SKUs
Tools: classify_intent → analyze_data → build_model → solve_optimization → explain_optimization
Result: Optimal inventory allocation with demand satisfaction and cost minimization
```

### **Healthcare Resource Allocation**
```
Problem: Allocate medical resources across departments and time periods
Tools: classify_intent → analyze_data → build_model → solve_optimization → simulate_scenarios
Result: Optimal resource allocation with patient flow simulation
```

---

## 🚀 **Getting Started**

### **Quick Test**
```bash
# Start MCP server
uvx dcisionai-mcp-server

# In your MCP client (Cursor IDE, Claude Desktop), try:
"Classify this optimization problem: I need to optimize my production schedule. I have 2 production lines that can produce 100 and 90 units per hour respectively, at costs of $50 and $60 per hour. I need to produce at least 500 units. Minimize total cost."
```

### **Complete Workflow Example**
```
1. "Classify this optimization problem: [your problem description]"
2. "Analyze the data requirements for this problem"
3. "Select the best solver for this optimization"
4. "Build a mathematical model for this problem"
5. "Solve the optimization and find the optimal solution"
6. "Explain the results in business terms"
7. "Run a simulation to analyze risks and alternatives"
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **MCP Server Not Starting**
```bash
# Check Python version (requires 3.10+)
python --version

# Check dependencies
pip list | grep dcisionai

# Check AWS credentials
aws sts get-caller-identity
```

#### **Tools Not Available in IDE**
```bash
# Restart your IDE completely
# Check MCP configuration file syntax
# Verify MCP server is running
```

#### **Optimization Failures**
```bash
# Check problem formulation
# Verify data quality
# Try different solver
# Check constraint feasibility
```

### **Debug Mode**
```bash
# Run with debug logging
export DcisionAI_DEBUG=true
uvx dcisionai-mcp-server
```

---

## 📚 **Advanced Usage**

### **Custom Solvers**
```python
# Add custom solver integration
from dcisionai_mcp_server.optimization_engine import OptimizationEngine

engine = OptimizationEngine()
engine.add_custom_solver("my_solver", solver_function)
```

### **Custom Validation**
```python
# Add custom business validation
from dcisionai_mcp_server.business_validation import BusinessValidator

validator = BusinessValidator()
validator.add_custom_validation("my_domain", validation_function)
```

### **Custom Simulation**
```python
# Add custom simulation engines
from dcisionai_mcp_server.simulation_engine import SimulationEngine

engine = SimulationEngine()
engine.add_custom_simulation("my_simulation", simulation_function)
```

---

## 🔄 **Updates and Maintenance**

### **Updating the MCP Server**
```bash
# Update via uvx
uvx --upgrade dcisionai-mcp-server

# Update via pip
pip install --upgrade dcisionai-mcp-server
```

### **Version Information**
```bash
# Check current version
uvx dcisionai-mcp-server --version

# Check available updates
pip list --outdated | grep dcisionai
```

---

## 📞 **Support**

- **Documentation**: [Full API Reference](../API_REFERENCE.md)
- **GitHub Issues**: [Report bugs and request features](https://github.com/dcisionai/dcisionai-mcp-platform/issues)
- **Community**: [Join our Discord](https://discord.gg/dcisionai)
- **Email**: support@dcisionai.com

---

*The DcisionAI MCP Server brings the power of AI-driven mathematical optimization directly to your development environment.*
