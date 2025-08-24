import requests
from .base import ExternalProgramSource

class YouTubeChannelSource(ExternalProgramSource):
    def __init__(self, channel_id, api_key):
        self.channel_id = channel_id
        self.api_key = api_key

    def fetch_programs(self):
        url = f"https://www.googleapis.com/youtube/v3/search?channelId={self.channel_id}&key={self.api_key}&part=snippet&type=video&maxResults=10"
        response = requests.get(url).json()
        programs = []

        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            programs.append({
                "title": snippet["title"],
                "description": snippet["description"],
                "category": "Documentary",  # You can customize later
                "language": "Arabic",
                "duration": "0:30:00",  # Placeholder, can fetch from videos API
                "publish_date": snippet["publishedAt"],
                "media_type": "documentary",
                "media_url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                "metadata": {}
            })
        return programs
