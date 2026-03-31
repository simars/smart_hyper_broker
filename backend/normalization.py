import ssl
import json
import urllib.request
from typing import List, Dict, Any
from cachetools import TTLCache, cached
import moomoo_service
import questrade_service

# Cache for position aggregation to protect rate limits (60 seconds TTL)
positions_cache = TTLCache(maxsize=1, ttl=60)
# Cache for exchange rate to protect rate limits (3600 seconds = 1 hr TTL)
exchange_rate_cache = TTLCache(maxsize=1, ttl=3600)

def strip_symbol(broker: str, symbol: str) -> str:
    """Normalize symbol to a unified string format."""
    if broker == "moomoo" and symbol.startswith("US."):
        return symbol[3:]
    return symbol


def _to_cad_usd(value: float, is_cad: bool, cad_usd_rate: float):
    """Return (value_cad, value_usd) for a value denominated in native currency."""
    if is_cad:
        return value, value / cad_usd_rate
    else:
        # Assume USD (or USD-pegged) as the non-CAD default
        return value * cad_usd_rate, value

@cached(cache=exchange_rate_cache)
def get_cad_usd_rate() -> float:
    """Fetch live CAD/USD exchange rate."""
    url = "https://open.er-api.com/v6/latest/USD"
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # for local dev network proxy issues
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return float(data.get("rates", {}).get("CAD", 1.35))
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
    
    return 1.35  # Fallback estimate

@cached(cache=positions_cache)
def get_normalized_positions() -> Dict[str, Any]:
    """Aggregate positions from multiple brokers into a single normalized schema."""
    moomoo_raw = []
    try:
        moomoo_raw = moomoo_service.fetch_positions()
    except Exception as e:
        print(f"Normalization: Moomoo fetch failed: {e}")

    questrade_raw = []
    errors = []
    try:
        questrade_raw = questrade_service.fetch_positions()
    except questrade_service.QuestradeAuthError as e:
        print(f"Normalization: Questrade auth failure: {e}")
        errors.append({
            "broker": "questrade",
            "type": "auth_error",
            "message": str(e)
        })
    except Exception as e:
        print(f"Normalization: Questrade general failure: {e}")
        errors.append({
            "broker": "questrade",
            "type": "general_error",
            "message": str(e)
        })
    
    cad_usd_rate = get_cad_usd_rate()
    unified_positions = []
    
    # Process Moomoo positions
    if moomoo_raw:
        for pos in moomoo_raw:
            # ... (existing loop content)
            raw_symbol = pos.get("code", "")
            if not raw_symbol:
                continue
                
            symbol = strip_symbol("moomoo", raw_symbol)
            market_val = float(pos.get("market_val", 0))
            
            asset_currency = pos.get("currency", "USD")
            is_cad = (asset_currency == "CAD")
            
            open_pnl = float(pos.get("unrealized_pl", 0))
            day_pnl  = float(pos.get("today_pl_val", 0))
            open_pnl_cad, open_pnl_usd = _to_cad_usd(open_pnl, is_cad, cad_usd_rate)
            day_pnl_cad,  day_pnl_usd  = _to_cad_usd(day_pnl,  is_cad, cad_usd_rate)

            unified_positions.append({
                "broker": "moomoo",
                "account_id": pos.get("account_id", "Unknown"),
                "account_type": pos.get("account_type", "Unknown"),
                "symbol": symbol,
                "qty": float(pos.get("qty", 0)),
                "closed_qty": float(pos.get("today_sell_qty", 0)),
                "average_buying_price": float(pos.get("average_cost", 0)),
                "day_pnl": day_pnl,
                "day_pnl_cad": day_pnl_cad,
                "day_pnl_usd": day_pnl_usd,
                "open_pnl": open_pnl,
                "open_pnl_cad": open_pnl_cad,
                "open_pnl_usd": open_pnl_usd,
                "closed_pnl": float(pos.get("realized_pl", 0)),
                "market_val": market_val,
                "market_val_usd": market_val if not is_cad else market_val / cad_usd_rate,
                "market_val_cad": market_val if is_cad else market_val * cad_usd_rate,
                "currency": asset_currency,
            })

    # Process Questrade positions
    if questrade_raw:
        for pos in questrade_raw:
            # ... (existing loop content)
            raw_symbol = pos.get("symbol", "")
            if not raw_symbol:
                continue
                
            symbol = strip_symbol("questrade", raw_symbol)
            qty = float(pos.get("openQuantity", 0))
            market_val = float(pos.get("currentMarketValue", 0))
            
            asset_currency = pos.get("currency", "CAD")
            is_cad = (asset_currency == "CAD")
            
            open_pnl = float(pos.get("openPnl", 0))
            day_pnl  = float(pos.get("dayPnl", 0))
            open_pnl_cad, open_pnl_usd = _to_cad_usd(open_pnl, is_cad, cad_usd_rate)
            day_pnl_cad,  day_pnl_usd  = _to_cad_usd(day_pnl,  is_cad, cad_usd_rate)

            unified_positions.append({
                "broker": "questrade",
                "account_id": pos.get("account_id", "Unknown"),
                "account_type": pos.get("account_type", "Unknown"),
                "symbol": symbol,
                "qty": qty,
                "closed_qty": float(pos.get("closedQuantity", 0)),
                "average_buying_price": float(pos.get("averageEntryPrice", 0)),
                "day_pnl": day_pnl,
                "day_pnl_cad": day_pnl_cad,
                "day_pnl_usd": day_pnl_usd,
                "open_pnl": open_pnl,
                "open_pnl_cad": open_pnl_cad,
                "open_pnl_usd": open_pnl_usd,
                "closed_pnl": float(pos.get("closedPnl", 0)),
                "market_val": market_val,
                "market_val_usd": market_val if not is_cad else market_val / cad_usd_rate,
                "market_val_cad": market_val if is_cad else market_val * cad_usd_rate,
                "currency": asset_currency,
            })
            
    return {
        "positions": unified_positions,
        "errors": errors
    }
