import os
import urllib.request
from questrade_api import Questrade
from questrade_token_manager import get_valid_credentials, QuestradeAuthError

# ─── WAF Bypass ────────────────────────────────────────────────────────────────
_original_urlopen = urllib.request.urlopen

def _patched_urlopen(url, *args, **kwargs):
    if isinstance(url, str) and 'questrade.com' in url:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        return _original_urlopen(req, *args, **kwargs)
    elif hasattr(url, 'full_url') and 'questrade.com' in url.full_url:
        url.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
    return _original_urlopen(url, *args, **kwargs)

urllib.request.urlopen = _patched_urlopen


def _is_token_valid(q: Questrade) -> bool:
    """Validate token via a real accounts call."""
    try:
        resp = q.accounts
        return isinstance(resp, dict) and 'accounts' in resp
    except Exception:
        return False


def _build_client() -> Questrade:
    """Build questrade client using manager-supplied credentials."""
    creds = get_valid_credentials()
    
    # Use the specific access token and server from our JSON/Manager
    q = Questrade(
        access_token=creds['access_token'],
        api_server=creds['api_server'],
        token_type=creds.get('token_type', 'Bearer')
    )
    
    if not _is_token_valid(q):
        # This might happen if the token just expired or was invalidated.
        print("Questrade: access token invalid. Refreshing...")
        from questrade_token_manager import refresh_token
        new_creds = refresh_token(creds['refresh_token'])
        q = Questrade(
            access_token=new_creds['access_token'],
            api_server=new_creds['api_server'],
            token_type=new_creds.get('token_type', 'Bearer')
        )
        if not _is_token_valid(q):
            raise QuestradeAuthError("Questrade re-auth failed after refresh.")
            
    return q


def _fetch_with_client(q: Questrade) -> list:
    """Fetch all account positions using client."""
    accounts_resp = q.accounts
    accounts = accounts_resp.get('accounts', [])
    print(f"Questrade: discovered {len(accounts)} account(s).")

    all_positions = []
    for acc in accounts:
        acc_num = acc.get('number')
        acc_type = acc.get('type', 'Unknown')
        try:
            pos_data = q.account_positions(acc_num)
            if pos_data and 'positions' in pos_data:
                for position in pos_data['positions']:
                    position['account_id'] = str(acc_num)
                    position['account_type'] = acc_type
                all_positions.extend(pos_data['positions'])
        except Exception as e:
            print(f"Questrade: error fetching positions for account {acc_num}: {e}")

    # Bulk-resolve native currency
    if all_positions:
        try:
            unique_sym_ids = list({str(p['symbolId']) for p in all_positions if p.get('symbolId')})
            if unique_sym_ids:
                meta_res = q.symbols(ids=",".join(unique_sym_ids))
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
        q = _build_client()
        return _fetch_with_client(q)
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
