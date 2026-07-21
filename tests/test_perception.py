import pytest
from playwright.sync_api import sync_playwright
from perception.dom_extractor import extract_dom

def test_extract_dom_generic():
    with sync_playwright() as p:
        # Changed to headless=False so you can see it!
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # You can change this URL to google.com, amazon.com, etc.
        test_url = "https://www.google.com"
        page.goto(test_url)
        
        # Run our extraction logic
        dom_summary = extract_dom(page)
        
        print(f"\n--- Extracted DOM Summary for {test_url} ---")
        # Safely print to avoid Windows terminal character encoding crashes (UnicodeEncodeError)
        print(dom_summary.encode('ascii', 'replace').decode('ascii'))
        print("-----------------------------\n")
        
        # Pause for 5 seconds so you can see the red boxes!
        page.wait_for_timeout(5000)
        
        # Generic Verifications:
        # 1. The summary should not be totally empty
        assert len(dom_summary) > 0, "No interactive elements were found on the page!"
        
        # 2. It should have successfully numbered at least the first element
        assert "[1]" in dom_summary, "Failed to number the elements correctly"
        
        browser.close()
