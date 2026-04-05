import pytest
from pydantic import ValidationError
from src.domain.models import Position, BrokerError, NormalizedPortfolio

def test_position_model_valid():
    """Test valid instantiation of Position."""
    pos = Position(
        broker="moomoo",
        account_id="ACC123",
        account_type="Margin",
        symbol="AAPL",
        qty=100.0,
        closed_qty=0.0,
        average_buying_price=150.0,
        day_pnl=50.0,
        day_pnl_cad=65.0,
        day_pnl_usd=50.0,
        open_pnl=200.0,
        open_pnl_cad=260.0,
        open_pnl_usd=200.0,
        closed_pnl=0.0,
        market_val=15200.0,
        market_val_cad=19760.0,
        market_val_usd=15200.0,
        currency="USD"
    )
    assert pos.symbol == "AAPL"
    assert pos.qty == 100.0

def test_position_model_invalid_types():
    """Test typing enforcement of Position model."""
    with pytest.raises(ValidationError):
        Position(
            broker="moomoo",
            account_id="ACC123",
            account_type="Margin",
            symbol="AAPL",
            qty="invalid_qty_string",  # Should cause validation error
            closed_qty=0.0,
            average_buying_price=150.0,
            day_pnl=50.0,
            day_pnl_cad=65.0,
            day_pnl_usd=50.0,
            open_pnl=200.0,
            open_pnl_cad=260.0,
            open_pnl_usd=200.0,
            closed_pnl=0.0,
            market_val=15200.0,
            market_val_cad=19760.0,
            market_val_usd=15200.0,
            currency="USD"
        )
