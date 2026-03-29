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
    from questrade_service import QuastradeAuthError
    try:
        positions = normalization.get_normalized_positions()
        return {"status": "success", "data": positions}
    except QuastradeAuthError as e:
        return {
            "status": "auth_error",
            "broker": "questrade",
            "message": str(e),
            "data": [],
        }

@app.get("/api/insights/manager-thesis")
def get_manager_thesis():
    """Returns structured Manager Thesis Validation findings from the rule-based analysis engine."""
    import insights
    from questrade_service import QuastradeAuthError
    try:
        return insights.generate_manager_thesis()
    except QuastradeAuthError as e:
        return {"title": "Manager Thesis Validation", "generated_at": "", "error": str(e), "findings": []}

@app.get("/api/insights/behavioral-bias")
def get_behavioral_bias():
    """Returns structured Behavioral Bias Report findings from the rule-based analysis engine."""
    import insights
    from questrade_service import QuastradeAuthError
    try:
        return insights.generate_behavioral_bias()
    except QuastradeAuthError as e:
        return {"title": "Behavioral Bias Report", "generated_at": "", "error": str(e), "findings": []}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    import normalization
    import asyncio
    try:
        while True:
            positions = normalization.get_normalized_positions()
            await websocket.send_json({"type": "positions_update", "data": positions})
            await asyncio.sleep(5)  # Steam updates every 5 seconds (cache protects APIs)
    except Exception as e:
        print(f"WebSocket connection closed: {e}")
