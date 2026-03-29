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
- **Normalization:** Python layer to unify tickers (e.g., stripping `US.` from Moomoo) and convert currency to a standard base logic utilizing a live CAD/USD exchange rate. Unified schema MUST explicitly include `account_id`, `account_type`, `market_val` (native currency), `average_buying_price`, `closed_qty`, `day_pnl`, `open_pnl` (Unrealized), and `closed_pnl` (Realized) properties mapping directly to each internal holding segment to sustain localized frontend PnL & analytical visualizations.

## Intelligence Integration
- Set up an MCP server connection mapped to NotebookLM.
- NotebookLM logic will ingest normalized positions to return a 'Manager Thesis Validation' report and a 'Behavioral Bias' report.
- Deliver actionable buy/sell signals to the frontend.
