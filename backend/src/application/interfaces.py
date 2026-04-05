from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.domain.models import Position

class BrokerGateway(ABC):
    @abstractmethod
    def fetch_positions(self, cad_usd_rate: float) -> List[Position]:
        """Fetch raw positions from the broker and return normalized Position models."""
        pass

    @property
    @abstractmethod
    def broker_name(self) -> str:
        """Name of the broker."""
        pass
