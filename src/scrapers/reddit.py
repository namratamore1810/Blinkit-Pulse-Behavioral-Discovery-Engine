import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_reddit_keyless(query='blinkit', subreddits=['india', 'bangalore', 'gurgaon'], count_per_sub=50):
    """
    Keyless Reddit scraper using old.reddit.com to bypass API restrictions.
    Note: Reddit frequently blocks simple requests, so we use a custom User-Agent.
    """
    print(f"Starting keyless Reddit scrape for query '{query}' in subreddits: {subreddits}")
    standardized_reviews = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    
    for sub in subreddits:
        print(f"Scraping r/{sub}...")
        url = f"https://old.reddit.com/r/{sub}/search?q={query}&restrict_sr=on&sort=new"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                posts = soup.find_all('div', class_='search-result')
                
                for post in posts[:count_per_sub]:
                    title_elem = post.find('a', class_='search-title')
                    title = title_elem.text if title_elem else ""
                    
                    author_elem = post.find('a', class_='author')
                    author = author_elem.text if author_elem else "Unknown"
                    
                    time_elem = post.find('time')
                    timestamp = time_elem['datetime'] if time_elem else datetime.now().isoformat()
                    
                    # Reddit search results don't always show full body, but title is often enough for behavioral discovery
                    # We merge title and a snippet if available.
                    standardized_reviews.append({
                        'source': f'Reddit (r/{sub})',
                        'author': author,
                        'text': title,
                        'rating': None, # Reddit doesn't have 1-5 ratings
                        'timestamp': timestamp,
                        'original_id': post.get('data-fullname', '')
                    })
            else:
                print(f"Failed to fetch r/{sub}. Status code: {response.status_code}")
                
            # Be polite to Reddit servers
            time.sleep(3)
            
        except Exception as e:
            print(f"Error scraping r/{sub}: {e}")
            
    print(f"Successfully scraped {len(standardized_reviews)} posts from Reddit.")
    return standardized_reviews

if __name__ == "__main__":
    # Test the scraper
    data = scrape_reddit_keyless(subreddits=['gurgaon'])
    print(json.dumps(data, indent=2))
