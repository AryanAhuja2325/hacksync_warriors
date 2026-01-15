# YouTube Discovery Test

from agents.youtube_discovery import discover_youtube_influencers
import json

print("\n" + "="*60)
print("TESTING YOUTUBE DISCOVERY")
print("="*60 + "\n")

# Test discovery
influencers = discover_youtube_influencers(
    domain="fitness",
    audience="college students",
    country="IN",
    min_followers=10000,
    max_followers=500000,
    max_results=5
)

# Display results
print("\n" + "="*60)
print("RESULTS")
print("="*60 + "\n")

for i, inf in enumerate(influencers, 1):
    print(f"{i}. {inf['name']}")
    print(f"   Platform: {inf['platform']}")
    print(f"   Subscribers: {inf['followers_formatted']} ({inf['followers']:,})")
    print(f"   Videos: {inf['video_count']}")
    print(f"   Views: {inf['view_count']:,}")
    print(f"   URL: {inf['url']}")
    print(f"   Status: {inf['verification_status']}")
    print()

# Save
with open("test_youtube_output.json", "w", encoding="utf-8") as f:
    json.dump(influencers, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(influencers)} influencers to test_youtube_output.json")
