#!/usr/bin/env python3
"""
Customer Token Generator for DcisionAI MCP Server
Generates unique access tokens for customers
"""

import secrets
import string
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List
import os

class CustomerTokenGenerator:
    def __init__(self, tokens_file: str = "customer-tokens.json"):
        self.tokens_file = tokens_file
        self.tokens = self.load_tokens()
    
    def load_tokens(self) -> Dict:
        """Load existing tokens from file."""
        if os.path.exists(self.tokens_file):
            with open(self.tokens_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_tokens(self):
        """Save tokens to file."""
        with open(self.tokens_file, 'w') as f:
            json.dump(self.tokens, f, indent=2)
    
    def generate_token(self, customer_name: str, customer_email: str, 
                      company: str, industry: str, use_case: str) -> str:
        """Generate a unique access token for a customer."""
        
        # Generate a secure random token
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        
        # Create token record
        token_record = {
            "token": token,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "company": company,
            "industry": industry,
            "use_case": use_case,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=365)).isoformat(),  # 1 year
            "status": "active",
            "usage_count": 0,
            "last_used": None,
            "notes": ""
        }
        
        # Store token
        self.tokens[token] = token_record
        self.save_tokens()
        
        return token
    
    def validate_token(self, token: str) -> Dict:
        """Validate a customer token."""
        if token not in self.tokens:
            return {"valid": False, "error": "Token not found"}
        
        token_record = self.tokens[token]
        
        # Check if token is active
        if token_record["status"] != "active":
            return {"valid": False, "error": "Token is inactive"}
        
        # Check if token has expired
        expires_at = datetime.fromisoformat(token_record["expires_at"])
        if datetime.utcnow() > expires_at:
            return {"valid": False, "error": "Token has expired"}
        
        # Update usage count
        token_record["usage_count"] += 1
        token_record["last_used"] = datetime.utcnow().isoformat()
        self.save_tokens()
        
        return {
            "valid": True,
            "customer_name": token_record["customer_name"],
            "customer_email": token_record["customer_email"],
            "company": token_record["company"],
            "industry": token_record["industry"],
            "use_case": token_record["use_case"]
        }
    
    def list_tokens(self) -> List[Dict]:
        """List all customer tokens."""
        return list(self.tokens.values())
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a customer token."""
        if token in self.tokens:
            self.tokens[token]["status"] = "revoked"
            self.save_tokens()
            return True
        return False
    
    def get_token_stats(self) -> Dict:
        """Get statistics about tokens."""
        total_tokens = len(self.tokens)
        active_tokens = sum(1 for t in self.tokens.values() if t["status"] == "active")
        revoked_tokens = sum(1 for t in self.tokens.values() if t["status"] == "revoked")
        
        # Count by industry
        industries = {}
        for token in self.tokens.values():
            industry = token["industry"]
            industries[industry] = industries.get(industry, 0) + 1
        
        return {
            "total_tokens": total_tokens,
            "active_tokens": active_tokens,
            "revoked_tokens": revoked_tokens,
            "industries": industries
        }

def main():
    generator = CustomerTokenGenerator()
    
    print("🎫 DcisionAI Customer Token Generator")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Generate new customer token")
        print("2. Validate customer token")
        print("3. List all tokens")
        print("4. Revoke token")
        print("5. View token statistics")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            print("\n📝 Generate New Customer Token")
            print("-" * 30)
            
            customer_name = input("Customer Name: ").strip()
            customer_email = input("Customer Email: ").strip()
            company = input("Company: ").strip()
            industry = input("Industry: ").strip()
            use_case = input("Use Case: ").strip()
            
            token = generator.generate_token(customer_name, customer_email, company, industry, use_case)
            
            print(f"\n✅ Token generated successfully!")
            print(f"Token: {token}")
            print(f"Customer: {customer_name} ({customer_email})")
            print(f"Company: {company}")
            print(f"Industry: {industry}")
            print(f"Use Case: {use_case}")
            print(f"\n🔗 Configuration URL: https://www.dcisionai.com/configure?token={token}")
        
        elif choice == "2":
            print("\n🔍 Validate Customer Token")
            print("-" * 30)
            
            token = input("Enter token to validate: ").strip()
            result = generator.validate_token(token)
            
            if result["valid"]:
                print("✅ Token is valid!")
                print(f"Customer: {result['customer_name']}")
                print(f"Email: {result['customer_email']}")
                print(f"Company: {result['company']}")
                print(f"Industry: {result['industry']}")
                print(f"Use Case: {result['use_case']}")
            else:
                print(f"❌ Token validation failed: {result['error']}")
        
        elif choice == "3":
            print("\n📋 All Customer Tokens")
            print("-" * 30)
            
            tokens = generator.list_tokens()
            if not tokens:
                print("No tokens found.")
            else:
                for token in tokens:
                    print(f"Token: {token['token'][:8]}...")
                    print(f"Customer: {token['customer_name']} ({token['customer_email']})")
                    print(f"Company: {token['company']}")
                    print(f"Status: {token['status']}")
                    print(f"Created: {token['created_at']}")
                    print(f"Usage: {token['usage_count']} times")
                    print("-" * 30)
        
        elif choice == "4":
            print("\n🚫 Revoke Customer Token")
            print("-" * 30)
            
            token = input("Enter token to revoke: ").strip()
            if generator.revoke_token(token):
                print("✅ Token revoked successfully!")
            else:
                print("❌ Token not found.")
        
        elif choice == "5":
            print("\n📊 Token Statistics")
            print("-" * 30)
            
            stats = generator.get_token_stats()
            print(f"Total Tokens: {stats['total_tokens']}")
            print(f"Active Tokens: {stats['active_tokens']}")
            print(f"Revoked Tokens: {stats['revoked_tokens']}")
            print("\nBy Industry:")
            for industry, count in stats['industries'].items():
                print(f"  {industry}: {count}")
        
        elif choice == "6":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
