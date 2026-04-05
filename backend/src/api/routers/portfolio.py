from fastapi import APIRouter, WebSocket, UploadFile, File
import asyncio
import os
import shutil
import uuid
from typing import Dict, Any

from src.application.portfolio_service import PortfolioService
from src.infrastructure.brokers.moomoo_gateway import MoomooGateway
from src.infrastructure.brokers.questrade_gateway import QuestradeGateway
from src.infrastructure.brokers.rbc_gateway import RbcGateway

router = APIRouter()

# Dependency Injection / Instantiation
gateways = [
    MoomooGateway(),
    QuestradeGateway(),
    RbcGateway()
]
portfolio_service = PortfolioService(gateways)

@router.get("/positions")
def get_positions():
    res = portfolio_service.get_normalized_positions()
    return {"status": "success", "data": [p.dict() for p in res.positions], "errors": [e.dict() for e in res.errors]}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            res = portfolio_service.get_normalized_positions()
            await websocket.send_json({
                "type": "positions_update", 
                "data": [p.dict() for p in res.positions],
                "errors": [e.dict() for e in res.errors]
            })
            await asyncio.sleep(5)
    except Exception as e:
        print(f"WebSocket connection closed: {e}")

@router.post("/upload/rbc")
async def upload_rbc_csv(file: UploadFile = File(...)):
    target_dir = "data/rbc"
    os.makedirs(target_dir, exist_ok=True)
    
    safe_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(target_dir, safe_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"RBC Upload: Saved file {file.filename} to {file_path}")
        # Note: In a robust DDD, we'd clear cache on the PortfolioService directly
        return {"status": "success", "message": f"Successfully processed {file.filename}"}
    except Exception as e:
        print(f"RBC Upload Error: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/questrade/token")
def update_questrade_token(payload: dict):
    from src.infrastructure.brokers.questrade_token_manager import refresh_token
    token = payload.get("refresh_token")
    if not token:
        return {"status": "error", "message": "No refresh token provided."}
    
    try:
        refresh_token(token)
        return {"status": "success", "message": "Questrade token updated successfully."}
    except Exception as e:
        print(f"Questrade: Manual token update failed: {e}")
        return {"status": "error", "message": str(e)}
