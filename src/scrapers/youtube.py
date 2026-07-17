import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load env variables directly in case it's run standalone
load_dotenv()

def scrape_youtube_comments(query='blinkit review', max_videos=5, max_comments_per_video=100):
    """
    Scrape YouTube comments using the official YouTube Data API v3.
    """
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key or api_key == 'your_youtube_api_key_here':
        print("YOUTUBE_API_KEY not found in .env. Skipping YouTube scraping.")
        return []
        
    print(f"Searching YouTube for '{query}' and fetching comments...")
    standardized_reviews = []
    
    # 1. Search for videos
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': max_videos,
        'key': api_key
    }
    
    try:
        search_response = requests.get(search_url, params=search_params).json()
        if 'items' not in search_response:
            print(f"YouTube Search Error: {search_response}")
            return []
            
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        
        # 2. Get comments for each video
        comment_url = "https://www.googleapis.com/youtube/v3/commentThreads"
        
        for video_id in video_ids:
            comment_params = {
                'part': 'snippet',
                'videoId': video_id,
                'maxResults': max_comments_per_video,
                'textFormat': 'plainText',
                'key': api_key
            }
            
            comments_response = requests.get(comment_url, params=comment_params).json()
            
            # If comments are disabled, the API returns an error for this video, just skip it
            if 'items' not in comments_response:
                continue
                
            for item in comments_response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                standardized_reviews.append({
                    'source': 'YouTube',
                    'author': comment.get('authorDisplayName', 'Unknown'),
                    'text': comment.get('textDisplay', ''),
                    'rating': None, # YouTube doesn't have 1-5 ratings for comments
                    'timestamp': comment.get('publishedAt', datetime.now().isoformat()),
                    'original_id': comment.get('videoId', video_id)
                })
                
        print(f"Successfully scraped {len(standardized_reviews)} comments from YouTube.")
        return standardized_reviews
        
    except Exception as e:
        print(f"Error scraping YouTube: {e}")
        return []

if __name__ == "__main__":
    data = scrape_youtube_comments()
    print(json.dumps(data, indent=2))

