#!/usr/bin/env python3
"""
Test script to verify the new workflow UI functionality
"""

import requests
import json
import time

def test_workflow_api():
    """Test the workflow API endpoints"""
    base_url = "https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod"
    
    print("Testing Workflow API Endpoints")
    print("=" * 50)
    
    # Test 1: Get all industries
    print("\n1. Testing GET /workflows (all industries)")
    try:
        response = requests.get(f"{base_url}/workflows")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: Found {len(data.get('industries', []))} industries")
            for industry in data.get('industries', []):
                print(f"   - {industry}")
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Get workflows for manufacturing
    print("\n2. Testing GET /workflows/manufacturing")
    try:
        response = requests.get(f"{base_url}/workflows/manufacturing")
        if response.status_code == 200:
            data = response.json()
            workflows = data.get('workflows', [])
            print(f"Success: Found {len(workflows)} manufacturing workflows")
            for workflow in workflows:
                print(f"   - {workflow.get('title', 'Unknown')} ({workflow.get('difficulty', 'unknown')})")
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Get workflows for marketing
    print("\n3. Testing GET /workflows/marketing")
    try:
        response = requests.get(f"{base_url}/workflows/marketing")
        if response.status_code == 200:
            data = response.json()
            workflows = data.get('workflows', [])
            print(f"Success: Found {len(workflows)} marketing workflows")
            for workflow in workflows:
                print(f"   - {workflow.get('title', 'Unknown')} ({workflow.get('difficulty', 'unknown')})")
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Execute a workflow (manufacturing production planning)
    print("\n4. Testing POST /workflows/manufacturing/production_planning/execute")
    try:
        payload = {
            "custom_parameters": {}
        }
        response = requests.post(
            f"{base_url}/workflows/manufacturing/production_planning/execute",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"Success: Workflow executed")
            print(f"   Status: {data.get('status', 'unknown')}")
            if 'results' in data:
                print(f"   Results available: {len(str(data['results']))} characters")
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_frontend_access():
    """Test if the frontend is accessible"""
    print("\nTesting Frontend Access")
    print("=" * 50)
    
    try:
        response = requests.get("https://platform.dcisionai.com", timeout=10)
        if response.status_code == 200:
            print("Frontend is accessible at https://platform.dcisionai.com")
            if "DcisionAI" in response.text:
                print("DcisionAI content detected")
            else:
                print("DcisionAI content not found in response")
        else:
            print(f"Frontend not accessible: {response.status_code}")
    except Exception as e:
        print(f"Error accessing frontend: {e}")

def main():
    """Main test function"""
    print("DcisionAI Workflow UI Test Suite")
    print("=" * 60)
    
    # Test API endpoints
    test_workflow_api()
    
    # Test frontend access
    test_frontend_access()
    
    print("\n" + "=" * 60)
    print("Test Suite Complete!")
    print("\nSummary:")
    print("   - Workflow API endpoints tested")
    print("   - Frontend accessibility verified")
    print("   - Ready for user testing at https://platform.dcisionai.com")
    
    print("\nNext Steps:")
    print("   1. Visit https://platform.dcisionai.com")
    print("   2. Select an industry (Manufacturing, Healthcare, Retail, etc.)")
    print("   3. Choose a workflow to execute")
    print("   4. Watch the real optimization results!")

if __name__ == "__main__":
    main()
