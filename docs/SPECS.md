# Project Specifications

## Frontend Requirements
- **Framework:** Next.js (App Router) configured with TypeScript.
- **Styling:** Tailwind CSS.
- **Components:** shadcn/ui.
- **Design Features:** Support for both dark and light modes.
- **Data Visualization:** Dashboard to display combined holdings from multiple brokers, calculated risk levels, and recommended macro adjustments.
- **Holdings Table:**
  - Every monetary cell MUST display the ISO currency code of the position's native currency (e.g. `$4,638 USD`) as a muted inline badge.
  - All columns MUST be sortable (ascending → descending → original order) with a visual indicator (↑ ↓ ⇅) on the active column header.
  - A fuzzy-match search bar MUST be rendered above the table, filtering rows by `symbol`, `broker`, and `account_type`. No exact match required. Shows a live result count.
- **Metrics Header:** The Net Asset Value, Unrealized PnL, and Daily PnL summary cards MUST aggregate in a user-selectable base currency (CAD by default, toggleable to USD via a pill control). Values are sourced from pre-converted `_cad` / `_usd` fields in the backend schema.

## Backend Requirements
- **Framework:** Python API (FastAPI preferred for robust async/MCP integration).
- **Moomoo Gateway:** Connect to OpenD gateway on `localhost:11111` via `moomoo` SDK. Requires handling the `unlock_trade` workflow for REAL accounts.
- **Questrade Gateway:** Setup `questrade-api` python wrapper using the token from the local `~/.questrade.json` file.
- **Normalization Service:** Aggregates holdings into a **Hybrid Response Schema**:
  - `positions`: Array of normalized position objects.
  - `errors`: Array of broker-specific errors (e.g. `auth_error`) to allow partial UI rendering even if one broker fails.
- **Schema Mapping:** Unified schema MUST explicitly include `account_id`, `account_type`, `market_val` (native currency), `average_buying_price`, `closed_qty`, `day_pnl`, `open_pnl` (Unrealized), and `closed_pnl` (Realized) properties.

## Intelligence Integration
- **Local Insights Engine:** `insights.py` acts as a rule-based intelligence layer analyzing the unified positions for concentration, currency mix, and psychological biases.
- **Insights API Schema:** 
  - `title`: Header for the report (e.g. "Manager Thesis").
  - `findings`: Array of objects: `{ type: "success" | "info" | "caution" | "warning", title: string, detail: string }`.
  - `error`: Optional string field for propagating auth or data errors to the UI gracefully.
- **MCP Future Integration:** Set up an MCP server connection mapped to NotebookLM to ingest normalized positions for generative analysis and actionable buy/sell signals.
