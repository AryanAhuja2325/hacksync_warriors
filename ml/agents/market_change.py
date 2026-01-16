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
        logger.error(f"Google Search API error: {e}")
        resp = getattr(e, 'response', None)
        if resp is not None:
            try:
                logger.error(f"Response: {resp.text}")
                if resp.status_code == 403:
                    logger.error("Google Custom Search API returned 403 Forbidden.")
            except ValueError:
                pass

        # Try optional SerpAPI fallback if configured
        SERPAPI_KEY = os.getenv("SERPAPI_KEY")
        if SERPAPI_KEY:
            logger.info("Attempting fallback to SerpAPI")
            try:
                return serpapi_search(query, num=num, country=country, recent_days=recent_days)
            except Exception as se:
                logger.error(f"SerpAPI fallback failed: {se}")

        return []


def serpapi_search(query: str, num: int = 5, country: Optional[str] = None, recent_days: Optional[int] = None) -> List[Dict[str, str]]:
    """Fallback search using SerpAPI"""
    if not SERPAPI_KEY:
        raise ValueError("SERPAPI_KEY not configured")

    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "num": min(num, 10)
    }

    if country:
        params["gl"] = country
    if recent_days:
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
                "snippet": item.get("snippet", "")
            })
        logger.info(f"SerpAPI returned {len(results)} results for: {query}")
        return results
    except requests.exceptions.RequestException as e:
        logger.error(f"SerpAPI error: {e}")
        raise


def _is_profile_link(link: str) -> bool:
    """
    Detect whether a link is an actual social media profile page (not a post).
    
    Returns True only for profile/channel pages, False for individual posts.
    """
    if not link:
        return False
    
    # Patterns for actual profile pages (strict matching)
    profile_patterns = [
        r'^https?://(www\.)?instagram\.com/[A-Za-z0-9_.-]+/?$',  # Profile only, not /p/ posts
        r'^https?://(www\.)?tiktok\.com/@[\w\.-]+/?$',  # Profile only, not /video/ posts
        r'^https?://(www\.)?twitter\.com/[A-Za-z0-9_]+/?$',  # Profile only, not /status/ posts
        r'^https?://(www\.)?linkedin\.com/in/[A-Za-z0-9-_%]+/?$',  # Profile only
        r'^https?://(www\.)?youtube\.com/(?:channel/|c/|user/|@)[A-Za-z0-9_\-@]+/?$'  # Channel only
    ]
    
    # Patterns for posts/content that should be EXCLUDED
    post_patterns = [
        r'/p/',  # Instagram posts
        r'/reel/',  # Instagram reels
        r'/status/',  # Twitter/X posts
        r'/Posts/',  # Twitter/X posts page
        r'/video/',  # TikTok videos
        r'/watch\?v=',  # YouTube videos
        r'/post/',  # LinkedIn posts
    ]
    
    # First check if it's a post (exclude these)
    for pattern in post_patterns:
        if re.search(pattern, link):
            return False
    
    # Then check if it matches profile patterns
    for pattern in profile_patterns:
        if re.match(pattern, link):
            return True
    
    return False


