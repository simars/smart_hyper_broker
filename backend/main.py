from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv(override=True)

app = FastAPI(title="Smart Hyper Broker API")

# Mount MCP (Model Context Protocol) Server for Intelligence Layer querying
from mcp_server import mcp
app.mount("/mcp", mcp.sse_app())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend is running."}

@app.get("/api/positions")
def get_positions():
    import normalization
    # Normalization now catches its own errors and returns a structured dict
    res = normalization.get_normalized_positions()
    return {"status": "success", "data": res["positions"], "errors": res["errors"]}

@app.post("/api/questrade/token")
def update_questrade_token(payload: dict):
    """Manually trigger a token refresh using a provided bootstrap refresh token."""
    from questrade_token_manager import refresh_token
    token = payload.get("refresh_token")
    if not token:
        return {"status": "error", "message": "No refresh token provided."}
    
    try:
        refresh_token(token)
        return {"status": "success", "message": "Questrade token updated successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/insights/manager-thesis")
def get_manager_thesis():
    """Returns structured Manager Thesis Validation findings from the rule-based analysis engine."""
    import insights
    import traceback
    try:
        return insights.generate_manager_thesis()
    except Exception as e:
        print(f"Error in manager-thesis: {e}")
        traceback.print_exc()
        return {"title": "Manager Thesis Validation", "generated_at": "", "error": str(e), "findings": []}

@app.get("/api/insights/behavioral-bias")
def get_behavioral_bias():
    """Returns structured Behavioral Bias Report findings from the rule-based analysis engine."""
    import insights
    import traceback
    try:
        return insights.generate_behavioral_bias()
    except Exception as e:
        print(f"Error in behavioral-bias: {e}")
        traceback.print_exc()
        return {"title": "Behavioral Bias Report", "generated_at": "", "error": str(e), "findings": []}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    import normalization
    import asyncio
    try:
        while True:
            res = normalization.get_normalized_positions()
            await websocket.send_json({
                "type": "positions_update", 
                "data": res["positions"],
                "errors": res["errors"]
            })
            await asyncio.sleep(5)
    except Exception as e:
        print(f"WebSocket connection closed: {e}")
