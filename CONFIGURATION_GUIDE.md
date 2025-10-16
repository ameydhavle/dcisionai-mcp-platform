# 🔧 Configuration Guide - DcisionAI Stealth Mode

## 📋 **Required Configuration Steps**

### **1. Email Configuration (Gmail)**

To send automated welcome emails to customers, you need to configure Gmail:

#### **Step 1: Enable 2-Factor Authentication**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication if not already enabled

#### **Step 2: Generate App Password**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click "App passwords" under "2-Step Verification"
3. Select "Mail" and "Other (custom name)"
4. Enter "DcisionAI MCP Server"
5. Copy the generated 16-character password

#### **Step 3: Update Configuration**
```bash
# Edit the configuration file
nano onboarding-config.json

# Update these fields:
{
  "email": "your-email@gmail.com",
  "password": "your-16-character-app-password"
}
```

### **2. Slack Configuration (Optional)**

For team notifications when customers are onboarded:

#### **Step 1: Create Slack Webhook**
1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app
3. Go to "Incoming Webhooks"
4. Create a webhook for your channel
5. Copy the webhook URL

#### **Step 2: Update Configuration**
```bash
# Update the configuration file
{
  "slack_webhook": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
}
```

### **3. Analytics Configuration (Optional)**

For usage tracking and analytics:

#### **Step 1: Set Up Analytics Endpoint**
You can use any analytics service or create a simple endpoint to receive usage data.

#### **Step 2: Update Configuration**
```bash
# Update the configuration file
{
  "analytics_endpoint": "https://your-analytics.com/api/usage"
}
```

## 🚀 **Quick Configuration**

### **Minimal Setup (Required)**
```bash
# Edit the configuration file
nano onboarding-config.json

# Update only these required fields:
{
  "email": "your-email@gmail.com",
  "password": "your-app-password",
  "github_org": "ameydhavle",
  "repo_name": "dcisionai-mcp-server"
}
```

### **Full Setup (Recommended)**
```bash
# Update all fields for complete functionality
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "email": "your-email@gmail.com",
  "password": "your-app-password",
  "github_org": "ameydhavle",
  "repo_name": "dcisionai-mcp-server",
  "slack_webhook": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
  "slack_invite_url": "https://join.slack.com/t/dcisionai/shared_invite/your-invite-link",
  "analytics_endpoint": "https://your-analytics.com/api/usage"
}
```

## 🔐 **Security Notes**

1. **Never commit passwords** to version control
2. **Use app passwords** instead of your main password
3. **Keep configuration files private**
4. **Use environment variables** for production

## ✅ **Configuration Checklist**

- [ ] Gmail app password generated
- [ ] Email configuration updated
- [ ] GitHub organization set correctly
- [ ] Repository name confirmed
- [ ] Slack webhook configured (optional)
- [ ] Analytics endpoint set up (optional)

## 🧪 **Test Configuration**

After updating the configuration, test it:

```bash
# Test the onboarding system
python onboard-customer.py

# This will create the configuration file if it doesn't exist
# and allow you to test the email and GitHub integration
```

## 📞 **Need Help?**

If you need help with configuration:
1. Check the error messages in the console
2. Verify your credentials are correct
3. Test each service individually
4. Check firewall and network settings

---

**Once configured, you'll be ready to onboard your first beta customers!**
