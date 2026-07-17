import json
import os
from datetime import datetime
from google_play_scraper import Sort, reviews

def scrape_google_play_reviews(app_id='com.grofers.customerapp', count=2000):
    """
    Scrape recent reviews from Google Play Store for the specified app.
    Blinkit's app ID is 'com.grofers.customerapp'.
    """
    print(f"Scraping up to {count} reviews from Google Play Store for {app_id}...")
    
    try:
        result, continuation_token = reviews(
            app_id,
            lang='en', # default language
            country='in', # India
            sort=Sort.NEWEST, # Get the newest reviews
            count=count
        )
        
        standardized_reviews = []
        for review in result:
            standardized_reviews.append({
                'source': 'Google Play Store',
                'author': review.get('userName', 'Unknown'),
                'text': review.get('content', ''),
                'rating': review.get('score', 0),
                'timestamp': review.get('at', datetime.now()).isoformat(),
                'original_id': review.get('reviewId', '')
            })
            
        print(f"Successfully scraped {len(standardized_reviews)} reviews from Google Play.")
        return standardized_reviews
        
    except Exception as e:
        print(f"Error scraping Google Play Store: {e}")
        return []

if __name__ == "__main__":
    # Test the scraper
    data = scrape_google_play_reviews(count=10)
    print(json.dumps(data, indent=2))
