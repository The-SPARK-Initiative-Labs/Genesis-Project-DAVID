# C:\David\src\web_scraper.py
# Simple web scraping tools for research without browser dependencies

import requests
import json
import time
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.current_url = None
        self.current_soup = None
    
    def fetch_page(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """Fetch and parse a webpage."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            self.current_url = url
            self.current_soup = BeautifulSoup(response.content, 'html.parser')
            
            return {
                "status": "success",
                "url": url,
                "title": self.current_soup.title.text.strip() if self.current_soup.title else "No title",
                "status_code": response.status_code,
                "content_length": len(response.content),
                "encoding": response.encoding
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to fetch {url}: {str(e)}"}
    
    def extract_text(self, selector: str = None) -> Dict[str, Any]:
        """Extract text from the current page."""
        try:
            if not self.current_soup:
                return {"status": "error", "message": "No page loaded"}
            
            if selector:
                elements = self.current_soup.select(selector)
                if not elements:
                    return {"status": "error", "message": f"No elements found for selector: {selector}"}
                text = " ".join([elem.get_text(strip=True) for elem in elements])
            else:
                text = self.current_soup.get_text(strip=True, separator=" ")
            
            return {
                "status": "success",
                "text": text,
                "length": len(text),
                "selector": selector or "entire page"
            }
        except Exception as e:
            return {"status": "error", "message": f"Text extraction failed: {str(e)}"}
    
    def extract_links(self, filter_domain: bool = True, link_text_contains: str = None) -> Dict[str, Any]:
        """Extract links from the current page."""
        try:
            if not self.current_soup:
                return {"status": "error", "message": "No page loaded"}
            
            links = []
            current_domain = urlparse(self.current_url).netloc if filter_domain else None
            
            for a_tag in self.current_soup.find_all('a', href=True):
                href = a_tag['href']
                text = a_tag.get_text(strip=True)
                
                # Convert relative URLs to absolute
                full_url = urljoin(self.current_url, href)
                
                # Apply filters
                if filter_domain and current_domain:
                    if urlparse(full_url).netloc != current_domain:
                        continue
                
                if link_text_contains and link_text_contains.lower() not in text.lower():
                    continue
                
                links.append({
                    "url": full_url,
                    "text": text[:100],
                    "full_text": text
                })
            
            return {
                "status": "success",
                "links": links,
                "count": len(links),
                "current_url": self.current_url
            }
        except Exception as e:
            return {"status": "error", "message": f"Link extraction failed: {str(e)}"}
    
    def extract_headings(self) -> Dict[str, Any]:
        """Extract all headings from the current page."""
        try:
            if not self.current_soup:
                return {"status": "error", "message": "No page loaded"}
            
            headings = []
            for level in range(1, 7):  # h1 to h6
                for heading in self.current_soup.find_all(f'h{level}'):
                    headings.append({
                        "level": level,
                        "text": heading.get_text(strip=True),
                        "tag": f"h{level}"
                    })
            
            return {
                "status": "success",
                "headings": headings,
                "count": len(headings)
            }
        except Exception as e:
            return {"status": "error", "message": f"Heading extraction failed: {str(e)}"}
    
    def extract_tables(self) -> Dict[str, Any]:
        """Extract tables from the current page."""
        try:
            if not self.current_soup:
                return {"status": "error", "message": "No page loaded"}
            
            tables = []
            for i, table in enumerate(self.current_soup.find_all('table')):
                rows = []
                for row in table.find_all('tr'):
                    cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                    if cells:
                        rows.append(cells)
                
                if rows:
                    tables.append({
                        "table_index": i,
                        "rows": rows,
                        "row_count": len(rows),
                        "column_count": len(rows[0]) if rows else 0
                    })
            
            return {
                "status": "success",
                "tables": tables,
                "count": len(tables)
            }
        except Exception as e:
            return {"status": "error", "message": f"Table extraction failed: {str(e)}"}
    
    def search_text(self, search_term: str, context_chars: int = 100) -> Dict[str, Any]:
        """Search for text on the current page with context."""
        try:
            if not self.current_soup:
                return {"status": "error", "message": "No page loaded"}
            
            full_text = self.current_soup.get_text()
            search_lower = search_term.lower()
            text_lower = full_text.lower()
            
            matches = []
            start = 0
            while True:
                pos = text_lower.find(search_lower, start)
                if pos == -1:
                    break
                
                # Extract context around the match
                context_start = max(0, pos - context_chars)
                context_end = min(len(full_text), pos + len(search_term) + context_chars)
                context = full_text[context_start:context_end]
                
                matches.append({
                    "position": pos,
                    "context": context.strip(),
                    "match_text": full_text[pos:pos + len(search_term)]
                })
                
                start = pos + 1
                if len(matches) >= 10:  # Limit results
                    break
            
            return {
                "status": "success",
                "found": len(matches) > 0,
                "count": len(matches),
                "matches": matches,
                "search_term": search_term
            }
        except Exception as e:
            return {"status": "error", "message": f"Search failed: {str(e)}"}
    
    def follow_link(self, link_text: str = None, link_url: str = None, partial_match: bool = True) -> Dict[str, Any]:
        """Follow a link by text or URL."""
        try:
            if not self.current_soup:
                return {"status": "error", "message": "No page loaded"}
            
            target_url = None
            
            if link_url:
                # Direct URL provided
                target_url = urljoin(self.current_url, link_url)
            elif link_text:
                # Find link by text
                for a_tag in self.current_soup.find_all('a', href=True):
                    text = a_tag.get_text(strip=True)
                    if partial_match:
                        if link_text.lower() in text.lower():
                            target_url = urljoin(self.current_url, a_tag['href'])
                            break
                    else:
                        if link_text.lower() == text.lower():
                            target_url = urljoin(self.current_url, a_tag['href'])
                            break
            
            if not target_url:
                return {"status": "error", "message": f"Link not found: {link_text or link_url}"}
            
            # Follow the link
            return self.fetch_page(target_url)
            
        except Exception as e:
            return {"status": "error", "message": f"Failed to follow link: {str(e)}"}

# Global scraper instance
_scraper = WebScraper()

# MCP Tool Functions
def web_fetch(url: str, timeout: int = 10) -> str:
    """Fetch and parse a webpage."""
    result = _scraper.fetch_page(url, timeout)
    return json.dumps(result, indent=2)

def web_extract_text(selector: str = None) -> str:
    """Extract text from current page or specific elements."""
    result = _scraper.extract_text(selector)
    return json.dumps(result, indent=2)

def web_extract_links(filter_domain: bool = True, link_text_contains: str = None) -> str:
    """Extract links from current page."""
    result = _scraper.extract_links(filter_domain, link_text_contains)
    return json.dumps(result, indent=2)

def web_extract_headings() -> str:
    """Extract all headings from current page."""
    result = _scraper.extract_headings()
    return json.dumps(result, indent=2)

def web_extract_tables() -> str:
    """Extract tables from current page."""
    result = _scraper.extract_tables()
    return json.dumps(result, indent=2)

def web_search_text(search_term: str, context_chars: int = 100) -> str:
    """Search for text on current page with context."""
    result = _scraper.search_text(search_term, context_chars)
    return json.dumps(result, indent=2)

def web_follow_link(link_text: str = None, link_url: str = None, partial_match: bool = True) -> str:
    """Follow a link by text or URL."""
    result = _scraper.follow_link(link_text, link_url, partial_match)
    return json.dumps(result, indent=2)

# Export tools
WEB_SCRAPER_TOOLS = {
    "web_fetch": web_fetch,
    "web_extract_text": web_extract_text,
    "web_extract_links": web_extract_links,
    "web_extract_headings": web_extract_headings,
    "web_extract_tables": web_extract_tables,
    "web_search_text": web_search_text,
    "web_follow_link": web_follow_link
}
