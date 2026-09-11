import sys
import time
from playwright.sync_api import sync_playwright
from perception.dom_extractor import extract_dom, check_for_captcha
from perception.vision_extractor import capture_vision_state
from reasoning.llm_reasoner import decide_next_action
from reasoning.vision_reasoner import decide_next_action_vision
from action.playwright_executor import execute_action

def run_agent(start_url: str, goal: str, max_steps: int = 10, perception_mode: str = "dom", step_callback = None):
    print(f"\n=========================================")
    print(f"STARTING AGENTIC AI (Mode: {perception_mode.upper()})")
    print(f"Goal: {goal}")
    print(f"URL: {start_url}")
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
            
        action_history = []
        success = False
        steps_taken = 0
        consecutive_errors = 0
        final_answer = ""
        
        for step in range(1, max_steps + 1):
            steps_taken = step
            print(f"\n--- STEP {step} ---")
            
            # Check for CAPTCHA before proceeding
            if check_for_captcha(page):
                print("\n[!] CAPTCHA / Security Challenge Detected!")
                if step_callback:
                    step_callback({
                        "type": "captcha_detected",
                        "step": step,
                        "message": "CAPTCHA / Security Challenge Detected! Solve it in the browser, then click Resume."
                    })
                input(">>> Please solve the CAPTCHA in the opened browser window, then press ENTER in this terminal to continue...")
                print("Resuming agent execution...\n")
                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass
                
            history_str = "\n".join(action_history) if action_history else "None"
            
            # Determine effective perception mode for this step (Hybrid Fallback Logic)
            current_step_mode = perception_mode.lower()
            if current_step_mode == "hybrid":
                try:
                    temp_dom = extract_dom(page)
                except Exception:
                    temp_dom = ""
                if not temp_dom.strip() or consecutive_errors >= 2:
                    print(f"[HYBRID FALLBACK TRIGGERED] DOM empty or consecutive errors ({consecutive_errors}). Switching to Vision Mode!")
                    current_step_mode = "vision"
                else:
                    current_step_mode = "dom"
            
            if current_step_mode == "vision":
                # 1. OBSERVE VISUALLY (Screenshots)
                print("Scanning page visually (capturing screenshot)...")
                screenshot_bytes, page_meta = capture_vision_state(page)
                
                # 2. REASON (Multimodal Brain)
                print("Thinking visually...")
                try:
                    decision = decide_next_action_vision(goal, screenshot_bytes, page_meta, history_str)
                except Exception as e:
                    print(f"Fatal error talking to Gemini Vision: {e}")
                    break
            else:
                # 1. OBSERVE DOM (HTML text)
                print("Scanning page (DOM)...")
                dom_summary = extract_dom(page)
                if not dom_summary.strip():
                    print("Error: Could not find any interactive elements on this page.")
                    break
                    
                # 2. REASON (Text Brain)
                print("Thinking...")
                try:
                    decision = decide_next_action(goal, dom_summary, history_str)
                except Exception as e:
                    print(f"Fatal error talking to Gemini: {e}")
                    break
                
            print(f"Thought: {decision.get('reasoning')}")
            
            # 3. ACT (Hands)
            result = execute_action(page, decision)
            action_history.append(f"Step {step}: {decision.get('action_type')} on element {decision.get('element_id')} -> {result}")
            
            if step_callback:
                step_callback({
                    "type": "step_update",
                    "step": step,
                    "mode": current_step_mode,
                    "thought": decision.get("reasoning"),
                    "action_type": decision.get("action_type"),
                    "element_id": decision.get("element_id"),
                    "text_to_type": decision.get("text_to_type"),
                    "final_answer": decision.get("final_answer"),
                    "result": result
                })
            
            if result.startswith("ERROR"):
                consecutive_errors += 1
            else:
                consecutive_errors = 0
            
            # Prevent premature done exit if a CAPTCHA or Cloudflare challenge is still active
            if result == "DONE" and check_for_captcha(page):
                print("\n[!] Action output 'done', but a CAPTCHA / Security Challenge is still active on screen!")
                input(">>> Please solve the CAPTCHA in the opened browser window, then press ENTER in this terminal to continue...")
                print("Resuming agent execution...\n")
                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass
                continue
            
            if result == "DONE":
                final_answer = decision.get("final_answer", "")
                print("\nGOAL ACCOMPLISHED! The agent has finished the task.")
                if final_answer:
                    print(f"\nFinal Answer:\n{final_answer}")
                success = True
                break
                
            # Give the page a second to react and let network requests settle before scanning again
            try:
                page.wait_for_load_state("networkidle", timeout=3000)
            except Exception:
                time.sleep(1) # Fallback if networkidle fails
            
        else:
            print(f"\nReached maximum step limit of {max_steps}. Stopping to prevent an infinite loop.")
            
        final_url = page.url
        # Leave browser open briefly if running manually, but close quickly for eval script
        page.wait_for_timeout(1000)
        browser.close()
        
        return {
            "success": success,
            "final_url": final_url,
            "steps": steps_taken,
            "final_answer": final_answer
        }

if __name__ == "__main__":
    print("\n=========================================")
    print("      AUTONOMOUS WEB AGENT RUNNER        ")
    print("=========================================\n")
    
    url_input = input("Enter starting URL [default: https://www.saucedemo.com]: ").strip()
    target_url = url_input if url_input else "https://www.saucedemo.com"
    
    goal_input = input("Enter your Goal [default: Log in with standard_user and secret_sauce]: ").strip()
    target_goal = goal_input if goal_input else "Log in with the username 'standard_user' and the password 'secret_sauce', and then click on the login button."
    
    mode_input = input("Enter perception mode (dom / vision / hybrid) [default: hybrid]: ").strip()
    target_mode = mode_input.lower() if mode_input in ["dom", "vision", "hybrid"] else "hybrid"
    
    result = run_agent(target_url, target_goal, max_steps=10, perception_mode=target_mode)
    print(f"\nFinal Outcome: {result}")
