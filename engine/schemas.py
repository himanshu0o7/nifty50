from pydantic import BaseModel, Field, validator, conint, confloat
from typing import List, Optional, Literal, Dict

class Greeks(BaseModel):
    delta: Optional[confloat(ge=-1, le=1)] = None
    vega: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    iv: Optional[float] = None

class TradeDecision(BaseModel):
    index: Literal["NIFTY50","BANKNIFTY"]
    action: Literal["BUY_CE","BUY_PE","EXIT","NO_TRADE"]
    strike: conint(gt=0)
    option_type: Literal["CE","PE"]
    expiry: str
    entry_type: Literal["LIMIT","MARKET"]
    entry: confloat(gt=0)
    stop_loss: confloat(gt=0)
    tsl: Optional[str] = None
    target: Optional[confloat(gt=0)] = None
    r_multiple: Optional[confloat(gt=0)] = None
    lots: conint(ge=1)
    confidence_pct: conint(ge=0, le=100)
    signal_stack: List[str] = []
    greeks: Greeks = Greeks()
    risk_check: str
    broker: Literal["angel_one","zerodha_kite","upstox"]
    reason: str
    timestamp: str
    backtest: Optional[bool] = False

class NoTrade(BaseModel):
    reason: str
    timestamp: str
    backtest: Optional[bool] = False

class BrokerEvent(BaseModel):
    stage: Literal["place","modify","cancel"]
    broker: Literal["angel_one","zerodha_kite","upstox"]
    client_order_id: str
    status: Literal["acknowledged","rejected","timeout","failover_triggered"]
    details: Optional[str] = None
    timestamp: str

class AgentEvent(BaseModel):
    type: Literal["config_error","heartbeat_lag","vol_spike_halt","cooldown_active","failover_complete"]
    details: Optional[str] = None
    timestamp: str

class AuditSnapshot(BaseModel):
    index: Literal["NIFTY50","BANKNIFTY"]
    ltp: float
    oc_summary: Dict[str, object]
    breadth: Dict[str, object]
    signal_stack: List[str]
    greeks_at_decision: Greeks
    risk_state: Dict[str, object]
    timestamp: str
    debug: Optional[Dict[str, object]] = None
