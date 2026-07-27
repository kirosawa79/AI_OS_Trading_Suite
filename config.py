# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class MarketConfig:
    """Configuración estructural de Horarios e Indicadores de Volatilidad"""
    market_timezone: str = "America/New_York"
    bollinger_window: int = 21
    bollinger_std: float = 2.1
    opening_shield_minutes: int = 30

@dataclass(frozen=True)
class RiskConfig:
    """Parámetros Institucionales de Gestión de Capital y Límites de Cuenta"""
    max_account_risk: float = 0.10  # Límite estricto del 10% de riesgo por operación
    default_iv_fallback: float = 0.35
    min_contract_price: float = 1.20

@dataclass(frozen=True)
class AIScoreConfig:
    """Umbrales Cuánticos para la Matriz de Puntuación Algorítmica (Fase 3)"""
    min_score_to_trade: int = 70    # Si el AI SCORE es menor a 70/100, la operación se bloquea
    weight_trend: int = 30
    weight_momentum: int = 30
    weight_volatility: int = 20
    weight_liquidity: int = 20

# Constant Maestras Reutilizables por el IndicatorEngine
EMA_PERIODS: List[int] = [9, 20, 40, 100, 200]

# Inicialización de Objetos de Configuración Global
MARKET = MarketConfig()
RISK = RiskConfig()
AI_SCORE = AIScoreConfig()
