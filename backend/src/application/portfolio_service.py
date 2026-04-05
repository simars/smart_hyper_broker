import ssl
import json
import urllib.request
from typing import List, Tuple
from cachetools import TTLCache, cached
from src.domain.models import Position, BrokerError, NormalizedPortfolio
from src.application.interfaces import BrokerGateway

# Import auth error type for typed error classification
try:
    from src.infrastructure.brokers.questrade_token_manager import QuestradeAuthError
except ImportError:
    QuestradeAuthError = None  # type: ignore

exchange_rate_cache = TTLCache(maxsize=1, ttl=3600)
positions_cache = TTLCache(maxsize=1, ttl=60)

class PortfolioService:
    def __init__(self, gateways: List[BrokerGateway]):
        self.gateways = gateways

    def strip_symbol(self, broker: str, symbol: str) -> str:
        if broker == "moomoo" and symbol.startswith("US."):
            return symbol[3:]
        return symbol

    def _to_cad_usd(self, value: float, is_cad: bool, cad_usd_rate: float) -> Tuple[float, float]:
        if is_cad:
            return value, value / cad_usd_rate
        else:
            return value * cad_usd_rate, value

    @staticmethod
    @cached(cache=exchange_rate_cache)
    def get_cad_usd_rate() -> float:
        url = "https://open.er-api.com/v6/latest/USD"
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=context, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    return float(data.get("rates", {}).get("CAD", 1.35))
        except Exception as e:
            print(f"Error fetching exchange rate: {e}")
        
        return 1.35  

    # @cached(cache=positions_cache) # Move cache to the router layer or adapt for instance method
    def get_normalized_positions(self) -> NormalizedPortfolio:
        unified_positions = []
        errors = []
        cad_usd_rate = self.get_cad_usd_rate()

        for gateway in self.gateways:
            try:
                raw_positions = gateway.fetch_positions(cad_usd_rate=cad_usd_rate)
                unified_positions.extend(raw_positions)
            except Exception as e:
                error_type = "general_error"
                if QuestradeAuthError and isinstance(e, QuestradeAuthError):
                    error_type = "auth_error"
                errors.append(BrokerError(
                    broker=gateway.broker_name,
                    type=error_type,
                    message=str(e)
                ))

        return NormalizedPortfolio(positions=unified_positions, errors=errors)
