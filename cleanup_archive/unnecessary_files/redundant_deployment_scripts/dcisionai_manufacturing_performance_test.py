#!/usr/bin/env python3
"""
DcisionAI Manufacturing MCP Server - Performance Testing Script
==============================================================

Comprehensive performance testing for all 6 manufacturing tools:
1. Intent Classification
2. Data Analysis & Requirements
3. Model Building & Optimization
4. Problem Solving (Solver Swarm)
5. Workflow Orchestration
6. Status Monitoring

Captures detailed metrics:
- Response times
- Tool availability
- Response quality
- Error rates
- Manufacturing domain accuracy

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import boto3
import json
import logging
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('manufacturing_performance_test.log')
    ]
)
logger = logging.getLogger("DcisionAI Manufacturing Performance Test")

# Project root path
PROJECT_ROOT = Path(__file__).parent.parent.parent

def setup_aws_client():
    """Setup AWS Bedrock AgentCore client"""
    try:
        client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        logger.info("✅ AWS Bedrock AgentCore client initialized")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to setup AWS client: {e}")
        raise

def invoke_manufacturing_agent(client, prompt: str, session_id: str) -> Dict[str, Any]:
    """Invoke the DcisionAI Manufacturing Agent with timing"""
    start_time = time.time()
    
    try:
        # Agent runtime ARN (from successful deployment)
        agent_runtime_arn = 'arn:aws:bedrock-agentcore:us-east-1:808953421331:runtime/dcisionai_manufacturing_mcp_server-nk8uWLCqPh'
        
        # Prepare the request
        request_body = {
            "input": {
                "prompt": prompt
            }
        }
        
        logger.info(f"🔗 Invoking Agent: {agent_runtime_arn}")
        logger.info(f"🆔 Session: {session_id}")
        logger.info(f"📝 Prompt: {prompt[:100]}...")
        
        # Make the API call
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(request_body),
            qualifier="DEFAULT"
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Parse response
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        return {
            'success': True,
            'response_time': response_time,
            'response': response_data,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        
        return {
            'success': False,
            'error': str(e),
            'response_time': response_time,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat()
        }

def validate_manufacturing_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the manufacturing response for correctness"""
    validation_results = {
        'tools_available': False,
        'manufacturing_domain': False,
        'response_format': False,
        'branding_correct': False,
        'server_ready': False
    }
    
    try:
        output = response.get('output', {})
        
        # Check if tools are available
        tools_available = output.get('tools_available', [])
        expected_tools = [
            "classify_manufacturing_intent",
            "analyze_data_requirements", 
            "build_optimization_model",
            "solve_optimization_problem",
            "manufacturing_optimization_workflow",
            "manufacturing_tools_status"
        ]
        
        validation_results['tools_available'] = all(tool in tools_available for tool in expected_tools)
        
        # Check manufacturing domain
        message = output.get('message', '')
        validation_results['manufacturing_domain'] = 'manufacturing' in message.lower()
        
        # Check response format
        validation_results['response_format'] = all(key in output for key in [
            'message', 'tools_available', 'server_ready', 'timestamp', 'model'
        ])
        
        # Check branding
        model_name = output.get('model', '')
        validation_results['branding_correct'] = 'dcisionai-manufacturing' in model_name
        
        # Check server readiness
        validation_results['server_ready'] = output.get('server_ready', False)
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
    
    return validation_results

