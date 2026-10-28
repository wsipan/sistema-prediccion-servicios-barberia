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

def crear_cita(cliente_id, servicio, fecha_hora):
    """Crea una cita para un cliente y devuelve sus datos."""
    servicio = servicio.strip()
    fecha_hora = fecha_hora.strip()

    if not servicio or not fecha_hora:
        raise ValueError("El servicio y la fecha/hora son obligatorios.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO citas (cliente_id, servicio, fecha_hora, estado)
            VALUES (?, ?, ?, 'pendiente')
            """,
            (cliente_id, servicio, fecha_hora)
        )

        cita = connection.execute(
            """
            SELECT id, cliente_id, servicio, fecha_hora, estado, creado_en
            FROM citas
            WHERE id = ?
            """,
            (cursor.lastrowid,)
        ).fetchone()

        return dict(cita)


def obtener_citas_cliente(cliente_id):
    """Devuelve las citas de un cliente."""
    with get_connection() as connection:
        citas = connection.execute(
            """
            SELECT id, cliente_id, servicio, fecha_hora, estado, creado_en
            FROM citas
            WHERE cliente_id = ?
            ORDER BY fecha_hora ASC
            """,
            (cliente_id,)
        ).fetchall()

        return [dict(cita) for cita in citas]

def existe_cita_en_horario(fecha_hora):
    """
    Comprueba si ya existe una cita activa en la fecha y hora indicadas.
    """
    with get_connection() as connection:
        cita = connection.execute(
            """
            SELECT id
            FROM citas
            WHERE fecha_hora = ?
              AND estado IN ('pendiente', 'confirmada')
            LIMIT 1
            """,
            (fecha_hora,)
        ).fetchone()

        return cita is not None

def obtener_historial_servicios_cliente(cliente_id):
    """
    Obtiene cronológicamente los servicios de las citas
    válidas de un cliente para utilizarlos en el modelo ML.
    """
    with get_connection() as connection:
        citas = connection.execute(
            """
            SELECT servicio
            FROM citas
            WHERE cliente_id = ?
              AND estado IN ('pendiente', 'confirmada', 'completada')
            ORDER BY fecha_hora ASC
            """,
            (cliente_id,)
        ).fetchall()

        return [
            cita["servicio"]
            for cita in citas
        ]

if __name__ == "__main__":
    init_db()
    print(f"Base de datos creada en: {DATABASE_PATH}")