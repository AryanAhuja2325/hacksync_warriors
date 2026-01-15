"""
Media Planning Agent - Rule-Based Platform & Content Strategy Recommendations
Pure deterministic logic, no LLMs or ML required.
"""

from typing import Dict, List, Any, Optional
import re
import json
import os
import time as time_module
from datetime import time

# ==================== STATIC DATA ====================

# Platform usage by age group (percentage of age group using platform)
PLATFORM_USAGE = {
    "13-17": {
        "TikTok": 0.67, "Instagram": 0.62, "Snapchat": 0.59, 
        "YouTube": 0.95, "Twitter": 0.23, "Facebook": 0.32
    },
    "18-24": {
        "Instagram": 0.76, "TikTok": 0.61, "YouTube": 0.93, 
        "Twitter": 0.42, "Snapchat": 0.48, "LinkedIn": 0.31, "Facebook": 0.71
    },
    "25-34": {
        "Instagram": 0.71, "Facebook": 0.77, "LinkedIn": 0.59, 
        "Twitter": 0.44, "YouTube": 0.91, "TikTok": 0.38, "Pinterest": 0.35
    },
    "35-44": {
        "Facebook": 0.73, "LinkedIn": 0.46, "Instagram": 0.57, 
        "YouTube": 0.87, "Twitter": 0.35, "Pinterest": 0.42
    },
    "45-54": {
        "Facebook": 0.70, "LinkedIn": 0.34, "YouTube": 0.83, 
        "Pinterest": 0.38, "Instagram": 0.43, "Twitter": 0.27
    },
    "55+": {
        "Facebook": 0.68, "YouTube": 0.79, "Pinterest": 0.32, 
        "LinkedIn": 0.24, "Instagram": 0.33
    }
}

# Domain to optimal platforms mapping
DOMAIN_PLATFORMS = {
    "fashion": ["Instagram", "Pinterest", "TikTok", "YouTube"],
    "beauty": ["Instagram", "TikTok", "YouTube", "Pinterest"],
    "tech": ["YouTube", "Twitter", "LinkedIn", "Reddit"],
    "food": ["Instagram", "TikTok", "Pinterest", "YouTube"],
    "fitness": ["Instagram", "YouTube", "TikTok"],
    "travel": ["Instagram", "YouTube", "Pinterest", "TikTok"],
    "education": ["YouTube", "LinkedIn", "Twitter", "Instagram"],
    "business": ["LinkedIn", "Twitter", "YouTube", "Facebook"],
    "gaming": ["YouTube", "Twitch", "Discord", "Twitter", "TikTok"],
    "sustainability": ["Instagram", "YouTube", "LinkedIn", "Twitter"],
    "finance": ["LinkedIn", "Twitter", "YouTube"],
    "health": ["Instagram", "YouTube", "Pinterest", "Facebook"],
    "parenting": ["Facebook", "Instagram", "Pinterest", "YouTube"],
    "lifestyle": ["Instagram", "Pinterest", "YouTube", "TikTok"]
}

# Content types by domain
DOMAIN_CONTENT = {
    "fashion": ["outfit posts", "styling tips", "haul videos", "lookbooks", "trend reports"],
    "beauty": ["tutorials", "product reviews", "get ready with me", "skincare routines"],
    "tech": ["product reviews", "tutorials", "unboxings", "comparisons", "how-to guides"],
    "food": ["recipes", "cooking videos", "food photography", "restaurant reviews"],
    "fitness": ["workout videos", "form checks", "transformation stories", "nutrition tips"],
    "travel": ["destination guides", "travel vlogs", "itineraries", "travel tips"],
    "education": ["explainer videos", "tutorials", "study tips", "course previews"],
    "business": ["thought leadership", "case studies", "tips & insights", "industry news"],
    "gaming": ["gameplay", "reviews", "walkthroughs", "live streams", "commentary"],
    "sustainability": ["eco tips", "product reviews", "lifestyle changes", "educational content"],
    "finance": ["market analysis", "investment tips", "financial literacy", "news commentary"],
    "health": ["wellness tips", "mental health", "medical info", "product reviews"],
    "parenting": ["parenting tips", "product reviews", "family vlogs", "educational content"],
    "lifestyle": ["day in life", "hauls", "home tours", "productivity tips", "aesthetic content"]
}

