from playwright.sync_api import Page
from perception.dom_extractor import extract_dom

def capture_vision_state(page: Page) -> tuple:
    """
    1. Annotates interactive elements on the page with red visual bounding boxes & ID labels.
    2. Takes a screenshot of the annotated page.
    3. Returns (screenshot_bytes, page_metadata_summary).
    """
    # Run the JavaScript injection to draw visual overlays on interactive elements
    _ = extract_dom(page)
    
    # Wait briefly for bounding box rendering to settle
    page.wait_for_timeout(300)
    
    # Capture full viewport screenshot
    screenshot_bytes = page.screenshot(type="png", full_page=False)
    
    # Gather basic page context metadata
    title = page.title()
    url = page.url
    meta_summary = f"PAGE TITLE: {title}\nPAGE URL: {url}"
    
    return screenshot_bytes, meta_summary

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    print("Testing Vision Extractor...")
    test_url = "https://www.saucedemo.com"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(test_url)
        page.wait_for_load_state("networkidle")
        
        screenshot_bytes, meta = capture_vision_state(page)
        
        output_file = "test_annotated_screenshot.png"
        with open(output_file, "wb") as f:
            f.write(screenshot_bytes)
            
        print(f"\nSuccessfully extracted vision state!")
        print(f"Metadata:\n{meta}")
        print(f"Annotated screenshot saved to: {output_file}")
        
        print("\nKeeping browser open for 5 seconds...")
        page.wait_for_timeout(5000)
        browser.close()
