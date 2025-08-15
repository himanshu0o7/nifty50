import pandas as pd
from datetime import datetime

class TradeMonitor:
    def __init__(self, config):
        self.trades = []
        self.config = config

    def add_trade(self, order):
        self.trades.append(order)
        pd.DataFrame(self.trades).to_csv("data/trade_logs.csv", index=False)

    def update(self):
        pass  # Can add live PnL tracking here