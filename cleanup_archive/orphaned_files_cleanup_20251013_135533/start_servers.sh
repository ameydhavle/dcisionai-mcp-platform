#!/bin/bash

echo "🚀 Starting DcisionAI Platform Servers..."

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $1 is already in use"
        return 1
    else
        echo "Port $1 is available"
        return 0
    fi
}

# Start MCP Server
echo "📡 Starting MCP Server on port 8000..."
cd dcisionai-mcp-manufacturing
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Start MCP server in background
python mcp_server.py &
MCP_PID=$!
echo "✅ MCP Server started with PID: $MCP_PID"

# Wait a moment for MCP server to start
sleep 3

# Start Backend Server
echo "🔧 Starting Backend Server on port 5001..."
cd ../aws-deployment/frontend/backend
python3 app.py &
BACKEND_PID=$!
echo "✅ Backend Server started with PID: $BACKEND_PID"

# Wait a moment for backend server to start
sleep 3

# Check if servers are running
echo "🔍 Checking server status..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ MCP Server is running on http://localhost:8000"
else
    echo "❌ MCP Server failed to start"
fi

if curl -s http://localhost:5001/health > /dev/null; then
    echo "✅ Backend Server is running on http://localhost:5001"
else
    echo "❌ Backend Server failed to start"
fi

echo ""
echo "🎉 Servers are starting up!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:5001"
echo "📡 MCP Server: http://localhost:8000"
echo ""
echo "To stop servers, run: kill $MCP_PID $BACKEND_PID"
echo "Or press Ctrl+C to stop this script"

# Keep script running
wait