def _calculate_relevance_score(result: Dict[str, str], domain: str, audience: str) -> float:
    """
    Calculate relevance score (0-10) for a search result based on domain and audience matching.
    
    Uses positive keyword matching (not blocklists) to ensure domain-agnostic filtering.
    Works for any domain: sustainable products, AI/ML, fitness, tech, etc.
    
    Args:
        result: Search result with title, link, snippet
        domain: Campaign domain (e.g., "sustainable products", "AI education")
        audience: Target audience (e.g., "college students")
    
    Returns:
        Float score from 0-10 (higher = more relevant)
    """
    title = result.get("title", "").lower()
    snippet = result.get("snippet", "").lower()
    link = result.get("link", "").lower()
    
    combined_text = f"{title} {snippet}"
    
    score = 0.0
    
    # Extract keywords from domain and audience
    domain_keywords = set(domain.lower().split())
    audience_keywords = set(audience.lower().split())
    
    # Remove common stop words
    stop_words = {'a', 'an', 'the', 'for', 'in', 'on', 'to', 'with', 'and', 'or', 'of'}
    domain_keywords = {kw for kw in domain_keywords if kw not in stop_words and len(kw) > 2}
    audience_keywords = {kw for kw in audience_keywords if kw not in stop_words and len(kw) > 2}
    
    # Score 1: Domain keyword matching (0-4 points)
    # MANDATORY: Must have at least 1 domain keyword match
    domain_matches = sum(1 for kw in domain_keywords if kw in combined_text)
    
    # HARD REQUIREMENT: If NO domain keywords found, instant rejection
    if domain_keywords and domain_matches == 0:
        return 0.0  # No domain relevance = useless result
    
    if domain_keywords:
        domain_match_ratio = domain_matches / len(domain_keywords)
        score += domain_match_ratio * 4
    
    # Score 2: Audience keyword matching (0-2 points)
    audience_matches = sum(1 for kw in audience_keywords if kw in combined_text)
    if audience_keywords:
        audience_match_ratio = audience_matches / len(audience_keywords)
        score += audience_match_ratio * 2
    
    # Score 3: Profile link bonus (0-2 points)
    if _is_profile_link(link):
        score += 2
    
    # Score 4: Influencer/creator indicators (0-2 points)
    influencer_terms = ['influencer', 'creator', 'content creator', 'youtuber', 'blogger', 'vlogger']
    if any(term in combined_text for term in influencer_terms):
        score += 1
    
    # Penalty: Generic high-authority accounts that don't match domain
    # Only penalize if domain keywords are COMPLETELY missing
    if domain_keywords and domain_matches == 0:
        # Check if it's a high-follower general account
        generic_indicators = ['million followers', 'verified account', 'official account']
        if any(indicator in combined_text for indicator in generic_indicators):
            score -= 2  # Penalty for generic celebrity accounts
    
    return max(0, min(10, score))  # Clamp between 0-10


def _get_platform_priorities(platforms: List[str], country: Optional[str] = None) -> Dict[str, int]:
    """
    Get platform search priorities based on user's requested platforms and country.
    
    Args:
        platforms: List of platforms from strategy (e.g., ["Instagram", "YouTube"])
        country: Country code (e.g., "IN" for India)
    
    Returns:
        Dictionary mapping platform domain to query weight
    """
    # Normalize platform names
    platform_map = {
        'instagram': 'instagram.com',
        'youtube': 'youtube.com',
        'tiktok': 'tiktok.com',
        'twitter': 'twitter.com',
        'x': 'twitter.com',  # X (formerly Twitter)
        'linkedin': 'linkedin.com',
        'facebook': 'facebook.com'
    }
    
    # Default priorities (Instagram and YouTube are most reliable for influencer discovery)
    default_priorities = {
        'instagram.com': 5,  # Highest priority - best for product influencers
        'youtube.com': 4,    # High priority - great for content creators
        'linkedin.com': 2,   # Medium priority - good for B2B/professional
        'twitter.com': 2,    # Medium priority - thought leaders
        'tiktok.com': 1      # Low priority - viral content
    }
    
    # TikTok is banned in India - set to 0
    if country and country.upper() == "IN":
        default_priorities['tiktok.com'] = 0
    
    if not platforms:
        return default_priorities
    
    # Build priorities from user's requested platforms
    priorities = {}
    for platform in platforms:
        platform_lower = platform.lower()
        if platform_lower in platform_map:
            site = platform_map[platform_lower]
            priorities[site] = 5  # High priority for requested platforms
    
    # If user specified platforms, still add others with lower priority
    if priorities:
        for site, default_weight in default_priorities.items():
            if site not in priorities:
                # Reduce weight for non-requested platforms
                priorities[site] = max(1, default_weight - 2)
    else:
        priorities = default_priorities
    
    # Apply country restrictions
    if country and country.upper() == "IN":
        priorities['tiktok.com'] = 0
    
    return priorities


