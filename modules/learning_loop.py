import pandas as pd

class LearningLoop:
    def __init__(self, config):
        self.config = config

    def run(self):
        df = pd.read_csv("data/trade_logs.csv")
        accuracy = (df['Result'] == 'Profit').mean() * 100

        if accuracy < 70:
            self.config['strategy']['min_confidence'] += 5
        elif accuracy > 90:
            self.config['strategy']['min_confidence'] -= 5

        print(f"Updated Confidence: {self.config['strategy']['min_confidence']}")
