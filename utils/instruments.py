from dataclasses import dataclass
from typing import Dict

# TODO: Replace with NSE instrument master pull; this is a minimal map.
LOT_SIZES: Dict[str, int] = {
    "NIFTY50": 50,
    "BANKNIFTY": 15,
}

@dataclass(frozen=True)
class InstrumentInfo:
    symbol: str
    lot_size: int

def get_instrument(symbol: str) -> InstrumentInfo:
    lot = LOT_SIZES.get(symbol)
    if not lot:
        raise ValueError(f"Unknown symbol for lot size: {symbol}")
    return InstrumentInfo(symbol, lot)
