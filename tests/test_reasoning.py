import os
import pytest
from reasoning.llm_reasoner import decide_next_action

def test_gemini_reasoning():
    # If the API key is missing, skip the test instead of crashing
    if not os.environ.get("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY environment variable is not set. Skipping test.")
        
    fake_goal = "Log into the website"
    fake_dom = '''
    [1] <input> "Username"
    [2] <input> "Password"
    [3] <button> "Login"
    '''
    
    print("\n--- Sending request to Gemini ---")
    decision = decide_next_action(fake_goal, fake_dom)
    print("Decision received from Gemini:")
    print(decision)
    print("---------------------------------")
    
    # Verify the LLM correctly decided to type into the first username field
    assert "action_type" in decision
    assert decision["action_type"] == "type"
    assert decision["element_id"] == 1
    assert "text_to_type" in decision
