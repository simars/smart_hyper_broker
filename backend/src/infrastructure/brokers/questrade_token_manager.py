import json
import os
import time
import requests
import threading
from typing import Optional, Dict, Any

# ─── Global Lock ─────────────────────────────────────────────────────────────
_refresh_lock = threading.Lock()

# ─── WAF Bypass ────────────────────────────────────────────────────────────────
QUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'questrade_tokens.json')

class QuestradeAuthError(Exception):
    """Raised when authentication with Questrade fails or credentials are missing."""
    pass

def load_tokens() -> Optional[Dict[str, Any]]:
    """Load token data from the local JSON file."""
    if not os.path.exists(TOKEN_PATH):
        return None
    try:
        with open(TOKEN_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return None

def save_tokens(token_data: Dict[str, Any]):
    """Save token data to the local JSON file with a timestamp."""
    token_data['fetched_at'] = int(time.time())
    with open(TOKEN_PATH, 'w') as f:
        json.dump(token_data, f, indent=2)

def is_token_expired(token_data: Dict[str, Any]) -> bool:
    """Check if the access token is expired based on fetched_at and expires_in."""
    fetched_at = token_data.get('fetched_at', 0)
    expires_in = token_data.get('expires_in', 0)
    current_time = int(time.time())
    # 60s buffer for safety
    return current_time >= (fetched_at + expires_in - 60)

def refresh_token(refresh_token_string: str) -> Dict[str, Any]:
    """Exchange a refresh token for a full credentials payload using the official REST API."""
    with _refresh_lock:
        # Re-check if the token was already refreshed by another thread while we were waiting for the lock
        current_tokens = load_tokens()
        if current_tokens and not is_token_expired(current_tokens):
            # If the refresh_token passed in is DIFFERENT from what's in the file, 
            # it might be a manual UI update, so we should proceed.
            # But if it's the SAME, it means someone else already refreshed it.
            if refresh_token_string == current_tokens.get('refresh_token'):
                print("Questrade: Token already refreshed by another thread. Skipping.")
                return current_tokens

        url = f"https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token={refresh_token_string}"
        
        print(f"Questrade: Attempting to refresh token via REST API...")
        try:
            # Use our WAF-bypass headers
            resp = requests.get(url, headers=QUEST_HEADERS, timeout=10)
            
            if resp.ok:
                data = resp.json()
                save_tokens(data)
                print(f"Questrade: Token refreshed and saved successfully. (Server: {data.get('api_server')})")
                return data
            else:
                print(f"Questrade: Token refresh failed: {resp.status_code} {resp.text}")
                # If we get a challenge or HTML back, it means WAF blocked us
                if '<html' in resp.text.lower():
                     raise QuestradeAuthError("Questrade WAF challenge detected. Please try a fresh token.")
                raise QuestradeAuthError(f"Questrade refresh failed: {resp.status_code} {resp.text}")
        except Exception as e:
            if isinstance(e, QuestradeAuthError):
                raise
            raise QuestradeAuthError(f"Network error during Questrade refresh: {e}")

def get_valid_credentials() -> Dict[str, Any]:
    """
    Get valid credentials. 
    1. Loads from JSON.
    2. If expired, attempts auto-refresh using stored refresh token.
    3. If everything fails, raises QuestradeAuthError.
    """
    tokens = load_tokens()
    if not tokens:
        raise QuestradeAuthError("No Questrade credentials found. Please connect via UI.")

    if not is_token_expired(tokens):
        return tokens

    # Attempt auto-refresh
    r_token = tokens.get('refresh_token')
    if not r_token:
        raise QuestradeAuthError("No refresh token available. Re-auth required.")
    
    try:
        return refresh_token(r_token)
    except Exception as e:
        raise QuestradeAuthError(f"Auto-refresh failed: {e}. Please re-auth via UI.")

def make_api_request(endpoint: str, params: Optional[Dict[str, Any]] = None, max_retries: int = 1) -> Dict[str, Any]:
    """Make an authenticated REST API call with automatic 401 retry."""
    creds = get_valid_credentials()
    
    headers = QUEST_HEADERS.copy()
    
    for attempt in range(max_retries + 1):
        # We RE-DERIVE the url at the start of each attempt to catch api_server changes
        base_url = creds['api_server'].rstrip('/')
        url = f"{base_url}/{endpoint.lstrip('/')}"
        headers['Authorization'] = f"{creds.get('token_type', 'Bearer')} {creds['access_token']}"
        
        print(f"Questrade API: Connecting to {url} (Attempt {attempt+1})...")
        
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            
            if resp.status_code == 401 and attempt < max_retries:
                print("Questrade API: 401 Unauthorized. Refreshing token and retrying...")
                # Force a refresh. This will update the file and return new creds.
                creds = refresh_token(creds['refresh_token'])
                # Loop will re-derive url and headers using new creds
                continue
                
            resp.raise_for_status()
            return resp.json()
            
        except requests.exceptions.HTTPError as e:
            if attempt == max_retries:
                print(f"Questrade API Error: {e.response.status_code} - {e.response.text}")
                raise QuestradeAuthError(f"Questrade API call failed: {e.response.status_code} {e.response.text}")
        except Exception as e:
            if attempt == max_retries:
                raise QuestradeAuthError(f"Questrade network error: {e}")
    
    return {}
