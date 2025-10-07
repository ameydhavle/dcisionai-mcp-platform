#!/usr/bin/env python3
"""
Frontend Deployment Script for DcisionAI Manufacturing Optimizer
===============================================================

This script deploys the React frontend to AWS S3 + CloudFront
and configures it to use the AWS Lambda backend endpoint.
"""

import boto3
import json
import os
import subprocess
import shutil
from pathlib import Path
import time

def build_react_app(backend_url):
    """Build the React app with the correct backend URL."""
    print("🔨 Building React application...")
    
    # Set environment variable for the backend URL
    env = os.environ.copy()
    env['REACT_APP_BACKEND_URL'] = backend_url
    
    # Build the React app
    result = subprocess.run(
        ['npm', 'run', 'build'],
        cwd='/Users/ameydhavle/Documents/DcisionAI/dcisionai-mcp-platform/dcisionai-mcp-manufacturing/web_app',
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Build failed: {result.stderr}")
        return None
    
    print("✅ React app built successfully")
    return '/Users/ameydhavle/Documents/DcisionAI/dcisionai-mcp-platform/dcisionai-mcp-manufacturing/web_app/build'

def create_s3_bucket(bucket_name, region='us-east-1'):
    """Create S3 bucket for hosting the frontend."""
    print(f"🪣 Creating S3 bucket: {bucket_name}")
    
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        if region == 'us-east-1':
            # us-east-1 doesn't need LocationConstraint
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print("✅ S3 bucket created")
    except s3_client.exceptions.BucketAlreadyExists:
        print("ℹ️  S3 bucket already exists")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print("ℹ️  S3 bucket already owned by you")
    
    # Disable block public access for static website hosting
    s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': False,
            'IgnorePublicAcls': False,
            'BlockPublicPolicy': False,
            'RestrictPublicBuckets': False
        }
    )
    
    # Configure bucket for static website hosting
    s3_client.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={
            'IndexDocument': {'Suffix': 'index.html'},
            'ErrorDocument': {'Key': 'index.html'}  # For SPA routing
        }
    )
    
    # Set bucket policy for public read access
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
    }
    
    s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(bucket_policy)
    )
    
    print("✅ S3 bucket configured for static hosting")
    return bucket_name

def upload_to_s3(build_dir, bucket_name):
    """Upload built React app to S3."""
    print("📤 Uploading files to S3...")
    
    s3_client = boto3.client('s3')
    
    # Upload all files from build directory
    for root, dirs, files in os.walk(build_dir):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, build_dir)
            s3_key = relative_path.replace('\\', '/')  # Ensure forward slashes
            
            # Set content type based on file extension
            content_type = 'text/html' if file.endswith('.html') else None
            if file.endswith('.js'):
                content_type = 'application/javascript'
            elif file.endswith('.css'):
                content_type = 'text/css'
            elif file.endswith('.json'):
                content_type = 'application/json'
            elif file.endswith('.png'):
                content_type = 'image/png'
            elif file.endswith('.jpg') or file.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif file.endswith('.svg'):
                content_type = 'image/svg+xml'
            
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            # Cache control for static assets
            if file.endswith(('.js', '.css', '.png', '.jpg', '.jpeg', '.svg')):
                extra_args['CacheControl'] = 'max-age=31536000'  # 1 year
            else:
                extra_args['CacheControl'] = 'no-cache'  # HTML files
            
            s3_client.upload_file(local_path, bucket_name, s3_key, ExtraArgs=extra_args)
            print(f"  📄 Uploaded: {s3_key}")
    
    print("✅ Files uploaded to S3")

