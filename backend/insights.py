"""
Portfolio intelligence analysis engine.
Produces structured, data-driven findings for the Manager Thesis and Behavioral Bias reports
by analysing the normalized unified position schema directly — no external LLM required.
"""
from __future__ import annotations
from datetime import datetime, timezone
import normalization


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pct(part: float, total: float) -> float:
    return round(part / total * 100, 1) if total else 0.0


def _fmt_usd(val: float) -> str:
    sign = "+" if val >= 0 else ""
    return f"{sign}${val:,.0f}"


# ─── Manager Thesis ───────────────────────────────────────────────────────────

def generate_manager_thesis() -> dict:
    """
    Validate whether the current allocations match a defensible macro thesis.
    Returns structured findings: concentration, currency split, PnL health, thesis label.
    """
    positions = normalization.get_normalized_positions().get("positions", [])
    findings = []

    if not positions:
        return {"title": "Manager Thesis Validation", "generated_at": _now(), "findings": [
            {"type": "info", "title": "No Position Data", "detail": "No active positions detected. Connect your brokers and try again."}
        ]}

    total_val = sum(p["market_val_usd"] for p in positions)
    total_open_pnl = sum(p["open_pnl_usd"] for p in positions)

    # ── Largest single position ───────────────────────────────────────────────
    sorted_by_val = sorted(positions, key=lambda p: p["market_val_usd"], reverse=True)
    top1 = sorted_by_val[0]
    top1_pct = _pct(top1["market_val_usd"], total_val)
    findings.append({
        "type": "caution" if top1_pct > 20 else "info",
        "title": f"{top1['symbol']} — Largest Position at {top1_pct}%",
        "detail": (
            f"Your largest single holding is {top1['symbol']} at ${top1['market_val_usd']:,.0f} USD "
            f"({top1_pct}% of total portfolio)."
            + (" This exceeds the 20% single-stock concentration guideline — ensure this is a deliberate high-conviction bet." if top1_pct > 20 else "")
        ),
    })

    # ── Top-5 concentration ───────────────────────────────────────────────────
    top5 = sorted_by_val[:5]
    top5_val = sum(p["market_val_usd"] for p in top5)
    top5_pct = _pct(top5_val, total_val)
    top5_names = ", ".join(p["symbol"] for p in top5)
    findings.append({
        "type": "warning" if top5_pct > 70 else ("caution" if top5_pct > 55 else "info"),
        "title": f"Top-5 Holdings: {top5_pct}% of Portfolio",
        "detail": f"{top5_names} represent {top5_pct}% of total value (${top5_val:,.0f} USD). {'Consider broadening your exposure.' if top5_pct > 70 else 'Moderate concentration — monitor closely.'}",
    })

    # ── Currency / geographic mix ─────────────────────────────────────────────
    usd_val = sum(p["market_val_usd"] for p in positions if p["currency"] != "CAD")
    cad_val = sum(p["market_val_usd"] for p in positions if p["currency"] == "CAD")
    usd_pct = _pct(usd_val, total_val)
    cad_pct = _pct(cad_val, total_val)
    findings.append({
        "type": "info",
        "title": f"Currency Mix: {usd_pct}% USD · {cad_pct}% CAD",
        "detail": (
            f"Your portfolio is {usd_pct}% USD-denominated and {cad_pct}% CAD-denominated by market value. "
            f"{'USD exposure is dominant — CAD strength could compress returns.' if usd_pct > 75 else 'Geographic currency split appears balanced.'}"
        ),
    })

    # ── Macro thesis label ────────────────────────────────────────────────────
    unique_symbols = {p["symbol"] for p in positions}
    etf_keywords = {"VFV", "XQQ", "ZEM", "ZDB", "TDB", "XUU", "XIU", "XEQT", "VEQT", "VGRO"}
    etf_count = len(unique_symbols & etf_keywords)
    equity_count = len(unique_symbols) - etf_count
    if equity_count > etf_count * 2:
        thesis = "Stock-Picker / Active"
        thesis_note = "Your portfolio skews toward individual equity selection. Ensure each stock has an explicit thesis."
    elif etf_count >= equity_count:
        thesis = "Passive / Index-Core"
        thesis_note = "Your portfolio is ETF-heavy — low cost and well-diversified. Watch for factor overlap."
    else:
        thesis = "Blended Active + Passive"
        thesis_note = "A mix of individual stocks and ETFs. Confirm your active bets aren't duplicating ETF exposure."
    findings.append({
        "type": "info",
        "title": f"Detected Thesis: {thesis}",
        "detail": thesis_note,
    })

    # ── Overall unrealized return ─────────────────────────────────────────────
    cost_basis = total_val - total_open_pnl
    overall_return_pct = _pct(total_open_pnl, cost_basis) if cost_basis > 0 else 0.0
    findings.append({
        "type": "success" if total_open_pnl >= 0 else "caution",
        "title": f"Unrealized Return: {'+' if total_open_pnl >= 0 else ''}{overall_return_pct}% ({_fmt_usd(total_open_pnl)} USD)",
        "detail": (
            f"Aggregate unrealized PnL across all {len(positions)} open positions. "
            + ("Portfolio is in the green overall — maintain discipline and avoid complacency." if total_open_pnl >= 0
               else "Portfolio is underwater overall — review your thesis and stop-loss discipline.")
        ),
    })

    return {"title": "Manager Thesis Validation", "generated_at": _now(), "findings": findings}


