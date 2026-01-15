"""
Content normalizer - converts platform-specific content to unified format.
"""

from typing import Dict, List, Any
from datetime import datetime
import dateutil.parser


def normalize_content(raw_data: Dict, platform: str) -> Dict:
    """
    Normalize content from any platform to unified schema.
    
    Args:
        raw_data: Platform-specific content data
        platform: Platform name ("YouTube", "Instagram", "Blog", etc.)
    
    Returns:
        Normalized content dict with standard fields
    """
    if platform == "YouTube":
        return _normalize_youtube(raw_data)
    elif platform == "Instagram":
        return _normalize_instagram(raw_data)
    elif platform == "Blog":
        return _normalize_blog(raw_data)
    else:
        return _normalize_generic(raw_data)


def normalize_content_list(raw_data_list: List[Dict], platform: str) -> List[Dict]:
    """Normalize a list of content items."""
    return [normalize_content(item, platform) for item in raw_data_list]


def _normalize_youtube(data: Dict) -> Dict:
    """Normalize YouTube video data."""
    return {
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "transcript": data.get("transcript", ""),
        "full_text": _combine_text(
            data.get("title", ""),
            data.get("description", ""),
            data.get("transcript", "")
        ),
        "tags": data.get("tags", []),
        "published_date": _parse_date(data.get("published_date")),
        "url": data.get("url", ""),
        "platform": "YouTube",
        "view_count": data.get("view_count", 0),
        "metadata": {
            "video_id": data.get("video_id", ""),
            "has_transcript": bool(data.get("transcript"))
        }
    }


def _normalize_instagram(data: Dict) -> Dict:
    """Normalize Instagram post data."""
    return {
        "title": "",  # Instagram posts don't have titles
        "description": data.get("caption", ""),
        "transcript": "",
        "full_text": data.get("caption", ""),
        "tags": _extract_hashtags(data.get("caption", "")),
        "published_date": _parse_date(data.get("published_date")),
        "url": data.get("url", ""),
        "platform": "Instagram",
        "view_count": data.get("likes", 0),
        "metadata": {
            "post_type": data.get("post_type", "image"),
            "likes": data.get("likes", 0),
            "comments": data.get("comments", 0)
        }
    }


def _normalize_blog(data: Dict) -> Dict:
    """Normalize blog post data (RSS feed)."""
    return {
        "title": data.get("title", ""),
        "description": data.get("summary", ""),
        "transcript": "",
        "full_text": _combine_text(
            data.get("title", ""),
            data.get("summary", ""),
            data.get("content", "")
        ),
        "tags": data.get("tags", []),
        "published_date": _parse_date(data.get("published")),
        "url": data.get("link", ""),
        "platform": "Blog",
        "view_count": 0,
        "metadata": {
            "author": data.get("author", "")
        }
    }


def _normalize_generic(data: Dict) -> Dict:
    """Fallback normalizer for unknown platforms."""
    return {
        "title": data.get("title", ""),
        "description": data.get("description", data.get("content", "")),
        "transcript": data.get("transcript", ""),
        "full_text": data.get("full_text", data.get("content", "")),
        "tags": data.get("tags", []),
        "published_date": _parse_date(data.get("published_date", data.get("date"))),
        "url": data.get("url", ""),
        "platform": data.get("platform", "Unknown"),
        "view_count": 0,
        "metadata": {}
    }


def _combine_text(*texts: str) -> str:
    """Combine multiple text fields into one, removing empty values."""
    return " ".join([text for text in texts if text and text.strip()])


def _parse_date(date_value: Any) -> str:
    """Parse date to ISO format string."""
    if not date_value:
        return ""
    
    if isinstance(date_value, str):
        try:
            parsed = dateutil.parser.parse(date_value)
            return parsed.isoformat()
        except:
            return date_value
    
    if isinstance(date_value, datetime):
        return date_value.isoformat()
    
    return str(date_value)


def _extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text."""
    if not text:
        return []
    
    words = text.split()
    hashtags = [word.strip("#").lower() for word in words if word.startswith("#")]
    return hashtags
