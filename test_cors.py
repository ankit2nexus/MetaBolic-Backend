#!/usr/bin/env python3
"""
Test CORS Configuration for Metabolical Backend
"""

import requests
import json
from datetime import datetime

def test_cors():
    """Test CORS configuration"""
    print("🧪 Testing CORS Configuration...")
    
    # Base URL for the API
    base_url = "https://metabolic-backend.onrender.com"
    
    # Test endpoints
    endpoints = [
        "/api/v1/health",
        "/api/v1/categories",
        "/api/v1/tag/sleep%20disorders?page=1&limit=5"
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 Testing: {base_url}{endpoint}")
        
        try:
            # Test OPTIONS request (CORS preflight)
            options_response = requests.options(f"{base_url}{endpoint}")
            print(f"   OPTIONS Status: {options_response.status_code}")
            print(f"   CORS Headers: {dict(options_response.headers)}")
            
            # Test GET request
            get_response = requests.get(f"{base_url}{endpoint}")
            print(f"   GET Status: {get_response.status_code}")
            
            if get_response.status_code == 200:
                data = get_response.json()
                if isinstance(data, dict):
                    print(f"   Response Keys: {list(data.keys())}")
                else:
                    print(f"   Response Type: {type(data)}")
            else:
                print(f"   Error: {get_response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ CORS Test completed at {datetime.now()}")

if __name__ == "__main__":
    test_cors()
