import requests
import json
import os
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import time

class WebScraper:
    def __init__(self, max_pages: int = 5, delay: float = 1.0):
        self.max_pages = max_pages
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search_google(self, query: str, num_results: int = 10) -> List[str]:
        """Search Google and return URLs (simplified version)"""
        # Note: In production, you'd want to use Google Custom Search API
        # This is a simplified version for demonstration
        search_urls = [
            f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
            f"https://www.reddit.com/search/?q={query.replace(' ', '%20')}",
        ]
        return search_urls[:num_results]

    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from a single URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            title = title.get_text().strip() if title else "No Title"
            
            # Extract main content
            content_selectors = [
                'main', 'article', '.content', '#content', 
                '.post-content', '.entry-content', 'p'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = ' '.join([elem.get_text().strip() for elem in elements])
                    break
            
            if not content:
                # Fallback to all paragraph text
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs])
            
            # Clean up content
            content = ' '.join(content.split())  # Remove extra whitespace
            
            return {
                "url": url,
                "title": title,
                "content": content[:5000],  # Limit content length
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "success"
            }
            
        except requests.RequestException as e:
            return {
                "url": url,
                "title": "Error",
                "content": f"Failed to scrape: {str(e)}",
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "error"
            }
        except Exception as e:
            return {
                "url": url,
                "title": "Error",
                "content": f"Parsing error: {str(e)}",
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "error"
            }

    def scrape_topic(self, topic: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Scrape multiple URLs related to a topic"""
        print(f"Searching for topic: {topic}")
        
        # Get URLs to scrape
        urls = self.search_google(topic, max_results)
        
        results = []
        for i, url in enumerate(urls[:self.max_pages]):
            print(f"Scraping {i+1}/{len(urls)}: {url}")
            
            result = self.scrape_url(url)
            results.append(result)
            
            # Add delay between requests
            if i < len(urls) - 1:
                time.sleep(self.delay)
        
        return results

    def save_results(self, results: List[Dict[str, Any]], topic: str) -> str:
        """Save scraping results to JSON file"""
        os.makedirs("data", exist_ok=True)
        
        filename = f"data/{topic.replace(' ', '_').lower()}_research.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to {filename}")
        return filename

def scrape_research_topic(topic: str, max_results: int = 5) -> Dict[str, Any]:
    """Main function to scrape research on a topic"""
    try:
        scraper = WebScraper(max_pages=max_results)
        results = scraper.scrape_topic(topic, max_results)
        
        # Filter successful results
        successful_results = [r for r in results if r["status"] == "success" and len(r["content"]) > 100]
        
        if successful_results:
            filename = scraper.save_results(successful_results, topic)
            
            return {
                "status": "success",
                "topic": topic,
                "results_count": len(successful_results),
                "filename": filename,
                "results": successful_results
            }
        else:
            return {
                "status": "error",
                "topic": topic,
                "message": "No successful scraping results",
                "results": results
            }
            
    except Exception as e:
        return {
            "status": "error",
            "topic": topic,
            "message": f"Scraping failed: {str(e)}",
            "results": []
        }

if __name__ == "__main__":
    # Test the scraper
    topic = "artificial intelligence"
    result = scrape_research_topic(topic, 3)
    print(json.dumps(result, indent=2))