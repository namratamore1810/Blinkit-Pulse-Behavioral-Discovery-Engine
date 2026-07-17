import json
from datetime import datetime

def scrape_twitter(query='blinkit', count=50):
    """
    Keyless Twitter/X scraping using ntscraper (which relies on Nitter instances).
    """
    print(f"Scraping Twitter for '{query}'...")
    try:
        from ntscraper import Nitter
        # Initialize without logging to keep console clean
        scraper = Nitter(log_level=1)
        
        # Fetch tweets
        tweets = scraper.get_tweets(query, mode='term', number=count)
        
        standardized_reviews = []
        if tweets and 'tweets' in tweets:
            for tweet in tweets['tweets']:
                standardized_reviews.append({
                    'source': 'Twitter/X',
                    'author': tweet.get('user', {}).get('username', 'Unknown'),
                    'text': tweet.get('text', ''),
                    'rating': None,
                    'timestamp': tweet.get('date', datetime.now().isoformat()),
                    'original_id': tweet.get('link', '')
                })
        
        print(f"Successfully scraped {len(standardized_reviews)} tweets from X/Twitter.")
        return standardized_reviews
    except ImportError:
        print("ntscraper is not installed. Run 'pip install ntscraper'.")
        return []
    except Exception as e:
        print(f"Error scraping Twitter/X (Nitter instances are frequently blocked by X): {e}")
        return []

if __name__ == "__main__":
    data = scrape_twitter(count=10)
    print(json.dumps(data, indent=2))
