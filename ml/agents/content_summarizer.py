"""
Content summarizer - analyzes creator content to extract themes, tone, and style.
"""

import os
from typing import List, Dict
from mistralai import Mistral
from dotenv import load_dotenv
import json

load_dotenv()


class ContentSummarizer:
    """Summarize creator content using AI to extract themes and style."""
    
    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-large-latest"
    
    def summarize_creator_themes(self, content_list: List[Dict]) -> Dict:
        """
        Analyze creator's content and extract key themes, style, and hooks.
        
        Args:
            content_list: List of normalized content dicts
        
        Returns:
            Summary dict with themes, tone, style, and actionable insights
        """
        if not content_list:
            return self._empty_summary()
        
        # Build analysis prompt
        prompt = self._build_analysis_prompt(content_list)
        
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
            
            analysis_text = response.choices[0].message.content
            
            # Parse the AI response into structured data
            summary = self._parse_analysis(analysis_text)
            
            # Add metadata
            summary["content_count"] = len(content_list)
            summary["platforms"] = list(set([item.get("platform", "Unknown") for item in content_list]))
            summary["date_range"] = self._get_date_range(content_list)
            
            return summary
        
        except Exception as e:
            print(f"Error summarizing content: {str(e)}")
            return self._empty_summary()
    
    def _build_analysis_prompt(self, content_list: List[Dict]) -> str:
        """Build prompt for content analysis."""
        
        # Prepare content summary for AI
        content_summaries = []
        for i, item in enumerate(content_list[:10], 1):  # Limit to 10 most recent
            title = item.get("title", "")
            description = item.get("description", "")[:300]  # Truncate long descriptions
            full_text = item.get("full_text", "")[:500]  # Use transcript/full text if available
            tags = ", ".join(item.get("tags", [])[:10])
            
            summary = f"""
Content {i}:
Title: {title}
Description: {description}
{f'Tags: {tags}' if tags else ''}
{f'Full Text (excerpt): {full_text}' if full_text else ''}
"""
            content_summaries.append(summary)
        
        content_block = "\n---\n".join(content_summaries)
        
        prompt = f"""Analyze this creator's recent content and provide insights for personalized outreach.

CREATOR'S RECENT CONTENT:
{content_block}

ANALYZE AND EXTRACT:

1. MAIN TOPICS (3-5 topics):
   - What themes do they consistently cover?
   - What specific subjects appear most?

2. CONTENT STYLE:
   - Educational / Entertainment / Inspirational / Lifestyle / Review-based
   - Pick the primary style

3. TONE:
   - Professional / Casual / Humorous / Motivational / Authentic
   - Describe their communication style

4. RECENT THEMES (3-5 specific themes from latest content):
   - What have they talked about recently?
   - Be specific, not generic

5. BRAND MENTIONS (if any):
   - Products or brands they've promoted
   - List any you can identify

6. AUDIENCE FOCUS:
   - Who are they speaking to?
   - What demographics or interests?

7. HOOK EXAMPLES (2-3 phrases or topics):
   - Specific video titles, topics, or phrases they use
   - Things we can reference in outreach

RETURN YOUR ANALYSIS IN THIS EXACT JSON FORMAT:
{{
  "main_topics": ["topic1", "topic2", "topic3"],
  "content_style": "style description",
  "tone": "tone description",
  "recent_themes": ["theme1", "theme2", "theme3"],
  "brand_mentions": ["brand1", "brand2"] or [],
  "audience_focus": "audience description",
  "hook_examples": ["hook1", "hook2"]
}}

IMPORTANT: Return ONLY the JSON, no additional text."""
        
        return prompt
    
    def _parse_analysis(self, analysis_text: str) -> Dict:
        """Parse AI analysis response into structured dict."""
        try:
            # Try to extract JSON from response
            # Sometimes AI adds markdown code blocks
            if "```json" in analysis_text:
                json_str = analysis_text.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_text:
                json_str = analysis_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = analysis_text.strip()
            
            parsed = json.loads(json_str)
            
            # Ensure all required fields exist
            return {
                "main_topics": parsed.get("main_topics", []),
                "content_style": parsed.get("content_style", ""),
                "tone": parsed.get("tone", ""),
                "recent_themes": parsed.get("recent_themes", []),
                "brand_mentions": parsed.get("brand_mentions", []),
                "audience_focus": parsed.get("audience_focus", ""),
                "hook_examples": parsed.get("hook_examples", [])
            }
        
        except Exception as e:
            print(f"Error parsing analysis: {str(e)}")
            # Fallback: try to extract info manually from text
            return self._extract_from_text(analysis_text)
    
    def _extract_from_text(self, text: str) -> Dict:
        """Fallback: extract insights from unstructured text."""
        return {
            "main_topics": [],
            "content_style": "",
            "tone": "",
            "recent_themes": [],
            "brand_mentions": [],
            "audience_focus": "",
            "hook_examples": [],
            "raw_analysis": text  # Store the raw text for reference
        }
    
    def _get_date_range(self, content_list: List[Dict]) -> Dict:
        """Get earliest and latest publication dates."""
        dates = [item.get("published_date") for item in content_list if item.get("published_date")]
        
        if not dates:
            return {"earliest": None, "latest": None}
        
        return {
            "earliest": min(dates),
            "latest": max(dates)
        }
    
    def _empty_summary(self) -> Dict:
        """Return empty summary structure."""
        return {
            "main_topics": [],
            "content_style": "",
            "tone": "",
            "recent_themes": [],
            "brand_mentions": [],
            "audience_focus": "",
            "hook_examples": [],
            "content_count": 0,
            "platforms": [],
            "date_range": {"earliest": None, "latest": None}
        }


# Convenience function
def summarize_content(content_list: List[Dict]) -> Dict:
    """
    Quick function to summarize content.
    
    Args:
        content_list: List of normalized content dicts
    
    Returns:
        Summary dict with themes and insights
    """
    summarizer = ContentSummarizer()
    return summarizer.summarize_creator_themes(content_list)
