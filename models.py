# -*- coding: utf-8 -*-
from dataclasses import dataclass

@dataclass
class SignalResult:
    ticker: str
    side: str
    price: float
    reason: str
    opening_shield: bool

@dataclass
class TradeRecord:
    ticker: str
    estrategia: str
    justificacion: str
    bloqueado: bool
    sesgo: str
