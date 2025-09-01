# marketdata/option_chain_provider.py
import os
import requests
from typing import Dict, Any, Optional
from utils.logger import log

class OptionChainProvider:
    """
    OI/IV/Greeks provider. Source 'sensibull' (preferred) or 'mock'.
    Env:
      SENSIBULL_BASE (default https://api.sensibull.com)
      SENSIBULL_AUTH = "Bearer <token>" or "cookie: <cookieStr>"
    """

    def __init__(self, source: str = "sensibull"):
        self.source = source
        self.base = os.environ.get("SENSIBULL_BASE", "https://api.sensibull.com")
        self.auth = os.environ.get("SENSIBULL_AUTH", "")

    def _headers(self) -> Dict[str, str]:
        if self.auth.startswith("cookie:"):
            return {"Cookie": self.auth.split("cookie:", 1)[1].strip()}
        elif self.auth.startswith("Bearer "):
            return {"Authorization": self.auth}
        return {}

    def get_snapshot(self, index: str) -> Dict[str, Any]:
        if self.source != "sensibull":
            # Fallback mock
            log.info("option_chain_snapshot", extra={"_extra": {"index": index, "source": "mock"}})
            return {"pcr": 1.05, "max_pain": 24600, "oi_trend": "CE_unwind PE_build", "atm": None}

        # Map NIFTY50 -> NIFTY for API
        symbol = "NIFTY" if index == "NIFTY50" else index

        # NOTE: The exact Sensibull path may differ; adjust if needed.
        # Try: /v1/option-chain?symbol=NIFTY OR /v2/option-chain/{symbol}
        url = f"{self.base}/v1/option-chain"
        try:
            resp = requests.get(url, params={"symbol": symbol}, headers=self._headers(), timeout=5)
            resp.raise_for_status()
            data = resp.json()

            # Normalize to our minimal schema
            oc = {
                "pcr": data.get("pcr"),
                "max_pain": data.get("maxPain") or data.get("max_pain"),
                "oi_trend": data.get("oiTrend") or data.get("oi_trend"),
                "atm": data.get("atm")  # expected like {"strike": 24600, "CE": {"ltp":.., "iv":.., "delta":..}, "PE": {...}}
            }
            log.info("option_chain_snapshot", extra={"_extra": {"index": index, "source": "sensibull"}})
            return oc
        except Exception as e:
            log.info("option_chain_snapshot_error", extra={"_extra": {"index": index, "err": str(e)}})
            # safe fallback to proceed
            return {"pcr": None, "max_pain": None, "oi_trend": None, "atm": None}
