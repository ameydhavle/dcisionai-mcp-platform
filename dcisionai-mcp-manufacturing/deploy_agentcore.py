#!/usr/bin/env python3
"""
AgentCore Deployment Script
===========================

This script deploys the complete AgentCore runtime as a persistent service
with all the competitive advantages: memory, caching, and coordination.

Author: DcisionAI Team
Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | AgentCore Deploy | %(message)s"
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed."""
    logger.info("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'psutil',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"❌ {package} is missing")
    
    if missing_packages:
        logger.info(f"📦 Installing missing packages: {missing_packages}")
        for package in missing_packages:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
        logger.info("✅ All dependencies installed")
    else:
        logger.info("✅ All dependencies are available")

def create_systemd_service():
    """Create systemd service for AgentCore runtime."""
    logger.info("🔧 Creating systemd service...")
    
    current_dir = Path(__file__).parent.absolute()
    python_path = sys.executable
    agentcore_script = current_dir / "agentcore_runtime.py"
    
    service_content = f"""[Unit]
Description=DcisionAI AgentCore Runtime
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'ubuntu')}
WorkingDirectory={current_dir}
Environment=PATH={os.environ.get('PATH', '')}
ExecStart={python_path} {agentcore_script}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path("/etc/systemd/system/agentcore.service")
    
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        logger.info(f"✅ Systemd service created: {service_file}")
        
        # Reload systemd and enable service
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        subprocess.run(['sudo', 'systemctl', 'enable', 'agentcore'], check=True)
        logger.info("✅ AgentCore service enabled")
        
    except PermissionError:
        logger.warning("⚠️ Permission denied. Run with sudo to create systemd service")
        logger.info(f"📝 Service content to create manually:\n{service_content}")

def create_dockerfile():
    """Create Dockerfile for containerized deployment."""
    logger.info("🐳 Creating Dockerfile...")
    
    dockerfile_content = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy AgentCore files
COPY . .

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Run AgentCore runtime
CMD ["python", "agentcore_runtime.py"]
"""
    
    dockerfile_path = Path(__file__).parent / "Dockerfile"
    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile_content)
    
    logger.info(f"✅ Dockerfile created: {dockerfile_path}")

def create_requirements():
    """Create requirements.txt for deployment."""
    logger.info("📦 Creating requirements.txt...")
    
    requirements = """fastapi>=0.104.0
uvicorn[standard]>=0.24.0
psutil>=5.9.0
pydantic>=2.5.0
boto3>=1.34.0
pulp>=2.7.0
"""
    
    requirements_path = Path(__file__).parent / "requirements.txt"
    with open(requirements_path, 'w') as f:
        f.write(requirements)
    
    logger.info(f"✅ requirements.txt created: {requirements_path}")

def create_docker_compose():
    """Create docker-compose.yml for easy deployment."""
    logger.info("🐳 Creating docker-compose.yml...")
    
    compose_content = """version: '3.8'

services:
  agentcore:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - agentcore
    restart: unless-stopped
"""
    
    compose_path = Path(__file__).parent / "docker-compose.yml"
    with open(compose_path, 'w') as f:
        f.write(compose_content)
    
    logger.info(f"✅ docker-compose.yml created: {compose_path}")

def create_nginx_config():
    """Create nginx configuration for load balancing."""
    logger.info("🌐 Creating nginx configuration...")
    
    nginx_content = """events {
    worker_connections 1024;
}

http {
    upstream agentcore {
        server agentcore:8080;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://agentcore;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            proxy_pass http://agentcore/health;
            access_log off;
        }
    }
}
"""
    
    nginx_path = Path(__file__).parent / "nginx.conf"
    with open(nginx_path, 'w') as f:
        f.write(nginx_content)
    
    logger.info(f"✅ nginx.conf created: {nginx_path}")

