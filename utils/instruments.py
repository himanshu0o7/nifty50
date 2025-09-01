# utils/instruments.py
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict

# Lot sizes — per your instruction
LOT_SIZES: Dict[str, int] = {
    "NIFTY50": 75,      # customized as requested
    "BANKNIFTY": 15,
}

# Map internal index name -> option symbol root used by brokers
INDEX_SYMBOL_ROOT = {
    "NIFTY50": "NIFTY",
    "BANKNIFTY": "BANKNIFTY",
}

IST = timezone(timedelta(hours=5, minutes=30))

@dataclass(frozen=True)
class InstrumentInfo:
    symbol: str
    lot_size: int
    root: str

def get_instrument(symbol: str) -> InstrumentInfo:
    lot = LOT_SIZES.get(symbol)
    if not lot:
        raise ValueError(f"Unknown symbol for lot size: {symbol}")
    root = INDEX_SYMBOL_ROOT.get(symbol, symbol)
    return InstrumentInfo(symbol, lot, root)

# -- Weekly expiry helper (custom weekday) -------------------------------------
# Python weekday(): Monday=0 ... Sunday=6
_WEEKDAY_MAP = {
    "MONDAY": 0, "TUESDAY": 1, "WEDNESDAY": 2, "THURSDAY": 3,
    "FRIDAY": 4, "SATURDAY": 5, "SUNDAY": 6
}

def next_weekly_expiry(index: str, from_dt: datetime | None = None, weekday_name: str = "TUESDAY") -> datetime:
    """Return next weekly expiry date at the given weekday (IST)."""
    wd_target = _WEEKDAY_MAP[weekday_name.upper()]
    now = (from_dt or datetime.now(IST)).date()
    # find next occurrence of target weekday (today+0..6)
    days_ahead = (wd_target - now.weekday()) % 7
    if days_ahead == 0:  # if today is the day, move to next week (avoid 'today' expiry in intraday runs)
        days_ahead = 7
    dt = datetime.combine(now + timedelta(days=days_ahead), datetime.min.time(), IST)
    return dt

# -- Tradingsymbol formatter (Angel One) ---------------------------------------
# Angel typically uses: ROOT + DDMMMYY + STRIKE + CE/PE, e.g. NIFTY25SEP24700CE
_MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

def _ddmmmyy(d: datetime) -> str:
    dd = f"{d.day:02d}"
    mmm = _MONTHS[d.month - 1]
    yy = f"{d.year % 100:02d}"
    return f"{dd}{mmm}{yy}"

def make_option_tradingsymbol(index: str, expiry_dt: datetime, strike: int, option_type: str) -> str:
    root = INDEX_SYMBOL_ROOT.get(index, index)
    return f"{root}{_ddmmmyy(expiry_dt)}{int(strike)}{option_type.upper()}"
