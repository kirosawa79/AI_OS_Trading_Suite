from __future__ import annotations
from market.data import download_ohlcv
from indicators.engine import calculate_indicators
from signals.engine import evaluate_signal
from market.session import opening_shield_active

def scan_tickers(tickers: list[str]):
    results=[]
    for ticker in tickers:
        try:
            data=calculate_indicators(download_ohlcv(ticker))
            signal=evaluate_signal(ticker,data,opening_shield_active(data.index[-1]))
            results.append({'ticker':ticker,'price':round(float(data['Close'].iloc[-1]),2),'strategy':signal.strategy,'score':signal.score,'authorized':signal.authorized,'error':''})
        except Exception as exc:
            results.append({'ticker':ticker,'price':None,'strategy':'ERROR','score':0,'authorized':False,'error':str(exc)})
    return results
