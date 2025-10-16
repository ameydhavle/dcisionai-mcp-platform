#!/usr/bin/env python3
"""
Customer Identification Tool for DcisionAI MCP Server Beta
"""

import json
import os
from datetime import datetime
from typing import Dict, List

class CustomerIdentifier:
    def __init__(self, customers_file: str = "potential-customers.json"):
        self.customers_file = customers_file
        self.potential_customers = self.load_customers()
    
    def load_customers(self) -> List[Dict]:
        """Load potential customers from file."""
        if os.path.exists(self.customers_file):
            with open(self.customers_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_customers(self):
        """Save potential customers to file."""
        with open(self.customers_file, 'w') as f:
            json.dump(self.potential_customers, f, indent=2)
    
    def add_customer(self, name: str, email: str, company: str, role: str, 
                    industry: str, use_case: str, relationship: str, 
                    trust_level: str, technical_level: str):
        """Add a potential customer."""
        customer = {
            "name": name,
            "email": email,
            "company": company,
            "role": role,
            "industry": industry,
            "use_case": use_case,
            "relationship": relationship,
            "trust_level": trust_level,
            "technical_level": technical_level,
            "status": "potential",
            "added_date": datetime.utcnow().isoformat(),
            "notes": ""
        }
        
        self.potential_customers.append(customer)
        self.save_customers()
        print(f"✅ Added potential customer: {name}")
    
    def list_customers(self):
        """List all potential customers."""
        if not self.potential_customers:
            print("No potential customers found.")
            return
        
        print(f"{'Name':<20} {'Company':<20} {'Industry':<15} {'Trust':<8} {'Tech':<8} {'Status':<10}")
        print("-" * 90)
        
        for customer in self.potential_customers:
            print(f"{customer['name']:<20} {customer['company']:<20} {customer['industry']:<15} {customer['trust_level']:<8} {customer['technical_level']:<8} {customer['status']:<10}")
    
    def get_customer_summary(self) -> Dict:
        """Get summary of potential customers."""
        if not self.potential_customers:
            return {"total": 0, "by_trust": {}, "by_industry": {}, "by_tech": {}}
        
        total = len(self.potential_customers)
        
        # Count by trust level
        by_trust = {}
        for customer in self.potential_customers:
            trust = customer['trust_level']
            by_trust[trust] = by_trust.get(trust, 0) + 1
        
        # Count by industry
        by_industry = {}
        for customer in self.potential_customers:
            industry = customer['industry']
            by_industry[industry] = by_industry.get(industry, 0) + 1
        
        # Count by technical level
        by_tech = {}
        for customer in self.potential_customers:
            tech = customer['technical_level']
            by_tech[tech] = by_tech.get(tech, 0) + 1
        
        return {
            "total": total,
            "by_trust": by_trust,
            "by_industry": by_industry,
            "by_tech": by_tech
        }
    
    def print_summary(self):
        """Print customer summary."""
        summary = self.get_customer_summary()
        
        print("📊 Potential Customer Summary")
        print("=" * 40)
        print(f"Total Potential Customers: {summary['total']}")
        print()
        
        print("By Trust Level:")
        for trust, count in summary['by_trust'].items():
            print(f"  {trust}: {count}")
        print()
        
        print("By Industry:")
        for industry, count in summary['by_industry'].items():
            print(f"  {industry}: {count}")
        print()
        
        print("By Technical Level:")
        for tech, count in summary['by_tech'].items():
            print(f"  {tech}: {count}")
    
    def get_recommendations(self) -> List[Dict]:
        """Get recommended beta customers."""
        # Prioritize high trust, technical customers with real use cases
        recommendations = []
        
        for customer in self.potential_customers:
            score = 0
            
            # Trust level scoring
            if customer['trust_level'] == 'high':
                score += 3
            elif customer['trust_level'] == 'medium':
                score += 2
            else:
                score += 1
            
            # Technical level scoring
            if customer['technical_level'] == 'advanced':
                score += 3
            elif customer['technical_level'] == 'intermediate':
                score += 2
            else:
                score += 1
            
            # Industry scoring (prefer target industries)
            target_industries = ['manufacturing', 'healthcare', 'retail', 'logistics', 'financial']
            if customer['industry'].lower() in target_industries:
                score += 2
            
            # Use case scoring (prefer specific use cases)
            if len(customer['use_case']) > 50:  # Detailed use case
                score += 2
            
            recommendations.append({
                'customer': customer,
                'score': score
            })
        
        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:10]  # Top 10 recommendations
    
    def print_recommendations(self):
        """Print recommended beta customers."""
        recommendations = self.get_recommendations()
        
        print("🎯 Recommended Beta Customers (Top 10)")
        print("=" * 50)
        
        for i, rec in enumerate(recommendations, 1):
            customer = rec['customer']
            score = rec['score']
            
            print(f"{i}. {customer['name']} ({customer['company']})")
            print(f"   Industry: {customer['industry']}")
            print(f"   Use Case: {customer['use_case'][:100]}...")
            print(f"   Trust: {customer['trust_level']}, Tech: {customer['technical_level']}")
            print(f"   Score: {score}/10")
            print()

def main():
    identifier = CustomerIdentifier()
    
    print("🎯 DcisionAI Beta Customer Identification Tool")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Add potential customer")
        print("2. List potential customers")
        print("3. View summary")
        print("4. Get recommendations")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\n📝 Add Potential Customer")
            print("-" * 30)
            
            name = input("Name: ").strip()
            email = input("Email: ").strip()
            company = input("Company: ").strip()
            role = input("Role/Title: ").strip()
            industry = input("Industry: ").strip()
            use_case = input("Use Case (optimization problem): ").strip()
            relationship = input("How you know them: ").strip()
            
            print("\nTrust Level:")
            print("1. High (close friend/colleague)")
            print("2. Medium (professional acquaintance)")
            print("3. Low (met once or referral)")
            trust_choice = input("Choose (1-3): ").strip()
            trust_level = {"1": "high", "2": "medium", "3": "low"}.get(trust_choice, "medium")
            
            print("\nTechnical Level:")
            print("1. Advanced (senior developer/data scientist)")
            print("2. Intermediate (some technical background)")
            print("3. Beginner (business user)")
            tech_choice = input("Choose (1-3): ").strip()
            technical_level = {"1": "advanced", "2": "intermediate", "3": "beginner"}.get(tech_choice, "intermediate")
            
            identifier.add_customer(name, email, company, role, industry, use_case, relationship, trust_level, technical_level)
        
        elif choice == "2":
            identifier.list_customers()
        
        elif choice == "3":
            identifier.print_summary()
        
        elif choice == "4":
            identifier.print_recommendations()
        
        elif choice == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
