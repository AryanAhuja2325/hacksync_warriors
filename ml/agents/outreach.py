import os
from mistralai import Mistral
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class OutreachGenerator:
    """
    Generates authentic, personalized outreach messages for influencer collaborations.
    Focuses on building genuine relationships rather than sounding promotional.
    """
    
    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-large-latest"
    
    def generate_outreach_message(
        self,
        influencer_data: Dict,
        brand_info: Dict,
        message_type: str = "initial_contact",
        content_summary: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Generate personalized outreach message for an influencer.
        
        Args:
            influencer_data: Dict containing influencer details
                - name: Influencer name
                - platform: Platform they're on
                - url: Their profile URL
                - niche: Their content niche
                - snippet: Description/bio snippet
            brand_info: Dict containing brand details
                - brand_name: Company/brand name
                - product_domain: Product category
                - target_audience: Who the product is for
                - collaboration_idea: Specific collaboration concept (optional)
            message_type: Type of outreach
                - "initial_contact": First time reaching out
                - "follow_up": Following up after no response
                - "partnership_proposal": Detailed partnership pitch
                - "casual_dm": Casual Instagram/social DM
                - "formal_email": Professional email format
            content_summary: Optional dict with creator's content analysis
                - main_topics: List of main topics they cover
                - recent_themes: Recent specific themes
                - tone: Their communication tone
                - hook_examples: Specific videos/posts to reference
        
        Returns:
            Dict with 'subject' and 'message' keys
        """
        
        # Build context-aware prompt
        prompt = self._build_outreach_prompt(influencer_data, brand_info, message_type, content_summary)
        
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            message_content = response.choices[0].message.content
            
            # Parse subject and body if it's an email format
            if message_type == "formal_email":
                subject, body = self._parse_email_format(message_content)
            else:
                subject = f"Collaboration with {brand_info.get('brand_name', 'our brand')}"
                body = message_content
            
            return {
                "subject": subject,
                "message": body,
                "message_type": message_type,
                "platform": influencer_data.get("platform", "Unknown")
            }
            
        except Exception as e:
            return {
                "subject": "Error generating outreach",
                "message": f"Error: {str(e)}",
                "message_type": message_type,
                "platform": influencer_data.get("platform", "Unknown")
            }
    
    def generate_bulk_outreach(
        self,
        influencers: List[Dict],
        brand_info: Dict,
        message_type: str = "initial_contact"
    ) -> List[Dict]:
        """
        Generate outreach messages for multiple influencers.
        
        Returns:
            List of dicts with influencer data + outreach message
        """
        results = []
        
        for influencer in influencers:
            outreach = self.generate_outreach_message(
                influencer_data=influencer,
                brand_info=brand_info,
                message_type=message_type
            )
            
            results.append({
                "influencer": influencer,
                "outreach": outreach
            })
        
        return results
    
    def _build_outreach_prompt(
        self,
        influencer_data: Dict,
        brand_info: Dict,
        message_type: str,
        content_summary: Optional[Dict] = None
    ) -> str:
        """Build the prompt for Mistral based on message type and context."""
        
        influencer_name = influencer_data.get("name", "there")
        platform = influencer_data.get("platform", "social media")
        niche = influencer_data.get("niche", influencer_data.get("snippet", "your content"))
        brand_name = brand_info.get("brand_name", "our brand")
        product_domain = brand_info.get("product_domain", "our products")
        target_audience = brand_info.get("target_audience", "our audience")
        collaboration_idea = brand_info.get("collaboration_idea", "")
        
        # Build content-aware context if summary provided
        content_context = ""
        if content_summary and content_summary.get("main_topics"):
            topics = ", ".join(content_summary.get("main_topics", [])[:3])
            recent_themes = content_summary.get("recent_themes", [])
            hook_examples = content_summary.get("hook_examples", [])
            tone = content_summary.get("tone", "")
            
            content_context = f"""
THEIR RECENT CONTENT (Use this to personalize!):
- Main Topics: {topics}
- Recent Themes: {', '.join(recent_themes[:3]) if recent_themes else 'N/A'}
- Content Tone: {tone if tone else 'N/A'}
{f'- Hook Examples: {hook_examples[0]}' if hook_examples else ''}

💡 PERSONALIZATION REQUIREMENT:
Reference their actual content! Mention a specific topic or recent theme.
Example: "Loved your recent video on {recent_themes[0] if recent_themes else 'topic'}..."
"""
        
        base_context = f"""You are a relationship manager reaching out to influencers for authentic collaborations.

INFLUENCER DETAILS:
- Name: {influencer_name}
- Platform: {platform}
- Content Focus: {niche}
{content_context}
BRAND DETAILS:
- Brand: {brand_name}
- Product Category: {product_domain}
- Target Audience: {target_audience}
{f'- Collaboration Idea: {collaboration_idea}' if collaboration_idea else ''}

CRITICAL RULES:
1. Sound like a real human, not a marketing bot
2. NO generic templates or copy-paste vibes
3. Show you actually looked at their content
4. Focus on mutual value, not just what you want
5. Keep it conversational and authentic
6. Don't oversell or sound desperate
7. Be specific about why YOU reached out to THEM
8. Make it feel like the start of a friendship, not a transaction
"""
        
        type_specific_instructions = {
            "initial_contact": """
Write a brief, friendly initial outreach message (3-4 sentences max).

TONE: Warm, genuine, like messaging a friend-of-a-friend
GOAL: Start a conversation, not close a deal
STRUCTURE:
- Quick genuine compliment about their specific content
- Brief mention of why you thought of them
- Casual question or invitation to chat

DO NOT include formal greetings or signatures. Just the message body.
""",
            
            "casual_dm": """
Write a super casual Instagram/social media DM (2-3 sentences).

TONE: Like sliding into DMs of someone you admire
VIBE: Short, punchy, emoji-friendly (use 1-2 relevant emojis MAX)
GOAL: Get them interested enough to reply

DO NOT sound salesy. Just genuine interest.
""",
            
            "follow_up": """
Write a brief follow-up message (2-3 sentences).

TONE: Friendly check-in, not pushy
GOAL: Gentle reminder without being annoying
STRUCTURE:
- Acknowledge they're probably busy
- Quick reminder of what you're about
- Easy out if not interested

Stay cool and understanding.
""",
            
            "formal_email": """
Write a professional but warm email.

FORMAT:
Subject: [Create compelling subject line]
---
[Email body]

TONE: Professional yet personable
STRUCTURE:
1. Personal greeting and genuine compliment
2. Brief brand introduction (1-2 sentences)
3. Why this partnership makes sense for THEM
4. Specific collaboration idea (keep flexible)
5. Easy next step
6. Warm sign-off

LENGTH: 150-200 words MAX. Nobody reads long emails.

Include both Subject line and body, separated by '---'
""",
            
            "partnership_proposal": """
Write a detailed partnership proposal message.

TONE: Professional but excited
STRUCTURE:
1. Genuine appreciation for their work
2. Brief brand story and mission
3. Why you see a perfect fit
4. Specific collaboration concepts (2-3 ideas)
5. What's in it for them (be specific)
6. Flexible next steps
7. Warm close

LENGTH: 200-300 words. Detailed but scannable.

DO NOT include subject line, just the message body.
"""
        }
        
        instruction = type_specific_instructions.get(
            message_type,
            type_specific_instructions["initial_contact"]
        )
        
        return base_context + "\n" + instruction
    
    def _parse_email_format(self, content: str) -> tuple:
        """Parse email content into subject and body."""
        
        if "---" in content:
            parts = content.split("---", 1)
            subject_part = parts[0].strip()
            body = parts[1].strip()
            
            # Extract subject from "Subject: ..." format
            if subject_part.startswith("Subject:"):
                subject = subject_part.replace("Subject:", "").strip()
            else:
                subject = subject_part
            
            return subject, body
        else:
            # If no separator, use first line as subject
            lines = content.split("\n", 1)
            subject = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else content
            
            return subject, body


def generate_outreach_for_influencer(
    influencer: Dict,
    brand_name: str,
    product_domain: str,
    target_audience: str,
    message_type: str = "initial_contact",
    collaboration_idea: Optional[str] = None,
    content_summary: Optional[Dict] = None
) -> Dict[str, str]:
    """
    Convenience function to generate outreach message for a single influencer.
    
    Args:
        influencer: Influencer data from market.py
        brand_name: Your brand/company name
        product_domain: What you sell/offer
        target_audience: Who it's for
        message_type: Type of outreach message
        collaboration_idea: Specific collaboration concept (optional)
        content_summary: Optional content analysis from content_summarizer.py
    
    Returns:
        Dict with subject and message
    """
    generator = OutreachGenerator()
    
    brand_info = {
        "brand_name": brand_name,
        "product_domain": product_domain,
        "target_audience": target_audience,
        "collaboration_idea": collaboration_idea
    }
    
    return generator.generate_outreach_message(
        influencer_data=influencer,
        brand_info=brand_info,
        message_type=message_type,
        content_summary=content_summary
    )


def generate_bulk_outreach_messages(
    influencers: List[Dict],
    brand_name: str,
    product_domain: str,
    target_audience: str,
    message_type: str = "initial_contact",
    collaboration_idea: Optional[str] = None
) -> List[Dict]:
    """
    Generate outreach messages for multiple influencers.
    
    Args:
        influencers: List of influencer data from market.py
        brand_name: Your brand/company name
        product_domain: What you sell/offer
        target_audience: Who it's for
        message_type: Type of outreach message
        collaboration_idea: Specific collaboration concept (optional)
    
    Returns:
        List of dicts with influencer data + outreach message
    """
    generator = OutreachGenerator()
    
    brand_info = {
        "brand_name": brand_name,
        "product_domain": product_domain,
        "target_audience": target_audience,
        "collaboration_idea": collaboration_idea
    }
    
    return generator.generate_bulk_outreach(
        influencers=influencers,
        brand_info=brand_info,
        message_type=message_type
    )


# Example usage
if __name__ == "__main__":
    # Example influencer data (as returned by market.py)
    sample_influencer = {
        "name": "Sarah Johnson",
        "platform": "Instagram",
        "url": "https://instagram.com/sarahjohnson",
        "niche": "sustainable fashion and lifestyle",
        "snippet": "Fashion blogger promoting eco-friendly brands"
    }
    
    # Generate different types of outreach
    print("=== CASUAL DM ===")
    dm = generate_outreach_for_influencer(
        influencer=sample_influencer,
        brand_name="EcoThreads",
        product_domain="sustainable fashion",
        target_audience="young women aged 18-30",
        message_type="casual_dm"
    )
    print(f"{dm['message']}\n")
    
    print("\n=== FORMAL EMAIL ===")
    email = generate_outreach_for_influencer(
        influencer=sample_influencer,
        brand_name="EcoThreads",
        product_domain="sustainable fashion",
        target_audience="young women aged 18-30",
        message_type="formal_email",
        collaboration_idea="Instagram content series featuring our new sustainable denim line"
    )
    print(f"Subject: {email['subject']}")
    print(f"\n{email['message']}\n")
    
    print("\n=== INITIAL CONTACT ===")
    initial = generate_outreach_for_influencer(
        influencer=sample_influencer,
        brand_name="EcoThreads",
        product_domain="sustainable fashion",
        target_audience="young women aged 18-30",
        message_type="initial_contact"
    )
    print(f"{initial['message']}\n")
