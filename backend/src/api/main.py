from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.api.routers import portfolio, insights

load_dotenv(override=True)

app = FastAPI(title="Smart Hyper Broker API (DDD)")

# Mount MCP Server if mcp_server exists
try:
    from mcp_server import mcp
    app.mount("/mcp", mcp.sse_app())
except ImportError:
    print("Warning: mcp_server not found or failed to load. Skipping MCP mount.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend is running with DDD Architecture."}

app.include_router(portfolio.router, prefix="/api", tags=["portfolio"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])
