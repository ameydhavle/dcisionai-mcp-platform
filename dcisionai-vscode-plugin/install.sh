#!/bin/bash

# DcisionAI VS Code Extension Installation Script

echo "🚀 Installing DcisionAI VS Code Extension..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Compile TypeScript
echo "🔨 Compiling TypeScript..."
npm run compile

# Package the extension
echo "📦 Packaging extension..."
npm run package

# Find the generated .vsix file
VSIX_FILE=$(find . -name "*.vsix" -type f | head -1)

if [ -z "$VSIX_FILE" ]; then
    echo "❌ Failed to create .vsix package"
    exit 1
fi

echo "✅ Extension packaged successfully: $VSIX_FILE"

# Check if VS Code is installed
if command -v code &> /dev/null; then
    echo "🔌 Installing extension in VS Code..."
    code --install-extension "$VSIX_FILE"
    echo "✅ Extension installed successfully!"
    echo "🎉 You can now use DcisionAI Optimization in VS Code!"
else
    echo "⚠️ VS Code CLI not found. Please install the extension manually:"
    echo "   1. Open VS Code"
    echo "   2. Go to Extensions view (Ctrl+Shift+X)"
    echo "   3. Click '...' menu and select 'Install from VSIX...'"
    echo "   4. Select: $VSIX_FILE"
fi

echo ""
echo "📋 Next steps:"
echo "   1. Configure AWS credentials in VS Code settings"
echo "   2. Set the MCP server path to your mcp-server directory"
echo "   3. Use Ctrl+Shift+P and search for 'DcisionAI' commands"
echo ""
echo "🎯 Happy optimizing!"
