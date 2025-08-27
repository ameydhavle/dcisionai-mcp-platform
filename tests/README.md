# DcisionAI MCP Platform - Test Suite

## 📁 Test Structure

```
tests/
├── 📄 README.md                    # This file
├── 🏃 run_all_tests.py            # Test runner script
├── 📦 __init__.py                 # Test package
│
├── 📁 unit/                       # Unit tests
│   ├── 📦 __init__.py
│   ├── 🧠 test_intent_tool.py
│   ├── 📊 test_solver_availability.py
│   ├── 🔧 test_solver_functionality.py
│   ├── 🔧 test_solver_fix.py
│   ├── 🏗️ test_model_builder_only.py
│   ├── 🔧 test_solver_only.py
│   └── 🔗 test_tool_imports.py
│
├── 📁 integration/                # Integration tests
│   ├── 📦 __init__.py
│   └── 🔄 test_refactored_tools.py
│
└── 📁 workflow/                   # Workflow tests
    ├── 📦 __init__.py
    └── 🚀 test_complete_workflow.py
```

## 🧪 Running Tests

### Run All Tests
```bash
python tests/run_all_tests.py
```

### Run Specific Test Types
```bash
# Unit tests only
python tests/run_all_tests.py --unit

# Integration tests only
python tests/run_all_tests.py --integration

# Workflow tests only
python tests/run_all_tests.py --workflow

# All tests (default)
python tests/run_all_tests.py --all
```

### Run Individual Tests
```bash
# Unit tests
python tests/unit/test_intent_tool.py
python tests/unit/test_solver_functionality.py

# Integration tests
python tests/integration/test_refactored_tools.py

# Workflow tests
python tests/workflow/test_complete_workflow.py
```

## 📋 Test Categories

### Unit Tests (`tests/unit/`)
- **Individual component testing**
- **Tool initialization and basic functionality**
- **Coefficient parsing and JSON response handling**
- **Solver availability and functionality**
- **Import and dependency testing**

### Integration Tests (`tests/integration/`)
- **Multi-component interactions**
- **Tool-to-tool communication**
- **Data flow between components**
- **Error handling across components**

### Workflow Tests (`tests/workflow/`)
- **Complete 4-stage optimization pipeline**
- **End-to-end manufacturing scenarios**
- **Production readiness validation**
- **Performance and reliability testing**

## 🎯 Test Coverage

### ✅ Covered Components
- Intent Classification Tool
- Data Analysis Tool
- Model Builder Tool
- Solver Tool (all 4 solvers)
- Coefficient parsing
- JSON response parsing
- Tool imports and initialization
- Complete workflow orchestration

### 🔧 Test Features
- **Timeout handling** (300s per test)
- **Error capture and reporting**
- **Success/failure tracking**
- **Comprehensive logging**
- **Production-ready validation**

## 🚀 Test Execution

### Prerequisites
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.mcp.txt
```

### Environment Setup
- **AWS credentials** configured
- **Strands framework** installed
- **All solver dependencies** available
- **Python 3.11+** environment

## 📊 Test Results

### Expected Outcomes
- **Unit Tests**: All individual components working
- **Integration Tests**: Multi-component interactions successful
- **Workflow Tests**: Complete pipeline execution successful

### Success Criteria
- ✅ No mock/fallback responses
- ✅ Real solver execution with meaningful objective values
- ✅ Proper coefficient parsing (not 0.0 values)
- ✅ Complete JSON response parsing
- ✅ Production-ready error handling

## 🔍 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure `src/` is in Python path
2. **AWS Credentials**: Configure AWS credentials properly
3. **Solver Dependencies**: Install all required solver packages
4. **Timeout Issues**: Increase timeout for complex tests

### Debug Mode
```bash
# Run with verbose output
python -v tests/unit/test_solver_functionality.py
```

---

**Last Updated**: August 26, 2025  
**Test Suite Version**: 1.0.0  
**Status**: ✅ Production Ready
