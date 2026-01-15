"""
Test Orchestrator with Reasoning Wrapper
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_copywriting_with_reasoning():
    """Test copywriting agent with reasoning"""
    print("=" * 80)
    print("TEST 1: COPYWRITING AGENT WITH REASONING")
    print("=" * 80)
    
    strategy = {
        "product": "EcoBottle - Sustainable Water Bottle",
        "audience": "environmentally conscious college students",
        "goal": "increase brand awareness",
        "tone": "friendly and inspiring",
        "platforms": ["Instagram", "TikTok"],
        "stylistics": "focus on sustainability and Gen Z lifestyle"
    }
    
    print("\n📝 Strategy:")
    print(json.dumps(strategy, indent=2))
    
    print("\n🔄 Calling /generate-copy endpoint...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-copy",
            json={"strategy": strategy},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ Response received!")
            print("\n" + "=" * 80)
            print("RESULT:")
            print("=" * 80)
            print(json.dumps(data['data']['result'], indent=2))
            
            print("\n" + "=" * 80)
            print("🧠 REASONING:")
            print("=" * 80)
            print(f"\n{data['data']['reason']}\n")
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection failed. Is the orchestrator running?")
        print("Run: python orchestrator.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def test_media_planning_with_reasoning():
    """Test media planning agent with reasoning"""
    print("\n" + "=" * 80)
    print("TEST 2: MEDIA PLANNING AGENT WITH REASONING")
    print("=" * 80)
    
    request_data = {
        "domain": "sustainable fashion",
        "target_audience": "environmentally conscious college students",
        "competitors": ["Everlane", "Patagonia", "Reformation"]
    }
    
    print("\n📝 Input:")
    print(json.dumps(request_data, indent=2))
    
    print("\n🔄 Calling /generate-media-plan endpoint...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-media-plan",
            json=request_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ Response received!")
            print("\n" + "=" * 80)
            print("RESULT:")
            print("=" * 80)
            print(f"\nRecommended Platforms: {len(data['recommended_platforms'])} platforms")
            for platform in data['recommended_platforms']:
                print(f"  • {platform['platform']} (score: {platform['relevance_score']})")
            
            print(f"\nContent Types: {', '.join(data['content_types'][:3])}...")
            print(f"Growth Strategies: {len(data['growth_strategies'])} strategies")
            print(f"Mistakes to Avoid: {len(data['mistakes_to_avoid'])} warnings")
            
            # Note: Need to check if reasoning is in the response
            # Currently media plan doesn't show reasoning in response model
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection failed. Is the orchestrator running?")
        print("Run: python orchestrator.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def check_server_status():
    """Check if orchestrator is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Orchestrator is running (version {data['version']})")
            print(f"Available agents: {', '.join(data['available_agents'])}")
            return True
    except:
        pass
    
    print("\n❌ Orchestrator is not running!")
    print("\nTo start it, run:")
    print("  python orchestrator.py")
    print("\nThen run this test again.")
    return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ORCHESTRATOR REASONING TEST SUITE")
    print("=" * 80)
    
    if check_server_status():
        print("\n")
        test_copywriting_with_reasoning()
        test_media_planning_with_reasoning()
        
        print("\n" + "=" * 80)
        print("✅ TESTS COMPLETE")
        print("=" * 80)
