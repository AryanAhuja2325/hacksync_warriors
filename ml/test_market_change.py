# Test the improved market_change.py

from agents.market_change import analyze_market
import json

print("\n" + "="*60)
print("TESTING IMPROVED MARKET ANALYSIS")
print("="*60 + "\n")

# Test strategy
test_strategy = {
    "product": "StyleHub - Women's Fashion Boutique",
    "domain": "women's fashion",
    "audience": "young women aged 18-30",
    "platforms": ["Instagram", "YouTube"],  # User specifies platforms
    "country": "IN"
}

print("Strategy:")
print(json.dumps(test_strategy, indent=2))
print("\n" + "="*60 + "\n")

# Run analysis
result = analyze_market(test_strategy)

# Display results
print("RESULTS:")
print("="*60)
print(f"Status: {result['status']}")
print(f"Domain: {result['domain']}")
print(f"Audience: {result['target_audience']}")
print(f"\nInfluencers Found: {len(result['influencers'])}\n")

for i, inf in enumerate(result['influencers'], 1):
    print(f"{i}. {inf['title']}")
    print(f"   URL: {inf['link']}")
    print(f"   Relevance Score: {inf.get('relevance_score', 'N/A')}/10")
    print(f"   Confidence: {inf.get('confidence', 'N/A')}")
    print(f"   Snippet: {inf['snippet'][:80]}...")
    print()

print("="*60)
print("\nInsights:")
print(json.dumps(result['insights'], indent=2))

print("\nRecommendations:")
for rec in result['recommendations']:
    print(f"  • {rec}")

# Save output
with open("market_change_test_output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\n💾 Saved to market_change_test_output.json")
