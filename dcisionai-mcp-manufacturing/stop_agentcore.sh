#!/bin/bash
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
