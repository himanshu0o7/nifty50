import os
import logging
import requests
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from smartapi import SmartConnect
from dotenv import load_dotenv
from ta import add_all_ta_features  # pip install ta (technical analysis library)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ANGEL_ONE_API_KEY")
        self.client_id = os.getenv("ANGEL_ONE_CLIENT_ID")
        self.password = os.getenv("ANGEL_ONE_PASSWORD")
        self.totp = os.getenv("ANGEL_ONE_TOTP")
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")

        if not all([self.api_key, self.client_id, self.password, self.totp, self.alpha_vantage_key]):
            raise ValueError("Missing environment variables for APIs")

        try:
            self.smart = SmartConnect(api_key=self.api_key)
            self.smart.generateSession(self.client_id, self.password, self.totp)
            logger.info("Authenticated with Angel One")
        except Exception as e:
            raise RuntimeError(f"Authentication failed: {e}")

        self.nifty_token = self._get_nifty_token()

    def _get_nifty_token(self):
        try:
            url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
            instruments = requests.get(url).json()
            for inst in instruments:
                if inst['exch_seg'] == 'NSE' and inst['symbol'].startswith('NIFTY') and inst['name'] == 'NIFTY 50':
                    return inst['token']
            raise ValueError("NIFTY 50 token not found")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch token: {e}")

    def get_market_data(self):
        try:
            data = self.smart.ltpData("NSE", "NIFTY 50", self.nifty_token)['data']
            return data
        except Exception as e:
            logger.error(f"Market data fetch failed: {e}")
            return {}

    def get_global_cues(self):
        try:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=^DJI&interval=5min&apikey={self.alpha_vantage_key}"
            data = requests.get(url).json().get("Time Series (5min)", {})
            return data
        except Exception as e:
            logger.error(f"Global cues fetch failed: {e}")
            return {}

    def get_historical_data(self, days=30):
        # Fetch historical Nifty 50 data (simplified; use smart.getCandleData for real)
        # For demo, assume fetching via Alpha Vantage or yfinance (adapt as needed)
        try:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=^NSEI&outputsize=compact&apikey={self.alpha_vantage_key}"
            data = requests.get(url).json().get("Time Series (Daily)", {})
            df = pd.DataFrame.from_dict(data, orient='index').astype(float)
            df = df.sort_index()
            df = add_all_ta_features(df, open="1. open", high="2. high", low="3. low", close="4. close", volume="5. volume")
            return df.tail(days)
        except Exception as e:
            logger.error(f"Historical data fetch failed: {e}")
            return pd.DataFrame()

class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, action_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class RLTrader:
    def __init__(self, state_size=10, action_size=3, batch_size=64, gamma=0.99, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, learning_rate=0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.model = DQN(state_size, action_size)
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()
        self.position = 0  # 0: no position, 1: long
        self.entry_price = 0

    def get_state(self, market_data, global_cues, historical_df):
        # Extract features: LTP, volume, RSI, MA, global change, etc.
        if not market_data or historical_df.empty:
            return np.zeros(self.state_size)
        ltp = market_data.get('ltp', 0)
        volume = market_data.get('volume', 0) if 'volume' in market_data else historical_df['volume'].iloc[-1]
        rsi = historical_df['momentum_rsi'].iloc[-1] if 'momentum_rsi' in historical_df else 50
        ma50 = historical_df['close'].rolling(50).mean().iloc[-1]
        global_change = list(global_cues.values())[0]['4. close'] if global_cues else 0
        state = np.array([ltp, volume, rsi, ma50, global_change, ltp - ma50, rsi - 50, volume / historical_df['volume'].mean(), float(global_change), 0])  # Pad to state_size
        return state[:self.state_size]

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return np.random.randint(self.action_size)  # Explore
        state = torch.FloatTensor(state).unsqueeze(0)
        q_values = self.model(state)
        return torch.argmax(q_values).item()  # Exploit

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        minibatch = np.random.choice(len(self.memory), self.batch_size, replace=False)
        states, actions, rewards, next_states, dones = zip(*[self.memory[i] for i in minibatch])
        states = torch.FloatTensor(np.array(states))
        next_states = torch.FloatTensor(np.array(next_states))
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        dones = torch.FloatTensor(dones)

        q_values = self.model(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        next_q_values = self.model(next_states).max(1)[0]
        targets = rewards + self.gamma * next_q_values * (1 - dones)

        loss = self.loss_fn(q_values, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def train(self, historical_df, episodes=100):
        for episode in range(episodes):
            state = self.get_state({}, {}, historical_df.iloc[:1])  # Start from beginning
            total_reward = 0
            for t in range(1, len(historical_df)):
                action = self.act(state)
                next_state = self.get_state({}, {}, historical_df.iloc[t:t+1])
                price = historical_df['close'].iloc[t]
                prev_price = historical_df['close'].iloc[t-1]

                if action == 1 and self.position == 0:  # Buy
                    self.position = 1
                    self.entry_price = price
                    reward = 0
                elif action == 2 and self.position == 1:  # Sell
                    reward = (price - self.entry_price) - 0.01 * abs(price - self.entry_price)  # Profit minus slippage
                    self.position = 0
                else:  # Hold
                    reward = 0 if self.position == 0 else (price - prev_price) * self.position  # Unrealized P/L

                done = t == len(historical_df) - 1
                self.remember(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward

                if done:
                    logger.info(f"Episode {episode+1}/{episodes} - Total Reward: {total_reward}")
                    break

            self.replay()

    def decide_trade(self, state):
        action = self.act(state)
        if action == 0:
            return "Hold"
        elif action == 1:
            return "Buy"
        return "Sell"

    def evolve(self, new_data):
        # Retrain with new data for self-evolution
        self.train(new_data, episodes=10)

if __name__ == "__main__":
    collector = DataCollector()
    historical_df = collector.get_historical_data(days=365)  # Fetch 1 year for training
    trader = RLTrader(state_size=10, action_size=3)

    # Train the bot (self-learning phase)
    trader.train(historical_df, episodes=200)

    # Live decision loop (self-decision, fast inference)
    while True:
        market = collector.get_market_data()
        global_cues = collector.get_global_cues()
        state = trader.get_state(market, global_cues, historical_df)
        decision = trader.decide_trade(state)
        logger.info(f"Decision: {decision} | Current LTP: {market.get('ltp', 'N/A')}")

        # Simulate trade execution (add real order placement via smart.placeOrder)
        # if decision == "Buy": smart.placeOrder(...)

        # Evolve periodically (self-evolving)
        if some_condition:  # e.g., end of day
            new_data = collector.get_historical_data(days=1)
            historical_df = pd.concat([historical_df, new_data])
            trader.evolve(new_data)

        time.sleep(60)  # Check every minute for speed