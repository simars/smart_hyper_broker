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

### 3. Intelligence / AI Layer (NotebookLM MCP)
- **Integration:** MCP (Model Context Protocol).
- **Role:** Queries a NotebookLM workspace equipped with our normalized positions data. It uses generative AI to analyze our holdings to detect behavioral biases and output macro adjustments.

### 4. Verification Workflow
- Local testing using a Browser Subagent to click through dashboard functionality.
