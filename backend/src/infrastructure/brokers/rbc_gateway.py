import os
import csv
import glob
from typing import List

from src.application.interfaces import BrokerGateway
from src.domain.models import Position

# Relative import of questrade get_quotes function if needed 
# For pure DDD, pricing should be an external service injected into gateways, but we'll import it here directly to match existing behavior.
import sys
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
                        last_price_str = row[header.index("Last Price")].replace(',', '')
                        last_price = float(last_price_str) if last_price_str else 0.0
                        day_change_str = row[header.index("Change $")].replace(',', '')
                        day_change_csv = float(day_change_str) if day_change_str else 0.0
                        
                        holdings.append({
                            "symbol": symbol,
                            "qty": qty,
                            "average_buying_price": avg_cost,
                            "currency": currency,
                            "csv_last_price": last_price,
                            "csv_day_change": day_change_csv
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
        
        symbols_to_quote = []
        for acc_id, data in accounts.items():
            for h in data['holdings']:
                symbols_to_quote.append((h['symbol'], h['currency']))
                
        # Use questrade quotes (would be cleaner to inject a Pricing/Quote service, but matching existing logic)
        live_quotes = QuestradeGateway.get_quotes(symbols_to_quote)
        
        for acc_id, data in accounts.items():
            for h in data['holdings']:
                sym = h['symbol']
                qty = h['qty']
                avg = h['average_buying_price']
                
                current_price = live_quotes.get(sym, {}).get('price', h['csv_last_price'])
                day_change = live_quotes.get(sym, {}).get('day_change', h['csv_day_change'])
                
                open_pnl = (current_price - avg) * qty if avg else 0
                day_pnl = day_change * qty
                
                asset_currency = h['currency']
                is_cad = (asset_currency == "CAD")
                
                open_pnl_cad, open_pnl_usd = _to_cad_usd(open_pnl, is_cad, cad_usd_rate)
                day_pnl_cad, day_pnl_usd = _to_cad_usd(day_pnl, is_cad, cad_usd_rate)
                
                market_val = current_price * qty
                
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
