"""
Test Market Agent - Google Custom Search API for Influencer Discovery
"""

from hacksync_warriors.ml.market import analyze_market, find_influencers
import json

print("\n" + "="*60)
print("TESTING MARKET AGENT (Google Custom Search)")
print("="*60 + "\n")

# Test 1: Direct influencer search
print("Test 1: Direct Influencer Search")
print("-" * 60)

result = find_influencers(
    domain="sustainable fashion",
    target_audience="college students",
    num_results=5,
    profiles_only=True,
    country="IN"
)

print(f"\nDomain: {result['domain']}")
print(f"Target Audience: {result['target_audience']}")
print(f"Influencers Found: {result['influencers_count']}\n")

for i, inf in enumerate(result['influencers'], 1):
    print(f"{i}. {inf['title'][:60]}...")
    print(f"   URL: {inf['link']}")
    print(f"   Snippet: {inf['snippet'][:100]}...")
    print()

# Test 2: Full market analysis
print("\n" + "="*60)
print("Test 2: Full Market Analysis")
print("="*60 + "\n")

strategy = {
    "product": "EcoBottle - Reusable Water Bottle",
    "domain": "sustainable products",
    "audience": "environmentally conscious college students",
    "goal": "increase brand awareness",
    "platforms": ["Instagram", "YouTube"],
    "country": "IN"
}

market_result = analyze_market(strategy)

print(f"Status: {market_result['status']}")
print(f"Domain: {market_result['domain']}")
print(f"Target Audience: {market_result['target_audience']}")
print(f"\nInfluencers Found: {len(market_result['influencers'])}")

print("\nInsights:")
for key, value in market_result['insights'].items():
    print(f"  {key}: {value}")

print("\nRecommendations:")
for rec in market_result['recommendations']:
    print(f"  • {rec}")

# Save results
with open("market_test_output.json", "w", encoding="utf-8") as f:
    json.dump(market_result, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved results to market_test_output.json")
