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
        # Return a structured error the frontend can display as a user-facing message
        return {
            "status": "auth_error",
            "broker": "questrade",
            "message": str(e),
            "data": [],
        }

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
