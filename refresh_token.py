#!/usr/bin/env python3

import requests
import json
import base64
from urllib.parse import urlencode

def refresh_access_token():
    """Get a fresh access token from Cognito"""
    
    # Load client info from gateway config
    with open('agentcore/gateway_config.json', 'r') as f:
        config = json.load(f)
    
    client_info = config['client_info']
    
    # Prepare the token request
    token_url = client_info['token_endpoint']
    
    # Create basic auth header
    client_credentials = f"{client_info['client_id']}:{client_info['client_secret']}"
    encoded_credentials = base64.b64encode(client_credentials.encode()).decode()
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {encoded_credentials}'
    }
    
    # Request body for client credentials grant
    data = {
        'grant_type': 'client_credentials',
        'scope': client_info['scope']
    }
    
    print(f"Requesting token from: {token_url}")
    print(f"Scope: {client_info['scope']}")
    
    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data['access_token']
        
        print(f"✅ New access token obtained!")
        print(f"Token expires in: {token_data.get('expires_in', 'unknown')} seconds")
        
        # Update the gateway config with new token
        config['access_token'] = access_token
        with open('agentcore/gateway_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Gateway config updated with new token")
        
        return access_token
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting token: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

if __name__ == "__main__":
    refresh_access_token()
