from typing import List, Tuple

def calc_vwap(prices: List[float], volumes: List[float]) -> float:
    assert len(prices) == len(volumes) and prices, "prices/volumes mismatch"
    num = sum(p*v for p, v in zip(prices, volumes))
    den = sum(volumes)
    return num / den if den else prices[-1]

def calc_cpr(ph: float, pl: float, pc: float) -> Tuple[float, float, float]:
    pivot = (ph + pl + pc) / 3.0
    bc = (ph + pl) / 2.0
    tc = 2 * pivot - bc
    return bc, pivot, tc
