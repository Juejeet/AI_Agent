import sys
import os
import json
import time
import pandas as pd
from datetime import datetime

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_loop import run_agent

def run_comparative_eval():
    tasks_file = os.path.join(os.path.dirname(__file__), "tasks.json")
    with open(tasks_file, "r") as f:
        tasks = json.load(f)
        
    modes = ["dom", "vision"]
    all_results = []
    
    print("====================================")
    print("STARTING COMPARATIVE BENCHMARK: DOM VS. VISION")
    print("====================================\n")
    
    for mode in modes:
        print(f"\n>>> RUNNING BENCHMARK MODE: {mode.upper()} <<<\n")
        
        for task in tasks:
            print(f"------------------------------------")
            print(f"Task: {task['id']} [{mode.upper()} Mode]")
            print(f"------------------------------------")
            
            start_time = time.time()
            try:
                outcome = run_agent(task["url"], task["goal"], max_steps=10, perception_mode=mode)
                elapsed_time = round(time.time() - start_time, 2)
                
                agent_reported_success = outcome.get("success", False)
                actual_url = outcome.get("final_url", "")
                steps = outcome.get("steps", 0)
                
                verified_success = False
                if agent_reported_success and task["expected_url_contains"] in actual_url:
                    verified_success = True
                    
                all_results.append({
                    "Mode": mode.upper(),
                    "Task ID": task["id"],
                    "Steps": steps,
                    "Time (s)": elapsed_time,
                    "Agent Claimed Success": agent_reported_success,
                    "Verified Success": verified_success
                })
                
            except Exception as e:
                print(f"Task crashed: {e}")
                all_results.append({
                    "Mode": mode.upper(),
                    "Task ID": task["id"],
                    "Steps": 0,
                    "Time (s)": round(time.time() - start_time, 2),
                    "Agent Claimed Success": False,
                    "Verified Success": False
                })
                
    df = pd.DataFrame(all_results)
    
    # Save log file
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs"), exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", f"compare_eval_{timestamp}.csv")
    df.to_csv(log_file, index=False)
    
    print("\n\n====================================")
    print("COMPARATIVE EVALUATION COMPLETE! REPORT CARD:")
    print("====================================\n")
    print(df.to_string(index=False))
    
    # Calculate summary per mode
    summary = df.groupby("Mode").agg(
        Success_Rate=("Verified Success", lambda x: f"{x.mean() * 100:.0f}%"),
        Avg_Steps=("Steps", "mean"),
        Avg_Time_Sec=("Time (s)", "mean")
    ).reset_index()
    
    print("\n\n====================================")
    print("PERCEPTION SUMMARY (DOM vs VISION):")
    print("====================================\n")
    print(summary.to_string(index=False))
    print(f"\nDetailed logs saved to: {log_file}")

if __name__ == "__main__":
    run_comparative_eval()
