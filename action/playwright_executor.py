from playwright.sync_api import Page

def execute_action(page: Page, decision: dict) -> str:
    """
    Takes the structured JSON decision from the LLM and executes it on the page.
    Returns a status string ('DONE', 'SUCCESS', or 'ERROR: ...') to feed back to the LLM.
    """
    action_type = decision.get("action_type")
    
    if action_type == "done":
        return "DONE"
        
    element_id = decision.get("element_id")
    if not element_id:
        error_msg = f"ERROR: No element_id provided for action '{action_type}'"
        print(f"-> {error_msg}")
        return error_msg
        
    # Find the element by the custom agent-id we injected during perception (Week 2)
    selector = f"[agent-id='{element_id}']"
    element = page.locator(selector).first
    
    # Wait briefly to ensure it exists
    if element.count() == 0:
        error_msg = f"ERROR: Element with agent-id {element_id} was not found on the page. It may have been removed or you hallucinated the ID."
        print(f"-> {error_msg}")
        return error_msg
        
    # Visual Polish: Highlight the element the agent is about to interact with in BLUE
    try:
        element.evaluate("el => { el.style.outline = '4px solid blue'; el.style.backgroundColor = 'rgba(0,0,255,0.2)'; }")
    except Exception:
        pass # Ignore if it fails to draw the highlight
    
    try:
        if action_type == "click":
            print(f"-> ACTION: Clicking element {element_id}")
            element.click(timeout=3000)
        elif action_type == "type":
            text = decision.get("text_to_type", "")
            print(f"-> ACTION: Typing '{text}' into element {element_id}")
            # fill() automatically clears the input first, which is usually what we want
            element.fill(text, timeout=3000)
        elif action_type == "type_and_enter":
            text = decision.get("text_to_type", "")
            print(f"-> ACTION: Typing '{text}' and pressing ENTER into element {element_id}")
            element.fill(text, timeout=3000)
            element.press("Enter")
        else:
            error_msg = f"ERROR: Unknown action type '{action_type}'"
            print(f"-> {error_msg}")
            return error_msg
    except Exception as e:
        error_msg = f"ERROR: Playwright failed to execute {action_type} on element {element_id}. Details: {str(e)}"
        print(f"-> {error_msg}")
        return error_msg
        
    # Slow down for 1 second so the human user can physically see what just happened!
    page.wait_for_timeout(1000)
    
    return "SUCCESS"
