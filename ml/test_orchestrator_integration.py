"""
Test the integrated orchestrator endpoints:
- Market discovery using Google Search
- Content-aware outreach generation
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001"

print("=" * 80)
print("TESTING ORCHESTRATOR v2.0 - NEW ENDPOINTS")
print("=" * 80)

print("\n1. TESTING MARKET DISCOVERY (Google Search)")
print("-" * 80)

market_request = {
    "domain": "women's fashion",
    "target_audience": "young women aged 18-30",
    "platforms": ["Instagram", "YouTube"],
    "country": "IN",
    "max_results": 5
}

try:
    response = requests.post(f"{BASE_URL}/discover-market-influencers", json=market_request)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {data['status']}")
        print(f"✓ Found: {data['count']} influencers")
        print(f"✓ Method: {data['discovery_method']}")
        print(f"\nTop 3 Results:")
        for i, inf in enumerate(data['influencers'][:3], 1):
            print(f"\n  {i}. {inf.get('title', 'N/A')}")
            print(f"     Platform: {inf.get('platform', 'N/A')}")
            print(f"     Relevance: {inf.get('relevance_score', 'N/A')}/10")
            print(f"     URL: {inf.get('link', 'N/A')[:80]}...")
            print(f"     Snippet: {inf.get('snippet', 'N/A')[:100]}...")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"✗ Request failed: {e}")

print("\n\n2. TESTING BASIC OUTREACH (No Content Analysis)")
print("-" * 80)

outreach_request_basic = {
    "influencer": {
        "name": "Fashion Influencer",
        "platform": "Instagram",
        "url": "https://instagram.com/fashioninfluencer",
        "niche": "women's fashion and styling"
    },
    "brand_name": "StyleHub",
    "product_domain": "women's fashion",
    "target_audience": "young women aged 18-30",
    "message_type": "casual_dm",
    "analyze_content": False
}

try:
    response = requests.post(f"{BASE_URL}/generate-content-aware-outreach", json=outreach_request_basic)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Status: {data['status']}")
        print(f"✓ Influencer: {data['influencer_name']}")
        print(f"\nMessage Type: {data['outreach']['message_type']}")
        print(f"\nOutreach Message:\n{data['outreach']['message']}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"✗ Request failed: {e}")

print("\n\n3. TESTING CONTENT-AWARE OUTREACH (With YouTube Analysis)")
print("-" * 80)

outreach_request_content_aware = {
    "influencer": {
        "name": "MKBHD",
        "platform": "YouTube",
        "url": "https://www.youtube.com/@mkbhd",
        "niche": "technology reviews"
    },
    "brand_name": "TechGear Pro",
    "product_domain": "tech accessories",
    "target_audience": "tech enthusiasts",
    "message_type": "formal_email",
    "collaboration_idea": "Product review series for wireless charging accessories",
    "analyze_content": True
}

try:
    print("Analyzing YouTube content... (this may take 10-20 seconds)")
    response = requests.post(f"{BASE_URL}/generate-content-aware-outreach", json=outreach_request_content_aware)
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Status: {data['status']}")
        print(f"✓ Influencer: {data['influencer_name']}")
        
        if data.get('content_analysis'):
            analysis = data['content_analysis']
            print(f"\nContent Analysis:")
            print(f"  Topics: {', '.join(analysis.get('main_topics', []))}")
            print(f"  Style: {analysis.get('content_style', 'N/A')}")
            print(f"  Tone: {analysis.get('tone', 'N/A')}")
            if analysis.get('recent_themes'):
                print(f"  Recent: {analysis['recent_themes'][0]}")
        
        print(f"\nSubject: {data['outreach']['subject']}")
        print(f"\nOutreach Message:\n{data['outreach']['message']}")
        
        print("\n📌 Notice how this message references ACTUAL content!")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"✗ Request failed: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE!")
print("=" * 80)
print("\nNOTE: Make sure orchestrator is running:")
print("  python orchestrator.py")
print("  or")
print("  uvicorn orchestrator:app --port 8001")
