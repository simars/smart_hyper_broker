# System Architecture

## Architecture Overview
The application follows a decoupled client-server architecture serving a frontend web layer while a Python backend handles gateway integrations and AI orchestration.

### 1. Frontend Application
- **Stack:** Next.js, Tailwind CSS, shadcn/ui.
- **State/Data:** `@tanstack/react-query` for request caching, alongside WebSockets for streaming live data.
- **Role:** Presents the unified dashboard, renders AI-generated manager thesis/bias reports, and displays actionable buy/sell opportunities dynamically.

### 2. Backend Orchestration (Python & FastAPI)
- **Stack:** Python FastAPI, `python-dotenv` for secure secret management (`.env`), and memory caching utilities for API rate-limit resilience.
- **Real-time Pipeline:** Exposes a WebSocket or Streaming API endpoint to dynamically push live valuations to the Next.js UI constraints.
- **Broker Connections:**
  - **Moomoo OpenD:** Active persistent connection to OpenD (`localhost:11111`) for live quotes, history, and real account trading execution (`unlock_trade`).
  - **Questrade API:** REST API pulling data via the `questrade-api` python wrapper utilizing `~/.questrade.json`.
- **Normalization Service:** Aggregates holdings, strips broker-specific annotations (like `US.`), fetches real-time CAD/USD FX rates, and reconciles the combined net asset value into a common base currency. Automatically binds `account_id` and `account_type` internally to allow frontend segregation features (like RRSP vs TFSA distributions).

### 3. Intelligence Layers
- **Local Rule-Based Analysis (`insights.py`):** A high-speed, local analyzer that produces the "Manager Thesis" and "Behavioral Bias" reports using rule-based algorithms for immediate user feedback.
- **Intelligence AI Layer (NotebookLM MCP):** An MCP-driven connection mapping to NotebookLM. Logic will ingest normalized positions to return generative deep-dive analysis and return actionable buy/sell signals to the frontend.

### 4. Error Handling & Resilience
- **Hybrid Data/Error Responses:** APIs (especially the Normalization API) return both data and error arrays. This allows the UI to render partial data (e.g. "Moomoo is up, Questrade is down") rather than failing entirely.
- **Safe-Fail Exceptions:** Backend endpoints wrap critical analytics in catch-all `try/except` blocks to propagate errors as structured JSON objects (200 status with an `error` key) to prevent CORS and network errors in the dashboard UI.

### 5. Verification Workflow
- Local testing using a Browser Subagent to click through dashboard functionality.
- CURL probes for validating the JSON integrity of normalized and intelligence payloads.
