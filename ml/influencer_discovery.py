"""
LLM-based Influencer Discovery Agent
Uses AI to suggest relevant influencers based on campaign strategy
"""

import os
import json
from mistralai import Mistral
from dotenv import load_dotenv
from typing import Dict, List, Any

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# System prompt for influencer discovery
SYSTEM_PROMPT = """You are an expert influencer marketing strategist with deep knowledge of social media creators across platforms.

Your task is to suggest relevant micro and nano influencers based on the campaign requirements.

Guidelines:
- Focus on authentic, niche creators (NOT mainstream celebrities)
- Follower range: 10k to 500k for Instagram/YouTube, 50k to 1M for TikTok
- Prioritize engagement and audience alignment over follower count
- Consider regional creators when location is specified
- Look for creators who genuinely align with the brand values
- Suggest a diverse mix of content styles and sub-niches

For each influencer, provide:
1. Name: Creator handle or real name
2. Platform: Instagram, YouTube, TikTok, etc.
3. Niche: Specific content category
4. Estimated followers: Approximate follower count (use K/M notation)
5. Reason: One compelling sentence explaining why they're relevant

Return ONLY valid JSON - no additional text or explanation."""


def discover_influencers(strategy: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use AI to discover relevant influencers based on campaign strategy
    
    Args:
        strategy: Marketing strategy JSON containing product, audience, goals, etc.
    
    Returns:
        Dictionary with:
        - influencers: List of suggested influencers
        - count: Number of suggestions
        - disclaimer: Transparency message
    """
    
    if not MISTRAL_API_KEY:
        raise ValueError("MISTRAL_API_KEY not found in environment")
    
    client = Mistral(api_key=MISTRAL_API_KEY)
    
    # Extract relevant info from strategy
    product = strategy.get('product', 'product')
    audience = strategy.get('audience', 'general audience')
    platforms = strategy.get('platforms', ['Instagram'])
    niche = strategy.get('stylistics', strategy.get('category', 'general'))
    location = strategy.get('location', 'India')
    
    # Build discovery prompt
    user_prompt = f"""Suggest 8 influencers for this campaign:

Product: {product}
Target Audience: {audience}
Preferred Platforms: {', '.join(platforms)}
Niche/Style: {niche}
Location: {location}

Requirements:
- Micro/nano influencers (10k-500k followers)
- NOT mainstream celebrities
- Authentic creators with engaged communities
- Relevant to the product and audience

Return as JSON array with this structure:
[
  {{
    "name": "CreatorHandle",
    "platform": "Instagram",
    "niche": "Specific category",
    "followers": "120k",
    "reason": "Why they're perfect for this campaign"
  }}
]

Provide ONLY the JSON array, no other text."""

    try:
        # Call Mistral API
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        # Remove markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        influencers = json.loads(content)
        
        # Validate structure
        if not isinstance(influencers, list):
            raise ValueError("Response is not a list")
        
        # Add metadata
        for inf in influencers:
            inf['source'] = 'ai_discovery'
            inf['verified'] = False
            inf['status'] = 'suggested'
        
        return {
            "influencers": influencers,
            "count": len(influencers),
            "disclaimer": "AI-suggested influencers based on campaign requirements. Please verify profiles before outreach.",
            "metadata": {
                "product": product,
                "audience": audience,
                "platforms": platforms,
                "location": location
            }
        }
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse AI response as JSON: {e}\nResponse: {content}")
    except Exception as e:
        raise Exception(f"Influencer discovery failed: {e}")


def generate_outreach_message(influencer: Dict[str, Any], campaign_details: Dict[str, Any]) -> str:
    """
    Generate personalized outreach message for an influencer
    
    Args:
        influencer: Influencer data (name, platform, niche, reason)
        campaign_details: Campaign strategy details
    
    Returns:
        Personalized outreach message
    """
    
    if not MISTRAL_API_KEY:
        raise ValueError("MISTRAL_API_KEY not found in environment")
    
    client = Mistral(api_key=MISTRAL_API_KEY)
    
    product = campaign_details.get('product', 'our product')
    brand_tone = campaign_details.get('tone', 'friendly and professional')
    
    outreach_prompt = f"""Write a personalized collaboration outreach message for this influencer:

Influencer: {influencer['name']}
Platform: {influencer['platform']}
Niche: {influencer['niche']}
Why they're relevant: {influencer['reason']}

Campaign:
Product: {product}
Brand Tone: {brand_tone}

Requirements:
- Keep it under 150 words
- Start with genuine appreciation for their content
- Briefly explain why they're a perfect fit
- Mention the collaboration opportunity
- Include a clear call-to-action
- Use {brand_tone} tone
- Make it feel personal, not templated

Write ONLY the message, no subject line or additional notes."""

    try:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": "You are an expert at writing authentic, personalized influencer outreach messages that get responses."},
                {"role": "user", "content": outreach_prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        raise Exception(f"Outreach generation failed: {e}")


if __name__ == "__main__":
    # Test the discovery agent
    test_strategy = {
        "product": "EcoBottle - Sustainable Water Bottle",
        "audience": "environmentally conscious college students",
        "platforms": ["Instagram", "YouTube"],
        "stylistics": "sustainability and campus lifestyle",
        "location": "India",
        "tone": "friendly and inspiring"
    }
    
    print("Testing Influencer Discovery Agent...")
    print("=" * 60)
    
    result = discover_influencers(test_strategy)
    
    print(f"\n✅ Discovered {result['count']} influencers")
    print(f"\n⚠️  {result['disclaimer']}\n")
    
    for i, inf in enumerate(result['influencers'], 1):
        print(f"{i}. {inf['name']} (@{inf['platform']})")
        print(f"   Niche: {inf['niche']}")
        print(f"   Followers: {inf['followers']}")
        print(f"   Why: {inf['reason']}")
        print()
    
    # Test outreach generation
    print("=" * 60)
    print("Testing Outreach Generation...\n")
    
    sample_influencer = result['influencers'][0]
    outreach = generate_outreach_message(sample_influencer, test_strategy)
    
    print(f"Outreach message for {sample_influencer['name']}:")
    print("-" * 60)
    print(outreach)
    print("-" * 60)
