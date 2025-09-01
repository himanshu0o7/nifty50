📘 KP5 Agent – Intraday Option Buyer (NIFTY / BANKNIFTY)

KP5 Agent is an autonomous intraday options trading bot.
It ingests live market data, generates signals, applies strict risk management, and executes orders through broker APIs.

⚡ Features

Execution: Angel One SmartAPI (live orders in NFO segment).

Market Data:

Sensibull → OI, IV, Greeks.

Broker websocket → live ticks.

Indices: NIFTY50 (lot size 75), BANKNIFTY (lot size 15).

Expiry Handling: Weekly expiry every Tuesday (customizable).

Risk Management:

Per-trade risk %

Max daily loss %

Stop-loss, trailing stop

Time guards & volatility halts

Communication: Telegram push alerts for entries, exits, errors.

Backtest Mode: Run same signals on historical bars.

Repository Structure

kp5_agent/
├─ config/
│  ├─ risk.yml             # risk & money management
│  └─ strategy.yml         # strategy toggles, expiry rules
├─ connectors/             # broker adapters (Angel One, etc.)
├─ marketdata/             # feeds & OI/Greeks providers
├─ engine/                 # signals, indicators, position sizing, schemas
├─ risk/                   # guards & audit logging
├─ utils/                  # instruments, logger, telegram
├─ backtest/               # backtest engine
└─ run_intraday.py         # orchestrator (data → signals → risk → orders)
