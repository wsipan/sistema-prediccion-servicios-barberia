import sqlite3
from pathlib import Path

# Carpeta principal del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Archivo donde SQLite guardará los datos
DATABASE_PATH = PROJECT_ROOT / "barberia.db"

def get_connection():
    """Abre una conexión con la base de datos."""
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def init_db():
    """Crea las tablas si todavía no existen."""
    with get_connection() as connection:
        columnas = {
            fila[1]
            for fila in connection.execute(
                "PRAGMA table_info(clientes)"
            )
        }

        # Añadirla únicamente si falta.
        if "password_hash" not in columnas:
            connection.execute(
                "ALTER TABLE clientes ADD COLUMN password_hash TEXT"
            )

        # Evitar correos duplicados ignorando mayúsculas y espacios
        # al principio o al final.
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_clientes_correo_unico
            ON clientes(LOWER(TRIM(correo)))
            WHERE correo IS NOT NULL AND TRIM(correo) <> ''
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


def buscar_cliente_por_correo(correo):
    """Busca una cuenta por correo, ignorando mayúsculas y espacios."""
    correo = correo.strip().lower()

    with get_connection() as connection:
        cliente = connection.execute(
            """
            SELECT id, nombre, telefono, correo, creado_en, password_hash
            FROM clientes
            WHERE LOWER(TRIM(correo)) = ?
            """,
            (correo,)
        ).fetchone()

        return dict(cliente) if cliente else None


def registrar_cliente(nombre, telefono, correo=None, password_hash=None):
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
            INSERT INTO clientes (nombre, telefono, correo, password_hash)
            VALUES (?, ?, ?, ?)
            """,
            (nombre, telefono, correo, password_hash)
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