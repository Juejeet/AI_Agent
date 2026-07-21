import sys
import time
from playwright.sync_api import sync_playwright
from perception.dom_extractor import extract_dom
from reasoning.llm_reasoner import decide_next_action
from action.playwright_executor import execute_action

def run_agent(start_url: str, goal: str, max_steps: int = 10):
    print(f"\n=========================================")
    print(f"🚀 STARTING AGENTIC AI")
    print(f"🎯 Goal: {goal}")
    print(f"🌐 URL: {start_url}")
    print(f"=========================================\n")
    
    with sync_playwright() as p:
        # Launch visible browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(start_url)
        
        # Wait a moment for the initial page to fully render
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass # Ignore if it takes too long
            
        last_action_feedback = None
        
        for step in range(1, max_steps + 1):
            print(f"\n--- STEP {step} ---")
            
            # 1. OBSERVE (Eyes)
            print("👀 Scanning page...")
            dom_summary = extract_dom(page)
            if not dom_summary.strip():
                print("❌ Error: Could not find any interactive elements on this page.")
                break
                
            # 2. REASON (Brain)
            print("🧠 Thinking...")
            try:
                decision = decide_next_action(goal, dom_summary, last_action_feedback)
            except Exception as e:
                print(f"❌ Fatal error talking to Gemini: {e}")
                break
                
            print(f"💬 Thought: {decision.get('reasoning')}")
            
            # 3. ACT (Hands)
            last_action_feedback = execute_action(page, decision)
            
            if last_action_feedback == "DONE":
                print("\n🎉 GOAL ACCOMPLISHED! The agent has finished the task.")
                break
                
            # Give the page a second to react and let network requests settle before scanning again
            try:
                page.wait_for_load_state("networkidle", timeout=3000)
            except Exception:
                time.sleep(1) # Fallback if networkidle fails
            
        else:
            print(f"\n⚠️ Reached maximum step limit of {max_steps}. Stopping to prevent an infinite loop.")
            
        # Leave browser open for a few seconds at the very end so the user can see the final result
        print("\nClosing browser in 5 seconds...")
        page.wait_for_timeout(5000)
        browser.close()

if __name__ == "__main__":
    # Test Scenario: Logging into SauceDemo automatically
    test_url = "https://www.google.com"
    test_goal = "search cars, and go to images. if a captcha appears, wait until it is cleared."
    
    run_agent(test_url, test_goal)
