#!/usr/bin/env python3
"""
Deploy DcisionAI Manufacturing Agent - Intent + Data to AgentCore
================================================================

Incremental testing deployment with Intent and Data tools enabled.
"""

import subprocess
import time
import json
from datetime import datetime

def run_command(command: str, description: str) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"🔄 {description}...")
    print(f"   Command: {command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
    else:
        print(f"❌ {description} failed")
        print(f"   Error: {result.stderr.strip()}")
        raise RuntimeError(f"{description} failed: {result.stderr.strip()}")
    
    return result

def deploy_agentcore():
    """Deploy the complete DcisionAI Manufacturing MCP Server to AgentCore."""
    print("🚀 DEPLOYING DcisionAI Manufacturing MCP Server")
    print("=" * 60)
    
    # Configuration
    region = "us-east-1"
    account_id = "808953421331"
    ecr_repo = f"{account_id}.dkr.ecr.{region}.amazonaws.com/dcisionai-manufacturing-agent"
    
    # Generate unique agent runtime name
    timestamp = int(time.time())
    unique_name = f"DcisionAI_Manufacturing_MCP_{timestamp}"
    
    print(f"📋 Configuration:")
    print(f"   Region: {region}")
    print(f"   Account ID: {account_id}")
    print(f"   ECR Repository: {ecr_repo}")
    print(f"   Agent Runtime Name: {unique_name}")
    print()
    
    try:
        # Step 1: Authenticate with ECR
        auth_command = f"aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {account_id}.dkr.ecr.{region}.amazonaws.com"
        run_command(auth_command, "ECR authentication")
        
        # Step 2: Build Docker image
        build_command = f"docker build -f Dockerfile.DcisionAI_Manufacturing_MCP -t {ecr_repo}:latest ."
        run_command(build_command, "Docker build")
        
        # Step 3: Push to ECR
        push_command = f"docker push {ecr_repo}:latest"
        run_command(push_command, "ECR push")
        
        # Step 4: Deploy to AgentCore
        role_arn = "arn:aws:iam::808953421331:role/AmazonBedrockAgentCoreSDKRuntime-us-east-1-3bddb2550f"
        
        deploy_command = f"""aws bedrock-agentcore-control create-agent-runtime \
            --agent-runtime-name "{unique_name}" \
            --agent-runtime-artifact '{{"containerConfiguration": {{"containerUri": "{ecr_repo}:latest"}}}}' \
            --network-configuration '{{"networkMode": "PUBLIC"}}' \
            --role-arn "{role_arn}" \
            --region {region}"""
        
        result = run_command(deploy_command, "AgentCore deployment")
        
        # Extract ARN and Runtime ID from response
        response_data = json.loads(result.stdout)
        agent_runtime_arn = response_data.get("agentRuntimeArn")
        agent_runtime_id = response_data.get("agentRuntimeId")
        
        if not agent_runtime_arn or not agent_runtime_id:
            raise RuntimeError("Failed to extract agent runtime ARN or ID from response")
        
        print(f"🎉 AgentCore deployment initiated successfully!")
        print(f"📋 Agent Runtime ARN: {agent_runtime_arn}")
        print(f"📋 Agent Runtime ID: {agent_runtime_id}")
        print()
        
        # Step 5: Wait for deployment to complete
        print("⏳ Waiting for AgentCore runtime to be ready...")
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            print(f"   Checking status (attempt {attempt}/{max_attempts})...")
            
            try:
                status_command = f"aws bedrock-agentcore-control get-agent-runtime --agent-runtime-id {agent_runtime_id} --region {region}"
                status_result = subprocess.run(status_command, shell=True, capture_output=True, text=True)
                
                if status_result.returncode == 0:
                    status_data = json.loads(status_result.stdout)
                    status = status_data.get("agentRuntime", {}).get("status")
                    
                    print(f"   Current status: {status}")
                    
                    if status == "READY":
                        print("✅ AgentCore runtime is ready!")
                        break
                    elif status == "FAILED":
                        raise RuntimeError("AgentCore runtime deployment failed")
                    elif status in ["CREATING", "UPDATING"]:
                        print("   Still creating/updating, waiting...")
                        time.sleep(30)
                    else:
                        print(f"   Unknown status: {status}, waiting...")
                        time.sleep(30)
                else:
                    print(f"   Status check failed: {status_result.stderr.strip()}")
                    time.sleep(30)
                    
            except Exception as e:
                print(f"   Status check error: {e}")
                time.sleep(30)
        
        if attempt >= max_attempts:
            print("⚠️ Timeout waiting for AgentCore runtime to be ready")
            print("   You can check the status manually with:")
            print(f"   aws bedrock-agentcore-control get-agent-runtime --agent-runtime-id {agent_runtime_id} --region {region}")
        else:
            print("🎉 Deployment completed successfully!")
            print(f"📋 Agent Runtime ARN: {agent_runtime_arn}")
            print(f"📋 Agent Runtime Name: {unique_name}")
            print()
            print("🧪 You can now test the runtime with:")
            print(f"   python tests/agentcore/test_agentcore_intent_data.py")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        raise

def main():
    """Main deployment function."""
    print(f"🕐 Deployment started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    deploy_agentcore()
    
    print(f"\n✅ Deployment process completed!")

if __name__ == "__main__":
    main()
