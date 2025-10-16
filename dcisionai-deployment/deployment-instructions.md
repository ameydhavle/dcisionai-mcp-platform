# 🚀 Deployment Instructions for www.dcisionai.com

## 📋 **Files to Upload**

Upload these files to your web server root directory:

```bash
# Required files:
install-dcisionai-mcp.sh          # Installation script
customer-configuration.html       # Main configuration page
customer-config-server.py         # Configuration server (optional)
generate-customer-token.py        # Token generator (backend)
```

## 🌐 **URL Structure**

After deployment, these URLs should work:

- **Main page**: https://www.dcisionai.com/
- **Installation script**: https://www.dcisionai.com/install-dcisionai-mcp.sh
- **Customer configuration**: https://www.dcisionai.com/configure?token=customer-token

## 🔧 **Server Configuration**

### **Apache (.htaccess)**
```apache
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

<Files "install-dcisionai-mcp.sh">
    Header set Content-Type "text/plain"
    Header set Content-Disposition "attachment; filename=install-dcisionai-mcp.sh"
</Files>
```

### **Nginx**
```nginx
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
```

## 🧪 **Testing Commands**

```bash
# Test installation script
curl -I https://www.dcisionai.com/install-dcisionai-mcp.sh

# Test main page
curl -I https://www.dcisionai.com/

# Test with customer token
curl -I "https://www.dcisionai.com/configure?token=test-token"
```

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

