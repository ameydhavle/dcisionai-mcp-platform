#!/usr/bin/env python3
"""
Customer Configuration Server for DcisionAI MCP Server
Serves the configuration page and handles customer tokens
"""

import os
import json
import hashlib
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser
import threading
import time

class CustomerConfigHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.tokens_file = "customer-tokens.json"
        super().__init__(*args, **kwargs)
    
    def load_tokens(self):
        """Load customer tokens from file."""
        if os.path.exists(self.tokens_file):
            with open(self.tokens_file, 'r') as f:
                return json.load(f)
        return {}
    
    def validate_token(self, token):
        """Validate a customer token."""
        tokens = self.load_tokens()
        
        if token not in tokens:
            return None
        
        token_record = tokens[token]
        
        # Check if token is active
        if token_record["status"] != "active":
            return None
        
        # Check if token has expired
        expires_at = datetime.fromisoformat(token_record["expires_at"])
        if datetime.utcnow() > expires_at:
            return None
        
        return token_record
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        if path == "/":
            self.serve_configuration_page()
        elif path == "/configure":
            token = query_params.get('token', [None])[0]
            if token:
                self.serve_customer_configuration(token)
            else:
                self.serve_configuration_page()
        elif path == "/install":
            self.serve_install_script()
        elif path == "/status":
            self.serve_status_page()
        else:
            self.send_error(404, "Not Found")
    
    def serve_configuration_page(self):
        """Serve the main configuration page."""
        try:
            with open("customer-configuration.html", "r") as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode())
        except FileNotFoundError:
            self.send_error(404, "Configuration page not found")
    
    def serve_customer_configuration(self, token):
        """Serve personalized configuration page for a customer."""
        token_record = self.validate_token(token)
        
        if not token_record:
            self.send_error(401, "Invalid or expired token")
            return
        
        # Create personalized configuration page
        content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DcisionAI MCP Server - Configuration</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 600px;
            width: 100%;
            text-align: center;
        }}
        
        .logo {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 1.1rem;
            margin-bottom: 30px;
        }}
        
        .welcome {{
            background: #e8f5e8;
            border: 1px solid #4caf50;
            color: #2e7d32;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
        }}
        
        .step {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }}
        
        .step-number {{
            background: #667eea;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
        }}
        
        .step-title {{
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .step-description {{
            color: #666;
            line-height: 1.6;
        }}
        
        .install-button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin: 20px 0;
            display: inline-block;
            text-decoration: none;
        }}
        
        .install-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }}
        
        .code-block {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 10px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9rem;
            margin: 15px 0;
            text-align: left;
            overflow-x: auto;
        }}
        
        .token-info {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: left;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🚀 DcisionAI</div>
        <div class="subtitle">AI-Powered Business Optimization MCP Server</div>
        
        <div class="welcome">
            <strong>Welcome, {token_record['customer_name']}!</strong><br>
            You're all set to configure your DcisionAI MCP Server.
        </div>
        
        <div class="token-info">
            <strong>Your Configuration Details:</strong><br>
            • Company: {token_record['company']}<br>
            • Industry: {token_record['industry']}<br>
            • Use Case: {token_record['use_case']}<br>
            • Token: {token[:8]}...{token[-8:]}<br>
            • Expires: {token_record['expires_at'][:10]}
        </div>
        
        <div class="step">
            <div class="step-title">
                <span class="step-number">1</span>
                One-Click Installation
            </div>
            <div class="step-description">
                Run this command to install and configure everything automatically:
            </div>
            <div class="code-block">
curl -sSL https://www.dcisionai.com/install-dcisionai-mcp.sh | bash
            </div>
            <a href="#" class="install-button" onclick="copyInstallCommand()">📋 Copy Install Command</a>
        </div>
        
        <div class="step">
            <div class="step-title">
                <span class="step-number">2</span>
                Get Your Access Token
            </div>
            <div class="step-description">
                Your personalized access token has been generated. Contact DcisionAI support to get your token.
            </div>
        </div>
        
        <div class="step">
            <div class="step-title">
                <span class="step-number">3</span>
                Configure Cursor IDE
            </div>
            <div class="step-description">
                The installation script automatically configures Cursor IDE integration. Just restart Cursor and you're ready to go!
            </div>
        </div>
        
        <div class="step">
            <div class="step-title">
                <span class="step-number">4</span>
                Start Optimizing
            </div>
            <div class="step-description">
                Ask Cursor IDE to help you with optimization problems:
            </div>
            <div class="code-block">
"Help me optimize my {token_record['use_case'].lower()}"
"Show me available {token_record['industry']} workflows"
"Build a model for my {token_record['company']} optimization needs"
            </div>
        </div>
        
        <div class="footer">
            <p>
                <strong>Need Help?</strong><br>
                📧 Email: <a href="mailto:support@dcisionai.com">support@dcisionai.com</a><br>
                📚 Documentation: <a href="https://github.com/ameydhavle/dcisionai-mcp-server">GitHub Repository</a>
            </p>
        </div>
    </div>
    
    <script>
        function copyInstallCommand() {{
            const command = 'curl -sSL https://www.dcisionai.com/install-dcisionai-mcp.sh | bash';
            
            if (navigator.clipboard) {{
                navigator.clipboard.writeText(command).then(() => {{
                    alert('✅ Install command copied to clipboard!');
                }});
            }} else {{
                const textArea = document.createElement('textarea');
                textArea.value = command;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('✅ Install command copied to clipboard!');
            }}
        }}
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())
    
    def serve_install_script(self):
        """Serve the installation script."""
        try:
            with open("install-dcisionai-mcp.sh", "r") as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(content.encode())
        except FileNotFoundError:
            self.send_error(404, "Install script not found")
    
    def serve_status_page(self):
        """Serve a status page showing server information."""
        tokens = self.load_tokens()
        total_tokens = len(tokens)
        active_tokens = sum(1 for t in tokens.values() if t["status"] == "active")
        
        content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>DcisionAI Configuration Server Status</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .status {{ background: #e8f5e8; padding: 20px; border-radius: 10px; }}
        .stats {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>🚀 DcisionAI Configuration Server</h1>
    <div class="status">
        <h2>Server Status: ✅ Online</h2>
        <p>Server is running and ready to serve customer configurations.</p>
    </div>
    
    <div class="stats">
        <h2>📊 Statistics</h2>
        <p>Total Tokens: {total_tokens}</p>
        <p>Active Tokens: {active_tokens}</p>
        <p>Server Time: {datetime.utcnow().isoformat()}</p>
    </div>
    
    <p><a href="/">← Back to Configuration Page</a></p>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())
    
    def log_message(self, format, *args):
        """Override to reduce log noise."""
        pass

def start_server(port=8080):
    """Start the customer configuration server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, CustomerConfigHandler)
    
    print(f"🚀 DcisionAI Configuration Server starting on port {port}")
    print(f"📱 Configuration page: http://localhost:{port}")
    print(f"📊 Status page: http://localhost:{port}/status")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="DcisionAI Customer Configuration Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the server on")
    parser.add_argument("--open", action="store_true", help="Open browser automatically")
    
    args = parser.parse_args()
    
    if args.open:
        # Open browser in a separate thread
        def open_browser():
            time.sleep(1)  # Wait for server to start
            webbrowser.open(f"http://localhost:{args.port}")
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    start_server(args.port)

if __name__ == "__main__":
    main()
