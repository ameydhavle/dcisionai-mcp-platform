#!/usr/bin/env python3
"""
Update existing CloudFront distribution with new S3 bucket
"""

import boto3
import json

def update_cloudfront_distribution():
    """Update the existing CloudFront distribution with new S3 bucket."""
    
    cloudfront = boto3.client('cloudfront')
    distribution_id = 'E33RDUTHDOYYXP'  # Existing distribution with custom domain
    new_s3_bucket = 'dcisionai-manufacturing-frontend-1759881141.s3-website-us-east-1.amazonaws.com'
    
    print(f"🔄 Updating CloudFront distribution {distribution_id}...")
    
    # Get current distribution config
    response = cloudfront.get_distribution_config(Id=distribution_id)
    config = response['DistributionConfig']
    etag = response['ETag']
    
    # Update the origin to point to new S3 bucket
    config['Origins']['Items'][0]['DomainName'] = new_s3_bucket
    
    # Update the distribution
    try:
        cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        print("✅ CloudFront distribution updated successfully!")
        print(f"🌐 Custom domain: https://platform.dcisionai.com")
        print("⏳ Changes may take 10-15 minutes to propagate globally.")
        
    except Exception as e:
        print(f"❌ Error updating CloudFront distribution: {e}")

if __name__ == "__main__":
    update_cloudfront_distribution()
