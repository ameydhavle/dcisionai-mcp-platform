#!/bin/bash

# DcisionAI Manufacturing Optimizer - Demo Startup Script
# =====================================================

echo "Starting DcisionAI Manufacturing Optimizer Demo"
echo "=================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js not found. Please install Node.js 16+ and try again."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.11+ and try again."
    exit 1
fi

# Check if MCP server is running
echo "Checking MCP server status..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "MCP server is running on localhost:8000"
else
    echo "Warning: MCP server not running. Please start it first:"
    echo "   cd .. && source venv/bin/activate && python mcp_server.py"
    echo ""
    echo "   Or run this script from the main dcisionai-mcp-manufacturing directory"
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing dependencies..."
if [ ! -d "node_modules" ]; then
    echo "Installing React dependencies..."
    npm install
fi

if [ ! -d "backend/venv" ]; then
    echo "Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Start backend server
echo "Starting backend server..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend server to start..."
sleep 3

# Check if backend is running
if curl -s http://localhost:5000/health > /dev/null; then
    echo "Backend server started on localhost:5000"
else
    echo "Error: Failed to start backend server"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start React frontend
echo "Starting React frontend..."
echo ""
echo "Demo is starting up!"
echo "   Web App: http://localhost:3000"
echo "   Backend: http://localhost:5000"
echo "   MCP Server: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Start React app
npm start

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    echo "All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for React to start
wait
