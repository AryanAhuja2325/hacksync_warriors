import os
import json
import re
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")  # Google Custom Search Engine ID
SERPAPI_KEY = os.getenv("SERPAPI_KEY")  # Optional SerpAPI key (fallback)


def search_google(query: str, num: int = 5, country: Optional[str] = None, recent_days: Optional[int] = None) -> List[Dict[str, str]]:
    """
    Search Google using Custom Search API.

    Args:
        query: Search query string
        num: Number of results to return (1-10)
        country: Optional country code to bias search (e.g., 'us', 'IN')
        recent_days: Optional, limit results to the last N days

    Returns:
        List of search results with title, link, and snippet
    """
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        logger.error("Missing GOOGLE_API_KEY or GOOGLE_CX environment variables")
        raise ValueError("Missing GOOGLE_API_KEY or GOOGLE_CX")

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": min(num, 10)  # API limit is 10 per request
    }

    # Optional country and date restrictions
    if country:
        params["gl"] = country
    if recent_days:
        # dateRestrict expects 'd[number]' for days (e.g., 'd7')
        params["dateRestrict"] = f"d{int(recent_days)}"

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])

        results = []
        for item in items:
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })

        logger.info(f"Google Search returned {len(results)} results for: {query}")
        return results

    except requests.exceptions.RequestException as e:
        # Provide clearer guidance for 403 errors and optionally fall back
        logger.error(f"Google Search API error: {e}")
        resp = getattr(e, 'response', None)
        if resp is not None:
            try:
                logger.error(f"Response: {resp.text}")
                data = resp.json()
                # If it's a 403, include actionable advice
                if resp.status_code == 403:
                    logger.error("Google Custom Search API returned 403 Forbidden. Likely causes:")
                    logger.error(" - Custom Search API is not enabled for your project")
                    logger.error(" - API key has API restrictions (allowed APIs) that block Custom Search")
                    logger.error(" - Key has application restrictions (IP/HTTP referrers) incompatible with this request")
                    logger.error("Fix: enable the Custom Search API in the Google Cloud Console, ensure the API key belongs to the same project, and remove restrictive key restrictions for testing.")
            except ValueError:
                # ignore json parsing errors
                pass

        # Try optional SerpAPI fallback if configured
        SERPAPI_KEY = os.getenv("SERPAPI_KEY")
        if SERPAPI_KEY:
            logger.info("Attempting fallback to SerpAPI since SERPAPI_KEY is present")
            try:
                return serpapi_search(query, num=num, country=country, recent_days=recent_days)
            except Exception as se:
                logger.error(f"SerpAPI fallback failed: {se}")

        return []


def serpapi_search(query: str, num: int = 5, country: Optional[str] = None, recent_days: Optional[int] = None) -> List[Dict[str, str]]:
    """
    Fallback search using SerpAPI (if SERPAPI_KEY provided).
    Docs: https://serpapi.com/
    """
    if not SERPAPI_KEY:
        raise ValueError("SERPAPI_KEY not configured")

    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "num": min(num, 10)
    }

    # Country and recent days support
    if country:
        params["gl"] = country
    if recent_days:
        # SerpAPI accepts 'tbs' param similar to Google: e.g., 'qdr:d7' for past 7 days
        params["tbs"] = f"qdr:d{int(recent_days)}"

    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        items = data.get("organic_results", [])
        results = []
        for item in items:
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", "") or item.get("snippet", "")
            })
        logger.info(f"SerpAPI returned {len(results)} results for: {query}")
        return results
    except requests.exceptions.RequestException as e:
        logger.error(f"SerpAPI error: {e}")
        raise


