from __future__ import annotations
import pandas as pd
import yfinance as yf
from config.settings import SETTINGS

class MarketDataError(RuntimeError):
    pass

def normalize_ohlcv(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if df is None or df.empty:
        raise MarketDataError(f"No se encontraron datos para {ticker}.")
    data = df.copy()
    if isinstance(data.columns, pd.MultiIndex):
        levels = [set(map(str, data.columns.get_level_values(i))) for i in range(data.columns.nlevels)]
        if ticker in levels[-1]:
            data = data.xs(ticker, axis=1, level=-1, drop_level=True)
        elif ticker in levels[0]:
            data = data.xs(ticker, axis=1, level=0, drop_level=True)
        else:
            data.columns = data.columns.get_level_values(0)
    rename = {c: str(c).strip().title() for c in data.columns}
    data = data.rename(columns=rename)
    required = ["Open", "High", "Low", "Close"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise MarketDataError(f"Faltan columnas OHLC: {', '.join(missing)}")
    keep = [c for c in ["Open","High","Low","Close","Volume"] if c in data.columns]
    data = data[keep].copy()
    for c in keep:
        data[c] = pd.to_numeric(data[c], errors="coerce")
    data = data.dropna(subset=required)
    if data.empty:
        raise MarketDataError(f"Los datos de {ticker} no contienen velas válidas.")
    return data.sort_index()

def download_ohlcv(ticker: str, period: str | None=None, interval: str | None=None) -> pd.DataFrame:
    ticker = ticker.upper().strip()
    if not ticker:
        raise MarketDataError("Ticker vacío.")
    raw = yf.download(
        ticker,
        period=period or SETTINGS.default_period,
        interval=interval or SETTINGS.default_interval,
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    return normalize_ohlcv(raw, ticker)
