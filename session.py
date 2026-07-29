# -*- coding: utf-8 -*-
import pandas as pd

def opening_shield_active(index: pd.Index) -> bool:
    """Evalúa de forma segura si la última vela corresponde al bloque de apertura (9:30 - 10:00 EST)"""
    if index is None or len(index) == 0:
        return False
    try:
        # Extrae el último elemento del índice de forma segura
        ultimo_registro = index[-1]
        
        # Si pandas lo guardó como objeto Timestamp nativo
        if hasattr(ultimo_registro, 'hour'):
            h = ultimo_registro.hour
            m = ultimo_registro.minute
            return (h == 9 and 30 <= m <= 59)
            
        # Resguardo de seguridad: si viene en formato string por fallos de conversión de Linux
        str_registro = str(ultimo_registro)
        if "09:30" in str_registro:
            return True
    except Exception:
        pass
    return False
