import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_trustpilot(url='https://www.trustpilot.com/review/blinkit.com', pages=1):
    """
    Scrape reviews from Trustpilot using BeautifulSoup.
    """
    print(f"Scraping {pages} pages of Trustpilot reviews from {url}...")
    standardized_reviews = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    
    for page in range(1, pages + 1):
        paginated_url = f"{url}?page={page}"
        try:
            response = requests.get(paginated_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Trustpilot review cards
                reviews = soup.find_all('section', class_='styles_reviewContentwrapper__zH_9M') # This class name might change, it's a common issue with Trustpilot
                # Fallback to generic article tag if specific class fails
                if not reviews:
                    reviews = soup.find_all('article', {'data-service-review-card-paper': 'true'})
                    
                for review in reviews:
                    text_elem = review.find('p', {'data-service-review-text-typography': 'true'})
                    text = text_elem.text if text_elem else ""
                    
                    if not text:
                        continue # Skip empty reviews
                        
                    # Extract rating (usually an image alt text like "Rated 1 out of 5 stars")
                    rating = None
                    rating_img = review.find('img', alt=lambda x: x and 'out of 5 stars' in x)
                    if rating_img:
                        try:
                            rating = int(rating_img['alt'].split(' ')[1])
                        except:
                            pass
                            
                    standardized_reviews.append({
                        'source': 'Trustpilot',
                        'author': 'Trustpilot User', # Author is usually outside this specific card, keeping it simple
                        'text': text,
                        'rating': rating,
                        'timestamp': datetime.now().isoformat(), # Trustpilot dates require parsing specific <time> tags, using now() for simplicity
                        'original_id': ''
                    })
            else:
                print(f"Failed to fetch Trustpilot page {page}. Status code: {response.status_code}")
                
        except Exception as e:
            print(f"Error scraping Trustpilot: {e}")
            
    print(f"Successfully scraped {len(standardized_reviews)} reviews from Trustpilot.")
    return standardized_reviews

if __name__ == "__main__":
    # Test the scraper
    data = scrape_trustpilot()
    print(json.dumps(data, indent=2))
