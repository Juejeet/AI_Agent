import os
import sys
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_loop import run_agent

app = FastAPI(title="Autonomous AI Browser Agent Dashboard")

# Mount static folder
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Agent Dashboard Server Active</h1>")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_running_loop()
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            action = payload.get("action")
            
            if action == "start":
                start_url = payload.get("url", "https://www.saucedemo.com")
                goal = payload.get("goal", "")
                mode = payload.get("mode", "hybrid")
                max_steps = int(payload.get("max_steps", 10))
                
                def sync_step_callback(step_data):
                    # Schedule WebSocket notification on event loop
                    asyncio.run_coroutine_threadsafe(
                        websocket.send_json(step_data), loop
                    )
                    
                # Send starting status message
                await websocket.send_json({
                    "type": "status",
                    "status": "running",
                    "message": f"Agent initialized in {mode.upper()} mode..."
                })
                
                # Execute run_agent in worker thread so FastAPI remains non-blocking
                outcome = await loop.run_in_executor(
                    None, 
                    run_agent, 
                    start_url, 
                    goal, 
                    max_steps, 
                    mode, 
                    sync_step_callback
                )
                
                # Send final completed message
                await websocket.send_json({
                    "type": "completed",
                    "outcome": outcome
                })
                
    except WebSocketDisconnect:
        print("WebSocket client disconnected.")
    except Exception as e:
        print(f"WebSocket Error: {e}")

if __name__ == "__main__":
    import uvicorn
    print("\n=========================================")
    print("  STARTING AGENT WEB DASHBOARD SERVER    ")
    print("  URL: http://127.0.0.1:8000             ")
    print("=========================================\n")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
