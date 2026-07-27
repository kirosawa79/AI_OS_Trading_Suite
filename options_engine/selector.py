from __future__ import annotations
from datetime import date
import math
import pandas as pd
import yfinance as yf
from config.settings import SETTINGS
from core.models import OptionContract

class OptionSelectionError(RuntimeError):
    pass

def choose_expiration(expirations: tuple[str, ...] | list[str]) -> str:
    today=date.today(); candidates=[]
    for value in expirations:
        try:
            dte=(date.fromisoformat(value)-today).days
            if SETTINGS.option_min_dte <= dte <= SETTINGS.option_absolute_max_dte:
                candidates.append((dte,value))
        except ValueError:
            continue
    if not candidates: raise OptionSelectionError("No existe un vencimiento aceptable.")
    preferred=[x for x in candidates if x[0] <= SETTINGS.option_target_max_dte]
    return min(preferred or candidates, key=lambda x:x[0])[1]

def _number(value, default=0.0):
    try:
        v=float(value)
        return v if math.isfinite(v) else default
    except (TypeError,ValueError): return default

def select_contract(ticker: str, strategy: str, spot: float) -> OptionContract:
    obj=yf.Ticker(ticker)
    expiration=choose_expiration(obj.options)
    chain=obj.option_chain(expiration)
    option_type="CALL" if "CALL" in strategy else "PUT"
    frame=chain.calls.copy() if option_type=="CALL" else chain.puts.copy()
    if frame.empty: raise OptionSelectionError("La cadena de opciones está vacía.")
    target=spot * (1.01 if option_type=="CALL" else 0.99)
    frame["distance"]=(pd.to_numeric(frame["strike"], errors="coerce")-target).abs()
    frame=frame.dropna(subset=["strike"]).sort_values(["distance","openInterest","volume"], ascending=[True,False,False])
    for _, row in frame.iterrows():
        bid=_number(row.get("bid")); ask=_number(row.get("ask")); last=_number(row.get("lastPrice"))
        if ask <= 0: continue
        mid=(bid+ask)/2 if bid>0 else ask
        spread=(ask-bid)/mid if bid>0 and mid>0 else 1.0
        oi=int(_number(row.get("openInterest"))); vol=int(_number(row.get("volume")))
        iv=_number(row.get("impliedVolatility"), -1)
        if iv <= 0 or spread > SETTINGS.max_option_spread_pct or oi < SETTINGS.min_open_interest or vol < SETTINGS.min_option_volume:
            continue
        return OptionContract(ticker,option_type,expiration,_number(row["strike"]),bid,ask,last,mid,iv,vol,oi,spread,str(row.get("contractSymbol", "")))
    raise OptionSelectionError("No se encontró un contrato que cumpla liquidez, spread e IV.")
