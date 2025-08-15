from smartapi import SmartConnect

class ExecutionEngine:
    def __init__(self, config):
        self.config = config
        self.smart = SmartConnect(api_key=config["api_keys"]["angel_one"])
        self.smart.generateSession(config["api_keys"]["angel_one_client"], "YOUR_PASSWORD", "YOUR_TOTP")

    def place_order(self, signal):
        # Example CE/PE Buy
        order = self.smart.placeOrder(
            variety="NORMAL",
            tradingsymbol="NIFTY24600CE",
            symboltoken="12345",
            transactiontype="BUY" if signal["Direction"]=="CALL" else "SELL",
            exchange="NSE",
            ordertype="MARKET",
            producttype="INTRADAY",
            duration="DAY",
            price=0,
            squareoff=signal["Target"],
            stoploss=signal["SL"],
            quantity=50
        )
        return order