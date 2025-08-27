# Enhanced DcisionAI Intent Tool - AWS-Style Agent-as-Tool Pattern

## Vision

The Enhanced DcisionAI Intent Tool implements **advanced intent classification with 6-specialist AWS-style agent-as-tool pattern** for understanding and routing manufacturing optimization queries. Our vision is to create an intelligent classification system that:

- **Accurately classifies user intent** across all manufacturing optimization domains using specialized experts
- **Provides domain expertise routing** with strict classification rules and conservative confidence scoring
- **Enables real consensus building** through expertise weighting and transparent reasoning
- **Coordinates AWS-style manager-worker delegation** for comprehensive intent understanding
- **Supports strict domain boundaries** ensuring specialists only classify within their expertise
- **Delivers enterprise-grade reliability** with NO fake responses and honest error handling

## What

The Enhanced DcisionAI Intent Tool is an **advanced intent classification system** that understands and routes manufacturing optimization queries using a 6-specialist AWS-style pattern:

### Core Capabilities

1. **6 Specialized Intent Classification Experts**
   - **Operations Research Specialist**: Mathematical optimization, linear programming, constraint optimization
   - **Production Systems Specialist**: Production workflows, manufacturing processes, line operations
   - **Supply Chain Specialist**: Logistics, inventory, distribution, procurement
   - **Quality Control Specialist**: Quality systems, compliance frameworks, standards, maintenance
   - **Sustainability Specialist**: Environmental impact, carbon footprint, green manufacturing
   - **Cost Optimization Specialist**: Cost accounting, financial modeling, economic optimization

2. **Strict Classification Rules**
   - **Domain Boundaries**: Each specialist only classifies problems within their expertise
   - **Conservative Confidence**: High confidence only when clearly in domain
   - **NOT_MY_DOMAIN**: Honest recognition when problems are outside specialist's domain
   - **Expertise Weighting**: Primary experts get 2.0x weight, secondary experts get 1.5x weight

3. **AWS-Style Manager-Worker Pattern**
   - **Manager Agent**: Coordinates delegation to 6 specialist workers
   - **Worker Tools**: Each specialist exposed as a tool for manager delegation
   - **Real Handoffs**: Genuine delegation with transparent consensus building
   - **Fallback Mechanism**: Direct agent calls if manager delegation fails

4. **Robust Consensus Building**
   - **Expertise Weighting**: Applies domain-specific weights for final classification
   - **Transparent Reasoning**: Clear explanation of how consensus was reached
   - **Multiple Strategies**: Unanimous, strong majority, simple majority, expertise-weighted
   - **Validation**: Cross-validation with primary and secondary experts

5. **Enterprise-Grade Reliability**
   - **NO Fake Responses**: All failures are honest and transparent
   - **Error Handling**: Robust error handling with fallback mechanisms
   - **JSON Parsing**: Multiple strategies for robust response parsing
   - **Timeout Handling**: Proper timeout management for long-running operations

## How

### Architecture Overview

```
EnhancedDcisionAI_Intent_Tool
├── Manager Agent (enhanced_intent_classification_manager)
│   ├── ops_research_classifier (Tool)
│   ├── production_systems_classifier (Tool)
│   ├── supply_chain_classifier (Tool)
│   ├── quality_classifier (Tool)
│   ├── sustainability_classifier (Tool)
│   └── cost_optimization_classifier (Tool)
├── Expertise Weighting System
├── Fallback Classification Mechanism
└── Performance Metrics Tracking
```

### Workflow Process

1. **Query Reception**
   - Receive user query or problem description
   - Preprocess and normalize query text
   - Extract key terms and concepts
   - Identify query context and domain indicators

2. **Manager Delegation**
   - Manager agent delegates to all 6 specialist tools
   - Each specialist analyzes query from their domain perspective
   - Apply strict classification rules and conservative confidence scoring
   - Collect responses from all specialists

3. **Consensus Building**
   - Aggregate classifications from all 6 specialists
   - Apply expertise weighting based on intent type
   - Calculate consensus confidence using multiple strategies
   - Generate transparent reasoning for final classification

4. **Result Processing**
   - Extract entities and objectives from specialist responses
   - Compile comprehensive classification metadata
   - Track performance metrics and execution times
   - Share insights via A2A coordination

5. **Fallback Handling**
   - If manager delegation fails, use direct agent calls
   - Implement robust JSON parsing with multiple strategies
   - Handle timeouts and errors gracefully
   - Maintain NO fake responses policy

### Key Components

#### Manager Agent
- **Purpose**: Coordinates delegation to 6 specialist workers using AWS-style pattern
- **Delegation**: Delegates to all specialists for comprehensive analysis
- **Consensus**: Builds consensus from specialist responses with expertise weighting
- **Output**: IntentClassification with category, confidence, and detailed reasoning

