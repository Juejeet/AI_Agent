from playwright.sync_api import sync_playwright

def verify_setup():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.saucedemo.com")
        title = page.title()
        print(f"Boss The load is successfull. Title: {title}")
        browser.close()

if __name__ == "__main__":
    verify_setup()
