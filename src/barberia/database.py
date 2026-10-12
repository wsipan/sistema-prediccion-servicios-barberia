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

def buscar_cliente_por_telefono(telefono):
    """Busca un cliente por su número de teléfono."""
    telefono = telefono.strip()

    with get_connection() as connection:
        connection.row_factory = sqlite3.Row

        cliente = connection.execute(
            """
            SELECT id, nombre, telefono, correo, creado_en
            FROM clientes
            WHERE telefono = ?
            """,
            (telefono,)
        ).fetchone()

        return dict(cliente) if cliente else None


def registrar_cliente(nombre, telefono, correo=None):
    """Registra un cliente y devuelve sus datos."""
    nombre = nombre.strip()
    telefono = telefono.strip()
    correo = correo.strip() if correo and correo.strip() else None

    if not nombre or not telefono:
        raise ValueError("El nombre y el teléfono son obligatorios.")

    with get_connection() as connection:
        connection.row_factory = sqlite3.Row

        cursor = connection.execute(
            """
            INSERT INTO clientes (nombre, telefono, correo)
            VALUES (?, ?, ?)
            """,
            (nombre, telefono, correo)
        )

        cliente = connection.execute(
            """
            SELECT id, nombre, telefono, correo, creado_en
            FROM clientes
            WHERE id = ?
            """,
            (cursor.lastrowid,)
        ).fetchone()

        return dict(cliente)

if __name__ == "__main__":
    init_db()
    print(f"Base de datos creada en: {DATABASE_PATH}")