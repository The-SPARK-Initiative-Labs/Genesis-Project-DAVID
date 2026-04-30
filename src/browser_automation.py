# C:\David\src\browser_automation.py
# Browser automation tools for MCP server

import json
import time
from typing import Optional, Dict, List, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager

class BrowserSession:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def start_session(self, headless: bool = True, timeout: int = 10) -> Dict[str, Any]:
        """Start a new browser session."""
        try:
            options = Options()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
            self.wait = WebDriverWait(self.driver, timeout)
            
            return {
                "status": "success",
                "message": "Browser session started",
                "session_id": id(self.driver)
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to start browser: {str(e)}"
            }
    
    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        try:
            if not self.driver:
                return {"status": "error", "message": "No browser session active"}
            
            self.driver.get(url)
            return {
                "status": "success",
                "url": self.driver.current_url,
                "title": self.driver.title,
                "message": f"Navigated to {url}"
            }
        except Exception as e:
            return {"status": "error", "message": f"Navigation failed: {str(e)}"}
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get current page information."""
        try:
            if not self.driver:
                return {"status": "error", "message": "No browser session active"}
            
            return {
                "status": "success",
                "url": self.driver.current_url,
                "title": self.driver.title,
                "page_source_length": len(self.driver.page_source)
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to get page info: {str(e)}"}
    
    def extract_text(self, selector: str = "body") -> Dict[str, Any]:
        """Extract text from page or specific element."""
        try:
            if not self.driver:
                return {"status": "error", "message": "No browser session active"}
            
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            text = element.text
            
            return {
                "status": "success",
                "text": text,
                "length": len(text)
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to extract text: {str(e)}"}
    
    def extract_links(self, filter_domain: bool = True) -> Dict[str, Any]:
        """Extract all links from current page."""
        try:
            if not self.driver:
                return {"status": "error", "message": "No browser session active"}
            
            links = []
            current_domain = self.driver.current_url.split('/')[2] if filter_domain else None
            
            for element in self.driver.find_elements(By.TAG_NAME, "a"):
                href = element.get_attribute("href")
                text = element.text.strip()
                
                if href:
                    if not filter_domain or current_domain in href:
                        links.append({
                            "url": href,
                            "text": text[:100],  # Limit text length
                            "full_text": text
                        })
            
            return {
                "status": "success",
                "links": links,
                "count": len(links)
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to extract links: {str(e)}"}
    
    def click_element(self, selector: str, selector_type: str = "css") -> Dict[str, Any]:
        """Click an element by selector."""
        try:
            if not self.driver:
                return {"status": "error", "message": "No browser session active"}
            
            by_type = By.CSS_SELECTOR if selector_type == "css" else By.XPATH
            element = self.wait.until(EC.element_to_be_clickable((by_type, selector)))
            element.click()
            
            return {
                "status": "success",
                "message": f"Clicked element: {selector}",
                "current_url": self.driver.current_url
            }
        except TimeoutException:
            return {"status": "error", "message": f"Element not found or clickable: {selector}"}
        except Exception as e:
            return {"status": "error", "message": f"Click failed: {str(e)}"}
    
    def scroll_page(self, direction: str = "down", pixels: int = 500) -> Dict[str, Any]:
        """Scroll the page."""
        try:
            if not self.driver:
                return {"status": "error", "message": "No browser session active"}
            
            if direction == "down":
                self.driver.execute_script(f"window.scrollBy(0, {pixels});")
            elif direction == "up":
                self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
            elif direction == "top":
                self.driver.execute_script("window.scrollTo(0, 0);")
            elif direction == "bottom":
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            return {
                "status": "success",
                "message": f"Scrolled {direction} by {pixels} pixels"
            }
        except Exception as e:
            return {"status": "error", "message": f"Scroll failed: {str(e)}"}
    
    def extract_tables(self) -> Dict[str, Any]:
        """Extract all tables from the page."""
        try:
            if not self.driver:
                return {"status": "error", "message": "No browser session active"}
            
            tables = []
            table_elements = self.driver.find_elements(By.TAG_NAME, "table")
            
            for i, table in enumerate(table_elements):
                rows = []
                for row in table.find_elements(By.TAG_NAME, "tr"):
                    cells = [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "td")]
                    if not cells:  # Try th elements for headers
                        cells = [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "th")]
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
            return {"status": "error", "message": f"Failed to extract tables: {str(e)}"}
    
    def search_text(self, search_term: str) -> Dict[str, Any]:
        """Search for text on the current page."""
        try:
            if not self.driver:
                return {"status": "error", "message": "No browser session active"}
            
            page_source = self.driver.page_source.lower()
            search_lower = search_term.lower()
            
            count = page_source.count(search_lower)
            found = count > 0
            
            # Try to find elements containing the text
            elements = []
            try:
                xpath = f"//*[contains(text(), '{search_term}')]"
                found_elements = self.driver.find_elements(By.XPATH, xpath)
                for elem in found_elements[:10]:  # Limit results
                    elements.append({
                        "tag": elem.tag_name,
                        "text": elem.text[:200],  # Limit text
                        "location": elem.location if elem.is_displayed() else None
                    })
            except:
                pass
            
            return {
                "status": "success",
                "found": found,
                "count": count,
                "elements": elements,
                "search_term": search_term
            }
        except Exception as e:
            return {"status": "error", "message": f"Search failed: {str(e)}"}
    
    def wait_for_element(self, selector: str, timeout: int = 10) -> Dict[str, Any]:
        """Wait for an element to appear."""
        try:
            if not self.driver:
                return {"status": "error", "message": "No browser session active"}
            
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            
            return {
                "status": "success",
                "message": f"Element found: {selector}",
                "text": element.text[:100] if element.text else "",
                "tag": element.tag_name
            }
        except TimeoutException:
            return {"status": "error", "message": f"Element not found within {timeout}s: {selector}"}
        except Exception as e:
            return {"status": "error", "message": f"Wait failed: {str(e)}"}
    
    def close_session(self) -> Dict[str, Any]:
        """Close the browser session."""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.wait = None
                return {"status": "success", "message": "Browser session closed"}
            else:
                return {"status": "info", "message": "No active browser session"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to close browser: {str(e)}"}

# Global browser session
_browser = BrowserSession()

# MCP Tool Functions
def browser_start(headless: bool = True, timeout: int = 10) -> str:
    """Start a browser session for web automation."""
    result = _browser.start_session(headless, timeout)
    return json.dumps(result, indent=2)

def browser_navigate(url: str) -> str:
    """Navigate to a URL."""
    result = _browser.navigate(url)
    return json.dumps(result, indent=2)

def browser_get_info() -> str:
    """Get current page information."""
    result = _browser.get_page_info()
    return json.dumps(result, indent=2)

def browser_extract_text(selector: str = "body") -> str:
    """Extract text from page or specific element."""
    result = _browser.extract_text(selector)
    return json.dumps(result, indent=2)

def browser_extract_links(filter_domain: bool = True) -> str:
    """Extract all links from current page."""
    result = _browser.extract_links(filter_domain)
    return json.dumps(result, indent=2)

def browser_click(selector: str, selector_type: str = "css") -> str:
    """Click an element by CSS selector or XPath."""
    result = _browser.click_element(selector, selector_type)
    return json.dumps(result, indent=2)

def browser_scroll(direction: str = "down", pixels: int = 500) -> str:
    """Scroll the page (down, up, top, bottom)."""
    result = _browser.scroll_page(direction, pixels)
    return json.dumps(result, indent=2)

def browser_extract_tables() -> str:
    """Extract all tables from the current page."""
    result = _browser.extract_tables()
    return json.dumps(result, indent=2)

def browser_search_text(search_term: str) -> str:
    """Search for text on the current page."""
    result = _browser.search_text(search_term)
    return json.dumps(result, indent=2)

def browser_wait_for_element(selector: str, timeout: int = 10) -> str:
    """Wait for an element to appear on the page."""
    result = _browser.wait_for_element(selector, timeout)
    return json.dumps(result, indent=2)

def browser_close() -> str:
    """Close the browser session."""
    result = _browser.close_session()
    return json.dumps(result, indent=2)

# Export functions for MCP server
BROWSER_TOOLS = {
    "browser_start": browser_start,
    "browser_navigate": browser_navigate, 
    "browser_get_info": browser_get_info,
    "browser_extract_text": browser_extract_text,
    "browser_extract_links": browser_extract_links,
    "browser_click": browser_click,
    "browser_scroll": browser_scroll,
    "browser_extract_tables": browser_extract_tables,
    "browser_search_text": browser_search_text,
    "browser_wait_for_element": browser_wait_for_element,
    "browser_close": browser_close
}