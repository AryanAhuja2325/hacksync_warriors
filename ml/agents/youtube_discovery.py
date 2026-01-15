import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
import time

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


class YouTubeDiscovery:
    """Discover real YouTube influencers using YouTube Data API v3"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or YOUTUBE_API_KEY
        if not self.api_key:
            raise ValueError("YouTube API key not found. Set YOUTUBE_API_KEY in .env")
        
        self.search_base = "https://www.googleapis.com/youtube/v3/search"
        self.channels_base = "https://www.googleapis.com/youtube/v3/channels"
    
    def search_channels(self, query: str, region: str = "IN", max_results: int = 10) -> List[Dict]:
        """
        Search for YouTube channels by query and region
        
        Args:
            query: Search query (e.g., "sustainable fashion college students")
            region: ISO 3166-1 alpha-2 country code (e.g., "IN" for India, "US" for USA)
            max_results: Number of results to return (max 50)
        
        Returns:
            List of channel data with IDs and basic info
        """
        params = {
            "part": "snippet",
            "q": query,
            "type": "channel",
            "regionCode": region,
            "maxResults": min(max_results, 50),
            "key": self.api_key
        }
        
        try:
            print(f"🔍 Searching YouTube: '{query}' in {region}")
            response = requests.get(self.search_base, params=params, timeout=10)
            response.raise_for_status()
            
            items = response.json().get("items", [])
            print(f"   Found {len(items)} channels")
            
            return items
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise Exception("YouTube API quota exceeded or invalid API key")
            raise Exception(f"YouTube API error: {e}")
        except Exception as e:
            raise Exception(f"Search failed: {e}")
    
    def get_channel_stats(self, channel_ids: List[str]) -> List[Dict]:
        """
        Fetch detailed statistics for channels (subscribers, views, video count)
        
        Args:
            channel_ids: List of YouTube channel IDs
        
        Returns:
            List of channel data with statistics
        """
        if not channel_ids:
            return []
        
        # YouTube API allows up to 50 IDs per request
        params = {
            "part": "statistics,snippet",
            "id": ",".join(channel_ids[:50]),
            "key": self.api_key
        }
        
        try:
            print(f"📊 Fetching stats for {len(channel_ids)} channels...")
            response = requests.get(self.channels_base, params=params, timeout=10)
            response.raise_for_status()
            
            items = response.json().get("items", [])
            return items
            
        except Exception as e:
            raise Exception(f"Stats fetch failed: {e}")
    
    def filter_by_subscriber_range(self, channels: List[Dict], min_subs: int = 10000, max_subs: int = 500000) -> List[Dict]:
        """
        Filter channels by subscriber count range
        
        Args:
            channels: List of channel data with statistics
            min_subs: Minimum subscriber count
            max_subs: Maximum subscriber count
        
        Returns:
            Filtered list of channels
        """
        filtered = []
        
        for channel in channels:
            try:
                # Some channels hide subscriber count
                if channel.get("statistics", {}).get("hiddenSubscriberCount"):
                    continue
                
                sub_count = int(channel.get("statistics", {}).get("subscriberCount", 0))
                
                if min_subs <= sub_count <= max_subs:
                    filtered.append(channel)
            except (ValueError, KeyError):
                continue
        
        print(f"   ✅ {len(filtered)} channels in range {min_subs:,}-{max_subs:,} subscribers")
        return filtered
    
    def format_influencer_data(self, channels: List[Dict]) -> List[Dict]:
        """
        Convert YouTube channel data to standardized influencer format
        
        Args:
            channels: List of channel data from YouTube API
        
        Returns:
            List of influencer dictionaries
        """
        influencers = []
        
        for channel in channels:
            try:
                snippet = channel.get("snippet", {})
                stats = channel.get("statistics", {})
                channel_id = channel.get("id", "")
                
                influencer = {
                    "name": snippet.get("title", "Unknown"),
                    "platform": "YouTube",
                    "niche": snippet.get("description", "")[:100],  # First 100 chars
                    "followers": int(stats.get("subscriberCount", 0)),
                    "followers_formatted": self._format_number(int(stats.get("subscriberCount", 0))),
                    "video_count": int(stats.get("videoCount", 0)),
                    "view_count": int(stats.get("viewCount", 0)),
                    "url": f"https://youtube.com/channel/{channel_id}",
                    "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url"),
                    "verification_status": "youtube_verified",
                    "source": "youtube_api_v3"
                }
                
                influencers.append(influencer)
                
            except Exception as e:
                print(f"⚠️  Error formatting channel: {e}")
                continue
        
        return influencers
    
    def discover_influencers(
        self,
        domain: str,
        audience: str = "",
        country: str = "IN",
        min_followers: int = 10000,
        max_followers: int = 500000,
        max_results: int = 8
    ) -> List[Dict]:
        """
        Main function: Discover YouTube influencers based on domain and audience
        
        Args:
            domain: Product/content domain (e.g., "sustainable fashion")
            audience: Target audience (e.g., "college students")
            country: ISO country code (default: "IN" for India)
            min_followers: Minimum subscriber count
            max_followers: Maximum subscriber count
            max_results: Maximum number of influencers to return
        
        Returns:
            List of influencer dictionaries
        """
        print(f"\n{'='*60}")
        print(f"🎯 YouTube Influencer Discovery")
        print(f"{'='*60}")
        print(f"Domain: {domain}")
        print(f"Audience: {audience}")
        print(f"Country: {country}")
        print(f"Follower range: {min_followers:,} - {max_followers:,}")
        print(f"{'='*60}\n")
        
        # Build search queries
        queries = self._build_search_queries(domain, audience, country)
        
        all_channel_ids = set()
        
        # Search across multiple queries
        for query in queries[:3]:  # Limit to 3 queries to save quota
            try:
                results = self.search_channels(query, region=country, max_results=10)
                
                # Extract channel IDs
                for item in results:
                    channel_id = item.get("id", {}).get("channelId")
                    if channel_id:
                        all_channel_ids.add(channel_id)
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"⚠️  Query failed: {e}")
                continue
        
        if not all_channel_ids:
            print("❌ No channels found")
            return []
        
        # Fetch detailed stats
        channels = self.get_channel_stats(list(all_channel_ids))
        
        # Filter by subscriber range
        filtered_channels = self.filter_by_subscriber_range(
            channels,
            min_subs=min_followers,
            max_subs=max_followers
        )
        
        # Format as influencer data
        influencers = self.format_influencer_data(filtered_channels)
        
        # Limit to max_results
        influencers = influencers[:max_results]
        
        print(f"\n✅ Discovery complete: {len(influencers)} influencers found\n")
        
        return influencers
    
    def _build_search_queries(self, domain: str, audience: str, country: str) -> List[str]:
        """Build multiple search queries from domain and audience"""
        queries = []
        
        country_name = {"IN": "India", "US": "USA", "GB": "UK"}.get(country, country)
        
        if audience:
            queries.append(f"{domain} {audience} {country_name}")
            queries.append(f"{audience} {domain}")
            queries.append(f"{domain} tips {country_name}")
        else:
            queries.append(f"{domain} {country_name}")
            queries.append(f"{domain} creators")
            queries.append(f"{domain} influencers")
        
        return queries
    
    def _format_number(self, num: int) -> str:
        """Format number with K/M suffix"""
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return str(num)


def discover_youtube_influencers(
    domain: str,
    audience: str = "",
    country: str = "IN",
    min_followers: int = 10000,
    max_followers: int = 500000,
    max_results: int = 8
) -> List[Dict]:
    """
    Convenience function for YouTube influencer discovery
    
    Args:
        domain: Product/content domain
        audience: Target audience (optional)
        country: ISO country code
        min_followers: Minimum subscriber count
        max_followers: Maximum subscriber count
        max_results: Maximum number of results
    
    Returns:
        List of influencer dictionaries
    """
    discovery = YouTubeDiscovery()
    return discovery.discover_influencers(
        domain=domain,
        audience=audience,
        country=country,
        min_followers=min_followers,
        max_followers=max_followers,
        max_results=max_results
    )


if __name__ == "__main__":
    # Test the discovery
    import json
    
    influencers = discover_youtube_influencers(
        domain="sustainable fashion",
        audience="college students",
        country="IN",
        max_results=8
    )
    
    # Print results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60 + "\n")
    
    for i, inf in enumerate(influencers, 1):
        print(f"{i}. {inf['name']}")
        print(f"   Subscribers: {inf['followers_formatted']} ({inf['followers']:,})")
        print(f"   Videos: {inf['video_count']}")
        print(f"   URL: {inf['url']}")
        print(f"   Niche: {inf['niche'][:80]}...")
        print()
    
    # Save to JSON
    with open("youtube_influencers.json", "w", encoding="utf-8") as f:
        json.dump(influencers, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved to youtube_influencers.json")
