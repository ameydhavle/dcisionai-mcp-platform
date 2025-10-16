#!/bin/bash

# DcisionAI SaaS Platform - Local Development Server Startup
# =========================================================

echo "🚀 Starting DcisionAI SaaS Platform..."
echo "======================================"

# Check if we're in the right directory
if [ ! -f "start_servers.sh" ]; then
    echo "❌ Please run this script from the saas-platform/deployment directory"
    exit 1
fi

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "📁 Project root: $PROJECT_ROOT"
echo "📁 Frontend: $FRONTEND_DIR"
echo "📁 Backend: $BACKEND_DIR"

# Check if directories exist
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Backend directory not found: $BACKEND_DIR"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if ports are available
if check_port 3000; then
    echo "⚠️  Port 3000 is already in use. Please stop the service using this port."
    exit 1
fi

if check_port 5001; then
    echo "⚠️  Port 5001 is already in use. Please stop the service using this port."
    exit 1
fi

echo "✅ Ports 3000 and 5001 are available"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install backend dependencies"
    exit 1
fi

echo "✅ Backend dependencies installed"

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install frontend dependencies"
        exit 1
    fi
fi

echo "✅ Frontend dependencies installed"

# Start backend server
echo "🔧 Starting backend server..."
cd "$BACKEND_DIR"
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if ! check_port 5001; then
    echo "❌ Backend failed to start on port 5001"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Backend server started (PID: $BACKEND_PID)"

# Start frontend server
echo "🔧 Starting frontend server..."
cd "$FRONTEND_DIR"
npm start &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

# Check if frontend is running
if ! check_port 3000; then
    echo "❌ Frontend failed to start on port 3000"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Frontend server started (PID: $FRONTEND_PID)"

# Display success message
echo ""
echo "🎉 DcisionAI SaaS Platform is now running!"
echo "=========================================="
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5001"
echo "❤️  Health Check: http://localhost:5001/health"
echo ""
echo "📊 Features:"
echo "  - Claude 3 Haiku model building"
echo "  - Enhanced constraint parser"
echo "  - PDLP solver integration"
echo "  - Real OR-Tools optimization"
echo ""
echo "🛑 To stop the servers:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "  Backend: Check terminal output"
echo "  Frontend: Check browser console"
echo ""

# Keep the script running and show logs
echo "📋 Server logs (Ctrl+C to stop):"
echo "================================"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID