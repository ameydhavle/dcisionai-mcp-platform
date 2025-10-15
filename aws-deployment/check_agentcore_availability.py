#!/usr/bin/env python3
"""
Check AgentCore Gateway Availability
==================================

This script checks if Amazon Bedrock AgentCore Gateway is available
in the current region and account.
"""

import boto3
import json
from datetime import datetime

def check_agentcore_availability():
    """Check if AgentCore Gateway is available."""
    print("🔍 Checking AgentCore Gateway Availability")
    print("=" * 50)
    
    try:
        # Check if the service is available
        gateway_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print("✅ AgentCore Gateway service is available")
        
        # Try to list gateways (this will fail if service is not available)
        try:
            response = gateway_client.list_gateways()
            print(f"✅ Can list gateways: {len(response.get('gateways', []))} found")
        except Exception as e:
            print(f"⚠️  Cannot list gateways: {e}")
        
        # Check account information
        sts_client = boto3.client('sts')
        account_info = sts_client.get_caller_identity()
        print(f"✅ Account ID: {account_info['Account']}")
        print(f"✅ Region: us-east-1")
        
        return True
        
    except Exception as e:
        print(f"❌ AgentCore Gateway service is not available: {e}")
        print("\nPossible reasons:")
        print("1. AgentCore Gateway is not available in us-east-1 region")
        print("2. Service is in preview and not enabled for your account")
        print("3. Insufficient permissions")
        print("4. Service is not yet available in your region")
        
        return False

def check_alternative_regions():
    """Check AgentCore Gateway availability in other regions."""
    print("\n🌍 Checking Alternative Regions")
    print("=" * 50)
    
    regions_to_check = ['us-west-2', 'eu-west-1', 'ap-southeast-1']
    
    for region in regions_to_check:
        try:
            gateway_client = boto3.client('bedrock-agentcore-control', region_name=region)
            print(f"✅ AgentCore Gateway available in {region}")
        except Exception as e:
            print(f"❌ AgentCore Gateway not available in {region}: {e}")

def main():
    """Main function to check AgentCore availability."""
    print("🚀 DcisionAI AgentCore Gateway Availability Check")
    print("=" * 60)
    
    # Check primary region
    is_available = check_agentcore_availability()
    
    if not is_available:
        # Check alternative regions
        check_alternative_regions()
        
        print("\n📋 Recommendations:")
        print("1. Wait for AgentCore Gateway to become available in your region")
        print("2. Use alternative optimization approaches (Lambda + Bedrock)")
        print("3. Consider using other agent frameworks (LangGraph, CrewAI)")
        print("4. Contact AWS support for early access")
    else:
        print("\n🎉 AgentCore Gateway is available! You can proceed with the setup.")

if __name__ == "__main__":
    main()
