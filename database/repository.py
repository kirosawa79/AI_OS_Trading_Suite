from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import pandas as pd
from config.settings import SETTINGS

class TradingRepository:
    def __init__(self, path: str | None=None):
        self.path=Path(path or SETTINGS.database_path)
        self.initialize()
    @contextmanager
    def connect(self):
        conn=sqlite3.connect(self.path)
        conn.row_factory=sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback(); raise
        finally: conn.close()
    def initialize(self):
        with self.connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS registro_operaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                estrategia TEXT NOT NULL,
                justificacion TEXT NOT NULL,
                bloqueado INTEGER NOT NULL,
                sesgo_detectado TEXT,
                fecha TEXT NOT NULL,
                precio REAL,
                score INTEGER,
                contrato TEXT,
                vencimiento TEXT,
                strike REAL,
                bid REAL,
                ask REAL,
                iv REAL,
                open_interest INTEGER,
                volumen INTEGER,
                riesgo_pct REAL,
                cantidad INTEGER,
                costo_total REAL,
                estado TEXT DEFAULT 'EVALUADA'
            )""")
            cols={r[1] for r in conn.execute("PRAGMA table_info(registro_operaciones)")}
            additions={
                'precio':'REAL','score':'INTEGER','contrato':'TEXT','vencimiento':'TEXT','strike':'REAL','bid':'REAL','ask':'REAL','iv':'REAL','open_interest':'INTEGER','volumen':'INTEGER','riesgo_pct':'REAL','cantidad':'INTEGER','costo_total':'REAL','estado':"TEXT DEFAULT 'EVALUADA'"
            }
            for name, typ in additions.items():
                if name not in cols: conn.execute(f"ALTER TABLE registro_operaciones ADD COLUMN {name} {typ}")
    def save_evaluation(self, **v):
        fields=['ticker','estrategia','justificacion','bloqueado','sesgo_detectado','fecha','precio','score','contrato','vencimiento','strike','bid','ask','iv','open_interest','volumen','riesgo_pct','cantidad','costo_total','estado']
        values=[v.get(x) for x in fields]
        values[5]=values[5] or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        q=','.join('?' for _ in fields)
        with self.connect() as conn:
            conn.execute(f"INSERT INTO registro_operaciones ({','.join(fields)}) VALUES ({q})", values)
    def recent(self, limit=50):
        with self.connect() as conn:
            return pd.read_sql_query("SELECT * FROM registro_operaciones ORDER BY id DESC LIMIT ?", conn, params=(limit,))
