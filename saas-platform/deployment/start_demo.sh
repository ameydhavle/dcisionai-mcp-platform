#!/bin/bash

# DcisionAI SaaS Platform - Demo Setup
# ====================================

echo "🎯 DcisionAI SaaS Platform Demo"
echo "==============================="

# Check if we're in the right directory
if [ ! -f "start_demo.sh" ]; then
    echo "❌ Please run this script from the saas-platform/deployment directory"
    exit 1
fi

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "📁 Project root: $PROJECT_ROOT"

# Check if MCP server is available
echo "🔍 Checking MCP server availability..."
if ! command -v uvx &> /dev/null; then
    echo "❌ uvx not found. Please install uv: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Test MCP server
echo "🧪 Testing MCP server connection..."
MCP_TEST=$(uvx dcisionai-mcp-server@1.0.11 --help 2>&1)
if [ $? -ne 0 ]; then
    echo "❌ MCP server test failed: $MCP_TEST"
    echo "💡 Make sure dcisionai-mcp-server@1.0.11 is available"
    exit 1
fi

echo "✅ MCP server is available"

# Start the demo
echo "🚀 Starting demo servers..."
./start_servers.sh &
DEMO_PID=$!

# Wait for servers to start
echo "⏳ Waiting for servers to start..."
sleep 15

# Check if servers are running
if ! lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Frontend server failed to start"
    kill $DEMO_PID 2>/dev/null
    exit 1
fi

if ! lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Backend server failed to start"
    kill $DEMO_PID 2>/dev/null
    exit 1
fi

echo "✅ Demo servers are running!"

# Display demo information
echo ""
echo "🎉 Demo is ready!"
echo "================"
echo ""
echo "🌐 Open your browser and go to: http://localhost:3000"
echo ""
echo "🧪 Try these demo queries:"
echo ""
echo "1. Portfolio Optimization:"
echo "   'I have $500,000 to invest and need help optimizing my portfolio allocation. I'm 38 years old, planning to retire at 60, and want to balance growth with risk management.'"
echo ""
echo "2. Production Planning:"
echo "   'Optimize production line efficiency with 50 workers across 3 manufacturing lines, considering skill sets, line capacities, and cost constraints'"
echo ""
echo "3. Supply Chain Optimization:"
echo "   'Optimize supply chain for 5 warehouses across different regions, considering demand forecasting, inventory costs, and transportation constraints'"
echo ""
echo "4. Resource Allocation:"
echo "   'Optimize resource allocation and improve operational efficiency across multiple departments with budget constraints'"
echo ""
echo "🔧 Backend API: http://localhost:5001"
echo "❤️  Health Check: http://localhost:5001/health"
echo ""
echo "📊 Features to demonstrate:"
echo "  ✅ Claude 3 Haiku model building"
echo "  ✅ Enhanced constraint parser"
echo "  ✅ PDLP solver integration"
echo "  ✅ Real OR-Tools optimization"
echo "  ✅ 3D visualization"
echo "  ✅ Sensitivity analysis"
echo ""
echo "🛑 To stop the demo:"
echo "  kill $DEMO_PID"
echo ""

# Open browser (if possible)
if command -v open &> /dev/null; then
    echo "🌐 Opening browser..."
    open http://localhost:3000
elif command -v xdg-open &> /dev/null; then
    echo "🌐 Opening browser..."
    xdg-open http://localhost:3000
fi

# Keep the script running
echo "📋 Demo is running. Press Ctrl+C to stop."
echo "========================================="

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping demo..."
    kill $DEMO_PID 2>/dev/null
    echo "✅ Demo stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for the demo process
wait $DEMO_PID