import sys
sys.path.append('C:/David/src')

from browser_automation import browser_start, browser_navigate, browser_extract_text, browser_close

print("Testing browser automation...")
result = browser_start(headless=True)
print("Start:", result)

result = browser_navigate("https://example.com")
print("Navigate:", result)

result = browser_extract_text()
print("Extract:", result[:200], "...")

result = browser_close()
print("Close:", result)
