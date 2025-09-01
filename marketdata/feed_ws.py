import asyncio, time
from typing import AsyncIterator, Dict, Any, Optional
from utils.logger import log

class FeedWS:
    """Broker/exchange websocket wrapper for ticks/LTP/depth"""

    def __init__(self, symbols: list[str]):
        self.symbols = symbols
        self._connected = False

    async def connect(self) -> None:
        # TODO: plug broker SDK here (Angel SmartAPI/Kite/Upstox)
        log.info("connecting feed", extra={"_extra": {"symbols": self.symbols}})
        self._connected = True

    async def ticks(self) -> AsyncIterator[Dict[str, Any]]:
        if not self._connected:
            await self.connect()
        # TODO: yield real ticks. This is a heartbeat stub.
        while True:
            ts = time.time()
            yield {"ts": ts, "symbol": "NIFTY50", "ltp": 24572.3}  # replace with real data
            await asyncio.sleep(1.0)

    async def close(self) -> None:
        self._connected = False
