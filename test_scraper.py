import sys
sys.path.append('C:/David/src')

from web_scraper import web_fetch, web_extract_text, web_extract_links

print("Testing web scraper...")

# Test fetch
result = web_fetch("https://example.com")
print("Fetch:", result)

# Test text extraction
result = web_extract_text()
print("Text:", result[:200], "...")

# Test link extraction  
result = web_extract_links()
print("Links:", result)