# Best posting times by platform (hour ranges in 24h format)
PLATFORM_POSTING_TIMES = {
    "Instagram": {
        "weekday": [(9, 11), (13, 15), (19, 21)],
        "weekend": [(11, 13), (19, 21)]
    },
    "TikTok": {
        "weekday": [(6, 9), (12, 14), (19, 23)],
        "weekend": [(9, 11), (14, 18), (19, 23)]
    },
    "Facebook": {
        "weekday": [(9, 10), (12, 14), (15, 16)],
        "weekend": [(12, 14), (16, 18)]
    },
    "LinkedIn": {
        "weekday": [(7, 9), (12, 13), (17, 18)],
        "weekend": []  # Not recommended
    },
    "Twitter": {
        "weekday": [(8, 10), (12, 13), (17, 18)],
        "weekend": [(9, 11), (19, 21)]
    },
    "YouTube": {
        "weekday": [(14, 16), (18, 22)],
        "weekend": [(9, 11), (14, 18)]
    },
    "Pinterest": {
        "weekday": [(14, 16), (20, 23)],
        "weekend": [(19, 23)]
    }
}

# Growth strategies by domain
DOMAIN_GROWTH = {
    "fashion": [
        "collaborate with micro-influencers",
        "use trending audio/hashtags",
        "post outfit inspiration consistently",
        "engage with fashion communities",
        "run giveaways with partner brands"
    ],
    "beauty": [
        "create tutorial content",
        "partner with beauty influencers",
        "use before/after content",
        "leverage user-generated content",
        "host live makeup sessions"
    ],
    "tech": [
        "create in-depth reviews",
        "share industry insights",
        "engage in tech communities",
        "collaborate with tech reviewers",
        "host Q&A sessions"
    ],
    "food": [
        "share quick recipe videos",
        "use trending food hashtags",
        "partner with food bloggers",
        "engage with food communities",
        "run recipe contests"
    ],
    "fitness": [
        "share transformation stories",
        "post workout challenges",
        "collaborate with fitness influencers",
        "create workout series",
        "host live workout sessions"
    ],
    "default": [
        "post consistently (3-5x per week)",
        "engage authentically with followers",
        "use relevant hashtags strategically",
        "collaborate with niche influencers",
        "analyze and optimize content performance"
    ]
}

# Common mistakes by domain
DOMAIN_MISTAKES = {
    "fashion": [
        "inconsistent aesthetic",
        "ignoring seasonal trends",
        "over-editing photos (unrealistic)",
        "not crediting designers/brands"
    ],
    "beauty": [
        "poor lighting in tutorials",
        "not disclosing sponsored content",
        "making unrealistic claims",
        "ignoring ingredient transparency"
    ],
    "tech": [
        "overly technical jargon",
        "not testing products thoroughly",
        "biased reviews without disclosure",
        "ignoring user experience"
    ],
    "default": [
        "posting inconsistently",
        "ignoring audience engagement",
        "using too many hashtags",
        "buying followers/engagement",
        "copying competitors exactly",
        "not tracking analytics"
    ]
}


# ==================== HELPER FUNCTIONS ====================

def infer_age_group(target_audience: str) -> str:
    """
    Infer age group from target audience description using keyword matching.
    """
    audience_lower = target_audience.lower()
    
    # Keyword mapping to age groups
    if any(word in audience_lower for word in ["teen", "teenager", "high school", "adolescent"]):
        return "13-17"
    
    if any(word in audience_lower for word in ["college", "university", "student", "gen z", "young adult"]):
        return "18-24"
    
    if any(word in audience_lower for word in ["millennial", "young professional", "20s", "30s"]):
        return "25-34"
    
    if any(word in audience_lower for word in ["professional", "parent", "40s", "middle age"]):
        return "35-44"
    
    if any(word in audience_lower for word in ["50s", "mature", "established"]):
        return "45-54"
    
    if any(word in audience_lower for word in ["senior", "retiree", "60+", "boomer"]):
        return "55+"
    
    # Default to broadest young adult range
    return "18-24"


