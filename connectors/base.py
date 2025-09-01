from abc import ABC, abstractmethod
from typing import Dict, Any

class BrokerConnector(ABC):
    @abstractmethod
    def place_order(self, symbol: str, side: str, qty: int, price: float | None, order_type: str) -> Dict[str, Any]:
        ...

    @abstractmethod
    def modify_order(self, order_id: str, price: float | None = None, qty: int | None = None) -> Dict[str, Any]:
        ...

    @abstractmethod
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        ...
