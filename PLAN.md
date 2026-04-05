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

## Phase 6: Holdings Table UX & Currency Normalization [Complete]
- [x] Extend normalization schema with `open_pnl_cad/usd` and `day_pnl_cad/usd` via `_to_cad_usd()` helper.
- [x] Extend `Position` TypeScript interface with 4 new FX-converted PnL fields.
- [x] Rewrite `MetricsHeader` with CAD/USD pill toggle; NAV, Unrealized PnL, Daily PnL aggregate in selected base currency.
- [x] Add per-cell currency ISO badge to all monetary columns in holdings table.
- [x] Fix `CA$` double-indicator: use `currencyDisplay: 'narrowSymbol'` in `Intl.NumberFormat`.
- [x] Add click-to-sort on all table columns (asc → desc → none cycle) with ↑↓⇅ indicators.
- [x] Add fuzzy-match search bar filtering by symbol, broker, account type with live result count.
- [x] Update `docs/SPECS.md` with formal requirements for all new UX features.

## Phase 7: Group by Symbol [Complete]
- [x] Add `GroupedPosition` type with account slots, broker list, and row count.
- [x] Implement `groupBySymbol()`: sum qty/PnL/market_val, qty-weighted avg entry, MIX currency for cross-currency edge case.
- [x] Add grouped boolean state (default: false = ungrouped) with toggle button in toolbar.
- [x] Grouped rows render all broker badges, ×N count chip, and per-account sub-line.
- [x] Search and sort apply independently in both views.
- [x] Lint: clean. Browser-verified: aggregation correct, toggle bidirectional, fuzzy search works in grouped mode.

## Phase 8: Questrade Auth Resilience & UI Re-auth [Complete]
- [x] Implement `QuestradeTokenManager` for manual refresh and JSON-based storage.
- [x] Update `questrade_service.py` to use `QuestradeTokenManager` with automatic rotation.
- [x] Refactor `normalization.py` to support partial success (Moomoo data + Questrade error).
- [x] Add `POST /api/questrade/token` to allow manual bootstrap/re-auth.
- [x] Implement `QuestradeConnectCard` in frontend to prompt for token only on failure.
- [x] Verify Moomoo data renders independently of Questrade auth state.
- [x] Verify that UI token submission restores Questrade connectivity and persists to `questrade_tokens.json`.

## Phase 9: RBC Direct Investing CSV Ingestion
- [ ] Backend: Create `data/rbc/` directory to store CSV uploads.
- [ ] Backend: Add a new `rbc_parser.py` to parse RBC CSVs, grouping by account and extracting latest holdings.
- [ ] Backend: Add quote fetching capability in `questrade_service.py` (`get_quotes()`) to enrich parsed RBC symbols with live real-time prices.
- [ ] Backend: Add `POST /api/upload/rbc` endpoint to allow users to upload multiple CSVs belonging to multiple accounts.
- [ ] Backend: Integrate `rbc_parser.py` into `normalization.py` to include RBC holdings in the global position map.
- [ ] Frontend: Add a CSV Uploader component (`components/UploadRbcCsv.tsx`) in the dashboard.
