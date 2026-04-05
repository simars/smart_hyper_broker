import os
import csv
import glob

def parse_rbc_files(data_dir='data/rbc'):
    # find all csvs
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
    
    # group by account
    accounts = {} # acc_id -> { "file": path, "mtime": float, "type": str, "holdings": [] }
    
    for fpath in csv_files:
        mtime = os.path.getmtime(fpath)
        
        with open(fpath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        acc_id = "Unknown_RBC"
        acc_type = "Unknown"
        for line in lines:
            if line.startswith("Account:"):
                # e.g., "Account: 69668018 - 69668018 - RESP Fami"
                parts = line.split('-')
                if len(parts) >= 2:
                    acc_id = parts[0].replace("Account:", "").strip()
                    acc_type = parts[-1].strip()
                break
                
        # If we already have a newer file for this account, skip
        if acc_id in accounts and accounts[acc_id]['mtime'] > mtime:
            continue
            
        # Parse holdings
        holdings = []
        parsing = False
        
        # Use csv.reader on lines
        # Remove any leading/trailing whitespace
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

def get_latest_holdings():
    """
    Parses RBC CSVs and fetches live quotes using questrade_service fallback.
    Returns a list of raw position dicts (before normalization matching).
    """
    import questrade_service # Ensure it's imported within the function if needed
    
    # Ensure directory exists just in case
    os.makedirs('data/rbc', exist_ok=True)
    
    accounts = parse_rbc_files()
    all_positions = []
    
    symbols_to_quote = []
    for acc_id, data in accounts.items():
        for h in data['holdings']:
            symbols_to_quote.append((h['symbol'], h['currency']))
            
    # Fetch live quotes
    live_quotes = questrade_service.get_quotes(symbols_to_quote)
    
    for acc_id, data in accounts.items():
        for h in data['holdings']:
            sym = h['symbol']
            qty = h['qty']
            avg = h['average_buying_price']
            
            # fallback to csv price/change if live quote not found
            current_price = live_quotes.get(sym, {}).get('price', h['csv_last_price'])
            day_change = live_quotes.get(sym, {}).get('day_change', h['csv_day_change'])
            
            open_pnl = (current_price - avg) * qty if avg else 0
            day_pnl = day_change * qty
            
            all_positions.append({
                "broker": "rbc",
                "account_id": acc_id,
                "account_type": data['type'],
                "symbol": sym,
                "qty": qty,
                "closed_qty": 0,
                "average_buying_price": avg,
                "day_pnl": day_pnl,
                "open_pnl": open_pnl,
                "closed_pnl": 0,
                "market_val": current_price * qty,
                "currency": h['currency']
            })
            
    return all_positions
