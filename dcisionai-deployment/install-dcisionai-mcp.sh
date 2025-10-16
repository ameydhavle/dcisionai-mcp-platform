#!/bin/bash

# DcisionAI MCP Server - Automated Installation Script
# This script provides seamless configuration for customers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
DCISIONAI_VERSION="1.0.0"
DCISIONAI_REPO="https://github.com/ameydhavle/dcisionai-mcp-server.git"
DCISIONAI_PACKAGE="dcisionai-mcp-server"

print_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    DcisionAI MCP Server                     ║"
    echo "║                Automated Installation Script                ║"
    echo "║                        Version $DCISIONAI_VERSION                        ║"
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

print_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect Python version
detect_python() {
    print_step "Detecting Python environment..."
    
    PYTHON_CMD=""
    PYTHON_VERSION=""
    
    # Try different Python versions
    for version in python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3; do
        if command_exists "$version"; then
            PYTHON_VERSION=$($version --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
            MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
            MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
            
            if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 8 ]; then
                PYTHON_CMD="$version"
                print_success "Found compatible Python: $version ($PYTHON_VERSION)"
                break
            fi
        fi
    done
    
    if [ -z "$PYTHON_CMD" ]; then
        print_error "Python 3.8+ not found. Please install Python 3.8 or newer."
        echo ""
        echo "Installation instructions:"
        echo "  macOS: brew install python@3.10"
        echo "  Ubuntu: sudo apt update && sudo apt install python3.10 python3.10-venv"
        echo "  Windows: Download from https://python.org"
        exit 1
    fi
    
    export PYTHON_CMD
    export PYTHON_VERSION
}

