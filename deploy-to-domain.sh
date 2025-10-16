#!/bin/bash

# Deploy DcisionAI Configuration System to www.dcisionai.com

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                DcisionAI Domain Deployment                   ║"
    echo "║                    www.dcisionai.com                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
DOMAIN="www.dcisionai.com"
FILES_TO_DEPLOY=(
    "install-dcisionai-mcp.sh"
    "customer-configuration.html"
    "customer-config-server.py"
    "generate-customer-token.py"
)

# Function to check if required files exist
check_files() {
    print_status "Checking required files..."
    
    for file in "${FILES_TO_DEPLOY[@]}"; do
        if [ -f "$file" ]; then
            print_success "✅ $file found"
        else
            print_error "❌ $file not found"
            exit 1
        fi
    done
}

# Function to test domain connectivity
test_domain() {
    print_status "Testing domain connectivity..."
    
    if curl -s --head "https://$DOMAIN" | head -n 1 | grep -q "200 OK"; then
        print_success "✅ Domain $DOMAIN is accessible"
    elif curl -s --head "http://$DOMAIN" | head -n 1 | grep -q "200 OK"; then
        print_warning "⚠️ Domain $DOMAIN is accessible via HTTP (HTTPS recommended)"
    else
        print_error "❌ Domain $DOMAIN is not accessible"
        print_warning "Please ensure your domain is properly configured"
        return 1
    fi
}

# Function to generate deployment instructions
generate_instructions() {
    print_status "Generating deployment instructions..."
    
    cat > deployment-instructions.md << EOF
# 🚀 Deployment Instructions for www.dcisionai.com

## 📋 **Files to Upload**

Upload these files to your web server root directory:

\`\`\`bash
# Required files:
install-dcisionai-mcp.sh          # Installation script
customer-configuration.html       # Main configuration page
customer-config-server.py         # Configuration server (optional)
generate-customer-token.py        # Token generator (backend)
\`\`\`

## 🌐 **URL Structure**

After deployment, these URLs should work:

- **Main page**: https://www.dcisionai.com/
- **Installation script**: https://www.dcisionai.com/install-dcisionai-mcp.sh
- **Customer configuration**: https://www.dcisionai.com/configure?token=customer-token

## 🔧 **Server Configuration**

### **Apache (.htaccess)**
\`\`\`apache
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

<Files "install-dcisionai-mcp.sh">
    Header set Content-Type "text/plain"
    Header set Content-Disposition "attachment; filename=install-dcisionai-mcp.sh"
</Files>
\`\`\`

### **Nginx**
\`\`\`nginx
server {
    listen 443 ssl;
    server_name www.dcisionai.com dcisionai.com;
    
    root /var/www/dcisionai.com;
    index customer-configuration.html;
    
    location /install-dcisionai-mcp.sh {
        add_header Content-Type text/plain;
        add_header Content-Disposition "attachment; filename=install-dcisionai-mcp.sh";
    }
}
\`\`\`

## 🧪 **Testing Commands**

\`\`\`bash
# Test installation script
curl -I https://www.dcisionai.com/install-dcisionai-mcp.sh

# Test main page
curl -I https://www.dcisionai.com/

# Test with customer token
curl -I "https://www.dcisionai.com/configure?token=test-token"
\`\`\`

## 📊 **Customer Experience**

Customers will use:
1. **Configuration link**: https://www.dcisionai.com/configure?token=customer-token
2. **Install command**: curl -sSL https://www.dcisionai.com/install-dcisionai-mcp.sh | bash
3. **Get access token** from support
4. **Start optimizing** with Cursor IDE

## 🎯 **Success Metrics**

- ✅ Installation script accessible via HTTPS
- ✅ Configuration page loads correctly
- ✅ Customer tokens work properly
- ✅ Installation completes successfully
- ✅ Cursor IDE integration works

EOF

    print_success "Deployment instructions saved to deployment-instructions.md"
}

# Function to create deployment package
create_package() {
    print_status "Creating deployment package..."
    
    PACKAGE_DIR="dcisionai-deployment"
    mkdir -p "$PACKAGE_DIR"
    
    # Copy files to package directory
    for file in "${FILES_TO_DEPLOY[@]}"; do
        cp "$file" "$PACKAGE_DIR/"
        print_success "✅ Copied $file to $PACKAGE_DIR/"
    done
    
    # Copy deployment instructions
    cp deployment-instructions.md "$PACKAGE_DIR/"
    
    # Create deployment script
    cat > "$PACKAGE_DIR/deploy.sh" << 'EOF'
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
EOF

    chmod +x "$PACKAGE_DIR/deploy.sh"
    
    # Create zip package
    zip -r "dcisionai-deployment.zip" "$PACKAGE_DIR" > /dev/null
    
    print_success "✅ Deployment package created: dcisionai-deployment.zip"
    print_success "✅ Deployment directory: $PACKAGE_DIR/"
}

# Function to test deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Test installation script locally
    if [ -f "install-dcisionai-mcp.sh" ]; then
        print_success "✅ Installation script exists and is executable"
    else
        print_error "❌ Installation script not found"
        return 1
    fi
    
    # Test configuration page
    if [ -f "customer-configuration.html" ]; then
        print_success "✅ Configuration page exists"
    else
        print_error "❌ Configuration page not found"
        return 1
    fi
    
    # Test customer token generator
    if [ -f "generate-customer-token.py" ]; then
        print_success "✅ Customer token generator exists"
    else
        print_error "❌ Customer token generator not found"
        return 1
    fi
    
    print_success "✅ All deployment files are ready"
}

# Main deployment function
main() {
    print_header
    
    print_status "Starting deployment preparation for $DOMAIN..."
    echo ""
    
    # Check files
    check_files
    echo ""
    
    # Test deployment
    test_deployment
    echo ""
    
    # Test domain (optional)
    if test_domain; then
        print_success "✅ Domain is accessible"
    else
        print_warning "⚠️ Domain test failed - continue with deployment anyway"
    fi
    echo ""
    
    # Generate instructions
    generate_instructions
    echo ""
    
    # Create package
    create_package
    echo ""
    
    print_success "🎉 Deployment preparation complete!"
    echo ""
    print_status "📋 Next Steps:"
    print_status "1. Upload files from dcisionai-deployment/ to your web server"
    print_status "2. Configure SSL and redirects (see deployment-instructions.md)"
    print_status "3. Test the deployment with the provided commands"
    print_status "4. Start onboarding your first customers!"
    echo ""
    print_status "🎯 Customer Experience:"
    print_status "   Configuration: https://www.dcisionai.com/configure?token=customer-token"
    print_status "   Installation: curl -sSL https://www.dcisionai.com/install-dcisionai-mcp.sh | bash"
    echo ""
    print_success "Your seamless configuration system is ready for production! 🚀"
}

# Run main function
main "$@"
