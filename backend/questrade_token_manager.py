import json
import os
import time
import requests
from typing import Optional, Dict, Any

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
    """Exchange a refresh token for a full credentials payload."""
    url = f"https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token={refresh_token_string}"
    
    print(f"Questrade: Attempting to refresh token...")
    try:
        resp = requests.get(url, timeout=10)
        if resp.ok:
            data = resp.json()
            save_tokens(data)
            print("Questrade: Token refreshed and saved successfully.")
            return data
        else:
            print(f"Questrade: Token refresh failed: {resp.status_code} {resp.text}")
            raise QuestradeAuthError(f"Questrade refresh failed: {resp.text}")
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
