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
