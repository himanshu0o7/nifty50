import requests

class TelegramBot:
    def __init__(self, config):
        self.token = config["api_keys"]["telegram_bot"]
        self.chat_id = config["api_keys"]["telegram_chat_id"]

    def send_alert(self, msg):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": msg}
        requests.post(url, data=payload)
