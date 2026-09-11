import os
import sys
from dotenv import load_dotenv
load_dotenv()

from agent_loop import run_agent

if __name__ == "__main__":
    url = "https://www.google.com"
    goal = "Which teams won every 5th match of the 2026 FIFA World Cup (Match 5, 10, 15, 20)?"
    
    print(f"Running agent on URL: {url}")
    print(f"Goal: {goal}\n")
    
    result = run_agent(url, goal, max_steps=8, perception_mode="hybrid")
    print("\nFinal Agent Result:", result)
