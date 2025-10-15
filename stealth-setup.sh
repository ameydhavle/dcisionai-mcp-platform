#!/bin/bash

# DcisionAI MCP Server - Stealth Mode Setup Script
# This script sets up private distribution infrastructure

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

# Function to create private GitHub repository
create_private_repo() {
    print_status "Setting up private GitHub repository..."
    
    # Check if GitHub CLI is installed
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed. Please install it first:"
        echo "  brew install gh  # macOS"
        echo "  apt install gh   # Ubuntu"
        echo "  choco install gh # Windows"
        exit 1
    fi
    
    # Check if user is authenticated
    if ! gh auth status &> /dev/null; then
        print_error "Not authenticated with GitHub. Please run: gh auth login"
        exit 1
    fi
    
    # Create private repository
    REPO_NAME="dcisionai-mcp-server"
    REPO_DESC="AI-powered business optimization MCP server (Private)"
    
    if gh repo view "$REPO_NAME" &> /dev/null; then
        print_warning "Repository $REPO_NAME already exists"
    else
        gh repo create "$REPO_NAME" --private --description "$REPO_DESC"
        print_success "Created private repository: $REPO_NAME"
    fi
    
    # Add remote if not exists
    if ! git remote get-url origin &> /dev/null; then
        git remote add origin "git@github.com:$(gh api user --jq .login)/$REPO_NAME.git"
        print_success "Added GitHub remote"
    fi
    
    # Push to repository
    git add .
    git commit -m "Initial commit: DcisionAI MCP Server" || true
    git push -u origin main
    
    print_success "Repository setup complete"
}

# Function to create customer invitation system
create_invitation_system() {
    print_status "Creating customer invitation system..."
    
    # Create invitation template
    cat > customer-invitation-template.md << 'EOF'
# 🎉 Welcome to DcisionAI MCP Server Private Beta

Dear [CUSTOMER_NAME],

You've been invited to join the private beta of **DcisionAI MCP Server**, an AI-powered business optimization tool that integrates directly with your IDE.

## 🚀 What You Get

- **6 Optimization Tools** - Intent classification, data analysis, model building, optimization solving, workflow templates, and end-to-end execution
- **21 Industry Workflows** - Manufacturing, healthcare, retail, marketing, financial, logistics, and energy
- **Real-time Optimization** - Get instant mathematical models and business insights
- **IDE Integration** - Use optimization tools directly in Cursor IDE

## 📋 Getting Started

### Step 1: Accept Repository Access
You should have received a GitHub repository invitation. Please accept it to access the private repository.

### Step 2: Install the MCP Server
```bash
# Install from private repository
pip install git+https://github.com/DcisionAI/dcisionai-mcp-server.git

# Or with authentication token
pip install git+https://<your-token>@github.com/DcisionAI/dcisionai-mcp-server.git
```

### Step 3: Configure Your IDE
Follow the installation guide in the repository to configure Cursor IDE.

### Step 4: Join Our Community
- **Private Slack**: [Invitation Link]
- **Support Email**: support@dcisionai.com
- **Documentation**: [Private Documentation Portal]

## 🔧 Quick Test

Once installed, try asking in Cursor:
- "Help me optimize my supply chain costs"
- "Show me available manufacturing workflows"
- "Build a production planning model"

## 📞 Support

If you need help:
1. Check the documentation in the repository
2. Join our private Slack workspace
3. Email support@dcisionai.com
4. Create an issue in the private repository

## 🎯 What's Next

- **Week 1**: Get familiar with the tools and workflows
- **Week 2**: Try real optimization problems
- **Week 3**: Provide feedback and suggestions
- **Week 4**: Advanced usage and optimization

We're excited to have you on board!

Best regards,
The DcisionAI Team

---
*This is a private beta. Please do not share this invitation or the repository access with others.*
EOF

    print_success "Created customer invitation template"
}