def create_cloudfront_distribution(bucket_name, region='us-east-1'):
    """Create CloudFront distribution for global CDN."""
    print("🌐 Creating CloudFront distribution...")
    
    cloudfront_client = boto3.client('cloudfront')
    
    # Get S3 website endpoint
    s3_website_url = f"{bucket_name}.s3-website-{region}.amazonaws.com"
    
    distribution_config = {
        'CallerReference': f"dcisionai-frontend-{int(time.time())}",
        'Comment': 'DcisionAI Manufacturing Optimizer Frontend',
        'DefaultRootObject': 'index.html',
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': 'S3-Origin',
                    'DomainName': s3_website_url,
                    'CustomOriginConfig': {
                        'HTTPPort': 80,
                        'HTTPSPort': 443,
                        'OriginProtocolPolicy': 'http-only'
                    }
                }
            ]
        },
        'DefaultCacheBehavior': {
            'TargetOriginId': 'S3-Origin',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'TrustedSigners': {
                'Enabled': False,
                'Quantity': 0
            },
            'ForwardedValues': {
                'QueryString': False,
                'Cookies': {'Forward': 'none'}
            },
            'MinTTL': 0,
            'DefaultTTL': 86400,  # 1 day
            'MaxTTL': 31536000,   # 1 year
            'Compress': True
        },
        'CacheBehaviors': {
            'Quantity': 1,
            'Items': [
                {
                    'PathPattern': 'static/*',
                    'TargetOriginId': 'S3-Origin',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'TrustedSigners': {
                        'Enabled': False,
                        'Quantity': 0
                    },
                    'ForwardedValues': {
                        'QueryString': False,
                        'Cookies': {'Forward': 'none'}
                    },
                    'MinTTL': 0,
                    'DefaultTTL': 31536000,  # 1 year for static assets
                    'MaxTTL': 31536000,
                    'Compress': True
                }
            ]
        },
        'CustomErrorResponses': {
            'Quantity': 1,
            'Items': [
                {
                    'ErrorCode': 404,
                    'ResponsePagePath': '/index.html',
                    'ResponseCode': '200',
                    'ErrorCachingMinTTL': 0
                }
            ]
        },
        'Enabled': True,
        'PriceClass': 'PriceClass_100'  # US, Canada, Europe
    }
    
    try:
        response = cloudfront_client.create_distribution(DistributionConfig=distribution_config)
        distribution_id = response['Distribution']['Id']
        domain_name = response['Distribution']['DomainName']
        
        print(f"✅ CloudFront distribution created: {domain_name}")
        print(f"🆔 Distribution ID: {distribution_id}")
        
        return {
            'id': distribution_id,
            'domain': domain_name,
            'status': response['Distribution']['Status']
        }
        
    except Exception as e:
        print(f"❌ CloudFront creation failed: {e}")
        return None

def update_frontend_config(backend_url):
    """Update frontend configuration to use AWS backend."""
    print("⚙️  Updating frontend configuration...")
    
    # Update the App.js file to use the AWS backend
    app_js_path = '/Users/ameydhavle/Documents/DcisionAI/dcisionai-mcp-platform/dcisionai-mcp-manufacturing/web_app/src/App.js'
    
    with open(app_js_path, 'r') as f:
        content = f.read()
    
    # Replace localhost backend URL with AWS URL
    updated_content = content.replace(
        'http://localhost:5001',
        backend_url
    )
    
    with open(app_js_path, 'w') as f:
        f.write(updated_content)
    
    print("✅ Frontend configuration updated")

def deploy_frontend(backend_url):
    """Deploy the frontend to AWS."""
    print("🚀 Starting frontend deployment to AWS")
    print("=" * 50)
    
    # Update frontend configuration
    update_frontend_config(backend_url)
    
    # Build React app
    build_dir = build_react_app(backend_url)
    if not build_dir:
        return None
    
    # Create S3 bucket
    bucket_name = f"dcisionai-manufacturing-frontend-{int(time.time())}"
    create_s3_bucket(bucket_name)
    
    # Upload to S3
    upload_to_s3(build_dir, bucket_name)
    
    # Create CloudFront distribution
    cloudfront_info = create_cloudfront_distribution(bucket_name)
    
    if cloudfront_info:
        print("\n✅ Frontend deployment completed!")
        print(f"🌐 CloudFront URL: https://{cloudfront_info['domain']}")
        print(f"🪣 S3 Website URL: http://{bucket_name}.s3-website-us-east-1.amazonaws.com")
        print(f"🆔 Distribution ID: {cloudfront_info['id']}")
        print(f"📊 Status: {cloudfront_info['status']}")
        
        return {
            'cloudfront_url': f"https://{cloudfront_info['domain']}",
            's3_url': f"http://{bucket_name}.s3-website-us-east-1.amazonaws.com",
            'distribution_id': cloudfront_info['id'],
            'bucket_name': bucket_name
        }
    else:
        print("\n❌ Frontend deployment failed!")
        return None

if __name__ == "__main__":
    # AWS Lambda backend URL
    backend_url = "https://qsykhd99ad.execute-api.us-east-1.amazonaws.com/prod"
    
    print("🚀 Deploying DcisionAI Manufacturing Optimizer Frontend to AWS")
    print("=" * 70)
    print(f"🔧 Backend URL: {backend_url}")
    print()
    
    result = deploy_frontend(backend_url)
    
    if result:
        print("\n🎉 Deployment Summary:")
        print(f"🌐 Frontend URL: {result['cloudfront_url']}")
        print(f"🔧 Backend URL: {backend_url}")
        print("\n⏳ Note: CloudFront distribution may take 10-15 minutes to fully deploy.")
        print("   You can access the S3 website URL immediately for testing.")
    else:
        print("\n❌ Deployment failed!")
