import time
import requests
import random
from typing import Dict, List, Tuple, Optional

API_BASE = "http://localhost:3000"
API_KEY = "brat"

def test_endpoint(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[float]:
    headers = {
        "access_token": API_KEY,
        "Content-Type": "application/json"
    }
    url = f"{API_BASE}{endpoint}"
    
    start_time = time.time()
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        end_time = time.time()
        duration_ms = (end_time - start_time)*1000
        
        if response.status_code >=400:
            print(f"Error {response.status_code} for {method}{endpoint}:{response.text}")
            return None
        
        return duration_ms
        
    except Exception as e:
        print(f"Exception for {method}{endpoint}:{e}")
        return None

def get_player_with_inventory():
    for player_id in random.sample(range(1, 1001), 20):  # checking 20 random players
        response = requests.get(
            f"{API_BASE}/players/{player_id}/inventory",
            headers={"access_token": API_KEY}
        )
        if response.status_code == 200:
            inventory = response.json()
            if inventory.get('items') and len(inventory['items']) > 0:
                return player_id, inventory['items'][0]['item_id']
    return None, None

def test_sequential_inventory_operations(player_id: int, item_id: int, enchantment_id: int):
    results = []
    
    print(f"Step 1: Adding item {item_id} to player {player_id} inventory")
    duration = test_endpoint(f"/players/{player_id}/inventory", "POST", {"item_id": item_id, "quantity": 2})
    if duration:
        results.append({
            'endpoint': f"POST /players/{player_id}/inventory",
            'description': "Add item to inventory",
            'duration_ms': duration
        })
        
        print(f"Step 2: Removing 1 quantity of item {item_id}")
        duration = test_endpoint(f"/players/{player_id}/inventory/{item_id}", "PATCH", {"quantity": 1})
        if duration:
            results.append({
                'endpoint': f"PATCH /players/{player_id}/inventory/{item_id}",
                'description': "Remove item quantity from inventory",
                'duration_ms': duration
            })
            
            print(f"Step 3: Enchanting item {item_id}")
            duration = test_endpoint(f"/players/{player_id}/inventory/{item_id}/enchant", "POST", {"enchantment_id": enchantment_id})
            if duration:
                results.append({
                    'endpoint': f"POST /players/{player_id}/inventory/{item_id}/enchant",
                    'description': "Enchant item in inventory",
                    'duration_ms': duration
                })
                
                print(f"Step 4: Removing enchantments from item {item_id}")
                duration = test_endpoint(f"/players/{player_id}/inventory/{item_id}/enchantments", "DELETE")
                if duration:
                    results.append({
                        'endpoint': f"DELETE /players/{player_id}/inventory/{item_id}/enchantments",
                        'description': "Remove enchantments from item",
                        'duration_ms': duration
                    })
    
    return results

def run_all_endpoint_tests():
    print("Testing all API endpoints")
    print()
    
    sample_player_id = random.randint(1, 1000)
    sample_item_id = random.randint(1, 1000)
    sample_enchantment_id = random.randint(1, 500)
    
    player_with_inventory, existing_item_id = get_player_with_inventory()
    if not player_with_inventory:
        print("Could not find player with inventory items")
        player_with_inventory = sample_player_id
        existing_item_id = sample_item_id
    
    print(f"Using player {sample_player_id} for basic tests")
    print(f"Using player {player_with_inventory} with item {existing_item_id} for existing inventory operations")
    print()
    
    results = []
    
 
    basic_endpoints = [

        ("/", "GET", None, "Root endpoint"),
        
        # Players 
        (f"/players/{sample_player_id}/inventory", "GET", None, "Get player inventory"),
        ("/players", "POST", {"username": f"test_user_{int(time.time())}"}, "Create player"),
        (f"/players/{player_with_inventory}/inventory", "GET", None, "Get inventory of player with items"),
        
        # Items
        ("/items", "GET", None, "Get all items"),
        ("/items?item_type=weapon", "GET", None, "Get items by type"),
        ("/items?rarity=common", "GET", None, "Get items by rarity"),
        ("/items?item_type=weapon&rarity=epic", "GET", None, "Get items by type and rarity"),
        (f"/items/{sample_item_id}", "GET", None, "Get specific item"),
        ("/items", "POST", {"name": f"Test Item {int(time.time())}", "item_type": "weapon", "rarity": "common"}, "Create item"),
        
        # Enchantments
        ("/enchantments", "GET", None, "Get all enchantments"),
        ("/enchantments", "POST", {"name": f"Test Enchantment {int(time.time())}", "effect_description": "Test effect"}, "Create enchantment"),
        (f"/enchantments/{sample_enchantment_id}/effect_description", "PUT", {"effect_description": "Updated effect"}, "Update enchantment"),
    ]
    
    for endpoint, method, data, description in basic_endpoints:
        print(f"Testing {method:6} {endpoint:50}", end=" ... ")
        
        duration = test_endpoint(endpoint, method, data)
        
        if duration is not None:
            print(f"{duration:7.2f}ms")
            results.append({
                'endpoint': f"{method} {endpoint}",
                'description': description,
                'duration_ms': duration
            })
        else:
            print("FAILED")
    
    print()


    print("Testing sequential inventory operations...")
    print()
    
    inventory_results = test_sequential_inventory_operations(sample_player_id, sample_item_id, sample_enchantment_id)
    results.extend(inventory_results)
    
    if player_with_inventory and existing_item_id:
        print()
        print("Testing operations on existing inventory...")
        print()
        
        print(f"Testing enchant on existing item {existing_item_id} in player {player_with_inventory} inventory")
        duration = test_endpoint(f"/players/{player_with_inventory}/inventory/{existing_item_id}/enchant", "POST", {"enchantment_id": sample_enchantment_id})
        if duration:
            results.append({
                'endpoint': f"POST /players/{player_with_inventory}/inventory/{existing_item_id}/enchant",
                'description': "Enchant existing item in inventory",
                'duration_ms': duration
            })
            
            print(f"Testing remove enchantments from existing item {existing_item_id}")
            duration = test_endpoint(f"/players/{player_with_inventory}/inventory/{existing_item_id}/enchantments", "DELETE")
            if duration:
                results.append({
                    'endpoint': f"DELETE /players/{player_with_inventory}/inventory/{existing_item_id}/enchantments",
                    'description': "Remove enchantments from existing item",
                    'duration_ms': duration
                })
    
    return results

def print_performance_results(results: List[Dict]):
    if not results:
        print("No successful tests to report")
        return
    
    sorted_results = sorted(results, key=lambda x: x['duration_ms'], reverse=True)
    
    print()
    print("PERFORMANCE RESULTS")

    print()
    print("All endpoints (slowest to fastest):")
    print()
    
    for i, result in enumerate(sorted_results, 1):
        print(f"{i:2d}. {result['endpoint']:50} {result['duration_ms']:7.2f}ms - {result['description']}")
    
    print()
    print("SUMMARY:")
    print()
    print(f"Total endpoints tested: {len(results)}")
    print(f"Fastest endpoint: {sorted_results[-1]['endpoint']} ({sorted_results[-1]['duration_ms']:.2f}ms)")
    print(f"Slowest endpoint: {sorted_results[0]['endpoint']} ({sorted_results[0]['duration_ms']:.2f}ms)")
    
    total_time = sum(r['duration_ms'] for r in results)
    avg_time = total_time / len(results)
    print(f"Average response time: {avg_time:.2f}ms")


def main():
    print("API Performance Testing")
    print("Testing all endpoints with existing data")
    print()
    
    results = run_all_endpoint_tests()
    
    print_performance_results(results)


if __name__ == "__main__":
    main()