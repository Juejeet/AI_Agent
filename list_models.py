import os
from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Please set GEMINI_API_KEY first!")
else:
    try:
        client = genai.Client(api_key=api_key)
        print("Available models:")
        for m in client.models.list():
            # We only care about models that start with 'gemini'
            if 'gemini' in m.name.lower():
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error fetching models: {e}")
