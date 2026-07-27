from dataclasses import dataclass, field

@dataclass(frozen=True)
class Settings:
    app_name: str = "AI-OS PRO v3 Institutional"
    database_path: str = "trading_system.db"
    market_timezone: str = "America/New_York"
    default_period: str = "60d"
    default_interval: str = "1h"
    ema_periods: tuple[int, ...] = (9, 20, 40, 100, 200)
    bollinger_window: int = 21
    bollinger_std: float = 2.1
    min_bars: int = 210
    opening_shield_minutes: int = 30
    max_risk_pct: float = 0.10
    min_justification_chars: int = 20
    option_min_dte: int = 7
    option_target_max_dte: int = 15
    option_absolute_max_dte: int = 45
    max_option_spread_pct: float = 0.20
    min_open_interest: int = 50
    min_option_volume: int = 1

SETTINGS = Settings()
