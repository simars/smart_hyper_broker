from pydantic import BaseModel
from typing import Optional

class Position(BaseModel):
    broker: str
    account_id: str
    account_type: str
    symbol: str
    qty: float
    closed_qty: float
    average_buying_price: float
    day_pnl: float
    day_pnl_cad: float
    day_pnl_usd: float
    open_pnl: float
    open_pnl_cad: float
    open_pnl_usd: float
    closed_pnl: float
    market_val: float
    market_val_cad: float
    market_val_usd: float
    currency: str

class BrokerError(BaseModel):
    broker: str
    type: str
    message: str

class NormalizedPortfolio(BaseModel):
    positions: list[Position]
    errors: list[BrokerError]