#### Specialist Tools
- **Operations Research**: CAPACITY_PLANNING, COST_OPTIMIZATION, PRODUCTION_SCHEDULING
- **Production Systems**: PRODUCTION_SCHEDULING, QUALITY_CONTROL, CAPACITY_PLANNING
- **Supply Chain**: SUPPLY_CHAIN, INVENTORY_OPTIMIZATION, DEMAND_FORECASTING
- **Quality Control**: QUALITY_CONTROL, MAINTENANCE
- **Sustainability**: ENVIRONMENTAL_OPTIMIZATION, COST_OPTIMIZATION
- **Cost Optimization**: COST_OPTIMIZATION, DEMAND_FORECASTING, CAPACITY_PLANNING

#### Expertise Weighting System
- **Primary Experts**: 2.0x weight for domain-specific intent types
- **Secondary Experts**: 1.5x weight for related intent types
- **Consensus Rules**: Unanimous (0.95), Strong Majority (0.85), Simple Majority (0.75)
- **Validation**: Cross-validation with multiple expert perspectives

#### IntentClassification
- **Structure**: Intent classification with confidence and detailed metadata
- **Categories**: PRODUCTION_SCHEDULING, CAPACITY_PLANNING, ENVIRONMENTAL_OPTIMIZATION, etc.
- **Confidence**: 0.0-1.0 confidence levels with expertise weighting
- **Metadata**: Comprehensive classification metadata and performance tracking

## Onboarding

### For Developers

#### Prerequisites
- Understanding of AWS-style agent-as-tool patterns
- Familiarity with manufacturing domains and optimization problems
- Knowledge of Strands framework and Agent patterns
- Experience with consensus building and expertise weighting
- Understanding of strict classification rules and domain boundaries

#### Getting Started

1. **Environment Setup**
   ```bash
   # Install dependencies
   pip install strands-agents strands-agents-tools bedrock-agentcore
   
   # Set up environment variables
   export ANTHROPIC_API_KEY="your_key"
   export AWS_ACCESS_KEY_ID="your_key"
   export AWS_SECRET_ACCESS_KEY="your_secret"
   ```

2. **Basic Usage**
   ```python
   from src.models.manufacturing.tools.intent import create_dcisionai_intent_tool
   
   # Initialize tool
   intent_tool = create_dcisionai_intent_tool()
   
   # Classify intent
   result = intent_tool.classify_intent(
       query="Optimize production scheduling for 5 products with capacity constraints"
   )
   
   print(f"Primary Intent: {result.primary_intent}")
   print(f"Confidence: {result.confidence}")
   print(f"Reasoning: {result.reasoning}")
   ```

3. **Advanced Usage**
   ```python
   # Get performance metrics
   metrics = intent_tool.get_performance_metrics()
   print(f"Execution Time: {metrics.execution_time}")
   print(f"Handoffs Performed: {metrics.handoffs_performed}")
   print(f"Consensus Achieved: {metrics.consensus_achieved}")
   
   # Access specialist consensus
   swarm_metadata = metrics.swarm_metadata
   specialist_consensus = swarm_metadata.get('specialist_consensus', {})
   for specialist, result_data in specialist_consensus.items():
       print(f"{specialist}: {result_data}")
   ```

#### Development Workflow

1. **Adding New Intent Categories**
   - Extend `IntentCategory` enum in `DcisionAI_Intent_Tool.py`
   - Update expertise weights in `expertise_weights` dictionary
   - Add classification rules to specialist prompts
   - Update consensus building logic

2. **Enhancing Specialist Expertise**
   - Modify specialist system prompts for domain-specific patterns
   - Update strict classification rules for new domains
   - Implement domain-specific confidence scoring
   - Add new specialist tools if needed

3. **Improving Consensus Building**
   - Enhance expertise weighting algorithms
   - Add new consensus strategies
   - Improve transparency in reasoning
   - Optimize fallback mechanisms

#### Testing

```python
# Run sustainability problem test
python src/models/manufacturing/tools/intent/tests/test_sustainability_problem.py

# Run production scheduling test
python src/models/manufacturing/tools/intent/tests/test_production_scheduling_problem.py

# Test individual specialists
from src.models.manufacturing.tools.intent.DcisionAI_Intent_Tool import ops_research_classifier
result = ops_research_classifier("Your test query here")
```

### Future Enhancements

#### Phase 1: Advanced Consensus Strategies
- Implement machine learning-based consensus weighting
- Add dynamic expertise adjustment based on performance
- Create adaptive classification strategies
- Build performance-based optimization

#### Phase 2: Enhanced Domain Coverage
- Add more specialized manufacturing domains
- Implement cross-domain intent recognition
- Create domain-specific classification patterns
- Add industry-specific expertise

