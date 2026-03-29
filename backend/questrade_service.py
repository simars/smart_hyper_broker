import os
import urllib.request
from questrade_api import Questrade

# ─── WAF Bypass ────────────────────────────────────────────────────────────────
# Monkey-patch urllib to include a browser User-Agent, bypassing Questrade's WAF
# which blocks Python's generic urllib agent with 403 responses.
_original_urlopen = urllib.request.urlopen

def _patched_urlopen(url, *args, **kwargs):
    if isinstance(url, str) and 'questrade.com' in url:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        return _original_urlopen(req, *args, **kwargs)
    elif hasattr(url, 'full_url') and 'questrade.com' in url.full_url:
        url.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
    return _original_urlopen(url, *args, **kwargs)

urllib.request.urlopen = _patched_urlopen


# ─── Typed Error for Auth Failures ─────────────────────────────────────────────
class QuastradeAuthError(Exception):
    """
    Raised when all Questrade authentication attempts are exhausted.
    Propagated to the API layer to return a structured UI-visible error.
    """
    pass


def _is_token_valid(q: Questrade) -> bool:
    """
    Perform a lightweight probe of the access token by calling accounts.
    Returns True only if the response contains a real 'accounts' key,
    guarding against silent error dicts like {'code': 1017, 'message': '...'}.
    """
    try:
        resp = q.accounts
        return isinstance(resp, dict) and 'accounts' in resp
    except Exception:
        return False


def _build_client() -> Questrade:
    """
    Two-stage client initialisation:
      Stage 1 — Try the on-disk token cache (~/.questrade.json).
                If the stored access token is expired, questrade-api will
                automatically use the stored refresh token to get a new one.
      Stage 2 — Fall back to QUESTRADE_REFRESH_TOKEN in .env.

    Raises QuastradeAuthError if both stages fail.
    """
    cache_path = os.path.expanduser('~/.questrade.json')

    # Stage 1: cache file present → let the library self-refresh
    if os.path.exists(cache_path):
        try:
            q = Questrade()
            if _is_token_valid(q):
                print("Questrade: authenticated via cache (auto-refreshed if needed).")
                return q
            print("Questrade: cache present but token invalid; falling back to .env token.")
        except Exception as e:
            print(f"Questrade: cache initialisation failed ({e}); falling back to .env token.")

    # Stage 2: bootstrap from .env refresh token
    token = os.getenv('QUESTRADE_REFRESH_TOKEN', '').strip()
    if not token or token == 'your_refresh_token_here':
        raise QuastradeAuthError(
            "No valid Questrade credentials found. "
            "Please log in to Questrade App Hub, generate a new API refresh token, "
            "and add it to your .env file as QUESTRADE_REFRESH_TOKEN."
        )

    try:
        q = Questrade(refresh_token=token)
        if _is_token_valid(q):
            print("Questrade: authenticated via .env refresh token.")
            return q
        raise QuastradeAuthError(
            "The QUESTRADE_REFRESH_TOKEN in .env is invalid or already used. "
            "Questrade refresh tokens are single-use. Please generate a new one."
        )
    except QuastradeAuthError:
        raise
    except Exception as e:
        raise QuastradeAuthError(
            f"Questrade authentication failed: {e}. "
            "Please generate a fresh refresh token from the Questrade App Hub."
        )


def _fetch_with_client(q: Questrade) -> list:
    """Fetch all account positions using an already-authenticated client."""
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

    # Bulk-resolve native currency for every symbolId
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
    """
    Public entry point.  Authentication flow:
      1. Build an authenticated client (_build_client).
      2. Attempt to fetch positions.
      3. If a mid-execution token expiry is detected (code 1017 / 401),
         force a re-auth from .env and retry ONCE.
      4. If the retry also fails, raise QuastradeAuthError so the API layer
         can return a structured, UI-visible error message.
    """
    # Attempt 1 — use cached / env token
    q = _build_client()

    try:
        return _fetch_with_client(q)
    except Exception as e:
        err_str = str(e)
        # Detect mid-execution token expiry signals
        is_token_expiry = (
            '1017' in err_str or
            '401' in err_str or
            'Access token is invalid' in err_str or
            'Unauthorized' in err_str
        )
        if not is_token_expiry:
            print(f"Questrade: non-auth error during fetch: {e}")
            return []

    # Attempt 2 — force re-auth from .env (cache is clearly stale)
    print("Questrade: access token expired mid-execution; forcing re-auth from .env token.")
    cache_path = os.path.expanduser('~/.questrade.json')
    try:
        if os.path.exists(cache_path):
            os.remove(cache_path)  # Bust the stale cache so _build_client re-bootstraps
    except OSError:
        pass

    token = os.getenv('QUESTRADE_REFRESH_TOKEN', '').strip()
    if not token or token == 'your_refresh_token_here':
        raise QuastradeAuthError(
            "Questrade access token expired and no valid QUESTRADE_REFRESH_TOKEN is available in .env. "
            "Please generate a new refresh token from the Questrade App Hub and restart the backend."
        )

    try:
        q2 = Questrade(refresh_token=token)
        if not _is_token_valid(q2):
            raise QuastradeAuthError(
                "Re-authentication with the .env refresh token failed. "
                "The token may already have been used. Please generate a fresh one."
            )
        print("Questrade: re-auth successful; retrying position fetch.")
        return _fetch_with_client(q2)
    except QuastradeAuthError:
        raise
    except Exception as e:
        raise QuastradeAuthError(
            f"Questrade re-authentication attempt failed: {e}. "
            "Please generate a new refresh token from the Questrade App Hub."
        )