def _is_profile_link(link: str) -> bool:
    """Detect whether a link is likely a social profile/handle page."""
    if not link:
        return False
    patterns = [
        r'^https?://(www\.)?instagram\.com/[@A-Za-z0-9_.-]+/?$',
        r'^https?://(www\.)?tiktok\.com/@[\w\.-]+/?',
        r'^https?://(www\.)?twitter\.com/[@A-Za-z0-9_\.-]+/?$',
        r'^https?://(www\.)?linkedin\.com/in/[A-Za-z0-9-_%]+/?$',
        r'^https?://(www\.)?youtube\.com/(?:channel/|c/|user/|@)[A-Za-z0-9_\-@]+(?:/.*)?$'
    ]
    for p in patterns:
        if re.match(p, link):
            return True
    return False


def find_influencers(domain: str, target_audience: str, num_results: int = 5, profiles_only: bool = True, country: Optional[str] = None, recent_days: Optional[int] = None) -> Dict[str, Any]:
    """
    Find top influencers for a specific domain and target audience using Google Search.
    Prefer social profile pages when `profiles_only=True` by using site: queries and
    filtering results to profile URLs.

    Args:
        domain: Industry/domain (e.g., "sustainable products", "fitness", "tech")
        target_audience: Target audience description (e.g., "millennials", "developers")
        num_results: Number of influencers to find (default 5)
        profiles_only: If True, prefer social profile pages (Instagram, YouTube, TikTok, etc.)
        country: Optional country code to bias/limit results (e.g., 'us', 'IN')
        recent_days: Optional, limit results to the last N days

    Returns:
        Dictionary containing influencer search results and metadata
    """
    logger.info(f"Finding influencers for domain: {domain}, audience: {target_audience}, profiles_only={profiles_only}, country={country}, recent_days={recent_days}")

    # Platform-specific site queries (search for profile pages)
    platform_sites = ["instagram.com", "youtube.com", "tiktok.com", "twitter.com", "linkedin.com"]

    queries = []
    if profiles_only:
        for site in platform_sites:
            queries.append(f"site:{site} {domain} {target_audience} influencer")
        # Also try common variants
        queries.append(f"site:instagram.com {domain} {target_audience}")
        queries.append(f"site:youtube.com {domain} {target_audience} channel")
    # Fallback/general queries
    queries.extend([
        f"top {domain} influencers for {target_audience}",
        f"{domain} instagram influencers {target_audience}",
        f"{domain} youtube creators {target_audience}",
        f"best {domain} content creators {target_audience}",
        f"{target_audience} {domain} thought leaders"
    ])

    all_results = []

    # Use up to first 4 queries to limit quota; you can adjust this
    for query in queries[:4]:
        # Prefer SerpAPI fallback if Google is blocked (handled in search_google)
        results = search_google(query, num=num_results, country=country, recent_days=recent_days)
        all_results.extend(results)

    # Deduplicate by link while preserving order
    seen_links = set()
    unique_results = []
    for result in all_results:
        link = result.get("link", "")
        if link and link not in seen_links:
            seen_links.add(link)
            unique_results.append(result)

    # If profiles_only, prioritize profile links
    if profiles_only:
        profile_links = [r for r in unique_results if _is_profile_link(r.get("link", ""))]
        other_links = [r for r in unique_results if not _is_profile_link(r.get("link", ""))]
        final_results = profile_links + other_links
    else:
        final_results = unique_results

    # Limit to requested number
    final_results = final_results[:num_results]

    return {
        "domain": domain,
        "target_audience": target_audience,
        "influencers_count": len(final_results),
        "influencers": final_results,
        "search_queries_used": queries[:4],
        "country": country,
        "recent_days": recent_days
    }


