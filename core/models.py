from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

@dataclass
class MarketSnapshot:
    ticker: str
    timestamp: datetime
    price: float
    indicators: dict[str, float]

@dataclass
class SignalResult:
    ticker: str
    strategy: str
    authorized: bool
    score: int
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

@dataclass
class PsychologyResult:
    blocked: bool
    bias: str
    message: str

@dataclass
class OptionContract:
    ticker: str
    option_type: str
    expiration: str
    strike: float
    bid: float
    ask: float
    last_price: float
    mid: float
    implied_volatility: float
    volume: int
    open_interest: int
    spread_pct: float
    contract_symbol: str = ""

@dataclass
class PositionPlan:
    capital: float
    risk_pct: float
    risk_budget: float
    unit_cost: float
    quantity: int
    total_cost: float
    valid: bool
    reason: str
