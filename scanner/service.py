# -*- coding: utf-8 -*-
from __future__ import annotations
import pandas as pd
from market.data import download_ohlcv
from indicators.engine import calculate_indicators
from signals.engine import evaluate_signal
from market.session import opening_shield_active

def scan_tickers(tickers: list[str]):
    results = []
    for ticker in tickers:
        try:
            # Descarga e inyección de indicadores institucionales de la v3
            raw_data = download_ohlcv(ticker)
            data = calculate_indicators(raw_data)
            
            # Evaluación perimetral del escudo de apertura de Nueva York
            shield_active = opening_shield_active(data.index)
            signal = evaluate_signal(ticker, data, shield_active)
            
            # Extractor adaptativo de precio para evitar errores MultiIndex
            last_close = data['Close'].iloc[-1]
            price_val = float(last_close.iloc[0] if isinstance(last_close, pd.Series) else last_close)
            
            # --- FORMATEADOR DE SEMÁFORO QUANT VISUAL ---
            score_num = int(signal.score)
            if score_num >= 90:
                score_visual = f"🟢 {score_num}"
            elif score_num >= 70:
                score_visual = f"🟡 {score_num}"
            else:
                score_visual = f"🔴 {score_num}"
            
            results.append({
                'ticker': ticker,
                'price': round(price_val, 2),
                'strategy': signal.strategy,
                'score': score_visual,  # El ojo procesa el color de inmediato
                'authorized': "✅ AUTORIZADA" if signal.authorized else "❌ BLOQUEADA",
                'error': ''
            })
        except Exception as exc:
            results.append({
                'ticker': ticker,
                'price': None,
                'strategy': 'ERROR',
                'score': "🔴 0",
                'authorized': "❌ FALLO",
                'error': str(exc)
            })
    return results
