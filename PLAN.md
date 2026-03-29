# Multi-Broker Dashboard & Rebalancer Task List

## Phase 2: Implementation

### 1. Project Initialization & Frontend Scaffolding
- [x] Initialize Next.js project (`npx create-next-app@latest frontend --typescript --tailwind --eslint --app`).
- [x] Implement strict state management via `@tanstack/react-query` to bridge API and UI.
- [x] Setup `shadcn/ui` and initialize dashboard layout.
- [x] Implement Dashboard structural layout with Dark/Light mode toggle.

### 2. Backend Scaffolding & Config
- [x] Initialize Python backend with FastAPI and `uvicorn`.
- [x] Set up secure centralized configuration (`.env` with `python-dotenv`) for Moomoo pins, Questrade configs, etc.
- [x] Implement Moomoo Service: connect to OpenD (`localhost:11111`), unlock trade for REAL accounts, and fetch positions.
- [x] Implement Questrade Service: install `questrade-api`, load token from `~/.questrade.json`, and fetch positions.
- [x] Setup API endpoint infrastructure (including a WebSocket endpoint for live updates).

### 3. Normalization Pipeline & Caching [Verified & Complete]
- [x] Create a normalization pipeline script.
- [x] Implement a Time-To-Live (TTL) caching layer to protect broker rate limits.
- [x] Implement symbol stripping logic (e.g., `US.AAPL` to `AAPL`).
- [x] Implement live CAD/USD exchange rate fetch integration.
- [x] Aggregate and map account balances and positions to a single unified schema.

### 4. Intelligence Integration (NotebookLM MCP) [Verified & Complete]
- [x] Implement NotebookLM MCP Client integration.
- [x] Create processing logic to pass normalized data to the models seamlessly.
- [x] Build endpoints to generate 'Manager Thesis Validation' and 'Behavioral Bias' reports.

### 5. Frontend Visualizations [Verified & Complete]
- [x] Build UI component for Combined Holdings matrix (listening to WebSocket updates).
- [x] Build UI component for Risk Levels visualization.
- [x] Build AI insights cards (Manager Thesis & Recommendations).
- [x] Bridge Frontend state to API calls using strict query hooks.

## Phase 3: Verification [Verified & Complete]
- [x] Setup testing harnesses securely.
- [x] Subagent frontend UI Walkthrough verification.