def extract_domain_keywords(domain: str) -> str:
    """
    Normalize domain to match known categories.
    """
    domain_lower = domain.lower()
    
    # Direct matches
    for key in DOMAIN_PLATFORMS.keys():
        if key in domain_lower:
            return key
    
    # Synonym mapping
    if "clothing" in domain_lower or "apparel" in domain_lower:
        return "fashion"
    if "makeup" in domain_lower or "cosmetic" in domain_lower:
        return "beauty"
    if "technology" in domain_lower or "software" in domain_lower or "gadget" in domain_lower:
        return "tech"
    if "restaurant" in domain_lower or "cooking" in domain_lower or "recipe" in domain_lower:
        return "food"
    if "workout" in domain_lower or "gym" in domain_lower or "exercise" in domain_lower:
        return "fitness"
    if "eco" in domain_lower or "green" in domain_lower or "sustainable" in domain_lower:
        return "sustainability"
    if "invest" in domain_lower or "money" in domain_lower or "banking" in domain_lower:
        return "finance"
    
    return "lifestyle"  # Default fallback


def get_platform_scores(age_group: str, domain_platforms: List[str]) -> Dict[str, float]:
    """
    Score platforms based on age group usage and domain relevance.
    """
    age_usage = PLATFORM_USAGE.get(age_group, PLATFORM_USAGE["18-24"])
    
    scores = {}
    for platform in domain_platforms:
        # Base score from age group usage
        base_score = age_usage.get(platform, 0.3)
        
        # Boost score if it's in top domain platforms
        domain_boost = 0.1
        
        scores[platform] = min(base_score + domain_boost, 1.0)
    
    return scores


def format_posting_times(time_ranges: List[tuple]) -> List[str]:
    """
    Convert time ranges to human-readable format.
    """
    formatted = []
    for start, end in time_ranges:
        start_suffix = "AM" if start < 12 else "PM"
        end_suffix = "AM" if end < 12 else "PM"
        
        start_12h = start if start <= 12 else start - 12
        end_12h = end if end <= 12 else end - 12
        
        if start_12h == 0:
            start_12h = 12
        if end_12h == 0:
            end_12h = 12
        
        formatted.append(f"{start_12h}{start_suffix}-{end_12h}{end_suffix}")
    
    return formatted


def analyze_competitors(competitors: List[str], domain: str) -> Dict[str, Any]:
    """
    Basic competitor analysis using heuristics.
    Returns insights about competitive landscape.
    """
    num_competitors = len(competitors)
    
    analysis = {
        "competition_level": "low" if num_competitors < 3 else "medium" if num_competitors < 6 else "high",
        "recommended_approach": "",
        "differentiation_tips": []
    }
    
    if analysis["competition_level"] == "high":
        analysis["recommended_approach"] = "niche down and focus on unique value proposition"
        analysis["differentiation_tips"] = [
            "identify underserved sub-niche",
            "create unique content format",
            "build strong community engagement",
            "focus on authenticity over perfection"
        ]
    elif analysis["competition_level"] == "medium":
        analysis["recommended_approach"] = "consistent quality content with strategic collaborations"
        analysis["differentiation_tips"] = [
            "develop signature content style",
            "engage actively with audience",
            "collaborate with complementary brands"
        ]
    else:
        analysis["recommended_approach"] = "establish strong presence and consistency"
        analysis["differentiation_tips"] = [
            "be first-mover in your niche",
            "build authority through education",
            "create content library"
        ]
    
    return analysis


# ==================== MAIN FUNCTION ====================

