#!/usr/bin/env python3
"""
Create Lambda Package with Dependencies
======================================

This script creates a proper Lambda deployment package with all dependencies
for the Bedrock AgentCore proxy.

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import os
import subprocess
import zipfile
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | Lambda Package | %(message)s"
)
logger = logging.getLogger(__name__)

def create_lambda_package():
    """Create a Lambda package with all dependencies."""
    logger.info("📦 Creating Lambda package with dependencies...")
    
    # Create package directory
    package_dir = "lambda_package"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # Copy the proxy file
    with open("bedrock_agentcore_proxy.py", "r") as src:
        with open(f"{package_dir}/lambda_function.py", "w") as dst:
            # Modify the file to work as a Lambda function
            content = src.read()
            # Replace the uvicorn.run() call with Lambda handler
            content = content.replace(
                'if __name__ == "__main__":\n    import uvicorn\n    logger.info("🚀 Starting Bedrock AgentCore Proxy...")\n    logger.info(f"🎯 Bedrock AgentCore ARN: {BEDROCK_AGENTCORE_ARN}")\n    logger.info("🌐 Proxy will handle AWS authentication for frontend")\n    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="info")',
                '''# Lambda handler
def lambda_handler(event, context):
    """Lambda handler for Bedrock AgentCore proxy."""
    from mangum import Mangum
    handler = Mangum(app)
    return handler(event, context)

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Bedrock AgentCore Proxy...")
    logger.info(f"🎯 Bedrock AgentCore ARN: {BEDROCK_AGENTCORE_ARN}")
    logger.info("🌐 Proxy will handle AWS authentication for frontend")
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="info")'''
            )
            dst.write(content)
    
    # Install dependencies
    logger.info("📥 Installing dependencies...")
    requirements = [
        "fastapi==0.104.1",
        "mangum==0.17.0",
        "boto3==1.34.0",
        "httpx==0.25.0",
        "pydantic==1.10.24",
        "starlette==0.27.0",
        "typing_extensions==4.8.0",
        "requests==2.31.0"
    ]
    
    for requirement in requirements:
        logger.info(f"Installing {requirement}...")
        subprocess.run([
            "pip", "install", requirement, 
            "-t", package_dir, 
            "--platform", "linux_x86_64",
            "--implementation", "cp",
            "--python-version", "3.11",
            "--only-binary=:all:",
            "--upgrade"
        ], check=True)
    
    # Create the zip file
    zip_filename = "bedrock_agentcore_proxy_with_deps.zip"
    logger.info(f"📦 Creating zip file: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    # Clean up
    shutil.rmtree(package_dir)
    
    logger.info(f"✅ Lambda package created: {zip_filename}")
    return zip_filename

if __name__ == "__main__":
    create_lambda_package()
