#!/bin/bash
# Quick deployment script for www.dcisionai.com

echo "🚀 Deploying DcisionAI Configuration System to www.dcisionai.com"
echo ""

# Set permissions
chmod +x install-dcisionai-mcp.sh
chmod +x customer-config-server.py
chmod +x generate-customer-token.py

echo "✅ Files ready for deployment"
echo ""
echo "📋 Next steps:"
echo "1. Upload all files to your web server root directory"
echo "2. Configure SSL and redirects (see deployment-instructions.md)"
echo "3. Test the deployment (see testing commands in instructions)"
echo "4. Start onboarding customers!"
echo ""
echo "🎯 Customer configuration URL: https://www.dcisionai.com/configure?token=customer-token"
echo "📥 Installation command: curl -sSL https://www.dcisionai.com/install-dcisionai-mcp.sh | bash"
