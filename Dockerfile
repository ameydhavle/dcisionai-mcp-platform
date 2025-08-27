# DcisionAI MCP Server - Custom ARM64 Dockerfile for AgentCore
# Based on AWS AgentCore requirements: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-custom.html

# Use ARM64 Python base image (REQUIRED by Amazon Bedrock AgentCore)
FROM --platform=linux/arm64 python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    git \
    cmake \
    ninja-build \
    build-essential \
    pkg-config \
    wget \
    libblas-dev \
    liblapack-dev \
    libgfortran5 \
    libgomp1 \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.mcp.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.mcp.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO
ENV ENVIRONMENT=production
ENV AWS_REGION=us-east-1
ENV AGENTCORE_ENVIRONMENT=true
ENV BEDROCK_AGENTCORE_RUNTIME=true

# Expose port 8080 (REQUIRED by AgentCore)
EXPOSE 8080

# Health check for port 8080
HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=40s \
            --retries=3 \
            CMD curl -f http://localhost:8080/ping || exit 1

# Run the DcisionAI Manufacturing Agent (REQUIRED by AgentCore)
CMD ["python", "src/mcp_server/DcisionAI_Manufacturing_Agent.py"]
