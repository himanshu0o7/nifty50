from typing import Dict, Any
from datetime import datetime, time
from utils.logger import log

def _parse_t(hhmm: str) -> time:
    h, m = map(int, hhmm.split(":"))
    return time(hour=h, minute=m)

def check_time_guards(now_ist: datetime, cfg: Dict[str, Any]) -> str | None:
    tg = cfg.get("time_guards", {})
    nnb = tg.get("no_trade_before")
    nne = tg.get("no_new_entry_after")
    now_t = now_ist.time()
    if nnb and now_t < _parse_t(nnb):
        return "time_guard:too_early"
    if nne and now_t > _parse_t(nne):
        return "time_guard:too_late"
    return None

def pretrade_blockers(day_pnl_pct: float, risk_cfg: Dict[str, Any], state: Dict[str, Any]) -> str | None:
    if day_pnl_pct <= -abs(risk_cfg.get("max_daily_loss_pct", 0.03)):
        return "risk_block:max_daily_loss"
    if state.get("vol_spike_halt"):
        return "risk_block:vol_spike"
    if state.get("cooldown_active"):
        return "risk_block:cooldown"
    if state.get("open_positions", 0) >= risk_cfg.get("max_positions", 1):
        return "risk_block:position_limit"
    return None
