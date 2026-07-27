from __future__ import annotations
import pandas as pd
from core.models import SignalResult

def evaluate_signal(ticker: str, data: pd.DataFrame, shield_active: bool=False) -> SignalResult:
    row = data.iloc[-1]
    price = float(row["Close"])
    call_stack = price > row["EMA9"] > row["EMA20"] > row["EMA40"] > row["EMA100"] > row["EMA200"]
    put_stack = price < row["EMA9"] < row["EMA20"] < row["EMA40"] < row["EMA100"] < row["EMA200"]
    call_breakout = price > row["BB_Sup"]
    put_breakout = price < row["BB_Inf"]
    score = 0
    reasons=[]
    warnings=[]
    strategy="SIN_ALERTA"
    if call_stack:
        score += 60; reasons.append("Abanico EMA alcista completo.")
    elif put_stack:
        score += 60; reasons.append("Abanico EMA bajista completo.")
    else:
        warnings.append("El abanico EMA no está completamente alineado.")
    if call_breakout:
        score += 25; reasons.append("Ruptura confirmada sobre la banda superior.")
    elif put_breakout:
        score += 25; reasons.append("Ruptura confirmada bajo la banda inferior.")
    if pd.notna(row.get("RSI14")):
        rsi=float(row["RSI14"])
        if call_stack and 50 <= rsi <= 75: score += 15; reasons.append("RSI compatible con momentum alcista.")
        elif put_stack and 25 <= rsi <= 50: score += 15; reasons.append("RSI compatible con momentum bajista.")
    if call_stack and call_breakout: strategy="CALL_EMA_BB"
    elif put_stack and put_breakout: strategy="PUT_EMA_BB"
    if shield_active:
        warnings.append("Shield de apertura activo.")
    authorized = strategy != "SIN_ALERTA" and not shield_active and score >= 75
    return SignalResult(ticker=ticker, strategy=strategy, authorized=authorized, score=min(score,100), reasons=reasons, warnings=warnings)
