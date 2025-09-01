from typing import Iterable, Dict, Any
from engine.schemas import TradeDecision, NoTrade
from utils.logger import log

def run_backtest(bars: Iterable[Dict[str, Any]], cfg: Dict[str, Any]) -> None:
    # TODO: implement reuse of signal/risk logic; keep same output contract
    for bar in bars:
        # produce NoTrade for now
        nt = NoTrade(reason="backtest_stub", timestamp=bar["ts"], backtest=True).dict()
        log.info("no_trade", extra={"_extra": nt})
