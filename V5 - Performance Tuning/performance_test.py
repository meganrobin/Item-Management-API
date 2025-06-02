import time
import requests

API_BASE = "http://localhost:3000"
API_KEY = "brat"

def test_endpoint(endpoint, method="GET", data=None):
    """Test a single endpoint and return timing"""
    headers = {
        "access_token": API_KEY,
        "Content-Type": "application/json"
    }
    url = f"{API_BASE}{endpoint}"
    
    print(f"Testing: {method} {endpoint}")
    
    start_time = time.time()
     
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        print(f"  Status: {response.status_code}")
        print(f"  Time: {duration_ms:.2f}ms")
        
        if response.status_code >= 400:
            print(f"  Error: {response.text}")
            return None
        
        return duration_ms
        
    except Exception as e:
        print(f"  Error: {e}")
        return None

def main():
    print("=== PERFORMANCE TEST ===\n")
    
    results = []
    
    # Test all endpoints
    tests = [
        ("/players/1/inventory", "GET", None),
        ("/items", "GET", None),
        ("/items?item_type=weapon", "GET", None),
        ("/items/1", "GET", None),
        ("/enchantments", "GET", None),
        ("/players/1/inventory", "POST", {"item_id": 1, "quantity": 1}),
        ("/players/1/inventory/1", "PATCH", {"quantity": 1}),
        ("/players/1/inventory/1/enchant", "POST", {"enchantment_id": 1})
    ]
    
    for endpoint, method, data in tests:
        duration = test_endpoint(endpoint, method, data)
        if duration is not None:
            results.append((f"{method} {endpoint}", duration))
        print() 



    if results:
        print("RESULTS:")
        results.sort(key=lambda x: x[1], reverse=True)
        
        for i, (endpoint, time_ms) in enumerate(results, 1):
            print(f"{i}. {endpoint}: {time_ms:.2f}ms")
        
        slowest = results[0]
        print(f"\nSLOWEST: {slowest[0]} ({slowest[1]:.2f}ms)")
    else:
        print("No successful tests to analyze")

if __name__ == "__main__":
    main()