def generate_media_plan(
    domain: str,
    target_audience: str,
    competitors: List[str] = None
) -> Dict[str, Any]:
    """
    Generate complete media plan based on domain, audience, and competitors.
    Pure rule-based logic.
    """
    competitors = competitors or []
    
    # Step 1: Infer age group
    age_group = infer_age_group(target_audience)
    
    # Step 2: Normalize domain
    normalized_domain = extract_domain_keywords(domain)
    
    # Step 3: Get relevant platforms for domain
    domain_platforms = DOMAIN_PLATFORMS.get(normalized_domain, DOMAIN_PLATFORMS["lifestyle"])
    
    # Step 4: Score platforms by age group
    platform_scores = get_platform_scores(age_group, domain_platforms)
    
    # Step 5: Select top platforms (score > 0.4)
    recommended_platforms = [
        {"platform": platform, "relevance_score": round(score, 2)}
        for platform, score in sorted(platform_scores.items(), key=lambda x: x[1], reverse=True)
        if score > 0.4
    ][:5]  # Top 5 platforms
    
    # Step 6: Generate posting times
    best_posting_times = {}
    for item in recommended_platforms:
        platform = item["platform"]
        times = PLATFORM_POSTING_TIMES.get(platform, {})
        
        best_posting_times[platform] = {
            "weekday": format_posting_times(times.get("weekday", [])),
            "weekend": format_posting_times(times.get("weekend", []))
        }
    
    # Step 7: Get content types
    content_types = DOMAIN_CONTENT.get(normalized_domain, DOMAIN_CONTENT["lifestyle"])
    
    # Step 8: Get growth strategies
    growth_strategies = DOMAIN_GROWTH.get(normalized_domain, DOMAIN_GROWTH["default"])
    
    # Step 9: Analyze competitors
    competitor_analysis = analyze_competitors(competitors, normalized_domain)
    
    # Step 10: Get mistakes to avoid
    mistakes = DOMAIN_MISTAKES.get(normalized_domain, DOMAIN_MISTAKES["default"])
    
    # Build final recommendation
    result = {
        "recommended_platforms": recommended_platforms,
        "best_posting_times": best_posting_times,
        "content_types": content_types,
        "growth_strategies": growth_strategies,
        "mistakes_to_avoid": mistakes,
        "competitor_insights": competitor_analysis,
        "metadata": {
            "inferred_age_group": age_group,
            "normalized_domain": normalized_domain,
            "target_audience": target_audience
        }
    }
    
    # Save to JSON file
    output_dir = "media_plans"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = int(time_module.time())
    json_filename = f"media_plan_{timestamp}.json"
    json_filepath = os.path.join(output_dir, json_filename)
    
    try:
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✓ Media plan saved: {json_filepath}")
    except Exception as e:
        print(f"Failed to save media plan: {str(e)}")
    
    return result


# ==================== EXAMPLE USAGE ====================

def main():
    """
    Example usage of the Media Planning Agent.
    """
    # Example 1: Fashion brand targeting college students
    print("=" * 80)
    print("EXAMPLE 1: Fashion Brand for College Students")
    print("=" * 80)
    
    plan1 = generate_media_plan(
        domain="sustainable fashion",
        target_audience="environmentally conscious college students",
        competitors=["Everlane", "Patagonia", "Reformation", "Girlfriend Collective"]
    )
    
    import json
    print(json.dumps(plan1, indent=2))
    
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Tech Product for Professionals")
    print("=" * 80)
    
    plan2 = generate_media_plan(
        domain="productivity software",
        target_audience="young professionals in their 30s",
        competitors=["Notion", "Asana"]
    )
    
    print(json.dumps(plan2, indent=2))
    
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Beauty Brand for Gen Z")
    print("=" * 80)
    
    plan3 = generate_media_plan(
        domain="clean beauty products",
        target_audience="Gen Z beauty enthusiasts",
        competitors=["Glossier", "Fenty Beauty", "Rare Beauty", "Milk Makeup", "Tower 28"]
    )
    
    print(json.dumps(plan3, indent=2))


if __name__ == "__main__":
    main()
