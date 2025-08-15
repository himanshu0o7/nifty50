class RiskManager:
    def __init__(self, config):
        self.config = config
        self.daily_loss = 0

    def validate(self, signal):
        # Daily loss check
        if self.daily_loss >= (self.config["risk"]["capital"] * self.config["risk"]["daily_loss_limit_pct"] / 100):
            return False
        # Confidence check
        if signal["Confidence"] < self.config["strategy"]["min_confidence"]:
            return False
        return True
