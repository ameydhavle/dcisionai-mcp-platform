#!/bin/bash
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