#### Phase 3: Performance Optimization
- Implement parallel specialist execution
- Add caching for common query patterns
- Create performance-based routing
- Build real-time adaptation mechanisms

## Design Decisions

### 1. AWS-Style Manager-Worker Pattern

**Decision**: Use manager agent with worker tools rather than direct agent calls.

**Rationale**:
- **Coordination**: Manager provides centralized coordination and consensus building
- **Scalability**: Easy to add new specialists without changing core logic
- **Reliability**: Fallback mechanism ensures system robustness
- **Transparency**: Clear delegation and consensus building process

**Alternatives Considered**:
- Direct agent calls without coordination
- Single monolithic classifier
- Rule-based classification system

### 2. 6-Specialist Architecture

**Decision**: Use exactly 6 specialized agents covering key manufacturing domains.

**Rationale**:
- **Coverage**: Covers all major manufacturing optimization domains
- **Expertise**: Each specialist has deep domain knowledge
- **Efficiency**: Optimal balance between coverage and complexity
- **Reliability**: Multiple perspectives ensure robust classification

**Implementation**:
- Operations Research: Mathematical optimization and OR models
- Production Systems: Production workflows and processes
- Supply Chain: Logistics and inventory management
- Quality Control: Quality systems and compliance
- Sustainability: Environmental impact and green manufacturing
- Cost Optimization: Financial modeling and cost analysis

### 3. Strict Classification Rules

**Decision**: Implement strict domain boundaries with conservative confidence scoring.

**Rationale**:
- **Accuracy**: Prevents specialists from overreaching outside their domain
- **Honesty**: Ensures NO fake responses and transparent classification
- **Quality**: High confidence only when clearly in domain
- **Reliability**: Builds trust through honest domain recognition

**Implementation**:
- NOT_MY_DOMAIN classification for out-of-domain problems
- Conservative confidence scoring (0.1-0.3 for low confidence)
- Clear domain boundaries in specialist prompts
- Transparent reasoning for all classifications

### 4. Expertise Weighting System

**Decision**: Apply domain-specific weights for final classification.

**Rationale**:
- **Accuracy**: Primary experts get higher weight for their domains
- **Fairness**: Secondary experts contribute appropriately
- **Transparency**: Clear weighting logic for consensus building
- **Quality**: Weighted consensus improves final classification accuracy

**Implementation**:
- Primary experts: 2.0x weight for their domain
- Secondary experts: 1.5x weight for related domains
- Consensus rules: Unanimous (0.95), Strong Majority (0.85), Simple Majority (0.75)
- Expertise-weighted confidence calculation

### 5. NO Fake Responses Policy

**Decision**: Implement strict policy against fake or made-up responses.

**Rationale**:
- **Trust**: Builds user trust through honest responses
- **Quality**: Prevents misleading classifications
- **Reliability**: Ensures system integrity and accuracy
- **Transparency**: Clear error handling and fallback mechanisms

**Implementation**:
- Honest error reporting with clear error messages
- Fallback mechanisms for failed operations
- Transparent confidence scoring
- Clear domain boundary recognition

### 6. Robust JSON Parsing

**Decision**: Implement multiple strategies for robust JSON response parsing.

**Rationale**:
- **Reliability**: Handles malformed JSON from LLM responses
- **Robustness**: Multiple parsing strategies ensure success
- **Quality**: Prevents parsing failures from affecting classification
- **Transparency**: Clear parsing error handling

**Implementation**:
- Direct JSON parsing as primary strategy
- Regex-based JSON extraction as secondary strategy
- JSON fixing for common issues as tertiary strategy
- Graceful fallback for parsing failures

### 7. Fallback Classification Mechanism

**Decision**: Implement direct agent calls as fallback when manager delegation fails.

**Rationale**:
- **Reliability**: Ensures system continues working even if manager fails
- **Robustness**: Multiple execution paths prevent complete failure
- **Performance**: Direct calls can be faster in some cases
- **Transparency**: Clear fallback logic and error handling

**Implementation**:
- Direct specialist tool calls when manager delegation fails
- Same consensus building logic for fallback results
- Performance tracking for both paths
- Transparent fallback indication in metadata

### 8. Comprehensive Performance Tracking

**Decision**: Implement detailed performance metrics and metadata tracking.

**Rationale**:
- **Monitoring**: Track system performance and reliability
- **Optimization**: Identify areas for improvement
- **Transparency**: Provide detailed execution information
- **Debugging**: Enable effective troubleshooting and debugging

**Implementation**:
- Execution time tracking
- Handoff and delegation metrics
- Consensus building statistics
- Specialist response tracking
- Comprehensive metadata collection
