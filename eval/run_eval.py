import sys
import os
import json
import pandas as pd
from datetime import datetime

# Add parent directory to sys.path so we can import from agent_loop
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_loop import run_agent

def run_evaluation():
    tasks_file = os.path.join(os.path.dirname(__file__), "tasks.json")
    with open(tasks_file, "r") as f:
        tasks = json.load(f)
        
    results = []
    print(f"Starting evaluation suite with {len(tasks)} tasks...")
    
    for task in tasks:
        print(f"\n====================================")
        print(f"EVALUATING TASK: {task['id']}")
        print(f"====================================")
        
        try:
            # We limit to 10 steps so it doesn't take forever
            outcome = run_agent(task["url"], task["goal"], max_steps=10)
            
            # Verify outcome
            agent_reported_success = outcome.get("success", False)
            actual_url = outcome.get("final_url", "")
            steps = outcome.get("steps", 0)
            
            # The agent succeeds if it said it was done AND the URL contains the expected keyword
            verified_success = False
            if agent_reported_success and task["expected_url_contains"] in actual_url:
                verified_success = True
                
            results.append({
                "Task ID": task["id"],
                "Goal": task["goal"],
                "Steps": steps,
                "Agent Claimed Success": agent_reported_success,
                "Verified Success": verified_success
            })
            
        except Exception as e:
            print(f"Task crashed: {e}")
            results.append({
                "Task ID": task["id"],
                "Goal": task["goal"],
                "Steps": 0,
                "Agent Claimed Success": False,
                "Verified Success": False
            })
            
    # Save and display results
    df = pd.DataFrame(results)
    
    # Save to logs
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs"), exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", f"eval_{timestamp}.csv")
    df.to_csv(log_file, index=False)
    
    print("\n\n====================================")
    print("EVALUATION COMPLETE! FINAL REPORT CARD:")
    print("====================================\n")
    print(df.to_string())
    
    success_rate = (df["Verified Success"].sum() / len(df)) * 100
    print(f"\nFinal Score: {success_rate:.0f}%")
    print(f"Logs saved to {log_file}")

if __name__ == "__main__":
    run_evaluation()
