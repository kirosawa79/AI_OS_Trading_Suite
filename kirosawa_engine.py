import pandas as pd
import numpy as np
from datetime import datetime, time

class KirosawaEngine:
    def __init__(self, tolerancia_pm40=0.005, mecha_max_porcentaje=0.15):
        self.tolerancia_pm40 = tolerancia_pm40
        self.mecha_max_porcentaje = mecha_max_porcentaje

    def calcular_indicadores(self, df):
        df['pm20'] = df['close'].rolling(window=20).mean()
        df['pm40'] = df['close'].rolling(window=40).mean()
        return df

    def evaluar_estrategia_pm40_call(self, df, hora_ny):
        inicio_operativo = time(11, 0, 0)
        fin_operativo = time(16, 0, 0)
        
        if not (inicio_operativo <= hora_ny <= fin_operativo):
            return {"status": False, "reason": f"BLOQUEADO: Fuera de horario operativo de compra ({hora_ny})."}

        if len(df) < 40:
            return {"status": False, "reason": "ERROR: Datos insuficientes para calcular PM40."}

        ultima_vela = df.iloc[-1]
        
        close_val = ultima_vela['close']
        open_val  = ultima_vela['open']
        high_val  = ultima_vela['high']
        low_val   = ultima_vela['low']
        pm20_val  = ultima_vela['pm20']
        pm40_val  = ultima_vela['pm40']

        cuerpo = abs(close_val - open_val)
        mecha_superior = high_val - max(close_val, open_val)
        
        tendencia_alcista = pm20_val > pm40_val
        cerca_pm40 = (low_val <= pm40_val * (1 + self.tolerancia_pm40)) and (high_val >= pm40_val * (1 - self.tolerancia_pm40))
        es_vela_verde = close_val > open_val
        sin_mecha_superior = mecha_superior < (cuerpo * self.mecha_max_porcentaje) if cuerpo > 0 else False

        if not tendencia_alcista:
            return {"status": False, "reason": "RECHAZADO: Estructura macro bajista o lateral (PM20 < PM40)."}
        if not cerca_pm40:
            return {"status": False, "reason": "RECHAZADO: El precio no ha corregido a la zona de compra del PM40."}
        if not es_vela_verde:
            return {"status": False, "reason": "RECHAZADO: Se requiere una vela verde de confirmación."}
        if not sin_mecha_superior:
            return {"status": False, "reason": "RECHAZADO: Vela verde inválida. Mecha superior muy larga."}

        return {
            "status": True,
            "strategy": "CALL_PM40",
            "reason": "¡ALERTA TÉCNICA ACTIVA! Configuración PM40 válida. Enviar al Director de Inversiones."
        }
