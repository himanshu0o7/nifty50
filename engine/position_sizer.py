from typing import Tuple
from utils.instruments import get_instrument
import math

def lots_for_risk(index: str, capital: float, per_trade_risk_pct: float, stop_pts: float, point_value: float) -> Tuple[int, float]:
    """
    Returns (lots, risk_amount). For options, approximate stop_pts * lot_size * point_value.
    point_value: rupees per option point (usually 1 for NIFTY options).
    """
    inst = get_instrument(index)
    risk_budget = capital * per_trade_risk_pct
    per_lot_risk = stop_pts * inst.lot_size * point_value
    lots = math.floor(risk_budget / per_lot_risk) if per_lot_risk > 0 else 0
    lots = max(lots, 0)
    return lots, risk_budget
