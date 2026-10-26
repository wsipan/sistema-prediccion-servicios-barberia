# Memoria del proyecto — Sistema de Barbería con Chatbot y Machine Learning

**Última actualización:** 26/10/2026

## Estado actual confirmado

El proyecto conserva el diseño del frontend, la base SQLite y el chatbot. La autenticación básica ya está funcionando de extremo a extremo.

### Funcionalidades confirmadas
- Registro de cuentas: funcionando.
- Contraseñas almacenadas mediante hash Argon2 con `pwdlib`.
- Login: funcionando.
- `GET /api/auth/me` reconoce al usuario después del login.
- La sesión se conserva después de recargar la página.
- Logout: funcionando.
- Después del logout, `/api/auth/me` vuelve a responder como usuario no autenticado (`401`).
- CSS servido correctamente.
- Chat accesible sin iniciar sesión.
- Base de datos existente conservada.

## Entorno funcional confirmado

- Python 3.13.5
- Git 2.52.0.windows.1
- FastAPI 0.143.0
- Uvicorn 0.54.0
- Pydantic 2.14.0
- Starlette 1.7.0
- pwdlib 0.3.1
- argon2-cffi 25.1.0
- itsdangerous 2.2.0
- python-dotenv 1.2.4
- NumPy 2.5.3
- pandas 2.3.3
- scikit-learn 1.9.1
- SciPy 1.18.1
- pytest 8.4.2

El `requirements.txt` del repositorio debe obtenerse del entorno funcional mediante:

```powershell
python -m pip freeze > requirements.txt
```

## Estructura conocida

```text
sistema-prediccion-servicios-barberia/
├── barberia.db
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── src/
    └── barberia/
        ├── main.py
        └── database.py
```

## Base de datos

SQLite: `barberia.db`.

Tablas conocidas:
- `clientes`
- `citas`
- `sqlite_sequence`

`clientes` contiene:
`id`, `nombre`, `telefono`, `correo`, `creado_en`, `password_hash`.

Existe el índice único `idx_clientes_correo_unico`; el teléfono también es único.

No borrar ni recrear `barberia.db` para corregir errores.

Se corrigió la conexión para devolver `sqlite3.Row`:

```python
def get_connection():
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
```

Esto solucionó el error de `dict(cliente)`.

También se diagnosticó `sqlite3.OperationalError: database is locked`. Para comprobar escritura:

```powershell
python -c "import sqlite3; c=sqlite3.connect('barberia.db', timeout=5); c.execute('BEGIN IMMEDIATE'); print('Base de datos disponible para escritura'); c.rollback(); c.close()"
```

## Autenticación

Rutas:

```text
POST /api/auth/registro
POST /api/auth/login
GET  /api/auth/me
POST /api/auth/logout
```

Flujo confirmado:

```text
Registro → hash Argon2 → cliente almacenado
Login → búsqueda por correo → verificación de contraseña
→ token de sesión firmado → cookie
→ /api/auth/me reconoce usuario
→ recarga conserva sesión
→ logout elimina sesión
→ /api/auth/me vuelve a 401
```

Nunca devolver `password_hash` al frontend.

### Secreto de sesión

Antes de iniciar Uvicorn en PowerShell:

```powershell
$env:BARBERIA_SESSION_SECRET = python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Comprobar sin revelar el secreto:

```powershell
if ($env:BARBERIA_SESSION_SECRET) { "Secret configurado correctamente" } else { "Secret NO configurado" }
```

Iniciar Uvicorn en esa misma terminal:

```powershell
python -m uvicorn src.barberia.main:app --reload
```

No subir el secreto a Git.

## Instalación para otro integrante

```powershell
git clone URL_DEL_REPOSITORIO
cd sistema-prediccion-servicios-barberia

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check

$env:BARBERIA_SESSION_SECRET = python -c "import secrets; print(secrets.token_urlsafe(48))"

python -m py_compile src/barberia/main.py src/barberia/database.py
python -m uvicorn src.barberia.main:app --reload
```

URLs:

```text
Aplicación: http://127.0.0.1:8000
Swagger:    http://127.0.0.1:8000/docs
CSS:        http://127.0.0.1:8000/static/styles.css
```

Si PowerShell impide activar `.venv`:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Base compartida por el equipo

El usuario indicó que quiere que todos los integrantes trabajen con la misma base de datos. La decisión arquitectónica queda **aplazada**.

Opciones a evaluar más adelante:
1. distribuir una misma `barberia.db` inicial mediante el repositorio;
2. migrar posteriormente a una base central (por ejemplo PostgreSQL) si se requieren datos compartidos en tiempo real.

No realizar esta migración todavía.

## Frontend

El diseño fue recuperado después de una regresión. Regla de trabajo:

**No reemplazar archivos completos del frontend para corregir problemas puntuales.**

Hacer cambios localizados en:
- `index.html`
- `styles.css`
- `script.js`

El chat permanece público. Al reservar, el sistema debe exigir autenticación sin perder innecesariamente el contexto de la conversación.

## Próxima etapa: citas

Con autenticación básica confirmada, el siguiente bloque de trabajo es implementar el flujo real de reservas.

Objetivos:
1. Revisar el esquema actual de `citas`.
2. Crear funciones de acceso a datos para citas.
3. Crear endpoints protegidos de citas.
4. Asociar siempre una cita al usuario autenticado desde la sesión, no confiar en un `cliente_id` enviado por el navegador.
5. Permitir crear y consultar citas.
6. Integrar el chat con el flujo de reserva.
7. Conservar el contexto del chat cuando se requiera login.
8. Añadir cancelación/reprogramación posteriormente.

Esquema conocido de `citas`:
- `id`
- `cliente_id`
- `servicio`
- `fecha_hora`
- `estado`
- `creado_en`

Antes de escribir código nuevo se debe inspeccionar el esquema real con `PRAGMA table_info(citas)`.

## Pendientes posteriores

- Gestión completa de citas.
- Validación de disponibilidad/horarios.
- Recordatorios por correo.
- Recuperación de contraseña.
- Rate limiting y endurecimiento de seguridad para producción.
- Decisión sobre base de datos compartida.
- Dataset histórico de servicios.
- Preparación, entrenamiento y evaluación del modelo de Machine Learning.
- Integración de la predicción con FastAPI y el frontend.

El módulo ML debe construirse después de disponer de suficientes citas reales o de un dataset de desarrollo claramente identificado como sintético.
