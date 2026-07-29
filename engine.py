from __future__ import annotations
import pandas as pd
from config.settings import SETTINGS

class IndicatorError(RuntimeError):
    pass

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) < SETTINGS.min_bars:
        raise IndicatorError(f"Se requieren al menos {SETTINGS.min_bars} velas; recibidas: {len(df)}.")
    data = df.copy()
    close = data["Close"]
    for period in SETTINGS.ema_periods:
        data[f"EMA{period}"] = close.ewm(span=period, adjust=False).mean()
    data["BB_Base"] = close.rolling(SETTINGS.bollinger_window).mean()
    std = close.rolling(SETTINGS.bollinger_window).std()
    data["BB_Sup"] = data["BB_Base"] + SETTINGS.bollinger_std * std
    data["BB_Inf"] = data["BB_Base"] - SETTINGS.bollinger_std * std
    data["BB_Width"] = (data["BB_Sup"] - data["BB_Inf"]) / data["BB_Base"]
    tr = pd.concat([
        data["High"] - data["Low"],
        (data["High"] - data["Close"].shift()).abs(),
        (data["Low"] - data["Close"].shift()).abs(),
    ], axis=1).max(axis=1)
    data["ATR14"] = tr.rolling(14).mean()
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, pd.NA)
    data["RSI14"] = 100 - (100 / (1 + rs))
    return data
