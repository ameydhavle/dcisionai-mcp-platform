#!/usr/bin/env python3
"""
Create CloudFront Distribution for DcisionAI Frontend
===================================================

This script creates a CloudFront distribution for the DcisionAI frontend
with proper caching and security configurations.
"""

import boto3
import json
from datetime import datetime

def create_cloudfront_distribution(bucket_name):
    """Create CloudFront distribution for the frontend."""
    print(f"Creating CloudFront distribution for bucket: {bucket_name}")
    
    cloudfront = boto3.client('cloudfront')
    
    # Get S3 bucket website endpoint
    s3_website_endpoint = f"{bucket_name}.s3-website-us-east-1.amazonaws.com"
    
    # CloudFront distribution configuration
    distribution_config = {
        'CallerReference': f'dcisionai-frontend-{int(datetime.now().timestamp())}',
        'Comment': 'DcisionAI Frontend Production Distribution',
        'DefaultRootObject': 'index.html',
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': 'S3-dcisionai-frontend',
                    'DomainName': s3_website_endpoint,
                    'CustomOriginConfig': {
                        'HTTPPort': 80,
                        'HTTPSPort': 443,
                        'OriginProtocolPolicy': 'http-only',
                        'OriginSslProtocols': {
                            'Quantity': 1,
                            'Items': ['TLSv1.2']
                        }
                    }
                }
            ]
        },
        'DefaultCacheBehavior': {
            'TargetOriginId': 'S3-dcisionai-frontend',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'TrustedSigners': {
                'Enabled': False,
                'Quantity': 0
            },
            'ForwardedValues': {
                'QueryString': False,
                'Cookies': {
                    'Forward': 'none'
                }
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
                    'PathPattern': '/static/*',
                    'TargetOriginId': 'S3-dcisionai-frontend',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'TrustedSigners': {
                        'Enabled': False,
                        'Quantity': 0
                    },
                    'ForwardedValues': {
                        'QueryString': False,
                        'Cookies': {
                            'Forward': 'none'
                        }
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
                    'ErrorCachingMinTTL': 300
                }
            ]
        },
        'Enabled': True,
        'PriceClass': 'PriceClass_100',  # US, Canada, Europe
        'HttpVersion': 'http2',
        'IsIPV6Enabled': True
    }
    
    try:
        response = cloudfront.create_distribution(DistributionConfig=distribution_config)
        distribution = response['Distribution']
        
        print(f"CloudFront distribution created successfully!")
        print(f"Distribution ID: {distribution['Id']}")
        print(f"Domain Name: {distribution['DomainName']}")
        print(f"Status: {distribution['Status']}")
        print(f"ARN: {distribution['ARN']}")
        
        return {
            'distribution_id': distribution['Id'],
            'domain_name': distribution['DomainName'],
            'status': distribution['Status'],
            'arn': distribution['ARN']
        }
        
    except Exception as e:
        print(f"Error creating CloudFront distribution: {e}")
        return None

def main():
    """Main function to create CloudFront distribution."""
    print("Creating CloudFront Distribution for DcisionAI Frontend")
    print("=" * 60)
    
    # Use the bucket name we created
    bucket_name = "dcisionai-frontend-production-1760500572"
    
    result = create_cloudfront_distribution(bucket_name)
    
    if result:
        print("\n" + "=" * 60)
        print("CloudFront Distribution Created Successfully!")
        print("=" * 60)
        print(f"Distribution ID: {result['distribution_id']}")
        print(f"Domain Name: {result['domain_name']}")
        print(f"Status: {result['status']}")
        print("\nNote: It may take 10-15 minutes for the distribution to be fully deployed.")
        print("You can check the status in the AWS Console.")
        
        # Save configuration
        config = {
            'bucket_name': bucket_name,
            'cloudfront': result,
            'created_at': datetime.now().isoformat()
        }
        
        with open('frontend_deployment_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\nConfiguration saved to: frontend_deployment_config.json")
    else:
        print("\nFailed to create CloudFront distribution.")

if __name__ == "__main__":
    main()