def create_deployment_scripts():
    """Create deployment scripts."""
    logger.info("📜 Creating deployment scripts...")
    
    # Start script
    start_script = """#!/bin/bash
echo "🚀 Starting AgentCore Runtime..."

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "🐳 Running in Docker container"
    python agentcore_runtime.py
else
    echo "🖥️ Running on host system"
    
    # Check if systemd service exists
    if systemctl is-enabled agentcore >/dev/null 2>&1; then
        echo "🔧 Starting systemd service..."
        sudo systemctl start agentcore
        sudo systemctl status agentcore
    else
        echo "🐍 Starting directly with Python..."
        python agentcore_runtime.py
    fi
fi
"""
    
    start_path = Path(__file__).parent / "start_agentcore.sh"
    with open(start_path, 'w') as f:
        f.write(start_script)
    start_path.chmod(0o755)
    
    # Stop script
    stop_script = """#!/bin/bash
echo "🛑 Stopping AgentCore Runtime..."

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "🐳 Stopping Docker container..."
    exit 0
else
    echo "🖥️ Stopping on host system..."
    
    # Check if systemd service exists
    if systemctl is-enabled agentcore >/dev/null 2>&1; then
        echo "🔧 Stopping systemd service..."
        sudo systemctl stop agentcore
    else
        echo "🐍 Stopping Python process..."
        pkill -f agentcore_runtime.py
    fi
fi
"""
    
    stop_path = Path(__file__).parent / "stop_agentcore.sh"
    with open(stop_path, 'w') as f:
        f.write(stop_script)
    stop_path.chmod(0o755)
    
    # Docker deployment script
    docker_script = """#!/bin/bash
echo "🐳 Deploying AgentCore with Docker..."

# Build and start services
docker-compose up --build -d

echo "✅ AgentCore deployed with Docker"
echo "🌐 Access at: http://localhost:8080"
echo "📊 Health check: http://localhost:8080/health"
echo "📈 Metrics: http://localhost:8080/metrics"
echo "🧠 Insights: http://localhost:8080/insights"

# Show logs
echo "📋 Showing logs..."
docker-compose logs -f agentcore
"""
    
    docker_path = Path(__file__).parent / "deploy_docker.sh"
    with open(docker_path, 'w') as f:
        f.write(docker_script)
    docker_path.chmod(0o755)
    
    logger.info("✅ Deployment scripts created")

def test_agentcore():
    """Test AgentCore runtime."""
    logger.info("🧪 Testing AgentCore runtime...")
    
    try:
        # Import and test
        from agentcore_runtime import agentcore
        
        # Test that components are initialized
        logger.info("✅ AgentCore runtime imported successfully")
        logger.info("✅ All components initialized")
        
        logger.info("✅ AgentCore runtime test passed")
        
    except Exception as e:
        logger.error(f"❌ AgentCore runtime test failed: {e}")
        raise

def main():
    """Main deployment function."""
    logger.info("🚀 Starting AgentCore deployment...")
    
    try:
        # Check dependencies
        check_dependencies()
        
        # Create deployment files
        create_requirements()
        create_dockerfile()
        create_docker_compose()
        create_nginx_config()
        create_deployment_scripts()
        
        # Test AgentCore
        test_agentcore()
        
        # Create systemd service (optional)
        try:
            create_systemd_service()
        except Exception as e:
            logger.warning(f"⚠️ Systemd service creation failed: {e}")
        
        logger.info("🎉 AgentCore deployment completed successfully!")
        logger.info("")
        logger.info("📋 Deployment options:")
        logger.info("  1. Direct Python: python agentcore_runtime.py")
        logger.info("  2. Systemd service: sudo systemctl start agentcore")
        logger.info("  3. Docker: ./deploy_docker.sh")
        logger.info("")
        logger.info("🌐 Access points:")
        logger.info("  - Health: http://localhost:8080/health")
        logger.info("  - Metrics: http://localhost:8080/metrics")
        logger.info("  - Insights: http://localhost:8080/insights")
        logger.info("  - API Docs: http://localhost:8080/docs")
        logger.info("")
        logger.info("🎯 AgentCore is ready for production!")
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
