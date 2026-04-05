import os
from questrade_token_manager import make_api_request, QuestradeAuthError

def _is_token_valid() -> bool:
    """Validate token via a real accounts call."""
    try:
        resp = make_api_request('v1/accounts')
        return isinstance(resp, dict) and 'accounts' in resp
    except Exception:
        return False


def _fetch_positions() -> list:
    """Fetch all account positions using REST API."""
    accounts_resp = make_api_request('v1/accounts')
    accounts = accounts_resp.get('accounts', [])
    print(f"Questrade: discovered {len(accounts)} account(s).")

    all_positions = []
    for acc in accounts:
        acc_num = acc.get('number')
        acc_type = acc.get('type', 'Unknown')
        try:
            pos_resp = make_api_request(f'v1/accounts/{acc_num}/positions')
            if pos_resp and 'positions' in pos_resp:
                for position in pos_resp['positions']:
                    position['account_id'] = str(acc_num)
                    position['account_type'] = acc_type
                all_positions.extend(pos_resp['positions'])
        except Exception as e:
            print(f"Questrade: error fetching positions for account {acc_num}: {e}")

    # Bulk-resolve native currency
    if all_positions:
        try:
            unique_sym_ids = list({str(p['symbolId']) for p in all_positions if p.get('symbolId')})
            if unique_sym_ids:
                meta_res = make_api_request('v1/symbols', params={'ids': ",".join(unique_sym_ids)})
                currency_map = {
                    sym['symbolId']: sym.get('currency', 'CAD')
                    for sym in meta_res.get('symbols', [])
                }
                for pos in all_positions:
                    pos['currency'] = currency_map.get(pos.get('symbolId'), 'CAD')
        except Exception as e:
            print(f"Questrade: error resolving currency metadata: {e}")

    return all_positions


def fetch_positions() -> list:
    """Public entry point for position fetching."""
    try:
        # make_api_request handles building client and refreshing tokens internally
        return _fetch_positions()
    except Exception as e:
        err_str = str(e)
        # Mid-execution catch-all for token issues
        is_token_expiry = (
            '1017' in err_str or
            '401' in err_str or
            'Unauthorized' in err_str
        )
        if is_token_expiry:
             print("Questrade: Mid-execution auth failure detected.")
             raise QuestradeAuthError(f"Questrade authentication failed: {e}")
        
        # Rethrow if it's already an AuthError
        if isinstance(e, QuestradeAuthError):
            raise
            
        print(f"Questrade: non-auth error during fetch: {e}")
        return []

def get_quotes(symbols_with_currency: list) -> dict:
    """
    Fetch real-time quotes for a list of tuples: (symbol, currency).
    Example: [('SHOP', 'CAD'), ('AAPL', 'USD')]
    Returns: {'SHOP': {'price': 164.58, 'day_change': 4.60}, ...}
    """
    if not symbols_with_currency:
        return {}
        
    # Apply heuristic: Add .TO to CAD symbols
    query_names = []
    symbol_map = {} # mapped_name -> original_name
    for sym, cur in symbols_with_currency:
        mapped = f"{sym}.TO" if cur == 'CAD' and not sym.endswith('.TO') else sym
        query_names.append(mapped)
        symbol_map[mapped] = sym

    try:
        # Fetch symbol IDs first
        res = make_api_request('v1/symbols', params={'names': ','.join(query_names)})
        if not res or 'symbols' not in res:
            return {}
            
        id_to_mapped = {str(x['symbolId']): x['symbol'] for x in res['symbols']}
        ids = list(id_to_mapped.keys())
        
        if not ids:
            return {}
            
        # Fetch quotes
        quotes_res = make_api_request('v1/markets/quotes', params={'ids': ','.join(ids)})
        if not quotes_res or 'quotes' not in quotes_res:
            return {}
            
        result = {}
        for q in quotes_res['quotes']:
            mapped_name = q.get('symbol')
            # Fallback to id mapping if symbol string differs
            if not mapped_name or mapped_name not in symbol_map:
                mapped_name = id_to_mapped.get(str(q.get('symbolId')))
                
            if mapped_name and mapped_name in symbol_map:
                orig_sym = symbol_map[mapped_name]
                last_price = q.get('lastTradePrice', 0)
                open_price = q.get('openPrice', 0)
                # Compute daily change per share
                day_change = last_price - open_price if open_price else 0
                result[orig_sym] = {
                    'price': last_price,
                    'day_change': day_change
                }
        return result
    except Exception as e:
        print(f"Questrade get_quotes error: {e}")
        return {}

