#!/usr/bin/env python3
"""
Deploy DcisionAI Manufacturing Agent to AgentCore using SDK Integration
Based on official Strands AgentCore deployment guide (Option A)
"""

import boto3
import subprocess
import json
import time
import sys
import os
from datetime import datetime

# Configuration
ACCOUNT_ID = "808953421331"
REGION = "us-east-1"
REPOSITORY_NAME = "dcisionai-manufacturing-agent"
IMAGE_TAG = "latest"
AGENT_RUNTIME_NAME = "DcisionAI_Manufacturing_SDK"
ROLE_ARN = f"arn:aws:iam::{ACCOUNT_ID}:role/AgentRuntimeRole"

# ECR repository URI
ECR_URI = f"{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com"
IMAGE_URI = f"{ECR_URI}/{REPOSITORY_NAME}:{IMAGE_TAG}"

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n🔄 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def main():
    print("🚀 Deploying DcisionAI Manufacturing Agent to AgentCore (SDK Integration)")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏗️ Agent Runtime Name: {AGENT_RUNTIME_NAME}")
    print(f"🐳 Docker Image: {IMAGE_URI}")
    
    # Step 1: Login to ECR
    run_command(
        f"aws ecr get-login-password --region {REGION} | docker login --username AWS --password-stdin {ECR_URI}",
        "Logging into ECR"
    )
    
    # Step 2: Build Docker image
    run_command(
        f"docker buildx build --platform linux/arm64 -t {IMAGE_URI} -f Dockerfile.AgentCore_SDK . --push",
        "Building and pushing Docker image"
    )
    
    # Step 3: Verify image exists
    run_command(
        f"aws ecr describe-images --repository-name {REPOSITORY_NAME} --region {REGION}",
        "Verifying ECR image"
    )
    
    # Step 4: Create AgentCore runtime
    print("\n🔄 Creating AgentCore runtime...")
    
    client = boto3.client('bedrock-agentcore-control', region_name=REGION)
    
    try:
        response = client.create_agent_runtime(
            agentRuntimeName=AGENT_RUNTIME_NAME,
            agentRuntimeArtifact={
                'containerConfiguration': {
                    'containerUri': IMAGE_URI
                }
            },
            networkConfiguration={"networkMode": "PUBLIC"},
            roleArn=ROLE_ARN
        )
        
        agent_runtime_arn = response['agentRuntimeArn']
        print(f"✅ AgentCore runtime created successfully!")
        print(f"📋 Agent Runtime ARN: {agent_runtime_arn}")
        print(f"📊 Status: {response['status']}")
        
        # Step 5: Wait for runtime to be ready
        print("\n⏳ Waiting for AgentCore runtime to be ready...")
        
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            try:
                status_response = client.get_agent_runtime(
                    agentRuntimeArn=agent_runtime_arn
                )
                
                status = status_response['agentRuntime']['status']
                print(f"📊 Current status: {status}")
                
                if status == 'ACTIVE':
                    print("✅ AgentCore runtime is now ACTIVE!")
                    break
                elif status in ['FAILED', 'DELETED']:
                    print(f"❌ AgentCore runtime failed with status: {status}")
                    sys.exit(1)
                else:
                    print(f"⏳ Still waiting... (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(10)
                    attempt += 1
                    
            except Exception as e:
                print(f"⚠️ Error checking status: {e}")
                time.sleep(10)
                attempt += 1
        
        if attempt >= max_attempts:
            print("❌ Timeout waiting for AgentCore runtime to be ready")
            sys.exit(1)
        
        # Step 6: Save deployment info
        deployment_info = {
            "deployment_time": datetime.now().isoformat(),
            "agent_runtime_name": AGENT_RUNTIME_NAME,
            "agent_runtime_arn": agent_runtime_arn,
            "image_uri": IMAGE_URI,
            "region": REGION,
            "status": "ACTIVE"
        }
        
        with open("agentcore_sdk_deployment.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"\n📄 Deployment info saved to: agentcore_sdk_deployment.json")
        
        # Step 7: Test the agent
        print("\n🧪 Testing the deployed agent...")
        
        test_script = f"""
import boto3
import json

# Test the deployed agent
client = boto3.client('bedrock-agentcore', region_name='{REGION}')

payload = json.dumps({{
    "input": {{
        "prompt": "I need to optimize my manufacturing production schedule for 3 products with different demand patterns and capacity constraints."
    }}
}})

response = client.invoke_agent_runtime(
    agentRuntimeArn='{agent_runtime_arn}',
    runtimeSessionId='test-session-{datetime.now().strftime("%Y%m%d%H%M%S")}',
    payload=payload,
    qualifier="DEFAULT"
)

response_body = response['response'].read()
response_data = json.loads(response_body)
print("Agent Response:", json.dumps(response_data, indent=2))
"""
        
        with open("test_agentcore_sdk.py", "w") as f:
            f.write(test_script)
        
        print("✅ Test script created: test_agentcore_sdk.py")
        print(f"🔗 Run: python test_agentcore_sdk.py")
        
        print(f"\n🎉 Deployment completed successfully!")
        print(f"📋 Agent Runtime ARN: {agent_runtime_arn}")
        print(f"🧪 Test with: python test_agentcore_sdk.py")
        
    except Exception as e:
        print(f"❌ Failed to create AgentCore runtime: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
