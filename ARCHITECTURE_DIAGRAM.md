# DcisionAI Platform Architecture

## Current Architecture (AgentCore Gateway + Qwen 30B)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                FRONTEND LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Production: https://platform.dcisionai.com                                    │
│  Local Dev:  http://localhost:3000                                             │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   React App     │    │   Hero.js       │    │ Optimization    │            │
│  │   (Main UI)     │    │   (Workflows)   │    │ Results.js      │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│           │                       │                       │                    │
│           └───────────────────────┼───────────────────────┘                    │
│                                   │                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    agentcore-config.js                                 │   │
│  │  • callGatewayTool() - MCP protocol communication                     │   │
│  │  • JWT Authentication with Cognito                                    │   │
│  │  • Response parsing and error handling                                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS/MCP Protocol
                                    │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AGENTCORE GATEWAY LAYER                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│  URL: https://dcisionai-gateway-0de1a655-ja1rhlcqjx.gateway.bedrock-agentcore. │
│       us-east-1.amazonaws.com/mcp                                              │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    Amazon Bedrock AgentCore Gateway                    │   │
│  │  • MCP Protocol Support                                               │   │
│  │  • JWT Authentication (Cognito)                                       │   │
│  │  • Tool Discovery and Routing                                         │   │
│  │  • Extended Execution Time                                            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                   │                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    Available Tools                                     │   │
│  │  • DcisionAI-Optimization-Tools-Fixed___classify_intent               │   │
│  │  • DcisionAI-Optimization-Tools-Fixed___analyze_data                  │   │
│  │  • DcisionAI-Optimization-Tools-Fixed___build_model                   │   │
│  │  • DcisionAI-Optimization-Tools-Fixed___solve_optimization            │   │
│  │  • DcisionAI-Optimization-Tools-Fixed___get_workflow_templates        │   │
│  │  • DcisionAI-Optimization-Tools-Fixed___execute_workflow              │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Lambda Invocation
                                    │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            LAMBDA FUNCTION LAYER                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Function: dcisionai-enhanced-workflows                                        │
│  ARN: arn:aws:lambda:us-east-1:808953421331:function:dcisionai-enhanced-workflows │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                enhanced_lambda_with_workflows.py                       │   │
│  │  • AgentCore Gateway tool call handling                               │   │
│  │  • 4-step optimization pipeline                                       │   │
│  │  • 21 industry-specific workflows                                     │   │
│  │  • Enhanced JSON parsing and error handling                           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                   │                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    Optimization Pipeline                               │   │
│  │  1. Intent Classification (Claude 3 Haiku)                            │   │
│  │  2. Data Analysis (Claude 3 Haiku)                                    │   │
│  │  3. Model Building (Qwen 30B Coder) ⭐                                │   │
│  │  4. Optimization Solving (Claude 3 Haiku)                             │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ AWS Bedrock API Calls
                                    │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            AI MODEL LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │  Claude 3 Haiku │    │  Claude 3 Sonnet│    │  Qwen 30B Coder │            │
│  │  (Fast Inference)│    │  (Complex Tasks)│    │  (Math Models)  │            │
│  │                 │    │                 │    │                 │            │
│  │ • Intent Class  │    │ • Complex       │    │ • Model Building│            │
│  │ • Data Analysis │    │   Reasoning     │    │ • Math JSON Gen │            │
│  │ • Optimization  │    │ • Advanced      │    │ • Real Variables│            │
│  │   Solving       │    │   Analysis      │    │ • Real Constraints│          │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    AWS Bedrock Service                                 │   │
│  │  • Model Selection and Routing                                        │   │
│  │  • Inference Profile Management                                       │   │
│  │  • Enterprise-grade Security and Reliability                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Real Optimization Results
                                    │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            OUTPUT LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    Real Optimization Data                              │   │
│  │  • Model Type: "mixed_integer_programming" (not "unknown")            │   │
│  │  • Variables: Real decision variables with proper names and bounds     │   │
│  │  • Constraints: Mathematical constraints based on the problem          │   │
│  │  • Objective: Proper mathematical expressions                          │   │
│  │  • Business Impact: Calculated from actual optimization results        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    Frontend Display                                    │   │
│  │  • Mathematical Formulation (Real)                                    │   │
│  │  • Business Impact (Calculated)                                       │   │
│  │  • 3D Decision Landscape (Interactive)                                │   │
│  │  • Sensitivity Analysis (Real-time)                                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Key Improvements with Qwen 30B Integration

### Before (Claude Models Only)
- Model Type: "unknown"
- Variables: Generic placeholder data
- Constraints: Basic template constraints
- Objective: Simple expressions
- Business Impact: Estimated values

### After (Qwen 30B Integration)
- Model Type: "mixed_integer_programming"
- Variables: 20+ realistic variables with proper names and bounds
- Constraints: 17+ realistic constraints including demand, capacity, labor, material
- Objective: Complex profit maximization with setup costs
- Business Impact: Calculated from actual optimization results

## Data Flow

1. **User Input** → Frontend (React)
2. **Frontend** → AgentCore Gateway (MCP Protocol)
3. **AgentCore Gateway** → Lambda Function (Tool Routing)
4. **Lambda Function** → AWS Bedrock (Model Selection)
5. **AWS Bedrock** → Qwen 30B/Claude Models (AI Processing)
6. **AI Models** → Lambda Function (Real Results)
7. **Lambda Function** → AgentCore Gateway (Response)
8. **AgentCore Gateway** → Frontend (MCP Response)
9. **Frontend** → User (Real Optimization Data)

## Technology Stack

- **Frontend**: React.js, TypeScript, Tailwind CSS
- **Gateway**: Amazon Bedrock AgentCore Gateway
- **Backend**: AWS Lambda (Python 3.9)
- **AI Models**: Qwen 30B Coder, Claude 3 Haiku, Claude 3 Sonnet
- **Protocol**: Model Context Protocol (MCP)
- **Authentication**: Amazon Cognito (JWT)
- **Hosting**: AWS S3 + CloudFront CDN
- **Monitoring**: AWS CloudWatch
