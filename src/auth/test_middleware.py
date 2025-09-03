"""
Simple test script for DcisionAI Authentication Middleware

This script tests the basic functionality without running a full server
"""

import asyncio
import json
from datetime import datetime

# Import our modules
from config import get_minimal_config, get_dev_config
from middleware import generate_api_key, hash_secret, verify_secret

def test_config():
    """Test configuration loading."""
    print("🧪 Testing Configuration...")
    
    # Test minimal config
    minimal_config = get_minimal_config()
    print(f"✅ Minimal config loaded: {minimal_config['environment']}")
    
    # Test dev config
    dev_config = get_dev_config()
    print(f"✅ Dev config loaded: {dev_config.environment}")
    
    # Test config validation
    from config import validate_auth_config
    errors = validate_auth_config(dev_config)
    if errors:
        print(f"⚠️  Config validation errors: {errors}")
    else:
        print("✅ Config validation passed")
    
    print()

def test_utilities():
    """Test utility functions."""
    print("🧪 Testing Utility Functions...")
    
    # Test API key generation
    api_key = generate_api_key("test")
    print(f"✅ API key generated: {api_key}")
    
    # Test secret hashing
    secret = "my-secret-password"
    hashed = hash_secret(secret)
    print(f"✅ Secret hashed: {hashed}")
    
    # Test secret verification
    is_valid = verify_secret(secret, hashed)
    print(f"✅ Secret verification: {is_valid}")
    
    # Test invalid secret
    is_invalid = verify_secret("wrong-password", hashed)
    print(f"✅ Invalid secret rejected: {not is_invalid}")
    
    print()

def test_auth_context():
    """Test AuthContext dataclass."""
    print("🧪 Testing AuthContext...")
    
    from middleware import AuthContext
    
    # Create auth context
    auth_context = AuthContext(
        tenant_id="test_tenant",
        user_id="test_user",
        permissions=["read", "write"],
        api_key_id="key_123",
        auth_method="api_key",
        ip_address="127.0.0.1",
        rate_limit_key="rate_limit:test_tenant:test_user"
    )
    
    print(f"✅ AuthContext created: {auth_context.tenant_id}")
    print(f"   User ID: {auth_context.user_id}")
    print(f"   Permissions: {auth_context.permissions}")
    print(f"   Auth Method: {auth_context.auth_method}")
    
    print()

def test_rate_limit_info():
    """Test RateLimitInfo dataclass."""
    print("🧪 Testing RateLimitInfo...")
    
    from middleware import RateLimitInfo
    
    # Create rate limit info
    rate_limit = RateLimitInfo(
        current=5,
        limit=100,
        reset_time=datetime.utcnow(),
        remaining=95
    )
    
    print(f"✅ RateLimitInfo created: {rate_limit.current}/{rate_limit.limit}")
    print(f"   Remaining: {rate_limit.remaining}")
    print(f"   Reset Time: {rate_limit.reset_time}")
    
    print()

async def test_middleware_initialization():
    """Test middleware initialization."""
    print("🧪 Testing Middleware Initialization...")
    
    try:
        from middleware import AuthenticationMiddleware
        
        # Get minimal config
        config = get_minimal_config()
        
        # Create middleware instance
        middleware = AuthenticationMiddleware(None, config)
        print("✅ Middleware initialized successfully")
        
        # Test configuration access
        print(f"   Environment: {middleware.config['environment']}")
        print(f"   API Keys Table: {middleware.config['api_keys_table']}")
        print(f"   Rate Limiting: {middleware.config['rate_limiting']['enabled']}")
        
    except Exception as e:
        print(f"❌ Middleware initialization failed: {e}")
    
    print()

def main():
    """Main test function."""
    print("🚀 DcisionAI Authentication Middleware Tests")
    print("=" * 50)
    
    # Run tests
    test_config()
    test_utilities()
    test_auth_context()
    test_rate_limit_info()
    
    # Run async tests
    asyncio.run(test_middleware_initialization())
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
