#!/usr/bin/env python3
"""
Deploy Fixed Lambda with Real PuLP Solver
==========================================

Deploy the enhanced Lambda function with REAL mathematical optimization using PuLP.
This fixes the "unbounded" error by replacing AI simulation with actual mathematical solving.
"""

import boto3
import zipfile
import os
import json
import time
from pathlib import Path

# Configuration
LAMBDA_FUNCTION_NAME = 'dcisionai-streaming-mcp-manufacturing'
REGION = 'us-east-1'
LAMBDA_FILE = 'enhanced_streaming_lambda.py'

def create_lambda_package():
    """Create Lambda deployment package with PuLP."""
    print("📦 Creating Lambda deployment package...")
    
    # Create temporary directory
    temp_dir = Path('/tmp/lambda_package')
    temp_dir.mkdir(exist_ok=True)
    
    # Copy Lambda function
    lambda_path = Path(LAMBDA_FILE)
    if not lambda_path.exists():
        print(f"❌ Lambda file not found: {LAMBDA_FILE}")
        return None
    
    # Copy to temp directory with correct name
    import shutil
    shutil.copy2(lambda_path, temp_dir / 'lambda_function.py')
    
    # Also copy with the original name for compatibility
    shutil.copy2(lambda_path, temp_dir / 'enhanced_streaming_lambda.py')
    
    # Install PuLP and dependencies
    print("🔧 Installing PuLP and dependencies...")
    import subprocess
    import sys
    
    # Install PuLP
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', 
        'pulp>=2.7.0', 
        'boto3>=1.34.0',
        '-t', str(temp_dir)
    ], check=True)
    
    # Create zip file
    zip_path = temp_dir / 'lambda_package.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file != 'lambda_package.zip':
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
    
    print(f"✅ Lambda package created: {zip_path}")
    return zip_path

def deploy_lambda(zip_path):
    """Deploy Lambda function."""
    print("🚀 Deploying Lambda function...")
    
    # Initialize Lambda client
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    # Read zip file
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    try:
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            ZipFile=zip_content
        )
        
        print(f"✅ Lambda function updated: {response['FunctionName']}")
        print(f"📊 Function ARN: {response['FunctionArn']}")
        print(f"⏱️  Last Modified: {response['LastModified']}")
        
        # Wait for update to complete
        print("⏳ Waiting for deployment to complete...")
        time.sleep(10)
        
        # Test the function
        print("🧪 Testing Lambda function...")
        test_response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'path': '/health',
                'httpMethod': 'GET'
            })
        )
        
        result = json.loads(test_response['Payload'].read())
        print(f"✅ Test result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

def main():
    """Main deployment function."""
    print("🚀 DcisionAI Lambda Deployment - Fixed with Real PuLP Solver")
    print("=" * 60)
    
    # Create package
    zip_path = create_lambda_package()
    if not zip_path:
        return False
    
    # Deploy
    success = deploy_lambda(zip_path)
    
    if success:
        print("\n🎉 Deployment successful!")
        print("✅ Lambda function now uses REAL PuLP mathematical solver")
        print("🔧 This fixes the 'unbounded' optimization errors")
        print("🌐 Test at: https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod/solve")
    else:
        print("\n❌ Deployment failed!")
        return False
    
    # Cleanup
    try:
        os.remove(zip_path)
        print("🧹 Cleaned up temporary files")
    except:
        pass
    
    return True

if __name__ == "__main__":
    main()
