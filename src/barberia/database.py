import sqlite3
from pathlib import Path

# Carpeta principal del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Archivo donde SQLite guardará los datos
DATABASE_PATH = PROJECT_ROOT / "barberia.db"


def get_connection():
    """Abre una conexión con la base de datos."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    """Crea las tablas si todavía no existen."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT NOT NULL UNIQUE,
                correo TEXT,
                creado_en TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS citas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                servicio TEXT NOT NULL,
                fecha_hora TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'pendiente',
                creado_en TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id)
                    REFERENCES clientes(id)
            )
        """)

if __name__ == "__main__":
    init_db()
    print(f"Base de datos creada en: {DATABASE_PATH}")