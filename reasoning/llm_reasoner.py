import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

def decide_next_action(goal: str, dom_summary: str, last_feedback: str = None) -> dict:
    """
    Sends the goal and DOM summary to Gemini and forces it to return 
    a structured JSON decision of what action to take next.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set! Please set it in your terminal before running.")
        
    client = genai.Client(api_key=api_key)
    
    feedback_section = ""
    if last_feedback:
        feedback_section = f"\nIMPORTANT FEEDBACK FROM YOUR PREVIOUS ACTION:\n{last_feedback}\nIf your last action was an ERROR, you must change your strategy and try something else to avoid getting stuck in a loop.\n"
    
    prompt = f"""
You are an autonomous web browser agent.
Your goal is: {goal}
{feedback_section}
Here is the current state of the web page, represented as a list of interactive elements:
{dom_summary}

Based on the goal and the elements available, decide the SINGLE next best action to take.
Return ONLY valid JSON matching the required schema. 
"""

    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "reasoning": {
                        "type": "STRING",
                        "description": "Brief explanation of why this action was chosen."
                    },
                    "action_type": {
                        "type": "STRING",
                        "description": "Must be one of: 'click', 'type', 'type_and_enter', 'done'. Use 'type_and_enter' if you need to press the Enter key after typing (like in a search box). Use 'done' if the goal is already achieved."
                    },
                    "element_id": {
                        "type": "INTEGER",
                        "description": "The ID of the element to interact with. Omit if action_type is 'done'."
                    },
                    "text_to_type": {
                        "type": "STRING",
                        "description": "The text to type if action_type is 'type'. Omit otherwise."
                    }
                },
                "required": ["reasoning", "action_type"]
            }
        )
    )
    
    return json.loads(response.text)
