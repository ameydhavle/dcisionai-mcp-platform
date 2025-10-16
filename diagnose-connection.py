#!/usr/bin/env python3
"""
Simple diagnostic tool to check AgentCore Gateway connection
"""

import json
import os
import sys
from datetime import datetime

def check_config():
    """Check configuration files."""
    print("🔍 Checking Configuration...")
    
    # Check config.json
    config_path = "aws-deployment/config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print("✅ config.json found")
            print(f"   Gateway URL: {config.get('gateway_url', 'Not set')}")
            print(f"   Access Token: {'Set' if config.get('access_token') else 'Not set'}")
            return config
        except Exception as e:
            print(f"❌ Error reading config.json: {e}")
    else:
        print("❌ config.json not found")
    
    return None

def check_env():
    """Check environment variables."""
    print("\n🔍 Checking Environment Variables...")
    
    env_vars = [
        'DCISIONAI_ACCESS_TOKEN',
        'DCISIONAI_GATEWAY_URL', 
        'DCISIONAI_GATEWAY_TARGET'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set")

def check_token_expiry(config):
    """Check if access token is expired."""
    if not config or not config.get('access_token'):
        return
    
    print("\n🔍 Checking Token Expiry...")
    
    try:
        import jwt
        token = config['access_token']
        
        # Decode without verification to check expiry
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        exp = decoded.get('exp')
        if exp:
            exp_date = datetime.fromtimestamp(exp)
            now = datetime.now()
            
            if now > exp_date:
                print(f"❌ Token expired on: {exp_date}")
                print("   You need to refresh the token")
            else:
                print(f"✅ Token valid until: {exp_date}")
        else:
            print("⚠️ No expiry found in token")
            
    except ImportError:
        print("⚠️ PyJWT not installed - cannot check token expiry")
    except Exception as e:
        print(f"⚠️ Error checking token: {e}")

def test_simple_connection():
    """Test basic connection to AgentCore Gateway."""
    print("\n🔍 Testing AgentCore Gateway Connection...")
    
    config = check_config()
    if not config:
        print("❌ Cannot test connection - no configuration found")
        return
    
    gateway_url = config.get('gateway_url')
    access_token = config.get('access_token')
    
    if not gateway_url or not access_token:
        print("❌ Missing gateway URL or access token")
        return
    
    try:
        import urllib.request
        import urllib.parse
        
        # Create a simple test request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        # Test payload
        test_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        data = json.dumps(test_payload).encode('utf-8')
        
        req = urllib.request.Request(gateway_url, data=data, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                print("✅ Connection successful!")
                print(f"   Status: {response.status}")
                print("   AgentCore Gateway is responding")
            else:
                print(f"❌ Connection failed: {response.status}")
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
        if e.code == 401:
            print("   This usually means the access token is invalid or expired")
        elif e.code == 403:
            print("   This usually means insufficient permissions")
    except urllib.error.URLError as e:
        print(f"❌ URL Error: {e.reason}")
        print("   Check your internet connection and gateway URL")
    except Exception as e:
        print(f"❌ Connection error: {e}")

def main():
    print("🚀 DcisionAI MCP Server - Connection Diagnostic")
    print("=" * 50)
    
    # Check configuration
    config = check_config()
    
    # Check environment variables
    check_env()
    
    # Check token expiry
    check_token_expiry(config)
    
    # Test connection
    test_simple_connection()
    
    print("\n📋 Summary:")
    print("If you see connection errors:")
    print("1. Check your internet connection")
    print("2. Verify the gateway URL is correct")
    print("3. Refresh your access token if expired")
    print("4. Check AgentCore Gateway status")
    print("\nTo refresh token, run: python3 refresh_token.py")

if __name__ == "__main__":
    main()
