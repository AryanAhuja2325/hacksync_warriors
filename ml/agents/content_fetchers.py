"""
Content fetchers for different platforms.
Phase 1: YouTube API + Transcript fetching
"""

import os
from typing import List, Dict, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()


class YouTubeFetcher:
    """Fetch YouTube video content including transcripts."""
    
    def __init__(self):
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY not found in environment variables")
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def fetch_creator_content(
        self,
        channel_id: Optional[str] = None,
        channel_url: Optional[str] = None,
        max_videos: int = 5
    ) -> List[Dict]:
        """
        Fetch recent videos from a YouTube creator.
        
        Args:
            channel_id: YouTube channel ID
            channel_url: YouTube channel URL (will extract ID)
            max_videos: Number of recent videos to fetch (default: 5)
        
        Returns:
            List of video data dicts
        """
        if not channel_id and not channel_url:
            raise ValueError("Either channel_id or channel_url must be provided")
        
        # Extract channel ID from URL if needed
        if channel_url and not channel_id:
            channel_id = self._extract_channel_id(channel_url)
        
        # Get recent videos
        videos = self._get_recent_videos(channel_id, max_videos)
        
        # Enrich each video with transcript
        enriched_videos = []
        for video in videos:
            video_data = {
                "video_id": video["id"],
                "title": video["title"],
                "description": video["description"],
                "published_date": video["published_at"],
                "url": f"https://www.youtube.com/watch?v={video['id']}",
                "tags": video.get("tags", []),
                "view_count": video.get("view_count", 0),
                "transcript": self._get_transcript(video["id"]),
                "platform": "YouTube"
            }
            enriched_videos.append(video_data)
        
        return enriched_videos
    
    def _extract_channel_id(self, url: str) -> str:
        """Extract channel ID from YouTube URL."""
        # Handle @username format
        if "/@" in url or "/c/" in url or "/user/" in url:
            # Need to search for channel by username
            username = url.split("/")[-1].replace("@", "")
            return self._search_channel_by_username(username)
        
        # Handle /channel/ format
        if "/channel/" in url:
            return url.split("/channel/")[-1].split("/")[0].split("?")[0]
        
        raise ValueError(f"Could not extract channel ID from URL: {url}")
    
    def _search_channel_by_username(self, username: str) -> str:
        """Search for channel ID by username."""
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=username,
                type="channel",
                maxResults=1
            )
            response = request.execute()
            
            if response.get("items"):
                return response["items"][0]["snippet"]["channelId"]
            else:
                raise ValueError(f"Channel not found for username: {username}")
        except Exception as e:
            raise ValueError(f"Error searching for channel: {str(e)}")
    
    def _get_recent_videos(self, channel_id: str, max_results: int) -> List[Dict]:
        """Get recent videos from a channel."""
        try:
            # Get uploads playlist ID
            request = self.youtube.channels().list(
                part="contentDetails",
                id=channel_id
            )
            response = request.execute()
            
            if not response.get("items"):
                return []
            
            uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            
            # Get videos from uploads playlist
            request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=max_results
            )
            response = request.execute()
            
            videos = []
            for item in response.get("items", []):
                video_id = item["contentDetails"]["videoId"]
                
                # Get video details
                video_request = self.youtube.videos().list(
                    part="snippet,statistics",
                    id=video_id
                )
                video_response = video_request.execute()
                
                if video_response.get("items"):
                    video_data = video_response["items"][0]
                    videos.append({
                        "id": video_id,
                        "title": video_data["snippet"]["title"],
                        "description": video_data["snippet"]["description"],
                        "published_at": video_data["snippet"]["publishedAt"],
                        "tags": video_data["snippet"].get("tags", []),
                        "view_count": int(video_data["statistics"].get("viewCount", 0))
                    })
            
            return videos
        
        except Exception as e:
            print(f"Error fetching videos: {str(e)}")
            return []
    
    def _get_transcript(self, video_id: str) -> Optional[str]:
        """Get transcript for a video."""
        try:
            # Try to get transcript (auto-generated or manual)
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Combine all transcript segments
            full_transcript = " ".join([segment["text"] for segment in transcript_list])
            return full_transcript
        
        except Exception as e:
            # Transcript not available
            return None


# Convenience function
def fetch_youtube_content(
    channel_url: str,
    max_videos: int = 5
) -> List[Dict]:
    """
    Quick function to fetch YouTube content.
    
    Args:
        channel_url: YouTube channel URL
        max_videos: Number of videos to fetch
    
    Returns:
        List of video data with transcripts
    """
    fetcher = YouTubeFetcher()
    return fetcher.fetch_creator_content(channel_url=channel_url, max_videos=max_videos)
