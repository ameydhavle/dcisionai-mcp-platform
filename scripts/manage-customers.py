#!/usr/bin/env python3
"""
Customer Management System for DcisionAI MCP Server
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class CustomerManager:
    def __init__(self, customers_file: str = "customers.json"):
        self.customers_file = customers_file
        self.customers = self.load_customers()
    
    def load_customers(self) -> Dict:
        """Load customers from file."""
        if os.path.exists(self.customers_file):
            with open(self.customers_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_customers(self):
        """Save customers to file."""
        with open(self.customers_file, 'w') as f:
            json.dump(self.customers, f, indent=2)
    
    def add_customer(self, email: str, name: str, company: str, tier: str = "beta"):
        """Add a new customer."""
        customer_id = email.lower().replace('@', '_at_').replace('.', '_')
        
        self.customers[customer_id] = {
            "email": email,
            "name": name,
            "company": company,
            "tier": tier,
            "status": "active",
            "joined_date": datetime.utcnow().isoformat(),
            "last_activity": None,
            "usage_count": 0
        }
        
        self.save_customers()
        print(f"✅ Added customer: {name} ({email})")
    
    def remove_customer(self, email: str):
        """Remove a customer."""
        customer_id = email.lower().replace('@', '_at_').replace('.', '_')
        
        if customer_id in self.customers:
            del self.customers[customer_id]
            self.save_customers()
            print(f"✅ Removed customer: {email}")
        else:
            print(f"❌ Customer not found: {email}")
    
    def list_customers(self):
        """List all customers."""
        if not self.customers:
            print("No customers found.")
            return
        
        print(f"{'Name':<20} {'Email':<30} {'Company':<20} {'Tier':<10} {'Status':<10}")
        print("-" * 90)
        
        for customer in self.customers.values():
            print(f"{customer['name']:<20} {customer['email']:<30} {customer['company']:<20} {customer['tier']:<10} {customer['status']:<10}")
    
    def update_customer_status(self, email: str, status: str):
        """Update customer status."""
        customer_id = email.lower().replace('@', '_at_').replace('.', '_')
        
        if customer_id in self.customers:
            self.customers[customer_id]['status'] = status
            self.save_customers()
            print(f"✅ Updated status for {email}: {status}")
        else:
            print(f"❌ Customer not found: {email}")

def main():
    manager = CustomerManager()
    
    print("🥷 DcisionAI Customer Management System")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Add customer")
        print("2. Remove customer")
        print("3. List customers")
        print("4. Update customer status")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            email = input("Email: ").strip()
            name = input("Name: ").strip()
            company = input("Company: ").strip()
            tier = input("Tier (beta/pro/enterprise): ").strip() or "beta"
            manager.add_customer(email, name, company, tier)
        
        elif choice == "2":
            email = input("Email to remove: ").strip()
            manager.remove_customer(email)
        
        elif choice == "3":
            manager.list_customers()
        
        elif choice == "4":
            email = input("Email: ").strip()
            status = input("New status (active/inactive/suspended): ").strip()
            manager.update_customer_status(email, status)
        
        elif choice == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