# Function to create access control system
create_access_control() {
    print_status "Creating access control system..."
    
    # Create customer management script
    cat > manage-customers.py << 'EOF'
#!/usr/bin/env python3
"""
Customer Management System for DcisionAI MCP Server
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class CustomerManager:
    def __init__(self, customers_file: str = "customers.json"):
        self.customers_file = customers_file
        self.customers = self.load_customers()
    
    def load_customers(self) -> Dict:
        """Load customers from file."""
        if os.path.exists(self.customers_file):
            with open(self.customers_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_customers(self):
        """Save customers to file."""
        with open(self.customers_file, 'w') as f:
            json.dump(self.customers, f, indent=2)
    
    def add_customer(self, email: str, name: str, company: str, tier: str = "beta"):
        """Add a new customer."""
        customer_id = email.lower().replace('@', '_at_').replace('.', '_')
        
        self.customers[customer_id] = {
            "email": email,
            "name": name,
            "company": company,
            "tier": tier,
            "status": "active",
            "joined_date": datetime.utcnow().isoformat(),
            "last_activity": None,
            "usage_count": 0
        }
        
        self.save_customers()
        print(f"✅ Added customer: {name} ({email})")
    
    def remove_customer(self, email: str):
        """Remove a customer."""
        customer_id = email.lower().replace('@', '_at_').replace('.', '_')
        
        if customer_id in self.customers:
            del self.customers[customer_id]
            self.save_customers()
            print(f"✅ Removed customer: {email}")
        else:
            print(f"❌ Customer not found: {email}")
    
    def list_customers(self):
        """List all customers."""
        if not self.customers:
            print("No customers found.")
            return
        
        print(f"{'Name':<20} {'Email':<30} {'Company':<20} {'Tier':<10} {'Status':<10}")
        print("-" * 90)
        
        for customer in self.customers.values():
            print(f"{customer['name']:<20} {customer['email']:<30} {customer['company']:<20} {customer['tier']:<10} {customer['status']:<10}")
    
    def update_customer_status(self, email: str, status: str):
        """Update customer status."""
        customer_id = email.lower().replace('@', '_at_').replace('.', '_')
        
        if customer_id in self.customers:
            self.customers[customer_id]['status'] = status
            self.save_customers()
            print(f"✅ Updated status for {email}: {status}")
        else:
            print(f"❌ Customer not found: {email}")

def main():
    manager = CustomerManager()
    
    print("🥷 DcisionAI Customer Management System")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Add customer")
        print("2. Remove customer")
        print("3. List customers")
        print("4. Update customer status")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            email = input("Email: ").strip()
            name = input("Name: ").strip()
            company = input("Company: ").strip()
            tier = input("Tier (beta/pro/enterprise): ").strip() or "beta"
            manager.add_customer(email, name, company, tier)
        
        elif choice == "2":
            email = input("Email to remove: ").strip()
            manager.remove_customer(email)
        
        elif choice == "3":
            manager.list_customers()
        
        elif choice == "4":
            email = input("Email: ").strip()
            status = input("New status (active/inactive/suspended): ").strip()
            manager.update_customer_status(email, status)
        
        elif choice == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
EOF

    chmod +x manage-customers.py
    print_success "Created customer management system"
}

# Function to create monitoring system
create_monitoring_system() {
    print_status "Creating monitoring system..."
    
    # Create usage tracking script
    cat > usage-tracker.py << 'EOF'
#!/usr/bin/env python3
"""
Usage Tracking System for DcisionAI MCP Server
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, List

class UsageTracker:
    def __init__(self, tracking_file: str = "usage.json"):
        self.tracking_file = tracking_file
        self.usage_data = self.load_usage_data()
    
    def load_usage_data(self) -> List[Dict]:
        """Load usage data from file."""
        if os.path.exists(self.tracking_file):
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_usage_data(self):
        """Save usage data to file."""
        with open(self.tracking_file, 'w') as f:
            json.dump(self.usage_data, f, indent=2)
    
    def track_usage(self, customer_id: str, tool_name: str, success: bool, duration: float = None):
        """Track tool usage."""
        usage_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "customer_id": customer_id,
            "tool": tool_name,
            "success": success,
            "duration": duration
        }
        
        self.usage_data.append(usage_record)
        self.save_usage_data()
        
        # Send to analytics endpoint (if configured)
        self.send_analytics(usage_record)
    
    def send_analytics(self, data: Dict):
        """Send usage data to analytics endpoint."""
        # Configure your analytics endpoint
        analytics_url = os.getenv("ANALYTICS_ENDPOINT")
        
        if analytics_url:
            try:
                requests.post(analytics_url, json=data, timeout=5)
            except Exception as e:
                print(f"Failed to send analytics: {e}")
    
    def get_usage_stats(self) -> Dict:
        """Get usage statistics."""
        if not self.usage_data:
            return {"total_usage": 0, "success_rate": 0, "top_tools": []}
        
        total_usage = len(self.usage_data)
        successful_usage = sum(1 for record in self.usage_data if record["success"])
        success_rate = (successful_usage / total_usage) * 100 if total_usage > 0 else 0
        
        # Count tool usage
        tool_counts = {}
        for record in self.usage_data:
            tool = record["tool"]
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        top_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_usage": total_usage,
            "success_rate": success_rate,
            "top_tools": top_tools,
            "unique_customers": len(set(record["customer_id"] for record in self.usage_data))
        }
    
    def print_stats(self):
        """Print usage statistics."""
        stats = self.get_usage_stats()
        
        print("📊 Usage Statistics")
        print("=" * 30)
        print(f"Total Usage: {stats['total_usage']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        print(f"Unique Customers: {stats['unique_customers']}")
        print(f"Top Tools: {stats['top_tools']}")

def main():
    tracker = UsageTracker()
    
    print("📊 DcisionAI Usage Tracker")
    print("=" * 30)
    
    while True:
        print("\nOptions:")
        print("1. Track usage")
        print("2. View statistics")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            customer_id = input("Customer ID: ").strip()
            tool_name = input("Tool name: ").strip()
            success = input("Success (y/n): ").strip().lower() == 'y'
            duration = input("Duration (seconds, optional): ").strip()
            duration = float(duration) if duration else None
            
            tracker.track_usage(customer_id, tool_name, success, duration)
            print("✅ Usage tracked")
        
        elif choice == "2":
            tracker.print_stats()
        
        elif choice == "3":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
EOF

    chmod +x usage-tracker.py
    print_success "Created usage tracking system"
}

# Function to create deployment package
create_deployment_package() {
    print_status "Creating deployment package..."
    
    # Create deployment script
    cat > deploy.sh << 'EOF'
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
EOF

    chmod +x deploy.sh
    print_success "Created deployment package"
}

# Main execution
main() {
    print_status "🥷 Setting up DcisionAI MCP Server - Stealth Mode"
    print_status "=================================================="
    
    # Check prerequisites
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install it first."
        exit 1
    fi
    
    # Create private repository
    create_private_repo
    
    # Create invitation system
    create_invitation_system
    
    # Create access control
    create_access_control
    
    # Create monitoring system
    create_monitoring_system
    
    # Create deployment package
    create_deployment_package
    
    print_success "🎉 Stealth mode setup complete!"
    print ""
    print "📋 Next steps:"
    print "1. Review and customize the generated files"
    print "2. Set up your analytics endpoint (optional)"
    print "3. Start inviting customers using manage-customers.py"
    print "4. Deploy using deploy.sh"
    print "5. Monitor usage with usage-tracker.py"
    print ""
    print "🔐 Remember: Keep your infrastructure private and monitor access carefully!"
}

# Run main function
main "$@"