# Function to create virtual environment
create_venv() {
    print_step "Creating Python virtual environment..."
    
    VENV_DIR="$HOME/.dcisionai-mcp"
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at $VENV_DIR"
        read -p "Do you want to recreate it? (y/N): " recreate
        if [[ $recreate =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
        else
            print_status "Using existing virtual environment"
            return 0
        fi
    fi
    
    $PYTHON_CMD -m venv "$VENV_DIR"
    print_success "Virtual environment created at $VENV_DIR"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
    
    export VENV_DIR
}

# Function to install dependencies
install_dependencies() {
    print_step "Installing DcisionAI MCP Server..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install the package
    if [ -d "dcisionai-mcp-server" ]; then
        print_status "Installing from local directory..."
        pip install -e dcisionai-mcp-server/
    else
        print_status "Installing from GitHub repository..."
        pip install git+$DCISIONAI_REPO
    fi
    
    print_success "DcisionAI MCP Server installed successfully"
}

# Function to configure environment
configure_environment() {
    print_step "Configuring environment variables..."
    
    CONFIG_DIR="$HOME/.dcisionai"
    CONFIG_FILE="$CONFIG_DIR/config.json"
    
    mkdir -p "$CONFIG_DIR"
    
    # Create configuration file
    cat > "$CONFIG_FILE" << EOF
{
  "version": "$DCISIONAI_VERSION",
  "python_path": "$VENV_DIR/bin/python",
  "mcp_module": "dcisionai_mcp_server.robust_mcp",
  "gateway_url": "https://dcisionai-gateway-0de1a655-ja1rhlcqjx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp",
  "gateway_target": "DcisionAI-Optimization-Tools-Fixed",
  "access_token": "YOUR_ACCESS_TOKEN_HERE",
  "installed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    
    print_success "Configuration file created at $CONFIG_FILE"
    print_warning "Please update the access_token in $CONFIG_FILE with your actual token"
    
    export CONFIG_FILE
}

# Function to configure Cursor IDE
configure_cursor() {
    print_step "Configuring Cursor IDE integration..."
    
    CURSOR_CONFIG_DIR="$HOME/.cursor"
    MCP_CONFIG_FILE="$CURSOR_CONFIG_DIR/mcp.json"
    
    mkdir -p "$CURSOR_CONFIG_DIR"
    
    # Read existing mcp.json or create new one
    if [ -f "$MCP_CONFIG_FILE" ]; then
        print_status "Updating existing Cursor MCP configuration..."
        # Backup existing config
        cp "$MCP_CONFIG_FILE" "$MCP_CONFIG_FILE.backup.$(date +%s)"
    else
        print_status "Creating new Cursor MCP configuration..."
        echo '{"mcpServers": {}}' > "$MCP_CONFIG_FILE"
    fi
    
    # Update mcp.json with DcisionAI configuration
    python3 -c "
import json
import os

config_file = '$MCP_CONFIG_FILE'
python_path = '$VENV_DIR/bin/python'

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
except:
    config = {'mcpServers': {}}

config['mcpServers']['dcisionai-optimization'] = {
    'command': python_path,
    'args': ['-m', 'dcisionai_mcp_server.robust_mcp'],
    'env': {
        'DCISIONAI_ACCESS_TOKEN': 'YOUR_ACCESS_TOKEN_HERE',
        'DCISIONAI_GATEWAY_URL': 'https://dcisionai-gateway-0de1a655-ja1rhlcqjx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp',
        'DCISIONAI_GATEWAY_TARGET': 'DcisionAI-Optimization-Tools-Fixed'
    },
    'disabled': False,
    'autoApprove': [
        'classify_intent',
        'analyze_data',
        'build_model',
        'solve_optimization',
        'get_workflow_templates',
        'execute_workflow'
    ]
}

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print('✅ Cursor IDE configuration updated')
"
    
    print_success "Cursor IDE configuration updated at $MCP_CONFIG_FILE"
    print_warning "Please update the DCISIONAI_ACCESS_TOKEN in $MCP_CONFIG_FILE with your actual token"
}

# Function to test installation
test_installation() {
    print_step "Testing installation..."
    
    # Test Python import
    if $VENV_DIR/bin/python -c "import dcisionai_mcp_server; print('✅ MCP server module imported successfully')" 2>/dev/null; then
        print_success "MCP server module test passed"
    else
        print_error "MCP server module test failed"
        return 1
    fi
    
    # Test CLI command
    if $VENV_DIR/bin/python -m dcisionai_mcp_server.cli --help >/dev/null 2>&1; then
        print_success "CLI command test passed"
    else
        print_error "CLI command test failed"
        return 1
    fi
    
    print_success "All tests passed!"
}

# Function to show next steps
show_next_steps() {
    print_step "Installation complete! Next steps:"
    echo ""
    echo "1. 🔑 Get your access token:"
    echo "   - Contact DcisionAI support for your access token"
    echo "   - Update the token in: $CONFIG_FILE"
    echo "   - Update the token in: $HOME/.cursor/mcp.json"
    echo ""
    echo "2. 🔄 Restart Cursor IDE:"
    echo "   - Close Cursor IDE completely"
    echo "   - Reopen Cursor IDE"
    echo "   - Look for 'dcisionai-optimization' in MCP servers"
    echo ""
    echo "3. 🧪 Test the integration:"
    echo "   - Ask Cursor: 'Help me optimize my supply chain costs'"
    echo "   - Ask Cursor: 'Show me available manufacturing workflows'"
    echo "   - Ask Cursor: 'Build a production planning model'"
    echo ""
    echo "4. 📞 Get support:"
    echo "   - Check the documentation: https://github.com/ameydhavle/dcisionai-mcp-server"
    echo "   - Contact support if you need help"
    echo ""
    print_success "🎉 DcisionAI MCP Server is ready to use!"
}

# Function to handle errors
handle_error() {
    print_error "Installation failed at step: $1"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check your internet connection"
    echo "2. Ensure you have Python 3.8+ installed"
    echo "3. Try running the script again"
    echo "4. Contact support if the issue persists"
    echo ""
    echo "Support: https://github.com/ameydhavle/dcisionai-mcp-server/issues"
    exit 1
}

# Main installation function
main() {
    print_header
    
    print_status "Starting DcisionAI MCP Server installation..."
    print_status "This will install the MCP server and configure Cursor IDE integration"
    echo ""
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root is not recommended. Please run as a regular user."
        exit 1
    fi
    
    # Trap errors
    trap 'handle_error "Unknown"' ERR
    
    # Installation steps
    detect_python || handle_error "Python detection"
    create_venv || handle_error "Virtual environment creation"
    install_dependencies || handle_error "Dependency installation"
    configure_environment || handle_error "Environment configuration"
    configure_cursor || handle_error "Cursor IDE configuration"
    test_installation || handle_error "Installation testing"
    
    echo ""
    show_next_steps
}

# Run main function
main "$@"
