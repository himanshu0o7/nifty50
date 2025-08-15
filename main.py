from modules.data_collector import DataCollector
from modules.filter_engine import FilterEngine
from modules.decision_engine import DecisionEngine
from modules.risk_manager import RiskManager
from modules.execution_engine import ExecutionEngine
from modules.trade_monitor import TradeMonitor
from modules.learning_loop import LearningLoop
from modules.telegram_bot import TelegramBot
import time, yaml

# Load config
config = yaml.safe_load(open("config.yaml"))

# Init modules
collector = DataCollector(config)
filters = FilterEngine(config)
decision = DecisionEngine(config)
risk = RiskManager(config)
executor = ExecutionEngine(config)
monitor = TradeMonitor(config)
learner = LearningLoop(config)
bot = TelegramBot(config)

print("[KP5Bot] SmartAI bot started...")

while True:
    try:
        # Step 1: Data
        market_data = collector.get_all_data()

        # Step 2: Filters
        filtered_data = filters.apply(market_data)

        # Step 3: Decision
        signal = decision.generate(filtered_data)

        # Step 4: Execution
        if signal and risk.validate(signal):
            order = executor.place_order(signal)
            bot.send_alert(f"✅ Trade Placed: {order}")
            monitor.add_trade(order)

        # Step 5: Monitor
        monitor.update()

        time.sleep(config["strategy"]["scan_interval_sec"])

    except Exception as e:
        bot.send_alert(f"⚠️ Error: {str(e)}")
