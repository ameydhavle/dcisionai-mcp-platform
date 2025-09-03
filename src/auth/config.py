"""
Authentication Configuration for DcisionAI Platform

This module provides configuration for all authentication-related features:
- API Key management
- OAuth 2.0 providers
- JWT settings
- Rate limiting
- Redis configuration
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class OAuthProvider:
    """OAuth provider configuration."""
    name: str
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    userinfo_url: str
    scopes: List[str]
    redirect_uri: str


@dataclass
class JWTConfig:
    """JWT configuration."""
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    audience: str
    issuer: str


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    enabled: bool
    default_limit: str
    burst_limit: str
    window_size_seconds: int
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: str


@dataclass
class AuthConfig:
    """Main authentication configuration."""
    environment: str
    api_keys_table: str
    admin_keys_table: str
    tenants_table: str
    oauth: OAuthProvider
    jwt: JWTConfig
    rate_limiting: RateLimitConfig
    ip_whitelist: List[str]
    session_timeout_minutes: int
    max_failed_attempts: int
    lockout_duration_minutes: int


def load_auth_config() -> AuthConfig:
    """Load authentication configuration from environment variables."""
    
    # Environment
    environment = os.getenv('ENVIRONMENT', 'dev')
    
    # DynamoDB table names
    api_keys_table = os.getenv('API_KEYS_TABLE', f'dcisionai-api-keys-{environment}')
    admin_keys_table = os.getenv('ADMIN_KEYS_TABLE', f'dcisionai-admin-keys-{environment}')
    tenants_table = os.getenv('TENANTS_TABLE', f'dcisionai-tenants-{environment}')
    
    # OAuth configuration
    oauth = OAuthProvider(
        name=os.getenv('OAUTH_PROVIDER_NAME', 'google'),
        client_id=os.getenv('OAUTH_CLIENT_ID', ''),
        client_secret=os.getenv('OAUTH_CLIENT_SECRET', ''),
        authorization_url=os.getenv('OAUTH_AUTHORIZATION_URL', ''),
        token_url=os.getenv('OAUTH_TOKEN_URL', ''),
        userinfo_url=os.getenv('OAUTH_USERINFO_URL', ''),
        scopes=os.getenv('OAUTH_SCOPES', 'openid email profile').split(','),
        redirect_uri=os.getenv('OAUTH_REDIRECT_URI', '')
    )
    
    # JWT configuration
    jwt = JWTConfig(
        secret_key=os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production'),
        algorithm=os.getenv('JWT_ALGORITHM', 'HS256'),
        access_token_expire_minutes=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '30')),
        refresh_token_expire_days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', '7')),
        audience=os.getenv('JWT_AUDIENCE', 'dcisionai-platform'),
        issuer=os.getenv('JWT_ISSUER', 'dcisionai-auth')
    )
    
    # Rate limiting configuration
    rate_limiting = RateLimitConfig(
        enabled=os.getenv('RATE_LIMITING_ENABLED', 'true').lower() == 'true',
        default_limit=os.getenv('RATE_LIMIT_DEFAULT', '1000/hour'),
        burst_limit=os.getenv('RATE_LIMIT_BURST', '2000/hour'),
        window_size_seconds=int(os.getenv('RATE_LIMIT_WINDOW', '3600')),
        redis_host=os.getenv('REDIS_HOST', 'localhost'),
        redis_port=int(os.getenv('REDIS_PORT', '6379')),
        redis_db=int(os.getenv('REDIS_DB', '0')),
        redis_password=os.getenv('REDIS_PASSWORD', '')
    )
    
    # Security settings
    ip_whitelist = os.getenv('IP_WHITELIST', '').split(',') if os.getenv('IP_WHITELIST') else []
    session_timeout_minutes = int(os.getenv('SESSION_TIMEOUT_MINUTES', '480'))  # 8 hours
    max_failed_attempts = int(os.getenv('MAX_FAILED_ATTEMPTS', '5'))
    lockout_duration_minutes = int(os.getenv('LOCKOUT_DURATION_MINUTES', '30'))
    
    return AuthConfig(
        environment=environment,
        api_keys_table=api_keys_table,
        admin_keys_table=admin_keys_table,
        tenants_table=tenants_table,
        oauth=oauth,
        jwt=jwt,
        rate_limiting=rate_limiting,
        ip_whitelist=ip_whitelist,
        session_timeout_minutes=session_timeout_minutes,
        max_failed_attempts=max_failed_attempts,
        lockout_duration_minutes=lockout_duration_minutes
    )


def get_auth_config_dict() -> Dict[str, Any]:
    """Get authentication configuration as a dictionary for middleware."""
    config = load_auth_config()
    
    return {
        'environment': config.environment,
        'api_keys_table': config.api_keys_table,
        'admin_keys_table': config.admin_keys_table,
        'tenants_table': config.tenants_table,
        'oauth': {
            'provider_name': config.oauth.name,
            'client_id': config.oauth.client_id,
            'client_secret': config.oauth.client_secret,
            'authorization_url': config.oauth.authorization_url,
            'token_url': config.oauth.token_url,
            'userinfo_url': config.oauth.userinfo_url,
            'scopes': config.oauth.scopes,
            'redirect_uri': config.oauth.redirect_uri
        },
        'jwt': {
            'secret_key': config.jwt.secret_key,
            'algorithm': config.jwt.algorithm,
            'access_token_expire_minutes': config.jwt.access_token_expire_minutes,
            'refresh_token_expire_days': config.jwt.refresh_token_expire_days,
            'audience': config.jwt.audience,
            'issuer': config.jwt.issuer
        },
        'rate_limiting': {
            'enabled': config.rate_limiting.enabled,
            'default_limit': config.rate_limiting.default_limit,
            'burst_limit': config.rate_limiting.burst_limit,
            'window_size_seconds': config.rate_limiting.window_size_seconds
        },
        'redis': {
            'enabled': config.rate_limiting.enabled,
            'host': config.rate_limiting.redis_host,
            'port': config.rate_limiting.redis_port,
            'db': config.rate_limiting.redis_db,
            'password': config.rate_limiting.redis_password
        },
        'security': {
            'ip_whitelist': config.ip_whitelist,
            'session_timeout_minutes': config.session_timeout_minutes,
            'max_failed_attempts': config.max_failed_attempts,
            'lockout_duration_minutes': config.lockout_duration_minutes
        }
    }


# Environment-specific configurations
def get_dev_config() -> AuthConfig:
    """Get development environment configuration."""
    os.environ['ENVIRONMENT'] = 'dev'
    os.environ['JWT_SECRET_KEY'] = 'dev-secret-key-change-in-production'
    os.environ['RATE_LIMITING_ENABLED'] = 'false'
    return load_auth_config()


def get_staging_config() -> AuthConfig:
    """Get staging environment configuration."""
    os.environ['ENVIRONMENT'] = 'staging'
    os.environ['RATE_LIMITING_ENABLED'] = 'true'
    return load_auth_config()


def get_prod_config() -> AuthConfig:
    """Get production environment configuration."""
    os.environ['ENVIRONMENT'] = 'prod'
    os.environ['RATE_LIMITING_ENABLED'] = 'true'
    os.environ['SESSION_TIMEOUT_MINUTES'] = '240'  # 4 hours for production
    return load_auth_config()


# Configuration validation
def validate_auth_config(config: AuthConfig) -> List[str]:
    """Validate authentication configuration and return list of errors."""
    errors = []
    
    # Check required fields
    if not config.jwt.secret_key or config.jwt.secret_key == 'your-secret-key-change-in-production':
        errors.append("JWT_SECRET_KEY must be set to a secure value in production")
    
    if not config.oauth.client_id and config.environment == 'prod':
        errors.append("OAUTH_CLIENT_ID must be set in production")
    
    if not config.oauth.client_secret and config.environment == 'prod':
        errors.append("OAUTH_CLIENT_SECRET must be set in production")
    
    # Check security settings
    if config.session_timeout_minutes > 1440:  # 24 hours
        errors.append("SESSION_TIMEOUT_MINUTES cannot exceed 24 hours")
    
    if config.max_failed_attempts < 3:
        errors.append("MAX_FAILED_ATTEMPTS should be at least 3")
    
    if config.lockout_duration_minutes < 15:
        errors.append("LOCKOUT_DURATION_MINUTES should be at least 15 minutes")
    
    return errors


# Configuration presets for different use cases
def get_minimal_config() -> Dict[str, Any]:
    """Get minimal configuration for testing."""
    return {
        'environment': 'production',
        'api_keys_table': 'dcisionai-api-keys-production',
        'admin_keys_table': 'dcisionai-admin-keys-production',
        'tenants_table': 'dcisionai-tenants-production',
        'oauth': {
            'provider_name': 'test',
            'client_id': 'test-client',
            'client_secret': 'test-secret',
            'authorization_url': 'http://localhost:8080/auth',
            'token_url': 'http://localhost:8080/token',
            'userinfo_url': 'http://localhost:8080/userinfo',
            'scopes': ['openid'],
            'redirect_uri': 'http://localhost:3000/callback'
        },
        'jwt': {
            'secret_key': 'test-secret-key',
            'algorithm': 'HS256',
            'access_token_expire_minutes': 30,
            'refresh_token_expire_days': 7,
            'audience': 'test-audience',
            'issuer': 'test-issuer'
        },
        'rate_limiting': {
            'enabled': False,
            'default_limit': '1000/hour',
            'burst_limit': '2000/hour',
            'window_size_seconds': 3600
        },
        'redis': {
            'enabled': False,
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': ''
        },
        'security': {
            'ip_whitelist': [],
            'session_timeout_minutes': 480,
            'max_failed_attempts': 5,
            'lockout_duration_minutes': 30
        }
    }


def get_enterprise_config() -> Dict[str, Any]:
    """Get enterprise-grade configuration."""
    return {
        'environment': 'enterprise',
        'api_keys_table': 'dcisionai-api-keys-enterprise',
        'admin_keys_table': 'dcisionai-admin-keys-enterprise',
        'tenants_table': 'dcisionai-tenants-enterprise',
        'oauth': {
            'provider_name': 'azure_ad',
            'client_id': os.getenv('AZURE_CLIENT_ID', ''),
            'client_secret': os.getenv('AZURE_CLIENT_SECRET', ''),
            'authorization_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
            'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
            'userinfo_url': 'https://graph.microsoft.com/v1.0/me',
            'scopes': ['openid', 'profile', 'email', 'User.Read'],
            'redirect_uri': os.getenv('AZURE_REDIRECT_URI', '')
        },
        'jwt': {
            'secret_key': os.getenv('JWT_SECRET_KEY', ''),
            'algorithm': 'RS256',
            'access_token_expire_minutes': 15,  # Shorter for security
            'refresh_token_expire_days': 1,     # Shorter for security
            'audience': 'dcisionai-enterprise',
            'issuer': 'dcisionai-auth'
        },
        'rate_limiting': {
            'enabled': True,
            'default_limit': '500/hour',        # Stricter limits
            'burst_limit': '1000/hour',
            'window_size_seconds': 3600
        },
        'redis': {
            'enabled': True,
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', '6379')),
            'db': int(os.getenv('REDIS_DB', '0')),
            'password': os.getenv('REDIS_PASSWORD', '')
        },
        'security': {
            'ip_whitelist': os.getenv('ENTERPRISE_IP_WHITELIST', '').split(','),
            'session_timeout_minutes': 120,     # 2 hours for enterprise
            'max_failed_attempts': 3,           # Stricter for enterprise
            'lockout_duration_minutes': 60      # Longer lockout
        }
    }


# Configuration loading helpers
def load_config_for_environment(env: str = None) -> AuthConfig:
    """Load configuration for specific environment."""
    if env:
        os.environ['ENVIRONMENT'] = env
    
    if env == 'dev':
        return get_dev_config()
    elif env == 'staging':
        return get_staging_config()
    elif env == 'prod':
        return get_prod_config()
    elif env == 'enterprise':
        return load_auth_config()  # Will use enterprise environment variables
    else:
        return load_auth_config()


def get_config_summary(config: AuthConfig) -> Dict[str, Any]:
    """Get a summary of the configuration for logging."""
    return {
        'environment': config.environment,
        'oauth_provider': config.oauth.name,
        'jwt_algorithm': config.jwt.algorithm,
        'rate_limiting_enabled': config.rate_limiting.enabled,
        'session_timeout_minutes': config.session_timeout_minutes,
        'max_failed_attempts': config.max_failed_attempts,
        'lockout_duration_minutes': config.lockout_duration_minutes
    }
