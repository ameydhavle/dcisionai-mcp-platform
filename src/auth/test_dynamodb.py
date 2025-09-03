"""
Test DynamoDB connection and API key lookup
"""

import boto3
import json

def test_dynamodb_connection():
    """Test DynamoDB connection and API key lookup."""
    
    print("🧪 Testing DynamoDB Connection...")
    
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Test API key lookup
        api_keys_table = dynamodb.Table('dcisionai-api-keys-dev')
        
        # Test with the API key we created
        api_key = 'dcisionai_api_1756862172_a63431f557a528a5'
        
        print(f"🔍 Looking up API key: {api_key[:20]}...")
        
        response = api_keys_table.get_item(Key={'api_key': api_key})
        
        if 'Item' in response:
            item = response['Item']
            print("✅ API key found!")
            print(f"   Tenant ID: {item.get('tenant_id')}")
            print(f"   User ID: {item.get('user_id')}")
            print(f"   Status: {item.get('status')}")
            print(f"   Permissions: {item.get('permissions')}")
            print(f"   Expires At: {item.get('expires_at')}")
        else:
            print("❌ API key not found")
            print(f"   Response: {response}")
        
        # Test admin key lookup
        admin_keys_table = dynamodb.Table('dcisionai-admin-keys-dev')
        admin_key = 'dcisionai_admin_1756862172_007c22df528abf58'
        
        print(f"\n🔍 Looking up Admin key: {admin_key[:20]}...")
        
        response = admin_keys_table.get_item(Key={'admin_key': admin_key})
        
        if 'Item' in response:
            item = response['Item']
            print("✅ Admin key found!")
            print(f"   Tenant ID: {item.get('tenant_id')}")
            print(f"   Status: {item.get('status')}")
            print(f"   Permissions: {item.get('permissions')}")
        else:
            print("❌ Admin key not found")
            print(f"   Response: {response}")
        
        # Test tenant lookup
        tenants_table = dynamodb.Table('dcisionai-tenants-dev')
        tenant_id = 'test_tenant_001'
        
        print(f"\n🔍 Looking up Tenant: {tenant_id}")
        
        response = tenants_table.get_item(Key={'tenant_id': tenant_id})
        
        if 'Item' in response:
            item = response['Item']
            print("✅ Tenant found!")
            print(f"   Name: {item.get('name')}")
            print(f"   Status: {item.get('status')}")
            print(f"   Plan: {item.get('plan')}")
        else:
            print("❌ Tenant not found")
            print(f"   Response: {response}")
        
    except Exception as e:
        print(f"❌ DynamoDB test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dynamodb_connection()
