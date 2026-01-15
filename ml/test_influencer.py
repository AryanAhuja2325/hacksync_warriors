"""
Test script for influencer scraper

Before running:
1. Add SCRAPINGBEE_API_KEY to .env file
2. Install dependencies: pip install -r requirements.txt
"""

from hacksync_warriors.ml.influencer_scraper import scrape_influencers
import json


def test_scraper():
    print("Testing Influencer Scraper...")
    print("=" * 60)
    
    # Test parameters
    platform = "instagram"
    category = "fitness"
    limit = 5
    
    print(f"Scraping {platform} influencers in {category} category...")
    print(f"Limit: {limit} per source\n")
    
    try:
        influencers = scrape_influencers(
            platform=platform,
            category=category,
            limit=limit
        )
        
        print(f"\n✅ Successfully scraped {len(influencers)} influencers\n")
        
        # Display results
        for i, inf in enumerate(influencers, 1):
            print(f"{i}. {inf['name']}")
            print(f"   Platform: {inf['platform']}")
            print(f"   Followers: {inf['followers']:,}" if inf['followers'] else "   Followers: Unknown")
            print(f"   Engagement: {inf['engagement']}" if inf['engagement'] else "   Engagement: Not available")
            print(f"   Category: {inf['category']}")
            print(f"   Source: {inf['source']}")
            print()
        
        # Save to JSON
        with open('influencers_output.json', 'w') as f:
            json.dump(influencers, f, indent=2)
        
        print(f"💾 Results saved to influencers_output.json")
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nMake sure SCRAPINGBEE_API_KEY is set in your .env file")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_scraper()