# ─── Behavioral Bias ──────────────────────────────────────────────────────────

def generate_behavioral_bias() -> dict:
    """
    Identify psychological biases anchoring the portfolio:
    sunk-cost fallacy, home-country bias, concentration risk, recency / momentum chasing.
    """
    positions = fetch_current_positions()
    findings = []

    if not positions:
        return {"title": "Behavioral Bias Report", "generated_at": _now(), "findings": [
            {"type": "info", "title": "No Position Data", "detail": "No active positions detected."}
        ]}

    total_val = sum(p["market_val_usd"] for p in positions)

    # ── Sunk-cost fallacy ─────────────────────────────────────────────────────
    # Significant losers: open_pnl_usd worse than -$200 OR worse than -5% of market val
    significant_threshold_usd = -200
    losers = [
        p for p in positions
        if p["open_pnl_usd"] < significant_threshold_usd
        or (p["market_val_usd"] > 0 and p["open_pnl_usd"] / p["market_val_usd"] < -0.05)
    ]
    losers_sorted = sorted(losers, key=lambda p: p["open_pnl_usd"])
    if losers_sorted:
        worst3 = losers_sorted[:3]
        callouts = "; ".join(
            f"{p['symbol']} ({_fmt_usd(p['open_pnl_usd'])} · {_pct(p['open_pnl_usd'], p['market_val_usd'])}%)"
            for p in worst3
        )
        findings.append({
            "type": "warning",
            "title": f"Sunk-Cost Risk: {len(losers_sorted)} Positions with Significant Open Loss",
            "detail": f"Worst offenders: {callouts}. Ask yourself: would you buy these at today's price? If not, review the rationale for holding.",
        })
    else:
        findings.append({
            "type": "success",
            "title": "No Sunk-Cost Signals Detected",
            "detail": "No positions with significant unrealized losses found. Portfolio losses are within tolerable thresholds.",
        })

    # ── Home-country bias ─────────────────────────────────────────────────────
    cad_val = sum(p["market_val_usd"] for p in positions if p["currency"] == "CAD")
    cad_pct = _pct(cad_val, total_val)
    findings.append({
        "type": "warning" if cad_pct > 45 else ("caution" if cad_pct > 30 else "success"),
        "title": f"Home-Country Bias: {cad_pct}% in CAD Assets",
        "detail": (
            f"{cad_pct}% of your portfolio (${cad_val:,.0f} USD equivalent) is in CAD-denominated assets. "
            + ("This is heavily home-biased. Canada represents ~3% of global market cap; consider broadening."
               if cad_pct > 45 else
               "Moderate CAD exposure — acceptable, but monitor for FX concentration risk."
               if cad_pct > 30 else
               "Healthy geographic diversification — minimal home-country bias detected.")
        ),
    })

    # ── Concentration risk (Herfindahl–Hirschman Index) ───────────────────────
    # HHI = sum of (market_share)^2 × 10,000. >2,500 = highly concentrated; 1,500–2,500 = moderate.
    hhi = sum((_pct(p["market_val_usd"], total_val) / 100) ** 2 for p in positions) * 10_000
    top1_sym = sorted(positions, key=lambda p: p["market_val_usd"], reverse=True)[0]["symbol"]
    findings.append({
        "type": "caution" if hhi > 2500 else ("info" if hhi > 1500 else "success"),
        "title": f"Concentration Index: {hhi:.0f} HHI",
        "detail": (
            f"Portfolio HHI is {hhi:.0f} (max 10,000 = one position). "
            + (f"Highly concentrated — {top1_sym} is the primary driver. Deliberate single-stock bets carry outsized idiosyncratic risk."
               if hhi > 2500 else
               f"Moderate concentration — {top1_sym} leads but diversification is adequate."
               if hhi > 1500 else
               "Well-diversified portfolio. Concentration risk appears managed.")
        ),
    })

    # ── Recency / momentum check (holding only winners) ──────────────────────
    gainers = [p for p in positions if p["open_pnl_usd"] > 0]
    big_gainers = [p for p in gainers if _pct(p["open_pnl_usd"], p["market_val_usd"] - p["open_pnl_usd"]) > 30]
    if big_gainers:
        names = ", ".join(p["symbol"] for p in sorted(big_gainers, key=lambda p: p["open_pnl_usd"], reverse=True)[:3])
        findings.append({
            "type": "caution",
            "title": f"Winner Overconfidence: {len(big_gainers)} Positions Up >30%",
            "detail": f"{names} are up >30% unrealized. Ensure you have a profit-taking plan and aren't holding purely due to recency bias.",
        })
    else:
        findings.append({
            "type": "info",
            "title": "No Overconfidence Signals",
            "detail": "No positions show extreme unrealized gains that might trigger winner-overconfidence or reluctance to trim.",
        })

    return {"title": "Behavioral Bias Report", "generated_at": _now(), "findings": findings}