def analyze_market(strategy: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze market and find relevant influencers based on strategy output.
    
    Args:
        strategy: Dictionary containing campaign strategy with domain/product and audience
        
    Expected strategy keys:
        - product: Product/service description
        - audience: Target audience
        - domain: Industry domain (optional, extracted from product if not provided)
        - platforms: List of marketing platforms
        
    Returns:
        Dictionary with market analysis including:
        - influencers: List of found influencers
        - market_insights: Additional market data
        - recommendations: Actionable recommendations
    """
    try:
        # Extract domain and audience from strategy
        domain = strategy.get("domain")
        product = strategy.get("product", "")
        audience = strategy.get("audience", "general audience")
        
        # If domain not explicitly provided, try to extract from product
        if not domain:
            # Simple extraction: take first few words of product description
            domain = " ".join(product.split()[:3]) if product else "general"
            logger.info(f"Domain extracted from product: {domain}")
        
        # Sanitize inputs
        domain = domain.strip()
        audience = audience.strip()
        
        if not domain or not audience:
            logger.warning("Missing domain or audience in strategy")
            return {
                "status": "error",
                "message": "Missing domain or target audience in strategy",
                "influencers": []
            }
        
        # Extract optional filters
        country = strategy.get("country")
        recent_days = strategy.get("recent_days")

        # Find influencers
        influencer_data = find_influencers(domain, audience, num_results=5, country=country, recent_days=recent_days)

        # Generate market insights
        insights = generate_market_insights(strategy, influencer_data)

        return {
            "status": "success",
            "domain": domain,
            "target_audience": audience,
            "influencers": influencer_data["influencers"],
            "insights": insights,
            "recommendations": generate_recommendations(influencer_data, strategy),
            "filters": {
                "country": country,
                "recent_days": recent_days
            }
        }
        
    except Exception as e:
        logger.error(f"Market analysis error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "influencers": []
        }


def generate_market_insights(strategy: Dict[str, Any], influencer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate insights based on influencer search results.
    
    Args:
        strategy: Campaign strategy
        influencer_data: Influencer search results
        
    Returns:
        Dictionary with market insights
    """
    influencers = influencer_data.get("influencers", [])
    
    # Analyze influencer types from snippets
    platform_mentions = {"instagram": 0, "youtube": 0, "tiktok": 0, "blog": 0, "twitter": 0}
    
    for inf in influencers:
        snippet = inf.get("snippet", "").lower()
        title = inf.get("title", "").lower()
        combined = snippet + " " + title
        
        for platform in platform_mentions.keys():
            if platform in combined:
                platform_mentions[platform] += 1
    
    # Determine most common platforms
    top_platforms = sorted(platform_mentions.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return {
        "total_influencers_found": len(influencers),
        "platform_distribution": dict(platform_mentions),
        "recommended_platforms": [p[0] for p in top_platforms if p[1] > 0],
        "search_effectiveness": "high" if len(influencers) >= 5 else "medium" if len(influencers) >= 3 else "low"
    }


def generate_recommendations(influencer_data: Dict[str, Any], strategy: Dict[str, Any]) -> List[str]:
    """
    Generate actionable recommendations based on influencer findings.
    
    Args:
        influencer_data: Influencer search results
        strategy: Campaign strategy
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    influencers = influencer_data.get("influencers", [])
    
    if len(influencers) >= 5:
        recommendations.append(
            f"Found {len(influencers)} relevant influencers. "
            "Consider reaching out to top 3 for collaboration opportunities."
        )
    elif len(influencers) >= 3:
        recommendations.append(
            f"Found {len(influencers)} potential influencers. "
            "Research their engagement rates before outreach."
        )
    else:
        recommendations.append(
            "Limited influencer results found. Consider broadening your domain or audience targeting."
        )
    
    # Platform-specific recommendations
    platforms = strategy.get("platforms", [])
    if "Instagram" in platforms:
        recommendations.append(
            "For Instagram campaigns, prioritize influencers with authentic engagement over follower count."
        )
    
    if "YouTube" in platforms:
        recommendations.append(
            "YouTube collaborations work best with product reviews or tutorial-style content."
        )
    
    recommendations.append(
        "Always verify influencer authenticity and audience demographics before partnership."
    )
    
    return recommendations


# Example usage
if __name__ == "__main__":
    # Test with sample strategy
    test_strategy = {
        "product": "EcoBottle - Reusable Water Bottle",
        "domain": "sustainable products",
        "audience": "environmentally conscious millennials",
        "goal": "increase brand awareness",
        "platforms": ["Instagram", "YouTube"]
    }
    
    result = analyze_market(test_strategy)
    print(json.dumps(result, indent=2))
