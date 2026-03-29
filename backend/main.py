from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv(override=True)

app = FastAPI(title="Smart Hyper Broker API")

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
    positions = normalization.get_normalized_positions()
    return {"status": "success", "data": positions}

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
