#!/usr/bin/env python3
"""
Customer Onboarding Automation for DcisionAI MCP Server
"""

import json
import os
import smtplib
import subprocess
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional

class CustomerOnboarding:
    def __init__(self, config_file: str = "onboarding-config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.customers_file = "customers.json"
        self.customers = self.load_customers()
    
    def load_config(self) -> Dict:
        """Load onboarding configuration."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        # Default configuration
        default_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email": "your-email@dcisionai.com",
            "password": "your-app-password",
            "github_org": "DcisionAI",
            "repo_name": "dcisionai-mcp-server",
            "slack_webhook": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
            "analytics_endpoint": "https://your-analytics.com/api/usage"
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"⚠️  Created default configuration file: {self.config_file}")
        print("Please update it with your actual credentials.")
        
        return default_config
    
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
    
    def add_customer_to_github(self, email: str, name: str) -> bool:
        """Add customer to GitHub repository."""
        try:
            # Check if GitHub CLI is available
            if not self.check_gh_cli():
                print("❌ GitHub CLI not available. Please install it first.")
                return False
            
            # Add user to repository
            cmd = [
                "gh", "api", "repos", f"{self.config['github_org']}/{self.config['repo_name']}/collaborators/{email}",
                "--method", "PUT",
                "--field", "permission=read"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Added {email} to GitHub repository")
                return True
            else:
                print(f"❌ Failed to add {email} to GitHub: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error adding customer to GitHub: {e}")
            return False
    
    def check_gh_cli(self) -> bool:
        """Check if GitHub CLI is available."""
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def send_welcome_email(self, email: str, name: str, company: str) -> bool:
        """Send welcome email to customer."""
        try:
            # Create email content
            subject = "🎉 Welcome to DcisionAI MCP Server Private Beta"
            
            html_content = f"""
            <html>
            <body>
                <h2>Welcome to DcisionAI MCP Server Private Beta!</h2>
                
                <p>Hi {name},</p>
                
                <p>You've been invited to join the private beta of <strong>DcisionAI MCP Server</strong>, 
                an AI-powered business optimization tool that integrates directly with your IDE.</p>
                
                <h3>🚀 What You Get</h3>
                <ul>
                    <li><strong>6 Optimization Tools</strong> - Intent classification, data analysis, model building, optimization solving, workflow templates, and end-to-end execution</li>
                    <li><strong>21 Industry Workflows</strong> - Manufacturing, healthcare, retail, marketing, financial, logistics, and energy</li>
                    <li><strong>Real-time Optimization</strong> - Get instant mathematical models and business insights</li>
                    <li><strong>IDE Integration</strong> - Use optimization tools directly in Cursor IDE</li>
                </ul>
                
                <h3>📋 Getting Started</h3>
                
                <h4>Step 1: Accept Repository Access</h4>
                <p>You should have received a GitHub repository invitation. Please accept it to access the private repository.</p>
                
                <h4>Step 2: Install the MCP Server</h4>
                <pre><code># Install from private repository
pip install git+https://github.com/{self.config['github_org']}/{self.config['repo_name']}.git

# Or with authentication token
pip install git+https://&lt;your-token&gt;@github.com/{self.config['github_org']}/{self.config['repo_name']}.git</code></pre>
                
                <h4>Step 3: Configure Your IDE</h4>
                <p>Follow the installation guide in the repository to configure Cursor IDE.</p>
                
                <h4>Step 4: Join Our Community</h4>
                <ul>
                    <li><strong>Private Slack</strong>: <a href="{self.config.get('slack_invite_url', '#')}">Join here</a></li>
                    <li><strong>Support Email</strong>: support@dcisionai.com</li>
                    <li><strong>Documentation</strong>: Available in the repository</li>
                </ul>
                
                <h3>🔧 Quick Test</h3>
                <p>Once installed, try asking in Cursor:</p>
                <ul>
                    <li>"Help me optimize my supply chain costs"</li>
                    <li>"Show me available manufacturing workflows"</li>
                    <li>"Build a production planning model"</li>
                </ul>
                
                <h3>📞 Support</h3>
                <p>If you need help:</p>
                <ol>
                    <li>Check the documentation in the repository</li>
                    <li>Join our private Slack workspace</li>
                    <li>Email support@dcisionai.com</li>
                    <li>Create an issue in the private repository</li>
                </ol>
                
                <h3>🎯 What's Next</h3>
                <ul>
                    <li><strong>Week 1</strong>: Get familiar with the tools and workflows</li>
                    <li><strong>Week 2</strong>: Try real optimization problems</li>
                    <li><strong>Week 3</strong>: Provide feedback and suggestions</li>
                    <li><strong>Week 4</strong>: Advanced usage and optimization</li>
                </ul>
                
                <p>We're excited to have you on board!</p>
                
                <p>Best regards,<br>
                The DcisionAI Team</p>
                
                <hr>
                <p><em>This is a private beta. Please do not share this invitation or the repository access with others.</em></p>
            </body>
            </html>
            """
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config['email']
            msg['To'] = email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['email'], self.config['password'])
                server.send_message(msg)
            
            print(f"✅ Welcome email sent to {email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {email}: {e}")
            return False
    
    def send_slack_notification(self, name: str, company: str, email: str) -> bool:
        """Send Slack notification about new customer."""
        try:
            import requests
            
            message = {
                "text": f"🎉 New customer onboarded!",
                "attachments": [
                    {
                        "color": "good",
                        "fields": [
                            {"title": "Name", "value": name, "short": True},
                            {"title": "Company", "value": company, "short": True},
                            {"title": "Email", "value": email, "short": True},
                            {"title": "Date", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "short": True}
                        ]
                    }
                ]
            }
            
            response = requests.post(self.config['slack_webhook'], json=message)
            
            if response.status_code == 200:
                print("✅ Slack notification sent")
                return True
            else:
                print(f"❌ Failed to send Slack notification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending Slack notification: {e}")
            return False
    
    def onboard_customer(self, email: str, name: str, company: str, tier: str = "beta") -> bool:
        """Complete customer onboarding process."""
        print(f"🚀 Onboarding customer: {name} ({email})")
        
        # Check if customer already exists
        customer_id = email.lower().replace('@', '_at_').replace('.', '_')
        if customer_id in self.customers:
            print(f"⚠️  Customer {email} already exists")
            return False
        
        # Add to GitHub repository
        github_success = self.add_customer_to_github(email, name)
        
        # Send welcome email
        email_success = self.send_welcome_email(email, name, company)
        
        # Send Slack notification
        slack_success = self.send_slack_notification(name, company, email)
        
        # Add to customers database
        self.customers[customer_id] = {
            "email": email,
            "name": name,
            "company": company,
            "tier": tier,
            "status": "active",
            "joined_date": datetime.utcnow().isoformat(),
            "last_activity": None,
            "usage_count": 0,
            "github_added": github_success,
            "email_sent": email_success,
            "slack_notified": slack_success
        }
        
        self.save_customers()
        
        # Summary
        print(f"\n📊 Onboarding Summary for {name}:")
        print(f"  GitHub Access: {'✅' if github_success else '❌'}")
        print(f"  Welcome Email: {'✅' if email_success else '❌'}")
        print(f"  Slack Notification: {'✅' if slack_success else '❌'}")
        
        success = github_success and email_success
        if success:
            print(f"🎉 Customer {name} successfully onboarded!")
        else:
            print(f"⚠️  Customer {name} onboarded with some issues. Please check manually.")
        
        return success
    
    def list_customers(self):
        """List all customers."""
        if not self.customers:
            print("No customers found.")
            return
        
        print(f"{'Name':<20} {'Email':<30} {'Company':<20} {'Tier':<10} {'Status':<10}")
        print("-" * 90)
        
        for customer in self.customers.values():
            print(f"{customer['name']:<20} {customer['email']:<30} {customer['company']:<20} {customer['tier']:<10} {customer['status']:<10}")
    
    def get_onboarding_stats(self) -> Dict:
        """Get onboarding statistics."""
        if not self.customers:
            return {"total": 0, "active": 0, "success_rate": 0}
        
        total = len(self.customers)
        active = sum(1 for c in self.customers.values() if c['status'] == 'active')
        successful = sum(1 for c in self.customers.values() if c.get('github_added', False) and c.get('email_sent', False))
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        return {
            "total": total,
            "active": active,
            "successful": successful,
            "success_rate": success_rate
        }

def main():
    onboarding = CustomerOnboarding()
    
    print("🥷 DcisionAI Customer Onboarding System")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Onboard new customer")
        print("2. List customers")
        print("3. View statistics")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            email = input("Email: ").strip()
            name = input("Name: ").strip()
            company = input("Company: ").strip()
            tier = input("Tier (beta/pro/enterprise): ").strip() or "beta"
            
            onboarding.onboard_customer(email, name, company, tier)
        
        elif choice == "2":
            onboarding.list_customers()
        
        elif choice == "3":
            stats = onboarding.get_onboarding_stats()
            print(f"\n📊 Onboarding Statistics:")
            print(f"  Total Customers: {stats['total']}")
            print(f"  Active Customers: {stats['active']}")
            print(f"  Successful Onboardings: {stats['successful']}")
            print(f"  Success Rate: {stats['success_rate']:.1f}%")
        
        elif choice == "4":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
