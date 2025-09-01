from typing import Dict, Any
from engine.schemas import TradeDecision, Greeks
from utils.logger import log

def detect(index: str, oc: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a signal dict with fields:
    { 'side': 'LONG'|'SHORT'|None, 'strength': 0-100, 'explain': str }
    """
    min_oi_delta = float(params.get("min_oi_delta_5m_pct", 5.0))
    # TODO: use real OI deltas. Here we mock a pass.
    side = "LONG" if oc.get("oi_trend","").startswith("CE_unwind") else None
    strength = 70 if side else 0
    return {"side": side, "strength": strength, "explain": f"oi_delta>=~{min_oi_delta}%, trend={oc.get('oi_trend')}"}
