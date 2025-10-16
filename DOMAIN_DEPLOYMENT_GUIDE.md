# 🌐 Domain Deployment Guide - www.dcisionai.com

## 🎯 **Deployment Overview**

Your seamless configuration system is now configured to use your domain `www.dcisionai.com`. Here's how to deploy it:

### **What Needs to Be Deployed:**

1. **Installation Script**: `install-dcisionai-mcp.sh`
2. **Configuration Web Page**: `customer-configuration.html`
3. **Configuration Server**: `customer-config-server.py` (optional)
4. **Customer Token System**: `generate-customer-token.py` (backend)

## 🚀 **Deployment Steps**

### **Step 1: Upload Files to Your Domain**

#### **Required Files:**
```bash
# Upload these files to your web server root:
install-dcisionai-mcp.sh          # Installation script
customer-configuration.html       # Main configuration page
customer-config-server.py         # Configuration server (optional)
generate-customer-token.py        # Token generator (backend)
```

#### **File Locations on Server:**
```
www.dcisionai.com/
├── install-dcisionai-mcp.sh      # https://www.dcisionai.com/install-dcisionai-mcp.sh
├── customer-configuration.html   # https://www.dcisionai.com/
├── configure/                    # https://www.dcisionai.com/configure?token=xxx
└── api/                         # Backend API endpoints
    ├── tokens/                  # Token management
    └── validate/                # Token validation
```

### **Step 2: Configure Web Server**

#### **Apache Configuration (.htaccess):**
```apache
# Enable HTTPS redirect
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Serve installation script with correct headers
<Files "install-dcisionai-mcp.sh">
    Header set Content-Type "text/plain"
    Header set Content-Disposition "attachment; filename=install-dcisionai-mcp.sh"
</Files>

# Enable CORS for API endpoints
<IfModule mod_headers.c>
    Header set Access-Control-Allow-Origin "*"
    Header set Access-Control-Allow-Methods "GET, POST, OPTIONS"
    Header set Access-Control-Allow-Headers "Content-Type, Authorization"
</IfModule>
```

#### **Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name www.dcisionai.com dcisionai.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name www.dcisionai.com dcisionai.com;
    
    # SSL configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;
    
    # Root directory
    root /var/www/dcisionai.com;
    index customer-configuration.html;
    
    # Serve installation script
    location /install-dcisionai-mcp.sh {
        add_header Content-Type text/plain;
        add_header Content-Disposition "attachment; filename=install-dcisionai-mcp.sh";
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **Step 3: Set Up Backend Services**

#### **Option 1: Simple File-Based (Recommended for Start)**
```bash
# Upload files directly to web server
# No backend services needed
# Customer tokens stored in JSON files
```

#### **Option 2: Full Backend Service**
```bash
# Deploy customer-config-server.py as a service
# Set up database for customer tokens
# Implement API endpoints for token management
```

### **Step 4: Test Deployment**

#### **Test Installation Script:**
```bash
# Test that the script is accessible
curl -I https://www.dcisionai.com/install-dcisionai-mcp.sh

# Test that it downloads correctly
curl -sSL https://www.dcisionai.com/install-dcisionai-mcp.sh | head -10
```

#### **Test Configuration Page:**
```bash
# Test main page
curl -I https://www.dcisionai.com/

# Test with customer token
curl -I "https://www.dcisionai.com/configure?token=test-token"
```

## 🎯 **Customer Experience with Your Domain**

### **What Customers See:**

1. **Professional Domain**: `www.dcisionai.com` (trustworthy and branded)
2. **Secure HTTPS**: All traffic encrypted
3. **Fast Loading**: Optimized for performance
4. **Mobile Responsive**: Works on all devices

### **Customer Journey:**
```
1. Customer receives email with link: https://www.dcisionai.com/configure?token=abc123
2. Clicks link → Personalized configuration page loads
3. Copies install command: curl -sSL https://www.dcisionai.com/install-dcisionai-mcp.sh | bash
4. Runs command → MCP server installs automatically
5. Gets access token → Configures and starts optimizing
```

## 🛠️ **Quick Deployment Commands**

### **Upload Files (using SCP):**
```bash
# Upload to your web server
scp install-dcisionai-mcp.sh user@your-server:/var/www/dcisionai.com/
scp customer-configuration.html user@your-server:/var/www/dcisionai.com/
scp customer-config-server.py user@your-server:/var/www/dcisionai.com/
scp generate-customer-token.py user@your-server:/var/www/dcisionai.com/
```

### **Set Permissions:**
```bash
# Make scripts executable
chmod +x /var/www/dcisionai.com/install-dcisionai-mcp.sh
chmod +x /var/www/dcisionai.com/customer-config-server.py
chmod +x /var/www/dcisionai.com/generate-customer-token.py
```

### **Test Deployment:**
```bash
# Test installation script
curl -sSL https://www.dcisionai.com/install-dcisionai-mcp.sh | head -5

# Test configuration page
curl -I https://www.dcisionai.com/
```

## 📊 **Monitoring and Analytics**

### **Track Customer Usage:**
```bash
# Monitor installation script downloads
tail -f /var/log/nginx/access.log | grep install-dcisionai-mcp.sh

# Monitor configuration page visits
tail -f /var/log/nginx/access.log | grep configure
```

### **Set Up Analytics:**
```bash
# Add Google Analytics to customer-configuration.html
# Track customer conversion rates
# Monitor installation success rates
```

## 🔒 **Security Considerations**

### **HTTPS Required:**
- ✅ **SSL Certificate** installed and working
- ✅ **HTTP to HTTPS redirect** configured
- ✅ **Secure headers** set properly

### **Access Control:**
- ✅ **Customer tokens** for access control
- ✅ **Rate limiting** on API endpoints
- ✅ **Input validation** on all forms

### **Monitoring:**
- ✅ **Error logging** enabled
- ✅ **Access logging** configured
- ✅ **Security monitoring** in place

## 🎉 **Ready for Production**

Once deployed, your customers will have a **professional, seamless experience**:

- ✅ **Branded domain**: `www.dcisionai.com`
- ✅ **One-click installation**: `curl -sSL https://www.dcisionai.com/install-dcisionai-mcp.sh | bash`
- ✅ **Personalized configuration**: `https://www.dcisionai.com/configure?token=customer-token`
- ✅ **Secure and fast**: HTTPS with optimized performance
- ✅ **Mobile responsive**: Works on all devices

**Your domain deployment is ready to provide a professional customer experience!** 🚀

---

**Next Steps:**
1. Upload files to your web server
2. Configure SSL and redirects
3. Test the complete customer journey
4. Start onboarding your first customers
