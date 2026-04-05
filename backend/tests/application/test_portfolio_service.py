import pytest
from unittest.mock import MagicMock
from src.application.portfolio_service import PortfolioService
from src.application.interfaces import BrokerGateway
from src.domain.models import Position, BrokerError

class DummyGatewaySuccess(BrokerGateway):
    @property
    def broker_name(self) -> str:
        return "dummy_success"

    def fetch_positions(self, cad_usd_rate: float) -> list[Position]:
        return [
            Position(
                broker="dummy_success",
                account_id="ACC1",
                account_type="Cash",
                symbol="TSLA",
                qty=10.0,
                closed_qty=0.0,
                average_buying_price=200.0,
                day_pnl=10.0,
                day_pnl_cad=13.0,
                day_pnl_usd=10.0,
                open_pnl=50.0,
                open_pnl_cad=65.0,
                open_pnl_usd=50.0,
                closed_pnl=0.0,
                market_val=2500.0,
                market_val_cad=3250.0,
                market_val_usd=2500.0,
                currency="USD"
            )
        ]

class DummyGatewayError(BrokerGateway):
    @property
    def broker_name(self) -> str:
        return "dummy_error"

    def fetch_positions(self, cad_usd_rate: float) -> list[Position]:
        raise Exception("Network failure")

def test_portfolio_service_aggregates_successfully():
    """Test PortfolioService aggregates positions correctly without errors."""
    service = PortfolioService(gateways=[DummyGatewaySuccess()])
    res = service.get_normalized_positions()
    
    assert len(res.errors) == 0
    assert len(res.positions) == 1
    assert res.positions[0].symbol == "TSLA"

def test_portfolio_service_handles_errors_gracefully():
    """Test PortfolioService isolates gateway exceptions into normalized errors array."""
    service = PortfolioService(gateways=[DummyGatewaySuccess(), DummyGatewayError()])
    res = service.get_normalized_positions()
    
    # Should contain the successful result...
    assert len(res.positions) == 1
    assert res.positions[0].broker == "dummy_success"
    
    # ...and report the error!
    assert len(res.errors) == 1
    assert res.errors[0].broker == "dummy_error"
    assert res.errors[0].type == "general_error"
    assert "Network failure" in res.errors[0].message
