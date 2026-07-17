import json
import os
from datetime import datetime

from scrapers import (
    scrape_google_play_reviews,
    scrape_reddit_keyless,
    scrape_trustpilot,
    scrape_youtube_comments,
    scrape_twitter,
)

def run_ingestion_pipeline():
    print("Starting Data Ingestion Pipeline...")
    all_feedback = []

    # 1. Google Play
    try:
        play_reviews = scrape_google_play_reviews(count=12000)
        all_feedback.extend(play_reviews)
    except Exception as e:
        print(f"Error scraping Google Play: {e}")

    # 2. Reddit
    try:
        reddit_posts = scrape_reddit_keyless(query='blinkit', subreddits=['india', 'bangalore', 'gurgaon', 'delhi', 'mumbai'], count_per_sub=100)
        all_feedback.extend(reddit_posts)
    except Exception as e:
        print(f"Error scraping Reddit: {e}")

    # 3. YouTube
    try:
        youtube_comments = scrape_youtube_comments(query='blinkit app review', max_videos=20, max_comments_per_video=250)
        all_feedback.extend(youtube_comments)
    except Exception as e:
        print(f"Error scraping YouTube: {e}")

    # 4. Trustpilot
    try:
        trustpilot_reviews = scrape_trustpilot()
        all_feedback.extend(trustpilot_reviews)
    except Exception as e:
        print(f"Error scraping Trustpilot: {e}")
        
    # 5. Twitter/X
    try:
        tweets = scrape_twitter(query='blinkit', count=100)
        all_feedback.extend(tweets)
    except Exception as e:
        print(f"Error scraping Twitter: {e}")

    print(f"\nTotal feedback collected: {len(all_feedback)} items.")

    # Save to data/raw/
    raw_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
    os.makedirs(raw_dir, exist_ok=True)
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(raw_dir, f'raw_feedback_{timestamp_str}.json')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(all_feedback, f, indent=4, ensure_ascii=False)
        
    print(f"Data successfully saved to {file_path}")
    return file_path

if __name__ == "__main__":
    run_ingestion_pipeline()
