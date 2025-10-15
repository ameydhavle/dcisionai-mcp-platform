#!/usr/bin/env python3
"""
Workflow Integration Example
===========================

Example showing how to integrate the workflow API with your application.
This demonstrates real workflow execution using the actual optimization engine.
"""

import requests
import json
from typing import Dict, Any, List

class DcisionAIWorkflowClient:
    """Client for interacting with DcisionAI workflow API."""
    
    def __init__(self, base_url: str = "https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod"):
        self.base_url = base_url
    
    def get_industries(self) -> List[str]:
        """Get list of available industries."""
        try:
            response = requests.get(f"{self.base_url}/workflows")
            data = response.json()
            
            if data.get('status') == 'success':
                return data.get('industries', [])
            else:
                print(f"Error getting industries: {data.get('error', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"Error getting industries: {e}")
            return []
    
    def get_workflows(self, industry: str) -> List[Dict[str, Any]]:
        """Get workflows for a specific industry."""
        try:
            response = requests.get(f"{self.base_url}/workflows/{industry}")
            data = response.json()
            
            if data.get('status') == 'success':
                return data.get('workflows', [])
            else:
                print(f"Error getting workflows for {industry}: {data.get('error', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"Error getting workflows: {e}")
            return []
    
    def get_workflow_details(self, industry: str, workflow_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific workflow."""
        try:
            response = requests.get(f"{self.base_url}/workflows/{industry}/{workflow_id}")
            data = response.json()
            
            if data.get('status') == 'success':
                return data.get('workflow', {})
            else:
                print(f"Error getting workflow details: {data.get('error', 'Unknown error')}")
                return {}
                
        except Exception as e:
            print(f"Error getting workflow details: {e}")
            return {}
    
    def execute_workflow(self, industry: str, workflow_id: str, custom_parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a predefined workflow with optional custom parameters."""
        try:
            payload = {
                "custom_parameters": custom_parameters or {}
            }
            
            response = requests.post(
                f"{self.base_url}/workflows/{industry}/{workflow_id}/execute",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            data = response.json()
            
            if data.get('status') == 'success':
                return data
            else:
                print(f"Error executing workflow: {data.get('error', 'Unknown error')}")
                return {}
                
        except Exception as e:
            print(f"Error executing workflow: {e}")
            return {}

def demonstrate_workflow_usage():
    """Demonstrate how to use the workflow API."""
    
    print("🚀 DcisionAI Workflow API Demonstration")
    print("=" * 50)
    
    # Initialize client
    client = DcisionAIWorkflowClient()
    
    # Step 1: Get available industries
    print("\n📋 Step 1: Getting available industries...")
    industries = client.get_industries()
    print(f"Available industries: {industries}")
    
    if not industries:
        print("❌ No industries available. Check your API connection.")
        return
    
    # Step 2: Get workflows for manufacturing industry
    print(f"\n🏭 Step 2: Getting workflows for manufacturing industry...")
    workflows = client.get_workflows('manufacturing')
    print(f"Found {len(workflows)} manufacturing workflows:")
    
    for workflow in workflows:
        print(f"  - {workflow['title']} ({workflow['difficulty']}, {workflow['estimated_time']})")
    
    if not workflows:
        print("❌ No workflows found for manufacturing industry.")
        return
    
    # Step 3: Get details for the first workflow
    first_workflow = workflows[0]
    print(f"\n🔍 Step 3: Getting details for '{first_workflow['title']}'...")
    
    workflow_details = client.get_workflow_details('manufacturing', first_workflow['id'])
    if workflow_details:
        print(f"Description: {workflow_details.get('description', 'N/A')}")
        print(f"Problem: {workflow_details.get('problem_description', 'N/A')[:100]}...")
    
    # Step 4: Execute the workflow
    print(f"\n⚡ Step 4: Executing workflow '{first_workflow['title']}'...")
    print("This will run the real 4-step optimization pipeline...")
    
    result = client.execute_workflow('manufacturing', first_workflow['id'])
    
    if result:
        print("✅ Workflow executed successfully!")
        
        # Display results
        workflow_info = result.get('workflow', {})
        pipeline = result.get('optimization_pipeline', {})
        
        print(f"\n📊 Results Summary:")
        print(f"  Workflow: {workflow_info.get('title', 'N/A')}")
        print(f"  Industry: {workflow_info.get('industry', 'N/A')}")
        print(f"  Category: {workflow_info.get('category', 'N/A')}")
        
        # Show optimization pipeline results
        if 'intent_classification' in pipeline:
            intent = pipeline['intent_classification'].get('result', {})
            print(f"  Intent: {intent.get('intent', 'N/A')} (confidence: {intent.get('confidence', 0):.2f})")
        
        if 'optimization_solution' in pipeline:
            solution = pipeline['optimization_solution'].get('result', {})
            print(f"  Status: {solution.get('status', 'N/A')}")
            print(f"  Objective Value: {solution.get('objective_value', 'N/A')}")
            print(f"  Solution: {solution.get('solution', {})}")
        
        execution_summary = result.get('execution_summary', {})
        print(f"  Real Optimization: {execution_summary.get('real_optimization', False)}")
        print(f"  Success: {execution_summary.get('success', False)}")
        
    else:
        print("❌ Workflow execution failed.")
    
    print(f"\n🎉 Demonstration completed!")

def test_all_industries():
    """Test workflows for all available industries."""
    
    print("\n🧪 Testing workflows for all industries...")
    print("=" * 50)
    
    client = DcisionAIWorkflowClient()
    industries = client.get_industries()
    
    for industry in industries:
        print(f"\n🏢 Testing {industry} industry...")
        workflows = client.get_workflows(industry)
        
        if workflows:
            print(f"  ✅ Found {len(workflows)} workflows")
            for workflow in workflows[:2]:  # Show first 2 workflows
                print(f"    - {workflow['title']} ({workflow['difficulty']})")
        else:
            print(f"  ❌ No workflows found")

if __name__ == "__main__":
    # Run the demonstration
    demonstrate_workflow_usage()
    
    # Test all industries
    test_all_industries()
    
    print("\n📚 Integration Notes:")
    print("1. All workflows use the real 4-step optimization pipeline")
    print("2. No mock data or canned responses - everything is genuine optimization")
    print("3. Results include intent classification, data analysis, model building, and solution")
    print("4. Custom parameters can be passed to modify workflow behavior")
    print("5. All workflows are industry-specific with realistic problem descriptions")
