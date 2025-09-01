import requests
from typing import Optional, Dict, Any

class TelegramClient:
    def __init__(self, bot_token: str, chat_id: str, base_url: str = "https://api.telegram.org"):
        self.base_url = base_url
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send(self, text: str, disable_web_page_preview: bool = True) -> None:
        # NOTE: handle exceptions in caller for reliability
        url = f"{self.base_url}/bot{self.bot_token}/sendMessage"
        requests.post(url, timeout=5, json={
            "chat_id": self.chat_id,
            "text": text,
            "disable_web_page_preview": disable_web_page_preview,
            "parse_mode": "Markdown"
        })

def render_entry_decision(idx: str, strike: int, lots: int, price: float, sl: float, conf: int, broker: str) -> str:
    return (f"*{idx}* BUY {strike} x{lots} @ {price:.1f} | SL {sl:.1f} | Conf {conf}% | Broker: {broker}")