def find_influencers(
    domain: str,
    target_audience: str,
    num_results: int = 5,
    profiles_only: bool = True,
    country: Optional[str] = None,
    recent_days: Optional[int] = None,
    platforms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Find top influencers with intelligent platform prioritization and relevance filtering.
    
    Searches for: Platform + Domain + Target Audience combined
    Filters: Only actual influencer profiles (not individual posts)
    
    Args:
        domain: Industry/domain (e.g., "sustainable products", "AI education")
        target_audience: Target audience (e.g., "college students")
        num_results: Number of influencers to find
        profiles_only: If True, prefer social profile pages
        country: Optional country code (e.g., 'IN')
        recent_days: Optional, limit to recent results
        platforms: List of platforms to prioritize (e.g., ["Instagram", "YouTube"])
    
    Returns:
        Dictionary with influencer results and metadata
    """
    logger.info(f"Finding influencers: domain={domain}, audience={target_audience}, platforms={platforms}, country={country}")
    
    # Get platform priorities based on user preferences and country
    platform_priorities = _get_platform_priorities(platforms or [], country)
    
    queries = []
    
    # Extract simplified audience keywords (remove verbose terms like "aged 18-30")
    audience_short = re.sub(r'\baged?\s+\d{1,2}[-\u2013]\d{1,2}\b', '', target_audience)
    audience_short = re.sub(r'\b\d{1,2}[-\u2013]\d{1,2}\b', '', audience_short)
    audience_words = [w for w in audience_short.split() if len(w) > 2][:3]  # Max 3 words
    audience_clean = ' '.join(audience_words)
    
    if profiles_only:
        # Build DOMAIN-FIRST queries: platform + domain + audience
        for site, weight in platform_priorities.items():
            if weight == 0:
                continue  # Skip banned/disabled platforms
            
            if weight >= 4:  # High priority platforms (user requested)
                # Query 1: Domain + influencer + country (most specific)
                queries.append(f"site:{site} {domain} influencer {country or ''}")
                # Query 2: Domain + audience + creator
                queries.append(f"site:{site} {domain} {audience_clean} creator")
                # Query 3: Domain + audience (general)
                queries.append(f"site:{site} {domain} {audience_clean}")
            elif weight >= 2:  # Medium priority
                # Single query: domain + country
                queries.append(f"site:{site} {domain} {country or ''}")
            # Skip weight 1 platforms to save quota
    
    # Add general queries (DOMAIN-FIRST, not audience-first)
    country_name = {"IN": "India", "US": "USA", "GB": "UK"}.get(country or "", country or "")
    queries.extend([
        f"{domain} influencer {country_name} {audience_clean}",
        f"{domain} creator {audience_clean}",
        f"best {domain} influencers {country_name}"
    ])
    
    all_results = []
    
    # Execute searches (limit to 6 queries to save quota)
    for query in queries[:6]:
        results = search_google(query, num=num_results, country=country, recent_days=recent_days)
        all_results.extend(results)
    
    # Deduplicate by link
    seen_links = set()
    unique_results = []
    for result in all_results:
        link = result.get("link", "")
        if link and link not in seen_links:
            seen_links.add(link)
            unique_results.append(result)
    
    # Filter: Remove non-profile pages (posts, videos, etc.)
    profile_results = []
    for result in unique_results:
        link = result.get("link", "")
        if _is_profile_link(link):
            profile_results.append(result)
        else:
            logger.debug(f"Filtered out non-profile: {link}")
    
    logger.info(f"Filtered to {len(profile_results)} profile pages from {len(unique_results)} total results")
    
    # Calculate relevance scores for profile results only
    scored_results = []
    for result in profile_results:
        score = _calculate_relevance_score(result, domain, target_audience)
        scored_results.append({
            **result,
            "relevance_score": round(score, 2),
            "confidence": "high" if score >= 7 else "medium" if score >= 4 else "low"
        })
    
    # Filter out low-relevance results (score < 3)
    filtered_results = [r for r in scored_results if r["relevance_score"] >= 3.0]
    
    # Sort by relevance score (highest first)
    filtered_results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Limit to requested number
    final_results = filtered_results[:num_results]
    
    logger.info(f"Found {len(final_results)} relevant influencer profiles")
    
    return {
        "influencers": final_results,  # Frontend expects this key
        "count": len(final_results),  # Alternative naming
        "domain": domain,
        "target_audience": target_audience,
        "search_queries_used": queries[:6],
        "country": country,
        "recent_days": recent_days,
        "platform_priorities": platform_priorities,
        "metadata": {
            "total_scanned": len(unique_results),
            "profiles_found": len(profile_results),
            "after_relevance_filter": len(filtered_results)
        }
    }


def analyze_market(strategy: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze market and find relevant influencers with intelligent filtering.
    
    Improvements:
    - Respects user's platform preferences
    - Calculates relevance scores for all results
    - Filters out irrelevant results automatically
    - Works for any domain (sustainable, AI/ML, fitness, etc.)
    
    Args:
        strategy: Campaign strategy dictionary
        
    Expected strategy keys:
        - product: Product/service description
        - audience: Target audience
        - domain: Industry domain (optional)
        - platforms: List of platforms (e.g., ["Instagram", "YouTube"])
        - country: Country code (optional)
        
    Returns:
        Dictionary with filtered, scored influencer results
    """
    try:
        # Extract strategy parameters
        domain = strategy.get("domain")
        product = strategy.get("product", "")
        audience = strategy.get("audience", "general audience")
        platforms = strategy.get("platforms", [])
        
        # Extract domain from product if not provided
        if not domain:
            domain = " ".join(product.split()[:3]) if product else "general"
            logger.info(f"Domain extracted from product: {domain}")
        
        domain = domain.strip()
        audience = audience.strip()
        
        if not domain or not audience:
            logger.warning("Missing domain or audience")
            return {
                "status": "error",
                "message": "Missing domain or target audience",
                "influencers": []
            }
        
        # Extract filters
        country = strategy.get("country")
        recent_days = strategy.get("recent_days")
        
        # Find influencers with intelligent filtering
        influencer_data = find_influencers(
            domain=domain,
            target_audience=audience,
            num_results=5,
            country=country,
            recent_days=recent_days,
            platforms=platforms
        )
        
        # Generate insights
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
                "recent_days": recent_days,
                "platforms": platforms
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
    """Generate insights with relevance scoring"""
    influencers = influencer_data.get("influencers", [])
    
    # Analyze platform distribution
    platform_mentions = {"instagram": 0, "youtube": 0, "tiktok": 0, "twitter": 0, "linkedin": 0}
    
    for inf in influencers:
        link = inf.get("link", "").lower()
        for platform in platform_mentions.keys():
            if platform in link:
                platform_mentions[platform] += 1
    
    # Calculate average relevance score
    avg_score = sum(inf.get("relevance_score", 0) for inf in influencers) / len(influencers) if influencers else 0
    
    # Count high-confidence results
    high_confidence = sum(1 for inf in influencers if inf.get("confidence") == "high")
    
    top_platforms = sorted(platform_mentions.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return {
        "total_influencers_found": len(influencers),
        "platform_distribution": dict(platform_mentions),
        "recommended_platforms": [p[0] for p in top_platforms if p[1] > 0],
        "average_relevance_score": round(avg_score, 2),
        "high_confidence_count": high_confidence,
        "search_effectiveness": "high" if len(influencers) >= 5 else "medium" if len(influencers) >= 3 else "low"
    }


def generate_recommendations(influencer_data: Dict[str, Any], strategy: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on filtered results"""
    recommendations = []
    influencers = influencer_data.get("influencers", [])
    
    if len(influencers) >= 5:
        high_conf = sum(1 for inf in influencers if inf.get("confidence") == "high")
        recommendations.append(
            f"Found {len(influencers)} relevant influencers ({high_conf} high-confidence). "
            "Review top 3-5 for collaboration."
        )
    elif len(influencers) >= 3:
        recommendations.append(
            f"Found {len(influencers)} potential influencers. "
            "Verify relevance and engagement before outreach."
        )
    else:
        recommendations.append(
            "Limited results found. Consider broadening domain or trying different platforms."
        )
    
    # Platform-specific advice
    platforms = strategy.get("platforms", [])
    if "Instagram" in platforms:
        recommendations.append(
            "Instagram: Prioritize micro-influencers (10k-100k) with authentic engagement."
        )
    
    if "YouTube" in platforms:
        recommendations.append(
            "YouTube: Look for creators with consistent upload schedules and engaged comment sections."
        )
    
    if "Twitter" in platforms or "LinkedIn" in platforms:
        recommendations.append(
            "Twitter/LinkedIn: Focus on thought leaders who regularly discuss your domain topics."
        )
    
    recommendations.append(
        "Always verify: (1) Content alignment, (2) Audience demographics, (3) Engagement authenticity."
    )
    
    return recommendations


# Example usage
if __name__ == "__main__":
    # Test with sustainable products
    test_strategy = {
        "product": "EcoBottle - Reusable Water Bottle",
        "domain": "sustainable products",
        "audience": "environmentally conscious college students",
        "platforms": ["Instagram", "YouTube"],
        "country": "IN"
    }
    
    result = analyze_market(test_strategy)
    print(json.dumps(result, indent=2))
