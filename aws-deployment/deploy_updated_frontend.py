#!/usr/bin/env python3
"""
Deploy Updated Frontend to platform.dcisionai.com
=================================================

This script deploys the updated React frontend with Perplexity-like UI
to the existing AWS infrastructure for platform.dcisionai.com.
"""

import boto3
import json
import os
import subprocess
import shutil
from pathlib import Path
import time

# Configuration
EXISTING_DISTRIBUTION_ID = 'E33RDUTHDOYYXP'
CUSTOM_DOMAIN = 'platform.dcisionai.com'
BACKEND_URL = 'https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod'
FRONTEND_DIR = '/Users/ameydhavle/Documents/DcisionAI/dcisionai-mcp-platform/aws-deployment/frontend'

def build_react_app():
    """Build the React app with the correct backend URL."""
    print("🔨 Building React application...")
    
    # Set environment variable for the backend URL
    env = os.environ.copy()
    env['REACT_APP_BACKEND_URL'] = BACKEND_URL
    
    # Build the React app
    result = subprocess.run(
        ['npm', 'run', 'build'],
        cwd=FRONTEND_DIR,
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Build failed: {result.stderr}")
        return None
    
    print("✅ React app built successfully")
    return f'{FRONTEND_DIR}/build'

def update_frontend_config():
    """Update frontend configuration to use AWS backend."""
    print("⚙️  Updating frontend configuration...")
    
    # Update the App.js file to use the AWS backend
    app_js_path = f'{FRONTEND_DIR}/src/App.js'
    
    with open(app_js_path, 'r') as f:
        content = f.read()
    
    # Replace localhost backend URL with AWS URL
    updated_content = content.replace(
        'http://localhost:5001',
        BACKEND_URL
    )
    
    # Also replace any hardcoded backend URLs
    updated_content = updated_content.replace(
        'https://hy1va2brhl.execute-api.us-east-1.amazonaws.com/prod',
        BACKEND_URL
    )
    
    with open(app_js_path, 'w') as f:
        f.write(updated_content)
    
    print("✅ Frontend configuration updated")

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

def update_cloudfront_distribution(bucket_name):
    """Update existing CloudFront distribution with new S3 bucket."""
    print(f"🌐 Updating CloudFront distribution {EXISTING_DISTRIBUTION_ID}...")
    
    cloudfront_client = boto3.client('cloudfront')
    
    try:
        # Get current distribution config
        current_config = cloudfront_client.get_distribution_config(Id=EXISTING_DISTRIBUTION_ID)
        config = current_config['DistributionConfig']
        etag = current_config['ETag']
        
        # Update the origin to point to new S3 bucket
        s3_website_url = f"{bucket_name}.s3-website-us-east-1.amazonaws.com"
        config['Origins']['Items'][0]['DomainName'] = s3_website_url
        
        # Update distribution
        response = cloudfront_client.update_distribution(
            Id=EXISTING_DISTRIBUTION_ID,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print("✅ CloudFront distribution updated successfully!")
        print(f"🌐 Custom domain: https://{CUSTOM_DOMAIN}")
        print("⏳ Changes may take 10-15 minutes to propagate globally.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating CloudFront distribution: {e}")
        return False

def invalidate_cloudfront_cache():
    """Invalidate CloudFront cache to ensure new content is served."""
    print("🔄 Invalidating CloudFront cache...")
    
    cloudfront_client = boto3.client('cloudfront')
    
    try:
        response = cloudfront_client.create_invalidation(
            DistributionId=EXISTING_DISTRIBUTION_ID,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': ['/*']
                },
                'CallerReference': f"frontend-update-{int(time.time())}"
            }
        )
        
        invalidation_id = response['Invalidation']['Id']
        print(f"✅ Cache invalidation created: {invalidation_id}")
        print("⏳ Cache invalidation may take 5-10 minutes to complete.")
        
        return invalidation_id
        
    except Exception as e:
        print(f"❌ Error creating cache invalidation: {e}")
        return None

def deploy_updated_frontend():
    """Deploy the updated frontend to platform.dcisionai.com."""
    print("🚀 Deploying Updated Frontend to platform.dcisionai.com")
    print("=" * 60)
    print(f"🔧 Backend URL: {BACKEND_URL}")
    print(f"🌐 Target Domain: {CUSTOM_DOMAIN}")
    print(f"🆔 CloudFront Distribution: {EXISTING_DISTRIBUTION_ID}")
    print()
    
    # Step 1: Update frontend configuration
    update_frontend_config()
    
    # Step 2: Build React app
    build_dir = build_react_app()
    if not build_dir:
        return False
    
    # Step 3: Create new S3 bucket
    bucket_name = f"dcisionai-frontend-updated-{int(time.time())}"
    create_s3_bucket(bucket_name)
    
    # Step 4: Upload to S3
    upload_to_s3(build_dir, bucket_name)
    
    # Step 5: Update CloudFront distribution
    if not update_cloudfront_distribution(bucket_name):
        return False
    
    # Step 6: Invalidate CloudFront cache
    invalidation_id = invalidate_cloudfront_cache()
    
    print("\n✅ Frontend deployment completed!")
    print(f"🌐 Your updated application will be available at: https://{CUSTOM_DOMAIN}")
    print(f"🪣 S3 Bucket: {bucket_name}")
    print(f"🆔 CloudFront Distribution: {EXISTING_DISTRIBUTION_ID}")
    if invalidation_id:
        print(f"🔄 Cache Invalidation: {invalidation_id}")
    print("\n⏳ Note: Changes may take 10-15 minutes to fully propagate globally.")
    
    return True

if __name__ == "__main__":
    success = deploy_updated_frontend()
    
    if success:
        print("\n🎉 Deployment Summary:")
        print(f"🌐 Frontend URL: https://{CUSTOM_DOMAIN}")
        print(f"🔧 Backend URL: {BACKEND_URL}")
        print("\n✨ Your updated Perplexity-like UI is now live!")
        print("⏳ Please wait 10-15 minutes for full global propagation.")
    else:
        print("\n❌ Deployment failed!")
        print("Please check the errors above and try again.")