def test_manufacturing_scenarios():
    """Test comprehensive manufacturing optimization scenarios"""
    
    # Real manufacturing optimization scenarios
    test_scenarios = [
        {
            'name': 'Production Line Optimization',
            'prompt': """I need to optimize my automotive production line for maximum efficiency. 
            We have 3 assembly stations with different processing times and quality metrics. 
            Station A takes 45 minutes with 98% quality, Station B takes 38 minutes with 95% quality, 
            and Station C takes 52 minutes with 99% quality. We need to process 500 units per day 
            while maintaining overall quality above 97%. Can you help me:
            1. Classify the optimization intent
            2. Analyze what data we need
            3. Build an optimization model
            4. Solve for the best configuration
            5. Orchestrate the workflow
            6. Monitor the solution status""",
            'expected_tools': ['classify_manufacturing_intent', 'analyze_data_requirements', 'build_optimization_model', 'solve_optimization_problem', 'manufacturing_optimization_workflow', 'manufacturing_tools_status']
        },
        {
            'name': 'Supply Chain Optimization',
            'prompt': """Our manufacturing supply chain needs optimization. We have 5 suppliers 
            with different lead times, costs, and reliability scores. Supplier A: 7 days, $100/unit, 95% reliability. 
            Supplier B: 5 days, $120/unit, 98% reliability. Supplier C: 10 days, $90/unit, 92% reliability. 
            Supplier D: 3 days, $150/unit, 99% reliability. Supplier E: 8 days, $110/unit, 96% reliability. 
            We need to minimize total cost while maintaining 97%+ reliability and max 7-day lead time. 
            Please use all available tools to solve this optimization problem.""",
            'expected_tools': ['classify_manufacturing_intent', 'analyze_data_requirements', 'build_optimization_model', 'solve_optimization_problem', 'manufacturing_optimization_workflow', 'manufacturing_tools_status']
        },
        {
            'name': 'Quality Control Analysis',
            'prompt': """We're experiencing quality issues in our electronics manufacturing process. 
            Current defect rate is 3.2% which is above our target of 1.5%. We have data on:
            - Temperature variations (180-220°C, target 200°C)
            - Humidity levels (40-60%, target 50%)
            - Component placement accuracy (98.5% current, 99.5% target)
            - Solder paste application (95% current, 98% target)
            - Inspection results from 3 different quality checkpoints
            
            Please analyze this manufacturing quality problem using all available tools 
            and provide an optimization solution to reduce defects to target levels.""",
            'expected_tools': ['classify_manufacturing_intent', 'analyze_data_requirements', 'build_optimization_model', 'solve_optimization_problem', 'manufacturing_optimization_workflow', 'manufacturing_tools_status']
        }
    ]
    
    return test_scenarios

def run_performance_test():
    """Run comprehensive performance test"""
    logger.info("🚀 Starting DcisionAI Manufacturing Performance Test")
    logger.info("=" * 60)
    
    # Setup AWS client
    client = setup_aws_client()
    
    # Get test scenarios
    test_scenarios = test_manufacturing_scenarios()
    
    # Performance metrics
    performance_metrics = {
        'total_tests': len(test_scenarios),
        'successful_tests': 0,
        'failed_tests': 0,
        'average_response_time': 0,
        'total_response_time': 0,
        'validation_results': [],
        'detailed_results': []
    }
    
    logger.info(f"📊 Testing {len(test_scenarios)} manufacturing scenarios")
    logger.info("=" * 60)
    
    for i, scenario in enumerate(test_scenarios, 1):
        logger.info(f"\n🧪 Test {i}/{len(test_scenarios)}: {scenario['name']}")
        logger.info("-" * 40)
        
        # Create unique session ID
        session_id = f"dcisionai-manufacturing-perf-{uuid.uuid4().hex[:8]}-{int(time.time())}"
        
        # Invoke agent
        result = invoke_manufacturing_agent(client, scenario['prompt'], session_id)
        
        if result['success']:
            performance_metrics['successful_tests'] += 1
            performance_metrics['total_response_time'] += result['response_time']
            
            # Validate response
            validation = validate_manufacturing_response(result['response'])
            performance_metrics['validation_results'].append(validation)
            
            # Log results
            logger.info(f"✅ Response Time: {result['response_time']:.2f}s")
            logger.info(f"✅ Tools Available: {validation['tools_available']}")
            logger.info(f"✅ Manufacturing Domain: {validation['manufacturing_domain']}")
            logger.info(f"✅ Response Format: {validation['response_format']}")
            logger.info(f"✅ Branding Correct: {validation['branding_correct']}")
            logger.info(f"✅ Server Ready: {validation['server_ready']}")
            
            # Log response summary
            output = result['response'].get('output', {})
            tools_available = output.get('tools_available', [])
            logger.info(f"🛠️ Tools Found: {len(tools_available)}/6")
            logger.info(f"📝 Message: {output.get('message', '')[:100]}...")
            
        else:
            performance_metrics['failed_tests'] += 1
            logger.error(f"❌ Test Failed: {result['error']}")
        
        # Store detailed result
        performance_metrics['detailed_results'].append({
            'scenario': scenario['name'],
            'result': result,
            'validation': validation if result['success'] else None
        })
        
        # Wait between tests
        if i < len(test_scenarios):
            logger.info("⏳ Waiting 5 seconds before next test...")
            time.sleep(5)
    
    # Calculate final metrics
    if performance_metrics['successful_tests'] > 0:
        performance_metrics['average_response_time'] = performance_metrics['total_response_time'] / performance_metrics['successful_tests']
    
    # Generate performance report
    generate_performance_report(performance_metrics)
    
    return performance_metrics

