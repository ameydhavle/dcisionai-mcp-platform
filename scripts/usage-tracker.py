#!/usr/bin/env python3
"""
Usage Tracking System for DcisionAI MCP Server
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, List

class UsageTracker:
    def __init__(self, tracking_file: str = "usage.json"):
        self.tracking_file = tracking_file
        self.usage_data = self.load_usage_data()
    
    def load_usage_data(self) -> List[Dict]:
        """Load usage data from file."""
        if os.path.exists(self.tracking_file):
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_usage_data(self):
        """Save usage data to file."""
        with open(self.tracking_file, 'w') as f:
            json.dump(self.usage_data, f, indent=2)
    
    def track_usage(self, customer_id: str, tool_name: str, success: bool, duration: float = None):
        """Track tool usage."""
        usage_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "customer_id": customer_id,
            "tool": tool_name,
            "success": success,
            "duration": duration
        }
        
        self.usage_data.append(usage_record)
        self.save_usage_data()
        
        # Send to analytics endpoint (if configured)
        self.send_analytics(usage_record)
    
    def send_analytics(self, data: Dict):
        """Send usage data to analytics endpoint."""
        # Configure your analytics endpoint
        analytics_url = os.getenv("ANALYTICS_ENDPOINT")
        
        if analytics_url:
            try:
                requests.post(analytics_url, json=data, timeout=5)
            except Exception as e:
                print(f"Failed to send analytics: {e}")
    
    def get_usage_stats(self) -> Dict:
        """Get usage statistics."""
        if not self.usage_data:
            return {"total_usage": 0, "success_rate": 0, "top_tools": []}
        
        total_usage = len(self.usage_data)
        successful_usage = sum(1 for record in self.usage_data if record["success"])
        success_rate = (successful_usage / total_usage) * 100 if total_usage > 0 else 0
        
        # Count tool usage
        tool_counts = {}
        for record in self.usage_data:
            tool = record["tool"]
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        top_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_usage": total_usage,
            "success_rate": success_rate,
            "top_tools": top_tools,
            "unique_customers": len(set(record["customer_id"] for record in self.usage_data))
        }
    
    def print_stats(self):
        """Print usage statistics."""
        stats = self.get_usage_stats()
        
        print("📊 Usage Statistics")
        print("=" * 30)
        print(f"Total Usage: {stats['total_usage']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")
        print(f"Unique Customers: {stats['unique_customers']}")
        print(f"Top Tools: {stats['top_tools']}")

def main():
    tracker = UsageTracker()
    
    print("📊 DcisionAI Usage Tracker")
    print("=" * 30)
    
    while True:
        print("\nOptions:")
        print("1. Track usage")
        print("2. View statistics")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            customer_id = input("Customer ID: ").strip()
            tool_name = input("Tool name: ").strip()
            success = input("Success (y/n): ").strip().lower() == 'y'
            duration = input("Duration (seconds, optional): ").strip()
            duration = float(duration) if duration else None
            
            tracker.track_usage(customer_id, tool_name, success, duration)
            print("✅ Usage tracked")
        
        elif choice == "2":
            tracker.print_stats()
        
        elif choice == "3":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
