#!/usr/bin/env python3
"""
API Key Management Script for DcisionAI Platform

This script provides comprehensive API key management functionality:
- Generate secure API keys
- Create API keys in DynamoDB
- Validate API keys
- List and manage existing keys
- Test authentication

Usage:
    python manage_api_keys.py --action create --tenant-id tenant123 --user-id user456
    python manage_api_keys.py --action validate --api-key your-api-key-here
    python manage_api_keys.py --action list --tenant-id tenant123
    python manage_api_keys.py --action test-auth --api-key your-api-key-here
"""

import argparse
import asyncio
import boto3
import hashlib
import json
import logging
import secrets
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class APIKeyManager:
    """Manages API keys for DcisionAI Platform."""
    
    def __init__(self, environment: str = 'production'):
        self.environment = environment
        self.dynamodb = boto3.resource('dynamodb')
        
        # Table names
        self.api_keys_table = self.dynamodb.Table(f'dcisionai-api-keys-{environment}')
        self.admin_keys_table = self.dynamodb.Table(f'dcisionai-admin-keys-{environment}')
        self.tenants_table = self.dynamodb.Table(f'dcisionai-tenants-{environment}')
        
        logger.info(f"Initialized API Key Manager for environment: {environment}")
    
    def generate_api_key(self, length: int = 32) -> str:
        """Generate a cryptographically secure API key."""
        # Generate random bytes and convert to hex
        random_bytes = secrets.token_bytes(length)
        api_key = random_bytes.hex()
        
        # Add prefix for identification
        return f"dcisionai_{api_key}"
    
    def generate_admin_key(self, length: int = 32) -> str:
        """Generate a cryptographically secure admin key."""
        # Generate random bytes and convert to hex
        random_bytes = secrets.token_bytes(length)
        admin_key = random_bytes.hex()
        
        # Add prefix for identification
        return f"dcisionai_admin_{admin_key}"
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for secure storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    async def create_tenant(self, tenant_id: str, tenant_name: str, 
                           description: str = "", max_api_keys: int = 10) -> Dict[str, Any]:
        """Create a new tenant in DynamoDB."""
        try:
            tenant_data = {
                'tenant_id': tenant_id,
                'tenant_name': tenant_name,
                'description': description,
                'max_api_keys': max_api_keys,
                'status': 'active',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'settings': {
                    'rate_limit_per_minute': 1000,
                    'rate_limit_burst': 100,
                    'ip_restrictions': [],
                    'allowed_domains': []
                }
            }
            
            await asyncio.to_thread(
                self.tenants_table.put_item,
                Item=tenant_data
            )
            
            logger.info(f"Created tenant: {tenant_id} ({tenant_name})")
            return tenant_data
            
        except Exception as e:
            logger.error(f"Failed to create tenant {tenant_id}: {e}")
            raise
    
    async def create_api_key(self, tenant_id: str, user_id: str, 
                           key_name: str, permissions: List[str] = None,
                           expires_in_days: int = 365, ip_restrictions: List[str] = None) -> Dict[str, Any]:
        """Create a new API key for a tenant."""
        try:
            # Generate API key
            api_key = self.generate_api_key()
            api_key_hash = self.hash_api_key(api_key)
            
            # Set default permissions if none provided
            if permissions is None:
                permissions = ['read', 'write']
            
            # Calculate expiration
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
            # Create API key record
            api_key_data = {
                'api_key': api_key,  # Store the original API key for lookup
                'tenant_id': tenant_id,
                'user_id': user_id,
                'key_name': key_name,
                'permissions': permissions,
                'status': 'active',
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': expires_at.isoformat(),
                'last_used_at': None,
                'usage_count': 0,
                'ip_restrictions': ip_restrictions or [],
                'metadata': {
                    'created_by': 'api_key_manager',
                    'environment': self.environment
                }
            }
            
            # Store in DynamoDB (hash the key for security)
            await asyncio.to_thread(
                self.api_keys_table.put_item,
                Item=api_key_data
            )
            
            # Return the actual API key (only shown once)
            result = {
                'api_key': api_key,
                'api_key_hash': api_key_hash,
                'tenant_id': tenant_id,
                'user_id': user_id,
                'key_name': key_name,
                'permissions': permissions,
                'expires_at': expires_at.isoformat(),
                'warning': 'Store this API key securely - it will not be shown again!'
            }
            
            logger.info(f"Created API key '{key_name}' for tenant {tenant_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create API key for tenant {tenant_id}: {e}")
            raise
    
    async def create_admin_key(self, tenant_id: str, user_id: str,
                             key_name: str, permissions: List[str] = None,
                             expires_in_days: int = 365) -> Dict[str, Any]:
        """Create a new admin key for a tenant."""
        try:
            # Generate admin key
            admin_key = self.generate_admin_key()
            admin_key_hash = self.hash_api_key(admin_key)
            
            # Set default admin permissions if none provided
            if permissions is None:
                permissions = ['admin', 'read', 'write', 'manage_users', 'manage_keys']
            
            # Calculate expiration
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
            # Create admin key record
            admin_key_data = {
                'admin_key': admin_key,  # Store the original admin key for lookup
                'tenant_id': tenant_id,
                'user_id': user_id,
                'key_name': key_name,
                'permissions': permissions,
                'status': 'active',
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': expires_at.isoformat(),
                'last_used_at': None,
                'usage_count': 0,
                'metadata': {
                    'created_by': 'api_key_manager',
                    'environment': self.environment
                }
            }
            
            # Store in DynamoDB
            await asyncio.to_thread(
                self.admin_keys_table.put_item,
                Item=admin_key_data
            )
            
            # Return the actual admin key (only shown once)
            result = {
                'admin_key': admin_key,
                'admin_key_hash': admin_key_hash,
                'tenant_id': tenant_id,
                'user_id': user_id,
                'key_name': key_name,
                'permissions': permissions,
                'expires_at': expires_at.isoformat(),
                'warning': 'Store this admin key securely - it will not be shown again!'
            }
            
            logger.info(f"Created admin key '{key_name}' for tenant {tenant_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create admin key for tenant {tenant_id}: {e}")
            raise
    
    async def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Validate an API key and return its information."""
        try:
            # Query DynamoDB with the original API key
            response = await asyncio.to_thread(
                self.api_keys_table.get_item,
                Key={'api_key': api_key}
            )
            
            if 'Item' not in response:
                return {'valid': False, 'error': 'Invalid API key'}
            
            api_key_data = response['Item']
            
            # Check if key is active
            if api_key_data.get('status') != 'active':
                return {'valid': False, 'error': 'API key is inactive'}
            
            # Check expiration
            if api_key_data.get('expires_at'):
                expires_at = datetime.fromisoformat(api_key_data['expires_at'])
                if datetime.utcnow() > expires_at:
                    return {'valid': False, 'error': 'API key has expired'}
            
            # Return key information (without sensitive data)
            return {
                'valid': True,
                'tenant_id': api_key_data['tenant_id'],
                'user_id': api_key_data['user_id'],
                'key_name': api_key_data['key_name'],
                'permissions': api_key_data.get('permissions', []),
                'created_at': api_key_data['created_at'],
                'expires_at': api_key_data.get('expires_at'),
                'last_used_at': api_key_data.get('last_used_at'),
                'usage_count': api_key_data.get('usage_count', 0)
            }
            
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return {'valid': False, 'error': f'Validation error: {str(e)}'}
    
    async def list_api_keys(self, tenant_id: str = None) -> List[Dict[str, Any]]:
        """List API keys, optionally filtered by tenant."""
        try:
            if tenant_id:
                # Query by tenant_id (assuming GSI exists)
                response = await asyncio.to_thread(
                    self.api_keys_table.query,
                    IndexName='tenant_id-index',
                    KeyConditionExpression='tenant_id = :tenant_id',
                    ExpressionAttributeValues={':tenant_id': tenant_id}
                )
            else:
                # Scan all keys
                response = await asyncio.to_thread(
                    self.api_keys_table.scan
                )
            
            keys = []
            for item in response.get('Items', []):
                keys.append({
                    'tenant_id': item['tenant_id'],
                    'user_id': item['user_id'],
                    'key_name': item['key_name'],
                    'permissions': item.get('permissions', []),
                    'status': item['status'],
                    'created_at': item['created_at'],
                    'expires_at': item.get('expires_at'),
                    'last_used_at': item.get('last_used_at'),
                    'usage_count': item.get('usage_count', 0)
                })
            
            return keys
            
        except Exception as e:
            logger.error(f"Failed to list API keys: {e}")
            raise
    
    async def deactivate_api_key(self, api_key: str) -> bool:
        """Deactivate an API key."""
        try:
            api_key_hash = self.hash_api_key(api_key)
            
            # Update status to inactive
            await asyncio.to_thread(
                self.api_keys_table.update_item,
                Key={'api_key': api_key_hash},
                UpdateExpression='SET #status = :status, updated_at = :updated_at',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'inactive',
                    ':updated_at': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Deactivated API key: {api_key_hash[:16]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate API key: {e}")
            return False
    
    async def test_authentication(self, api_key: str) -> Dict[str, Any]:
        """Test API key authentication with a mock request."""
        try:
            # Validate the API key
            validation_result = await self.validate_api_key(api_key)
            
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'http_status': 401
                }
            
            # Simulate successful authentication
            auth_context = {
                'tenant_id': validation_result['tenant_id'],
                'user_id': validation_result['user_id'],
                'permissions': validation_result['permissions'],
                'auth_method': 'api_key',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return {
                'success': True,
                'auth_context': auth_context,
                'http_status': 200,
                'message': 'Authentication successful'
            }
            
        except Exception as e:
            logger.error(f"Authentication test error: {e}")
            return {
                'success': False,
                'error': f'Test error: {str(e)}',
                'http_status': 500
            }


async def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(description='DcisionAI API Key Manager')
    parser.add_argument('--action', required=True, 
                       choices=['create', 'validate', 'list', 'test-auth', 'create-tenant', 'create-admin'],
                       help='Action to perform')
    parser.add_argument('--environment', default='production',
                       help='Environment (default: production)')
    parser.add_argument('--tenant-id', help='Tenant ID')
    parser.add_argument('--user-id', help='User ID')
    parser.add_argument('--key-name', help='Key name/description')
    parser.add_argument('--api-key', help='API key to validate/test')
    parser.add_argument('--permissions', nargs='+', help='Permissions for the key')
    parser.add_argument('--expires-in-days', type=int, default=365,
                       help='Days until key expires (default: 365)')
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = APIKeyManager(args.environment)
    
    try:
        if args.action == 'create-tenant':
            if not args.tenant_id or not args.key_name:
                print("Error: --tenant-id and --key-name are required for create-tenant")
                sys.exit(1)
            
            tenant = await manager.create_tenant(args.tenant_id, args.key_name)
            print(f"✅ Created tenant: {json.dumps(tenant, indent=2)}")
            
        elif args.action == 'create':
            if not all([args.tenant_id, args.user_id, args.key_name]):
                print("Error: --tenant-id, --user-id, and --key-name are required for create")
                sys.exit(1)
            
            api_key = await manager.create_api_key(
                args.tenant_id, args.user_id, args.key_name,
                args.permissions, args.expires_in_days
            )
            print(f"✅ Created API key: {json.dumps(api_key, indent=2)}")
            
        elif args.action == 'create-admin':
            if not all([args.tenant_id, args.user_id, args.key_name]):
                print("Error: --tenant-id, --user-id, and --key-name are required for create-admin")
                sys.exit(1)
            
            admin_key = await manager.create_admin_key(
                args.tenant_id, args.user_id, args.key_name,
                args.permissions, args.expires_in_days
            )
            print(f"✅ Created admin key: {json.dumps(admin_key, indent=2)}")
            
        elif args.action == 'validate':
            if not args.api_key:
                print("Error: --api-key is required for validate")
                sys.exit(1)
            
            result = await manager.validate_api_key(args.api_key)
            print(f"🔍 Validation result: {json.dumps(result, indent=2)}")
            
        elif args.action == 'list':
            keys = await manager.list_api_keys(args.tenant_id)
            print(f"📋 API Keys: {json.dumps(keys, indent=2)}")
            
        elif args.action == 'test-auth':
            if not args.api_key:
                print("Error: --api-key is required for test-auth")
                sys.exit(1)
            
            result = await manager.test_authentication(args.api_key)
            print(f"🧪 Authentication test: {json.dumps(result, indent=2)}")
            
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
