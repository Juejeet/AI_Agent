import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

def decide_next_action_vision(goal: str, screenshot_bytes: bytes, page_meta: str, action_history: str = None) -> dict:
    """
    Sends screenshot image and goal to Gemini Multimodal Vision API and forces it to return 
    a structured JSON decision of what action to take next.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set!")
        
    client = genai.Client(api_key=api_key)
    
    history_section = ""
    if action_history and action_history != "None":
        history_section = f"\nPAST ACTIONS HISTORY:\n{action_history}\nReview your past actions to avoid repeating mistakes or getting stuck in infinite loops. If you have already achieved the goal, output 'done'.\n"
        
    prompt = f"""
You are an autonomous web browser vision agent.
Your goal is: {goal}
{history_section}
{page_meta}

Look carefully at the provided screenshot of the current web page.
Interactive elements have red bounding boxes with numerical ID labels drawn directly on top of them.
Identify which element ID to interact with to achieve the goal.

Based on the goal and visual state in the screenshot, decide the SINGLE next best action to take.
Return ONLY valid JSON matching the required schema.
"""

    image_part = types.Part.from_bytes(data=screenshot_bytes, mime_type="image/png")

    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=[image_part, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "reasoning": {
                        "type": "STRING",
                        "description": "Brief explanation of what you visually observe in the screenshot and why this action was chosen."
                    },
                    "action_type": {
                        "type": "STRING",
                        "description": "Must be one of: 'click', 'type', 'type_and_enter', 'done'. Use 'type_and_enter' if you need to press the Enter key after typing. Use 'done' ONLY when the entire goal has been fully accomplished."
                    },
                    "element_id": {
                        "type": "INTEGER",
                        "description": "The numerical red label ID of the element to interact with. Omit if action_type is 'done'."
                    },
                    "text_to_type": {
                        "type": "STRING",
                        "description": "The text to type if action_type is 'type' or 'type_and_enter'. Omit otherwise."
                    },
                    "final_answer": {
                        "type": "STRING",
                        "description": "If action_type is 'done', provide a clear, direct, detailed plain-English answer summarizing the findings that solve the user's goal. Omit otherwise."
                    }
                },
                "required": ["reasoning", "action_type"]
            }
        )
    )
    
    return json.loads(response.text)
