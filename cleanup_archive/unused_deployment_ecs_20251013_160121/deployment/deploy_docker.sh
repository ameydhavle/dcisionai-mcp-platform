#!/bin/bash
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
