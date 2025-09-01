import os, time, yaml, asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from utils.logger import log
from utils.instruments import get_instrument
from marketdata.feed_ws import FeedWS
from marketdata.option_chain_provider import OptionChainProvider
from marketdata.sentiment_news import get_breadth
from engine.signal_oi_momentum import detect as sig_oi
from engine.signal_cpr_vwap import detect as sig_cpr
from engine.indicators import calc_cpr, calc_vwap
from engine.position_sizer import lots_for_risk
from engine.schemas import TradeDecision, NoTrade
from risk.risk_guard import pretrade_blockers, check_time_guards
from risk.audit import emit_audit_snapshot
from connectors.angel_one import AngelOneConnector

def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ist_now() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

async def main():
    # --- Load configs
    risk_cfg = load_yaml("config/risk.yml")
    strat_cfg = load_yaml("config/strategy.yml")
    primary = strat_cfg["execution"]["primary_broker"]
    index = strat_cfg["universe"]["indices"][0]  # choose first for demo

    # --- Market data
    feed = FeedWS([index])
    ocp = OptionChainProvider("NSE")
    connector = AngelOneConnector()  # TODO: map per primary

    capital = float(os.environ.get("CAPITAL", "17000"))  # rupees
    day_pnl_pct = 0.0
    risk_state = {"open_positions": 0, "vol_spike_halt": False, "cooldown_active": False}

    async for tick in feed.ticks():
        now = ist_now()
        # Guards
        tg = check_time_guards(now, risk_cfg)
        if tg:
            payload = NoTrade(reason=tg, timestamp=now.isoformat()).dict()
            log.info("no_trade", extra={"_extra": payload})
            continue
        blk = pretrade_blockers(day_pnl_pct, risk_cfg, risk_state)
        if blk:
            payload = NoTrade(reason=blk, timestamp=now.isoformat()).dict()
            log.info("no_trade", extra={"_extra": payload})
            continue

        ltp = float(tick["ltp"])
        oc = ocp.get_snapshot(index)
        breadth = get_breadth()

        # CPR/VWAP demo inputs — replace with rolling bars
        day_high, day_low, prev_close = ltp+50, ltp-50, ltp-25
        bc, pivot, tc = calc_cpr(day_high, day_low, prev_close)
        vwap = ltp - 10  # stub

        s1 = sig_oi(index, oc, strat_cfg["signals"]["oi_momentum"])
        s2 = sig_cpr(index, ltp, vwap, {"bc": bc, "pivot": pivot, "tc": tc}, strat_cfg["signals"]["cpr_vwap"])

        signal_stack = []
        side = None
        strength = 0
        if s1["side"] == "LONG" and s2["side"] == "LONG":
            side, strength = "BUY", int((s1["strength"] + s2["strength"]) / 2)
            signal_stack = [f"oi_momentum:{s1['explain']}", f"cpr_vwap:{s2['explain']}"]

        if not side:
            snap = emit_audit_snapshot(index, ltp, oc, breadth, [s1, s2], {"delta": None, "iv": None}, risk_state, now.isoformat())
            log.info("no_trade", extra={"_extra": {"no_trade": {"reason":"mixed_signals", "timestamp": now.isoformat()}}})
            continue

        # Sizing (assume 1% SL distance of LTP for demo; replace with ATR or rule)
        stop_pts = max(ltp * 0.01, 5.0)
        point_value = 1.0
        lots, risk_budget = lots_for_risk(index, capital, risk_cfg["per_trade_risk_pct"], stop_pts, point_value)
        if lots < 1:
            payload = NoTrade(reason="under_min_size", timestamp=now.isoformat()).dict()
            log.info("no_trade", extra={"_extra": payload})
            continue

        # Build decision
        strike = int(round(ltp / 50) * 50)
        td = TradeDecision(
            index=index, action="BUY_CE", strike=strike, option_type="CE",
            expiry="2099-12-31", entry_type="LIMIT", entry=ltp, stop_loss=ltp - stop_pts,
            tsl="ATR(1.5)x", target=None, r_multiple=1.5, lots=lots,
            confidence_pct=min(strength, 95), signal_stack=signal_stack,
            greeks={"delta": None, "iv": None}, risk_check="passed",
            broker=primary, reason="Confluence: OI momentum + CPR/VWAP", timestamp=now.isoformat()
        ).dict()

        # (Execution stub)
        # ack = connector.place_order(symbol=f"{index}{strike}CE", side="BUY", qty=lots*get_instrument(index).lot_size, price=ltp, order_type="LIMIT")
        log.info("trade_decision", extra={"_extra": {"trade_decision": td}})

if __name__ == "__main__":
    asyncio.run(main())
