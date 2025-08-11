#!/usr/bin/env python3
"""
Test script to verify pagination is working for doctor consultations
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your server runs on a different port
API_ENDPOINT = "/api/consultations/doctor/consultations/"

def test_pagination():
    """Test pagination functionality"""
    
    # Test parameters
    test_params = [
        {"page": 1, "page_size": 5},
        {"page": 2, "page_size": 5},
        {"page": 1, "page_size": 10},
        {"status": "scheduled", "page": 1, "page_size": 5},
        {"search": "test", "page": 1, "page_size": 5},
    ]
    
    print("Testing pagination for doctor consultations...")
    print("=" * 50)
    
    for i, params in enumerate(test_params, 1):
        print(f"\nTest {i}: Testing with parameters {params}")
        
        try:
            response = requests.get(f"{BASE_URL}{API_ENDPOINT}", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has pagination structure
                if 'results' in data and 'count' in data:
                    print(f"✅ Pagination working correctly")
                    print(f"   - Total count: {data.get('count', 0)}")
                    print(f"   - Results on this page: {len(data.get('results', []))}")
                    print(f"   - Next page: {data.get('next', 'None')}")
                    print(f"   - Previous page: {data.get('previous', 'None')}")
                else:
                    print(f"❌ Response doesn't have pagination structure")
                    print(f"   Response keys: {list(data.keys())}")
                    
            elif response.status_code == 401:
                print(f"❌ Authentication required - please login first")
            else:
                print(f"❌ Request failed with status code: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Could not connect to server at {BASE_URL}")
            print(f"   Make sure the Django server is running")
            break
        except Exception as e:
            print(f"❌ Error occurred: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Pagination test completed!")

if __name__ == "__main__":
    test_pagination() 