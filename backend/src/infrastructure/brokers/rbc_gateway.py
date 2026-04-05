import os
import csv
import glob
from typing import List

from src.application.interfaces import BrokerGateway
from src.domain.models import Position

from src.infrastructure.brokers.questrade_gateway import QuestradeGateway

def _to_cad_usd(value: float, is_cad: bool, cad_usd_rate: float):
    if is_cad:
        return value, value / cad_usd_rate
    else:
        return value * cad_usd_rate, value

class RbcGateway(BrokerGateway):
    def __init__(self, data_dir='data/rbc'):
        self.data_dir = data_dir

    @property
    def broker_name(self) -> str:
        return "rbc"

    def parse_rbc_files(self):
        csv_files = glob.glob(os.path.join(self.data_dir, '*.csv'))
        accounts = {}
        
        for fpath in csv_files:
            mtime = os.path.getmtime(fpath)
            
            with open(fpath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            acc_id = "Unknown_RBC"
            acc_type = "Unknown"
            for line in lines:
                if line.startswith("Account:"):
                    parts = line.split('-')
                    if len(parts) >= 2:
                        acc_id = parts[0].replace("Account:", "").strip()
                        acc_type = parts[-1].strip()
                    break
                    
            if acc_id in accounts and accounts[acc_id]['mtime'] > mtime:
                continue
                
            holdings = []
            parsing = False
            clean_lines = [line.strip() for line in lines]
            reader = csv.reader(clean_lines)
            header = []
            
            for row in reader:
                if not row:
                    continue
                if row[0] == "Important Information":
                    break
                    
                if "Symbol" in row and "Quantity" in row:
                    header = row
                    parsing = True
                    continue
                    
                if parsing and len(row) == len(header):
                    symbol = row[header.index("Symbol")]
                    if not symbol:
                        continue
                    try:
                        qty = float(row[header.index("Quantity")].replace(',', ''))
                        avg_cost_str = row[header.index("Average Cost")].replace(',', '')
                        avg_cost = float(avg_cost_str) if avg_cost_str else 0.0
                        currency = row[header.index("Currency")]
                        
                        holdings.append({
                            "symbol": symbol,
                            "qty": qty,
                            "average_buying_price": avg_cost,
                            "currency": currency
                        })
                    except Exception as e:
                        print(f"RBC Parser: Skipping row for {symbol} due to error: {e}")
                    
            accounts[acc_id] = {
                "file": fpath,
                "mtime": mtime,
                "type": acc_type,
                "holdings": holdings
            }
        return accounts

    def fetch_positions(self, cad_usd_rate: float) -> List[Position]:
        os.makedirs(self.data_dir, exist_ok=True)
        accounts = self.parse_rbc_files()
        domain_positions = []
        
        # Collect all symbols. RBC CSV Currency reflects *account settlement currency*,
        # not necessarily the stock's native listing market (e.g. GOOG in a CAD RRSP is
        # still a USD-listed stock on NASDAQ — GOOG.TO does not exist).
        # Strategy: try USD quote first for every symbol. If it returns a price > 0, use it
        # and override asset_currency to USD. If USD returns 0, fall back to CAD (.TO).
        all_symbols = []
        for acc_id, data in accounts.items():
            for h in data['holdings']:
                all_symbols.append(h['symbol'])

        unique_symbols = list(dict.fromkeys(all_symbols))  # deduplicated, order-preserving

        # Fetch as USD first
        usd_quotes = QuestradeGateway.get_quotes([(sym, 'USD') for sym in unique_symbols])
        # Fetch as CAD (.TO) for any that return 0 or are missing from USD results
        cad_fallback_syms = [sym for sym in unique_symbols
                             if not usd_quotes.get(sym, {}).get('price', 0.0)]
        cad_quotes = QuestradeGateway.get_quotes([(sym, 'CAD') for sym in cad_fallback_syms]) if cad_fallback_syms else {}

        def resolve_quote(sym: str):
            """Returns (price, day_change, resolved_currency)."""
            usd_price = usd_quotes.get(sym, {}).get('price', 0.0)
            if usd_price and usd_price > 0:
                return usd_price, usd_quotes[sym].get('day_change', 0.0), 'USD'
            cad_price = cad_quotes.get(sym, {}).get('price', 0.0)
            if cad_price and cad_price > 0:
                return cad_price, cad_quotes[sym].get('day_change', 0.0), 'CAD'
            return 0.0, 0.0, 'USD'  # Unknown, default to USD

        for acc_id, data in accounts.items():
            for h in data['holdings']:
                sym = h['symbol']
                qty = h['qty']
                avg = h['average_buying_price']
                csv_currency = h['currency']  # account settlement currency from CSV (e.g. CAD for RRSP)

                live_price, day_change, quote_currency = resolve_quote(sym)

                # The avg_cost in the CSV is denominated in csv_currency (account settlement currency).
                # To compute valid PnL, market_val must be in the same currency.
                # If the live quote is in a different currency, convert it.
                if live_price > 0 and quote_currency != csv_currency:
                    if quote_currency == 'USD' and csv_currency == 'CAD':
                        # Convert USD price → CAD
                        current_price = live_price * cad_usd_rate
                        day_change_converted = day_change * cad_usd_rate
                    elif quote_currency == 'CAD' and csv_currency == 'USD':
                        # Convert CAD price → USD
                        current_price = live_price / cad_usd_rate
                        day_change_converted = day_change / cad_usd_rate
                    else:
                        current_price = live_price
                        day_change_converted = day_change
                else:
                    current_price = live_price
                    day_change_converted = day_change

                asset_currency = csv_currency  # report in account's settlement currency
                is_cad = (asset_currency == "CAD")

                market_val = current_price * qty
                open_pnl = market_val - (avg * qty)  # both in csv_currency now ✓
                day_pnl = day_change_converted * qty

                open_pnl_cad, open_pnl_usd = _to_cad_usd(open_pnl, is_cad, cad_usd_rate)
                day_pnl_cad, day_pnl_usd = _to_cad_usd(day_pnl, is_cad, cad_usd_rate)

                print(f"RBC: {sym} qty={qty} avg={avg:.2f} live={live_price:.2f}({quote_currency}) display={current_price:.2f}({asset_currency}) mv={market_val:.2f} pnl={open_pnl:.2f}")
                
                domain_positions.append(Position(
                    broker=self.broker_name,
                    account_id=acc_id,
                    account_type=data['type'],
                    symbol=sym,
                    qty=qty,
                    closed_qty=0.0,
                    average_buying_price=avg,
                    day_pnl=day_pnl,
                    day_pnl_cad=day_pnl_cad,
                    day_pnl_usd=day_pnl_usd,
                    open_pnl=open_pnl,
                    open_pnl_cad=open_pnl_cad,
                    open_pnl_usd=open_pnl_usd,
                    closed_pnl=0.0,
                    market_val=market_val,
                    market_val_cad=market_val if is_cad else market_val * cad_usd_rate,
                    market_val_usd=market_val if not is_cad else market_val / cad_usd_rate,
                    currency=asset_currency
                ))
                
        return domain_positions
