import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

class DataCollector:
    def __init__(self):
        self.tz_ny = pytz.timezone("America/New_York")

    def obtener_datos_intradia(self, ticker):
        try:
            asset = yf.Ticker(ticker)
            df = asset.history(period="15d", interval="1h")
            
            if df.empty:
                return None, {"status": False, "reason": f"No se encontraron datos para {ticker}."}
            
            df = df.reset_index()
            df = df.rename(columns={
                "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"
            })
            
            hora_actual_ny = datetime.now(self.tz_ny).time()
            return df, {"status": True, "hora_ny": hora_actual_ny}
            
        except Exception as e:
            return None, {"status": False, "reason": str(e)}
