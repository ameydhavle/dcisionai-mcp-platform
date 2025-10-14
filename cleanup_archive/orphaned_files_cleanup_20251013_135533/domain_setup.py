#!/usr/bin/env python3
"""
Custom Domain Setup for DcisionAI Manufacturing Optimizer
========================================================

This script configures the custom domain platform.dcisionai.com
for the frontend CloudFront distribution.
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def create_ssl_certificate(domain_name, region='us-east-1'):
    """Create SSL certificate for the custom domain."""
    print(f"🔒 Creating SSL certificate for {domain_name}...")
    
    acm_client = boto3.client('acm', region_name=region)
    
    try:
        # Request certificate
        response = acm_client.request_certificate(
            DomainName=domain_name,
            SubjectAlternativeNames=[f"*.{domain_name.split('.', 1)[1]}"],  # Add wildcard for subdomains
            ValidationMethod='DNS',
            DomainValidationOptions=[
                {
                    'DomainName': domain_name,
                    'ValidationDomain': domain_name
                }
            ]
        )
        
        certificate_arn = response['CertificateArn']
        print(f"✅ SSL certificate created: {certificate_arn}")
        
        # Get validation records
        cert_details = acm_client.describe_certificate(CertificateArn=certificate_arn)
        validation_records = []
        
        for option in cert_details['Certificate']['DomainValidationOptions']:
            if 'ResourceRecord' in option:
                validation_records.append({
                    'name': option['ResourceRecord']['Name'],
                    'type': option['ResourceRecord']['Type'],
                    'value': option['ResourceRecord']['Value']
                })
        
        print("📋 DNS validation records needed:")
        for record in validation_records:
            print(f"  {record['name']} {record['type']} {record['value']}")
        
        return certificate_arn, validation_records
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidDomainValidationOptionsException':
            print("ℹ️  Certificate may already exist or be in progress")
            # Try to find existing certificate
            try:
                paginator = acm_client.get_paginator('list_certificates')
                for page in paginator.paginate():
                    for cert in page['CertificateSummaryList']:
                        if cert['DomainName'] == domain_name:
                            return cert['CertificateArn'], []
            except:
                pass
        print(f"❌ Certificate creation failed: {e}")
        return None, []

def update_cloudfront_distribution(distribution_id, domain_name, certificate_arn):
    """Update CloudFront distribution with custom domain and SSL certificate."""
    print(f"🌐 Updating CloudFront distribution with custom domain...")
    
    cloudfront_client = boto3.client('cloudfront')
    
    try:
        # Get current distribution config
        current_config = cloudfront_client.get_distribution_config(Id=distribution_id)
        config = current_config['DistributionConfig']
        etag = current_config['ETag']
        
        # Update configuration
        config['Aliases'] = {
            'Quantity': 1,
            'Items': [domain_name]
        }
        
        config['ViewerCertificate'] = {
            'ACMCertificateArn': certificate_arn,
            'SSLSupportMethod': 'sni-only',
            'MinimumProtocolVersion': 'TLSv1.2_2021'
        }
        
        # Update distribution
        response = cloudfront_client.update_distribution(
            Id=distribution_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print(f"✅ CloudFront distribution updated")
        print(f"🆔 Distribution ID: {distribution_id}")
        print(f"🌐 Custom Domain: {domain_name}")
        
        return response['Distribution']
        
    except ClientError as e:
        print(f"❌ CloudFront update failed: {e}")
        return None

def create_route53_records(domain_name, distribution_domain):
    """Create Route 53 DNS records for the custom domain."""
    print(f"🌍 Creating Route 53 DNS records...")
    
    route53_client = boto3.client('route53')
    
    try:
        # Extract the hosted zone domain (remove subdomain)
        domain_parts = domain_name.split('.')
        if len(domain_parts) >= 2:
            hosted_zone_domain = '.'.join(domain_parts[-2:])  # e.g., dcisionai.com
        else:
            hosted_zone_domain = domain_name
        
        # Find hosted zone
        hosted_zones = route53_client.list_hosted_zones()
        hosted_zone_id = None
        
        for zone in hosted_zones['HostedZones']:
            if zone['Name'] == f"{hosted_zone_domain}.":
                hosted_zone_id = zone['Id'].split('/')[-1]
                break
        
        if not hosted_zone_id:
            print(f"❌ Hosted zone for {hosted_zone_domain} not found")
            print("Please create a hosted zone in Route 53 first")
            return False
        
        print(f"✅ Found hosted zone: {hosted_zone_id}")
        
        # Create A record (alias to CloudFront)
        change_batch = {
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domain_name,
                        'Type': 'A',
                        'AliasTarget': {
                            'DNSName': distribution_domain,
                            'EvaluateTargetHealth': False,
                            'HostedZoneId': 'Z2FDTNDATAQYW2'  # CloudFront hosted zone ID
                        }
                    }
                }
            ]
        }
        
        response = route53_client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch=change_batch
        )
        
        print(f"✅ DNS record created for {domain_name}")
        print(f"🆔 Change ID: {response['ChangeInfo']['Id']}")
        
        return True
        
    except ClientError as e:
        print(f"❌ Route 53 record creation failed: {e}")
        return False

def wait_for_certificate_validation(certificate_arn, region='us-east-1'):
    """Wait for SSL certificate validation to complete."""
    print("⏳ Waiting for SSL certificate validation...")
    
    acm_client = boto3.client('acm', region_name=region)
    
    max_wait_time = 1800  # 30 minutes
    wait_time = 0
    
    while wait_time < max_wait_time:
        try:
            cert_details = acm_client.describe_certificate(CertificateArn=certificate_arn)
            status = cert_details['Certificate']['Status']
            
            if status == 'ISSUED':
                print("✅ SSL certificate validated successfully")
                return True
            elif status == 'FAILED':
                print("❌ SSL certificate validation failed")
                return False
            
            print(f"⏳ Certificate status: {status} (waiting...)")
            time.sleep(30)
            wait_time += 30
            
        except ClientError as e:
            print(f"❌ Error checking certificate status: {e}")
            return False
    
    print("⏰ Certificate validation timeout")
    return False

def setup_custom_domain(domain_name, distribution_id, distribution_domain):
    """Set up custom domain for the CloudFront distribution."""
    print(f"🚀 Setting up custom domain: {domain_name}")
    print("=" * 60)
    
    # Step 1: Create SSL certificate
    certificate_arn, validation_records = create_ssl_certificate(domain_name)
    
    if not certificate_arn:
        print("❌ Cannot proceed without SSL certificate")
        return False
    
    # Step 2: Wait for certificate validation (if validation records provided)
    if validation_records:
        print("\n📋 Please add these DNS validation records to your domain:")
        for record in validation_records:
            print(f"  {record['name']} {record['type']} {record['value']}")
        
        input("\nPress Enter after adding the validation records...")
        
        if not wait_for_certificate_validation(certificate_arn):
            print("❌ Certificate validation failed")
            return False
    
    # Step 3: Update CloudFront distribution
    distribution = update_cloudfront_distribution(distribution_id, domain_name, certificate_arn)
    
    if not distribution:
        print("❌ CloudFront update failed")
        return False
    
    # Step 4: Create Route 53 DNS records
    if not create_route53_records(domain_name, distribution_domain):
        print("❌ DNS record creation failed")
        return False
    
    print("\n✅ Custom domain setup completed!")
    print(f"🌐 Your application will be available at: https://{domain_name}")
    print("⏳ Note: DNS propagation may take 5-15 minutes")
    
    return True

if __name__ == "__main__":
    # Configuration
    domain_name = "platform.dcisionai.com"
    distribution_id = "E33RDUTHDOYYXP"  # From previous deployment
    distribution_domain = "d2wt30rmau7mse.cloudfront.net"  # From previous deployment
    
    print("🚀 Setting up custom domain for DcisionAI Manufacturing Optimizer")
    print("=" * 70)
    print(f"🌐 Domain: {domain_name}")
    print(f"🆔 CloudFront Distribution ID: {distribution_id}")
    print()
    
    success = setup_custom_domain(domain_name, distribution_id, distribution_domain)
    
    if success:
        print("\n🎉 Custom domain setup completed successfully!")
        print(f"🌐 Your application will be available at: https://{domain_name}")
        print("⏳ Please wait 5-15 minutes for DNS propagation")
    else:
        print("\n❌ Custom domain setup failed!")
        print("Please check the errors above and try again")