def generate_performance_report(metrics: Dict[str, Any]):
    """Generate comprehensive performance report"""
    logger.info("\n" + "=" * 60)
    logger.info("📊 DcisionAI Manufacturing Performance Report")
    logger.info("=" * 60)
    
    # Overall metrics
    logger.info(f"🎯 Total Tests: {metrics['total_tests']}")
    logger.info(f"✅ Successful: {metrics['successful_tests']}")
    logger.info(f"❌ Failed: {metrics['failed_tests']}")
    logger.info(f"📈 Success Rate: {(metrics['successful_tests']/metrics['total_tests']*100):.1f}%")
    
    if metrics['successful_tests'] > 0:
        logger.info(f"⏱️ Average Response Time: {metrics['average_response_time']:.2f}s")
        logger.info(f"⏱️ Total Response Time: {metrics['total_response_time']:.2f}s")
    
    # Validation summary
    if metrics['validation_results']:
        validation_summary = {
            'tools_available': sum(1 for v in metrics['validation_results'] if v['tools_available']),
            'manufacturing_domain': sum(1 for v in metrics['validation_results'] if v['manufacturing_domain']),
            'response_format': sum(1 for v in metrics['validation_results'] if v['response_format']),
            'branding_correct': sum(1 for v in metrics['validation_results'] if v['branding_correct']),
            'server_ready': sum(1 for v in metrics['validation_results'] if v['server_ready'])
        }
        
        logger.info("\n🔍 Validation Summary:")
        logger.info(f"   Tools Available: {validation_summary['tools_available']}/{metrics['successful_tests']}")
        logger.info(f"   Manufacturing Domain: {validation_summary['manufacturing_domain']}/{metrics['successful_tests']}")
        logger.info(f"   Response Format: {validation_summary['response_format']}/{metrics['successful_tests']}")
        logger.info(f"   Branding Correct: {validation_summary['branding_correct']}/{metrics['successful_tests']}")
        logger.info(f"   Server Ready: {validation_summary['server_ready']}/{metrics['successful_tests']}")
    
    # Detailed results
    logger.info("\n📋 Detailed Results:")
    for i, result in enumerate(metrics['detailed_results'], 1):
        logger.info(f"\n   Test {i}: {result['scenario']}")
        if result['result']['success']:
            logger.info(f"      ✅ Response Time: {result['result']['response_time']:.2f}s")
            logger.info(f"      ✅ Tools: {len(result['result']['response'].get('output', {}).get('tools_available', []))}/6")
        else:
            logger.info(f"      ❌ Error: {result['result']['error']}")
    
    # Save detailed report to file
    report_file = PROJECT_ROOT / "manufacturing_performance_report.json"
    with open(report_file, 'w') as f:
        json.dump(metrics, f, indent=2, default=str)
    
    logger.info(f"\n📄 Detailed report saved to: {report_file}")
    logger.info("🎉 Performance testing completed!")

if __name__ == "__main__":
    try:
        performance_metrics = run_performance_test()
        sys.exit(0 if performance_metrics['failed_tests'] == 0 else 1)
    except Exception as e:
        logger.error(f"❌ Performance test failed: {e}")
        sys.exit(1)
