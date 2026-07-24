import sqlite3
from datetime import datetime

class TradingDatabase:
    def __init__(self, db_name="trading_system.db"):
        self.db_name = db_name
        self.crear_tablas()

    def conectar(self):
        return sqlite3.connect(self.db_name)

    def crear_tablas(self):
        conn = self.conectar()
        cursor = conn.cursor()
        
        # Usamos un nombre de tabla nuevo para evitar bloqueos de archivos viejos de OneDrive
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registro_operaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                estrategia TEXT NOT NULL,
                justificacion TEXT NOT NULL,
                bloqueado INTEGER NOT NULL,
                sesgo_detectado TEXT,
                fecha TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()

    def registrar_consulta(self, ticker, estrategia, justificacion, bloqueado, sesgo):
        conn = self.conectar()
        cursor = conn.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO registro_operaciones (ticker, estrategia, justificacion, bloqueado, sesgo_detectado, fecha)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ticker, estrategia, justificacion, 1 if bloqueado else 0, sesgo, fecha_actual))
        
        conn.commit()
        conn.close()
        print("\n💾 Registro guardado con éxito en la base de datos local (trading_system.db).")
