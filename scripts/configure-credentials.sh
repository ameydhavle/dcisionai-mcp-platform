#!/bin/bash

# DcisionAI MCP Server - Credential Configuration Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Function to configure email credentials
configure_email() {
    print_status "Configuring email credentials..."
    
    echo "To send automated welcome emails, you need to:"
    echo "1. Enable 2-Factor Authentication on your Google account"
    echo "2. Generate an App Password for Gmail"
    echo ""
    echo "Steps:"
    echo "1. Go to: https://myaccount.google.com/security"
    echo "2. Enable 2-Factor Authentication"
    echo "3. Go to 'App passwords' under '2-Step Verification'"
    echo "4. Select 'Mail' and 'Other (custom name)'"
    echo "5. Enter 'DcisionAI MCP Server'"
    echo "6. Copy the 16-character password"
    echo ""
    
    read -p "Enter your Gmail address: " email
    read -s -p "Enter your Gmail App Password (16 characters): " password
    echo ""
    
    # Update configuration
    python3 -c "
import json
import sys

try:
    with open('onboarding-config.json', 'r') as f:
        config = json.load(f)
    
    config['email'] = '$email'
    config['password'] = '$password'
    
    with open('onboarding-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print('✅ Email configuration updated')
except Exception as e:
    print(f'❌ Error updating configuration: {e}')
    sys.exit(1)
"
    
    print_success "Email configuration complete"
}

# Function to configure GitHub settings
configure_github() {
    print_status "Configuring GitHub settings..."
    
    # Get current GitHub user
    github_user=$(gh api user --jq .login)
    print_status "Current GitHub user: $github_user"
    
    # Update configuration
    python3 -c "
import json
import sys

try:
    with open('onboarding-config.json', 'r') as f:
        config = json.load(f)
    
    config['github_org'] = '$github_user'
    config['repo_name'] = 'dcisionai-mcp-server'
    
    with open('onboarding-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print('✅ GitHub configuration updated')
except Exception as e:
    print(f'❌ Error updating configuration: {e}')
    sys.exit(1)
"
    
    print_success "GitHub configuration complete"
}

# Function to test configuration
test_configuration() {
    print_status "Testing configuration..."
    
    # Test GitHub access
    if gh repo view ameydhavle/dcisionai-mcp-server &> /dev/null; then
        print_success "✅ GitHub repository access confirmed"
    else
        print_error "❌ GitHub repository access failed"
        return 1
    fi
    
    # Test email configuration
    python3 -c "
import json
import smtplib
from email.mime.text import MIMEText

try:
    with open('onboarding-config.json', 'r') as f:
        config = json.load(f)
    
    if config['password'] == 'YOUR_APP_PASSWORD_HERE':
        print('⚠️  Email not configured - skipping test')
    else:
        # Test SMTP connection
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['email'], config['password'])
        server.quit()
        print('✅ Email configuration test passed')
except Exception as e:
    print(f'❌ Email configuration test failed: {e}')
"
    
    print_success "Configuration test complete"
}

# Function to show current configuration
show_configuration() {
    print_status "Current configuration:"
    echo ""
    
    if [ -f "onboarding-config.json" ]; then
        python3 -c "
import json

with open('onboarding-config.json', 'r') as f:
    config = json.load(f)

print('📧 Email Configuration:')
print(f'  Email: {config[\"email\"]}')
print(f'  Password: {\"***\" if config[\"password\"] != \"YOUR_APP_PASSWORD_HERE\" else \"Not configured\"}')
print('')
print('🐙 GitHub Configuration:')
print(f'  Organization: {config[\"github_org\"]}')
print(f'  Repository: {config[\"repo_name\"]}')
print('')
print('📊 Optional Services:')
print(f'  Slack Webhook: {\"Configured\" if config[\"slack_webhook\"] != \"https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK\" else \"Not configured\"}')
print(f'  Analytics Endpoint: {\"Configured\" if config[\"analytics_endpoint\"] != \"https://your-analytics.com/api/usage\" else \"Not configured\"}')
"
    else
        print_error "Configuration file not found"
    fi
}

# Main menu
main() {
    print_status "🔧 DcisionAI MCP Server - Credential Configuration"
    print_status "=================================================="
    
    while true; do
        echo ""
        echo "Options:"
        echo "1. Configure email credentials"
        echo "2. Configure GitHub settings"
        echo "3. Test configuration"
        echo "4. Show current configuration"
        echo "5. Exit"
        echo ""
        
        read -p "Enter your choice (1-5): " choice
        
        case $choice in
            1)
                configure_email
                ;;
            2)
                configure_github
                ;;
            3)
                test_configuration
                ;;
            4)
                show_configuration
                ;;
            5)
                print_success "Configuration complete!"
                break
                ;;
            *)
                print_error "Invalid choice. Please try again."
                ;;
        esac
    done
}

# Run main function
main "$@"
