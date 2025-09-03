"""
Setup DynamoDB Tables for DcisionAI Authentication Testing

This script creates the necessary DynamoDB tables for testing the authentication middleware
"""

import boto3
import json
from datetime import datetime, timedelta
import secrets

def create_dynamodb_tables():
    """Create DynamoDB tables for authentication testing."""
    
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    # Table configurations
    tables_config = [
        {
            'name': 'dcisionai-api-keys-dev',
            'key_schema': [
                {'AttributeName': 'api_key', 'KeyType': 'HASH'}
            ],
            'attribute_definitions': [
                {'AttributeName': 'api_key', 'AttributeType': 'S'}
            ],
            'billing_mode': 'PAY_PER_REQUEST'
        },
        {
            'name': 'dcisionai-admin-keys-dev',
            'key_schema': [
                {'AttributeName': 'admin_key', 'KeyType': 'HASH'}
            ],
            'attribute_definitions': [
                {'AttributeName': 'admin_key', 'AttributeType': 'S'}
            ],
            'billing_mode': 'PAY_PER_REQUEST'
        },
        {
            'name': 'dcisionai-tenants-dev',
            'key_schema': [
                {'AttributeName': 'tenant_id', 'KeyType': 'HASH'}
            ],
            'attribute_definitions': [
                {'AttributeName': 'tenant_id', 'AttributeType': 'S'}
            ],
            'billing_mode': 'PAY_PER_REQUEST'
        }
    ]
    
    created_tables = []
    
    for table_config in tables_config:
        table_name = table_config['name']
        
        try:
            # Check if table already exists
            existing_table = dynamodb.Table(table_name)
            existing_table.load()
            print(f"✅ Table {table_name} already exists")
            created_tables.append(existing_table)
            
        except dynamodb.meta.client.exceptions.ResourceNotFoundException:
            # Create table
            print(f"🔄 Creating table {table_name}...")
            
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=table_config['key_schema'],
                AttributeDefinitions=table_config['attribute_definitions'],
                BillingMode=table_config['billing_mode']
            )
            
            # Wait for table to be created
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            print(f"✅ Table {table_name} created successfully")
            created_tables.append(table)
    
    return created_tables

def create_sample_data():
    """Create sample data for testing."""
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    # Create sample tenant
    tenants_table = dynamodb.Table('dcisionai-tenants-dev')
    
    sample_tenant = {
        'tenant_id': 'test_tenant_001',
        'name': 'Test Tenant',
        'contact_email': 'test@dcisionai.com',
        'plan': 'starter',
        'status': 'active',
        'created_at': datetime.utcnow().isoformat(),
        'settings': {
            'max_concurrent_jobs': 10,
            'rate_limit': '1000/hour',
            'storage_limit_gb': 100
        }
    }
    
    try:
        tenants_table.put_item(Item=sample_tenant)
        print(f"✅ Sample tenant created: {sample_tenant['tenant_id']}")
    except Exception as e:
        print(f"⚠️  Could not create sample tenant: {e}")
    
    # Create sample admin key
    admin_keys_table = dynamodb.Table('dcisionai-admin-keys-dev')
    
    admin_key = f"dcisionai_admin_{int(datetime.utcnow().timestamp())}_{secrets.token_hex(8)}"
    
    sample_admin_key = {
        'admin_key': admin_key,
        'name': 'Test Admin Key',
        'status': 'active',
        'created_at': datetime.utcnow().isoformat(),
        'permissions': ['admin'],
        'tenant_id': 'test_tenant_001'
    }
    
    try:
        admin_keys_table.put_item(Item=sample_admin_key)
        print(f"✅ Sample admin key created: {admin_key}")
        print(f"⚠️  Please save this admin key securely for testing!")
    except Exception as e:
        print(f"⚠️  Could not create sample admin key: {e}")
    
    # Create sample API key
    api_keys_table = dynamodb.Table('dcisionai-api-keys-dev')
    
    api_key = f"dcisionai_api_{int(datetime.utcnow().timestamp())}_{secrets.token_hex(8)}"
    
    sample_api_key = {
        'api_key': api_key,
        'api_key_id': f"key_{secrets.token_hex(8)}",
        'name': 'Test API Key',
        'tenant_id': 'test_tenant_001',
        'user_id': 'test_user_001',
        'status': 'active',
        'created_at': datetime.utcnow().isoformat(),
        'expires_at': (datetime.utcnow() + timedelta(days=365)).isoformat(),
        'permissions': ['read', 'write'],
        'ip_restrictions': []
    }
    
    try:
        api_keys_table.put_item(Item=sample_api_key)
        print(f"✅ Sample API key created: {api_key}")
        print(f"⚠️  Please save this API key securely for testing!")
    except Exception as e:
        print(f"⚠️  Could not create sample API key: {e}")
    
    return {
        'tenant_id': sample_tenant['tenant_id'],
        'admin_key': admin_key,
        'api_key': api_key
    }

def test_authentication():
    """Test authentication with the created keys."""
    
    print("\n🧪 Testing Authentication...")
    
    # Get the sample keys
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    try:
        # Test API key lookup
        api_keys_table = dynamodb.Table('dcisionai-api-keys-dev')
        response = api_keys_table.scan(Limit=1)
        
        if response['Items']:
            api_key = response['Items'][0]['api_key']
            print(f"✅ API key lookup successful: {api_key[:20]}...")
        else:
            print("❌ No API keys found")
            
        # Test admin key lookup
        admin_keys_table = dynamodb.Table('dcisionai-admin-keys-dev')
        response = admin_keys_table.scan(Limit=1)
        
        if response['Items']:
            admin_key = response['Items'][0]['admin_key']
            print(f"✅ Admin key lookup successful: {admin_key[:20]}...")
        else:
            print("❌ No admin keys found")
            
        # Test tenant lookup
        tenants_table = dynamodb.Table('dcisionai-tenants-dev')
        response = tenants_table.scan(Limit=1)
        
        if response['Items']:
            tenant_id = response['Items'][0]['tenant_id']
            print(f"✅ Tenant lookup successful: {tenant_id}")
        else:
            print("❌ No tenants found")
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")

def main():
    """Main function to set up DynamoDB tables and sample data."""
    
    print("🚀 Setting up DynamoDB Tables for DcisionAI Authentication Testing")
    print("=" * 70)
    
    try:
        # Create tables
        print("\n📋 Creating DynamoDB Tables...")
        tables = create_dynamodb_tables()
        
        # Create sample data
        print("\n📝 Creating Sample Data...")
        sample_data = create_sample_data()
        
        # Test authentication
        test_authentication()
        
        print("\n" + "=" * 70)
        print("✅ Setup Complete!")
        print("\n📋 Sample Data Created:")
        print(f"   Tenant ID: {sample_data['tenant_id']}")
        print(f"   Admin Key: {sample_data['admin_key']}")
        print(f"   API Key: {sample_data['api_key']}")
        print("\n⚠️  IMPORTANT: Save these keys securely for testing!")
        print("\n🔗 Next Steps:")
        print("   1. Update your environment variables with these table names")
        print("   2. Test the authentication middleware with these keys")
        print("   3. Use the API key to test protected endpoints")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
