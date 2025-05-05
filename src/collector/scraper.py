import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    """Scrape text content from a website."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract paragraphs with sufficient length
        paragraphs = soup.find_all('p')
        return [p.get_text() for p in paragraphs if len(p.get_text()) > 50]
    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return []
