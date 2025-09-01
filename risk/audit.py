from typing import Dict, Any
from utils.logger import log

def emit_audit_snapshot(index: str, ltp: float, oc: dict, breadth: dict, signal_stack: list[str],
                        greeks_at_decision: dict, risk_state: dict, ts: str) -> dict:
    snap = {
        "audit_snapshot": {
            "index": index,
            "ltp": ltp,
            "oc_summary": oc,
            "breadth": breadth,
            "signal_stack": signal_stack,
            "greeks_at_decision": greeks_at_decision,
            "risk_state": risk_state,
            "timestamp": ts,
        }
    }
    log.info("audit_snapshot", extra={"_extra": snap})
    return snap
