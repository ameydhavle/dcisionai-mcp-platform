#!/bin/bash

# DcisionAI MCP Server - Deployment Script

set -e

echo "🚀 Deploying DcisionAI MCP Server..."

# Build the package
echo "📦 Building package..."
cd dcisionai-mcp-server
python -m build
cd ..

# Create deployment directory
DEPLOY_DIR="deployment-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DEPLOY_DIR"

# Copy files
cp dcisionai-mcp-server/dist/*.tar.gz "$DEPLOY_DIR/"
cp dcisionai-mcp-server/dist/*.whl "$DEPLOY_DIR/"
cp customer-invitation-template.md "$DEPLOY_DIR/"
cp STEALTH_DEPLOYMENT_GUIDE.md "$DEPLOY_DIR/"

# Create installation script
cat > "$DEPLOY_DIR/install.sh" << 'INSTALL_EOF'
#!/bin/bash

# DcisionAI MCP Server - Customer Installation Script

set -e

echo "🥷 Installing DcisionAI MCP Server..."

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$python_version < 3.8" | bc -l) -eq 1 ]]; then
    echo "❌ Python 3.8+ required. Current version: $python_version"
    exit 1
fi

# Install package
echo "📦 Installing MCP server..."
pip install dcisionai-mcp-server-*.whl

# Create Cursor configuration
echo "🔧 Configuring Cursor IDE..."
CURSOR_CONFIG_DIR="$HOME/.cursor"
mkdir -p "$CURSOR_CONFIG_DIR"

# Backup existing config
if [ -f "$CURSOR_CONFIG_DIR/mcp.json" ]; then
    cp "$CURSOR_CONFIG_DIR/mcp.json" "$CURSOR_CONFIG_DIR/mcp.json.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Add DcisionAI MCP server to config
cat >> "$CURSOR_CONFIG_DIR/mcp.json" << 'CURSOR_EOF'
{
  "mcpServers": {
    "dcisionai-optimization": {
      "command": "python",
      "args": ["-m", "dcisionai_mcp_server.robust_mcp"],
      "env": {
        "DCISIONAI_ACCESS_TOKEN": "YOUR_ACCESS_TOKEN_HERE",
        "DCISIONAI_GATEWAY_URL": "YOUR_GATEWAY_URL_HERE",
        "DCISIONAI_GATEWAY_TARGET": "DcisionAI-Optimization-Tools-Fixed"
      },
      "disabled": false,
      "autoApprove": [
        "classify_intent",
        "analyze_data",
        "build_model",
        "solve_optimization",
        "get_workflow_templates",
        "execute_workflow"
      ]
    }
  }
}
CURSOR_EOF

echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update the environment variables in ~/.cursor/mcp.json"
echo "2. Restart Cursor IDE"
echo "3. Test with: 'Help me optimize my supply chain costs'"
echo ""
echo "📞 Support: support@dcisionai.com"
INSTALL_EOF

chmod +x "$DEPLOY_DIR/install.sh"

echo "✅ Deployment package created: $DEPLOY_DIR"
echo ""
echo "📋 Package contents:"
ls -la "$DEPLOY_DIR"
echo ""
echo "🚀 Ready for distribution!"
