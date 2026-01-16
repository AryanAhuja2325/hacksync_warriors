"""
Test Unified Server.py - All Endpoints
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_health_check():
    """Test server health"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_parse_strategy():
    """Test strategy parser"""
    print("\n" + "="*80)
    print("TEST 2: Parse Strategy")
    print("="*80)
    
    payload = {
        "input_data": "We are Swasya, a sustainable jeans brand. We use scrapped and old fabrics to make new jeans. We want to promote our brand to college kids and make them aware of our motto. We want the campaign to be energetic and fun.",
        "input_type": "text"
    }
    
    response = requests.post(f"{BASE_URL}/parse-strategy", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Strategy Parsed:")
        print(json.dumps(data.get('strategy', {}), indent=2))
        return data.get('strategy', {})
    else:
        print(f"Error: {response.text}")
        return None


def test_generate_copy(strategy):
    """Test copywriting agent"""
    print("\n" + "="*80)
    print("TEST 3: Generate Copy")
    print("="*80)
    
    if not strategy:
        print("Skipping - no strategy available")
        return
    
    payload = {"strategy": strategy}
    
    response = requests.post(f"{BASE_URL}/generate-copy", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Copy Generated: ✓")
        print(f"Sample: {str(data)[:200]}...")
    else:
        print(f"Error: {response.text}")


def test_generate_mood_board(strategy):
    """Test visual agent"""
    print("\n" + "="*80)
    print("TEST 4: Generate Mood Board")
    print("="*80)
    
    if not strategy:
        print("Skipping - no strategy available")
        return
    
    payload = {
        "strategy": strategy,
        "num_variations": 2,  # Just 2 for testing
        "image_size": "1024x1024"
    }
    
    print("Generating mood board (this may take 30-60 seconds)...")
    
    response = requests.post(f"{BASE_URL}/generate-mood-board", json=payload, timeout=120)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Mood Board Generated: ✓")
        print(f"Status: {data.get('status')}")
        print(f"Images: {data.get('total_generated')}/{payload['num_variations']}")
        print(f"Theme: {data.get('visual_theme')}")
    else:
        print(f"Error: {response.text}")


def test_generate_media_plan(strategy):
    """Test media planning agent"""
    print("\n" + "="*80)
    print("TEST 5: Generate Media Plan")
    print("="*80)
    
    if not strategy:
        print("Skipping - no strategy available")
        return
    
    payload = {"strategy": strategy}
    
    response = requests.post(f"{BASE_URL}/generate-media-plan", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Media Plan Generated: ✓")
        print(f"Platforms: {len(data.get('platforms', []))}")
        print(f"Top Platform: {data.get('platforms', [{}])[0].get('name', 'N/A')}")
    else:
        print(f"Error: {response.text}")


def test_discover_influencers(strategy):
    """Test influencer discovery"""
    print("\n" + "="*80)
    print("TEST 6: Discover Influencers")
    print("="*80)
    
    if not strategy:
        print("Skipping - no strategy available")
        return
    
    payload = {"strategy": {**strategy, "location": "India"}}
    
    response = requests.post(f"{BASE_URL}/discover-influencers", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Influencers Discovered: ✓")
        print(f"Count: {data.get('count', 0)}")
        if data.get('influencers'):
            print(f"Sample: {data['influencers'][0].get('name', 'N/A')}")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("UNIFIED SERVER TEST SUITE")
    print("Testing server.py on http://127.0.0.1:8001")
    print("="*80)
    
    try:
        # Test health
        if not test_health_check():
            print("\n✗ Server not responding. Make sure server.py is running!")
            exit(1)
        
        # Parse strategy (foundation for other tests)
        strategy = test_parse_strategy()
        
        # Test other endpoints
        test_generate_copy(strategy)
        test_generate_mood_board(strategy)
        test_generate_media_plan(strategy)
        test_discover_influencers(strategy)
        
        print("\n" + "="*80)
        print("✓ ALL TESTS COMPLETED")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to server")
        print("Please start the server with: python server.py")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
