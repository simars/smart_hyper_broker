import json
import os
import urllib.request
from questrade_api import Questrade

# Monkey-patch to bypass Questrade Web Application Firewall (WAF) blocking the Python generic urllib agent.
_original_urlopen = urllib.request.urlopen

def _patched_urlopen(url, *args, **kwargs):
    if isinstance(url, str) and 'questrade.com' in url:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        return _original_urlopen(req, *args, **kwargs)
    elif hasattr(url, 'full_url') and 'questrade.com' in url.full_url:
        url.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
    return _original_urlopen(url, *args, **kwargs)

urllib.request.urlopen = _patched_urlopen

def fetch_positions():
    try:
        q = None
        # Step 1: Check if caching file exists. If it does, use standard cache flow.
        cache_path = os.path.expanduser('~/.questrade.json')
        if os.path.exists(cache_path):
            try:
                q_test = Questrade()
                # A quick ping to confirm the token inside the cache actually works
                # If it's broken, questrade-api complains about 'token_data' natively
                if q_test.accounts:
                    q = q_test
            except Exception:
                pass
                
        # Step 2: If the cache is entirely missing or corrupted, bootstrap via .env
        if not q:
            token = os.getenv('QUESTRADE_REFRESH_TOKEN')
            if token and token != 'your_refresh_token_here':
                q = Questrade(refresh_token=token)
            else:
                raise Exception("Missing or Invalid Questrade configuration. Please enter a fresh refresh token into .env")
        
        all_positions = []
        accounts = q.accounts.get('accounts', [])
        print(f"Discovered {len(accounts)} Questrade accounts.")
        
        for acc in accounts:
            acc_num = acc.get('number')
            acc_type = acc.get('type', 'Unknown')
            try:
                # Returns something like {'positions': [...] }
                pos_data = q.account_positions(acc_num)
                if pos_data and 'positions' in pos_data:
                    for position in pos_data['positions']:
                        position['account_id'] = str(acc_num)
                        position['account_type'] = acc_type
                    all_positions.extend(pos_data['positions'])
            except Exception as e_pos:
                print(f"Error fetching Questrade positions for account {acc_num}: {e_pos}")

        if all_positions:
            try:
                # Deduplicate explicit symbol_ids structurally across all accounts
                unique_sym_ids = list(set([str(p.get('symbolId')) for p in all_positions if p.get('symbolId')]))
                if unique_sym_ids:
                    # Request bulk validation mapping from native metadata layer
                    sym_id_str = ",".join(unique_sym_ids)
                    meta_res = q.symbols(ids=sym_id_str)
                    
                    # Convert resolved array into hash schema directly indexing over symbolId
                    currency_map = {}
                    for sym_meta in meta_res.get('symbols', []):
                        currency_map[sym_meta.get('symbolId')] = sym_meta.get('currency', 'CAD')
                        
                    # Apply mappings uniformly
                    for pos in all_positions:
                        sid = pos.get('symbolId')
                        pos['currency'] = currency_map.get(sid, 'CAD')
            except Exception as e_meta:
                print(f"Error resolving native Questrade currency maps: {e_meta}")
                
        return all_positions
    except Exception as e:
        if "403: Forbidden" in str(e) or "400: Bad Request" in str(e):
            print("Questrade Error [Expired/Used Token]: Your refresh token in '.env' was already used or has expired. Please log into Questrade, generate a fresh token, and save it in .env.")
        else:
            print(f"Error fetching Questrade accounts/positions: {e}")
        return []
