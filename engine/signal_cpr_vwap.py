from typing import Dict, Any

def detect(index: str, ltp: float, vwap: float, cpr: Dict[str, float], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a signal dict:
    { 'side': 'LONG'|'SHORT'|None, 'strength': 0-100, 'explain': str }
    """
    above_vwap = ltp > vwap
    above_tc = ltp > cpr["tc"]
    if params.get("require_above_vwap_for_longs", True) and above_vwap and above_tc:
        return {"side": "LONG", "strength": 75, "explain": "above VWAP & above CPR-TC"}
    return {"side": None, "strength": 0, "explain": "no cpr/vwap alignment"}
