# -*- coding: utf-8 -*-
import pandas as pd

def opening_shield_active(index: pd.Index) -> bool:
    """Evalúa si la última vela corresponde a los primeros 30 minutos de Wall Street (9:30 - 10:00 EST)"""
    if index is None or len(index) == 0:
        return False
    try:
        # Extrae la hora y minuto nativo de la última vela sin importar la zona horaria del servidor
        ultimo_registro = index[-1]
        if hasattr(ultimo_registro, 'time'):
            h = ultimo_registro.time().hour
            m = ultimo_registro.time().minute
            # Filtro perimetral: Verdadero si está entre las 9:30 AM y las 9:59 AM
            return (h == 9 and 30 <= m <= 59)
    except Exception:
        pass
    return False
