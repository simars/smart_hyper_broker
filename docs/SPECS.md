# Project Specifications

## Frontend Requirements
- **Framework:** Next.js (App Router) configured with TypeScript.
- **Styling:** Tailwind CSS.
- **Components:** shadcn/ui.
- **Design Features:** Support for both dark and light modes.
- **Data Visualization:** Dashboard to display combined holdings from multiple brokers, calculated risk levels, and recommended macro adjustments.

## Backend Requirements
- **Framework:** Python API (FastAPI preferred for robust async/MCP integration).
- **Moomoo Gateway:** Connect to OpenD gateway on `localhost:11111` via `moomoo` SDK. Requires handling the `unlock_trade` workflow for REAL accounts.
- **Questrade Gateway:** Setup `questrade-api` python wrapper using the token from the local `~/.questrade.json` file.
- **Normalization:** Python layer to unify tickers (e.g., stripping `US.` from Moomoo) and convert currency to a standard base logic utilizing a live CAD/USD exchange rate. Unified schema MUST explicitly include `account_id`, `account_type`, `market_val` (native currency), `average_buying_price`, `closed_qty`, `day_pnl`, `open_pnl` (Unrealized), and `closed_pnl` (Realized) properties mapping directly to each internal holding segment to sustain localized frontend PnL & analytical visualizations.

## Intelligence Integration
- Set up an MCP server connection mapped to NotebookLM.
- NotebookLM logic will ingest normalized positions to return a 'Manager Thesis Validation' report and a 'Behavioral Bias' report.
- Deliver actionable buy/sell signals to the frontend.
