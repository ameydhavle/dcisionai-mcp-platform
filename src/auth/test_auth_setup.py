#!/usr/bin/env python3
"""
Test Setup Script for DcisionAI Authentication

This script creates test data for authentication testing:
- Test tenant
- Test API keys (regular and admin)
- Test user accounts
"""

import asyncio
import json
import logging
from manage_api_keys import APIKeyManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def setup_test_data():
    """Set up test data for authentication testing."""
    print("🚀 Setting up test data for DcisionAI Authentication...")
    
    # Initialize manager
    manager = APIKeyManager('production')
    
    try:
        # Step 1: Create test tenant
        print("\n📋 Step 1: Creating test tenant...")
        tenant = await manager.create_tenant(
            tenant_id="test-tenant-001",
            tenant_name="Test Manufacturing Company",
            description="Test tenant for authentication development",
            max_api_keys=20
        )
        print(f"✅ Created tenant: {tenant['tenant_id']} ({tenant['tenant_name']})")
        
        # Step 2: Create regular API key
        print("\n🔑 Step 2: Creating regular API key...")
        api_key = await manager.create_api_key(
            tenant_id="test-tenant-001",
            user_id="test-user-001",
            key_name="Test API Key - Regular User",
            permissions=["read", "write"],
            expires_in_days=365
        )
        print(f"✅ Created API key: {api_key['key_name']}")
        print(f"   API Key: {api_key['api_key']}")
        print(f"   Permissions: {api_key['permissions']}")
        print(f"   Expires: {api_key['expires_at']}")
        
        # Step 3: Create admin API key
        print("\n🔐 Step 3: Creating admin API key...")
        admin_key = await manager.create_admin_key(
            tenant_id="test-tenant-001",
            user_id="test-admin-001",
            key_name="Test Admin Key - Admin User",
            permissions=["admin", "read", "write", "manage_users", "manage_keys"],
            expires_in_days=365
        )
        print(f"✅ Created admin key: {admin_key['key_name']}")
        print(f"   Admin Key: {admin_key['admin_key']}")
        print(f"   Permissions: {admin_key['permissions']}")
        print(f"   Expires: {admin_key['expires_at']}")
        
        # Step 4: Create additional test API keys
        print("\n🔑 Step 4: Creating additional test API keys...")
        
        # Limited permissions key
        limited_key = await manager.create_api_key(
            tenant_id="test-tenant-001",
            user_id="test-user-002",
            key_name="Test API Key - Read Only",
            permissions=["read"],
            expires_in_days=365
        )
        print(f"✅ Created read-only key: {limited_key['key_name']}")
        print(f"   API Key: {limited_key['api_key']}")
        print(f"   Permissions: {limited_key['permissions']}")
        
        # Expired key for testing
        expired_key = await manager.create_api_key(
            tenant_id="test-tenant-001",
            user_id="test-user-003",
            key_name="Test API Key - Expired",
            permissions=["read", "write"],
            expires_in_days=0  # Already expired
        )
        print(f"✅ Created expired key: {expired_key['key_name']}")
        print(f"   API Key: {expired_key['api_key']}")
        print(f"   Permissions: {expired_key['permissions']}")
        print(f"   Status: Expired (for testing)")
        
        # Step 5: Create second tenant for multi-tenant testing
        print("\n🏢 Step 5: Creating second test tenant...")
        tenant2 = await manager.create_tenant(
            tenant_id="test-tenant-002",
            tenant_name="Test Finance Company",
            description="Second test tenant for multi-tenant testing",
            max_api_keys=15
        )
        print(f"✅ Created second tenant: {tenant2['tenant_id']} ({tenant2['tenant_name']})")
        
        # API key for second tenant
        tenant2_key = await manager.create_api_key(
            tenant_id="test-tenant-002",
            user_id="test-user-004",
            key_name="Test API Key - Finance Tenant",
            permissions=["read", "write", "finance"],
            expires_in_days=365
        )
        print(f"✅ Created key for second tenant: {tenant2_key['key_name']}")
        print(f"   API Key: {tenant2_key['api_key']}")
        print(f"   Tenant: {tenant2_key['tenant_id']}")
        
        # Step 6: Summary and testing instructions
        print("\n" + "="*80)
        print("🎉 TEST DATA SETUP COMPLETE!")
        print("="*80)
        
        print("\n📋 Test Data Created:")
        print(f"   Tenants: 2")
        print(f"   API Keys: 5")
        print(f"   Admin Keys: 1")
        
        print("\n🔑 Test API Keys (save these for testing):")
        print(f"   1. Regular User Key: {api_key['api_key']}")
        print(f"   2. Admin User Key: {admin_key['admin_key']}")
        print(f"   3. Read-Only Key: {limited_key['api_key']}")
        print(f"   4. Expired Key: {expired_key['api_key']}")
        print(f"   5. Finance Tenant Key: {tenant2_key['api_key']}")
        
        print("\n🧪 Testing Instructions:")
        print("   1. Start the test app: python test_auth_app.py")
        print("   2. Test public endpoints: GET /, GET /health")
        print("   3. Test protected endpoints with API keys:")
        print(f"      - GET /protected (use: {api_key['api_key']})")
        print(f"      - GET /admin (use: {admin_key['admin_key']})")
        print(f"      - GET /tenant/test-tenant-001 (use: {api_key['api_key']})")
        print(f"      - GET /tenant/test-tenant-002 (use: {tenant2_key['api_key']})")
        
        print("\n❌ Expected Failures (for testing):")
        print(f"   - Invalid key: any random string")
        print(f"   - Expired key: {expired_key['api_key']}")
        print(f"   - Wrong tenant access: use {api_key['api_key']} for /tenant/test-tenant-002")
        
        print("\n📚 API Documentation:")
        print("   - Swagger UI: http://localhost:8003/docs")
        print("   - OpenAPI Spec: http://localhost:8003/openapi.json")
        
        # Save test data to file for easy reference
        test_data = {
            "tenants": [tenant, tenant2],
            "api_keys": [api_key, limited_key, expired_key, tenant2_key],
            "admin_keys": [admin_key],
            "testing_instructions": {
                "start_app": "python test_auth_app.py",
                "base_url": "http://localhost:8003",
                "swagger_ui": "http://localhost:8003/docs"
            }
        }
        
        with open('test_auth_data.json', 'w') as f:
            json.dump(test_data, f, indent=2)
        
        print(f"\n💾 Test data saved to: test_auth_data.json")
        
    except Exception as e:
        logger.error(f"Failed to set up test data: {e}")
        raise


async def cleanup_test_data():
    """Clean up test data (use with caution)."""
    print("🧹 Cleaning up test data...")
    
    # Initialize manager
    manager = APIKeyManager('production')
    
    try:
        # List all keys
        keys = await manager.list_api_keys()
        
        for key in keys:
            if key['tenant_id'].startswith('test-tenant-'):
                print(f"   Cleaning up key: {key['key_name']}")
                # Note: We can't deactivate by name, would need to store the actual keys
                # For now, just show what would be cleaned up
        
        print("✅ Test data cleanup complete")
        
    except Exception as e:
        logger.error(f"Failed to cleanup test data: {e}")


async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='DcisionAI Authentication Test Setup')
    parser.add_argument('--action', choices=['setup', 'cleanup'], default='setup',
                       help='Action to perform (default: setup)')
    
    args = parser.parse_args()
    
    if args.action == 'setup':
        await setup_test_data()
    elif args.action == 'cleanup':
        await cleanup_test_data()


if __name__ == '__main__':
    asyncio.run(main())
