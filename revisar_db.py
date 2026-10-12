import sqlite3
from pathlib import Path

# Ubicación de la base de datos
ruta_db = Path(__file__).resolve().parent / "barberia.db"

conexion = sqlite3.connect(ruta_db)
cursor = conexion.cursor()

# Consultar las tablas existentes
cursor.execute("PRAGMA table_list")
tablas = cursor.fetchall()

print("Base de datos:", ruta_db)
print("\nTablas encontradas:")

for tabla in tablas:
    nombre = tabla[1]

    if nombre not in ("sqlite_schema", "sqlite_temp_schema"):
        print(f"\nTabla: {nombre}")

        cursor.execute(f'PRAGMA table_info("{nombre}")')

        for columna in cursor.fetchall():
            print(f"  - {columna[1]} (tipo: {columna[2]})")

conexion.close()