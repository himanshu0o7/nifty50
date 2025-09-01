# connectors/angel_one.py
import os
from typing import Dict, Any
from connectors.base import BrokerConnector
from utils.logger import log

from SmartApi import SmartConnect  # pip install smartapi-python
import pyotp

class AngelOneConnector(BrokerConnector):
    def __init__(self) -> None:
        api_key = os.environ["ANGEL_API_KEY"]
        client = os.environ["ANGEL_CLIENT_CODE"]
        password = os.environ["ANGEL_PASSWORD"]
        totp_secret = os.environ["ANGEL_TOTP_SECRET"]

        self.smart = SmartConnect(api_key=api_key)
        totp = pyotp.TOTP(totp_secret).now()
        login = self.smart.generateSession(client, password, totp)
        self.feed_token = self.smart.getfeedToken()
        log.info("angelone_login_ok", extra={"_extra": {"client": client}})

        # cache instruments (once)
        self._nfo = self.smart.getInstruments("NFO")
        self._token_map = {row["tradingsymbol"]: row["token"] for row in self._nfo}

    def _resolve_token(self, tradingsymbol: str) -> str:
        token = self._token_map.get(tradingsymbol)
        if not token:
            raise ValueError(f"Symbol token not found for {tradingsymbol}")
        return token

    def place_order(self, symbol: str, side: str, qty: int, price: float | None, order_type: str) -> Dict[str, Any]:
        """
        symbol: tradingsymbol e.g., NIFTY25SEP24700CE
        side: "BUY" or "SELL"
        order_type: "MARKET" or "LIMIT"
        """
        token = self._resolve_token(symbol)
        payload = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": side,
            "exchange": "NFO",
            "ordertype": order_type,
            "producttype": "INTRADAY",
            "duration": "DAY",
            "quantity": int(qty),
        }
        if order_type == "LIMIT" and price is not None:
            payload["price"] = float(price)

        try:
            res = self.smart.placeOrder(**payload)
            log.info("broker_event", extra={"_extra": {"broker_event": {
                "stage": "place", "broker": "angel_one", "client_order_id": res.get("orderid"),
                "status": "acknowledged", "details": "", "timestamp": ""}}})
            return {"status": "acknowledged", "order_id": res.get("orderid")}
        except Exception as e:
            log.info("broker_event", extra={"_extra": {"broker_event": {
                "stage": "place", "broker": "angel_one", "status": "rejected", "details": str(e)}}})
            raise

    def modify_order(self, order_id: str, price: float | None = None, qty: int | None = None) -> Dict[str, Any]:
        # implement when needed; SmartAPI uses modifyOrder(variety, orderid, ...)
        return {"status": "noop", "order_id": order_id}

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        try:
            res = self.smart.cancelOrder(variety="NORMAL", orderid=order_id)
            return {"status": "acknowledged", "order_id": order_id}
        except Exception as e:
            return {"status": "rejected", "details": str(e)}
