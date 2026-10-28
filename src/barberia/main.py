import os
import re
from datetime import datetime

import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from fastapi import Request, Response
from pwdlib import PasswordHash
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature, SignatureExpired

from .ml.predecir import predecir_servicio

# Importar base de datos
from .database import (
    buscar_cliente_por_correo,
    buscar_cliente_por_telefono,
    registrar_cliente,
    crear_cita,
    obtener_citas_cliente,
    existe_cita_en_horario,
    obtener_historial_servicios_cliente
)

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = FastAPI(
    title="Sistema de Barbería",
    description="API del asistente virtual de la barbería",
    version="0.1.0",
)

# Servir los archivos CSS y JavaScript
app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static",
)


# Estructura del mensaje recibido
class ChatRequest(BaseModel):
    message: str

class ClienteRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    telefono: str = Field(min_length=1, max_length=20)
    correo: str | None = None

class RegistroCuentaRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    correo: str = Field(min_length=5, max_length=254)
    telefono: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    correo: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class CrearCitaRequest(BaseModel):
    servicio: str = Field(min_length=1, max_length=100)
    fecha_hora: datetime

password_hasher = PasswordHash.recommended()

SESSION_COOKIE = "barberia_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 días


def get_session_serializer():
    secret = os.getenv("BARBERIA_SESSION_SECRET")

    if not secret:
        raise HTTPException(
            status_code=500,
            detail="La autenticación no está configurada en el servidor.",
        )

    return URLSafeTimedSerializer(
        secret_key=secret,
        salt="barberia-auth-v1",
    )


def obtener_cliente_autenticado(request: Request):
    """Verifica la cookie y devuelve el cliente autenticado."""
    token = request.cookies.get(SESSION_COOKIE)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Debes iniciar sesión para continuar.",
        )

    try:
        datos = get_session_serializer().loads(
            token,
            max_age=SESSION_MAX_AGE,
        )
        cliente_id = datos.get("cliente_id")

        if not isinstance(cliente_id, int):
            raise HTTPException(
                status_code=401,
                detail="La sesión no es válida.",
            )

    except (BadSignature, SignatureExpired):
        raise HTTPException(
            status_code=401,
            detail="La sesión ha expirado o no es válida.",
        )

    from .database import get_connection

    with get_connection() as connection:
        cliente = connection.execute(
            """
            SELECT id, nombre, telefono, correo, creado_en
            FROM clientes
            WHERE id = ?
            """,
            (cliente_id,),
        ).fetchone()

    if not cliente:
        raise HTTPException(
            status_code=401,
            detail="La cuenta ya no existe.",
        )

    return dict(cliente)

# Página principal
@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


# Primera ruta de prueba del chatbot
@app.post("/api/chat")
def chat(request: ChatRequest):
    text = request.message.lower().strip()

    # Cancelación antes de reserva
    if "cancelar" in text or "anular" in text:
        response = (
            "Puedo ayudarte a iniciar una cancelación. "
            "Todavía no podemos modificar citas reales."
        )

    elif any(word in text for word in [
        "reservar", "agendar", "cita", "disponibilidad"
    ]):
        response = (
            "¡Claro! Para preparar una reserva necesitaremos "
            "el servicio, la fecha y la hora. "
            "Todavía no podemos guardar citas."
        )

    elif any(word in text for word in [
        "servicio", "corte", "barba", "precio", "precios"
    ]):
        response = (
            "Próximamente podremos consultar el catálogo "
            "real de servicios y sus precios."
        )

    elif any(word in text for word in [
        "horario", "abren", "cierran", "atienden"
    ]):
        response = (
            "Todavía no hemos configurado los horarios reales "
            "de la barbería."
        )

    elif "gracias" in text:
        response = "¡Con gusto! ¿Necesitas algo más?"

    elif any(word in text for word in [
        "hola", "buenos dias", "buenas tardes", "buenas noches"
    ]):
        response = (
            "¡Hola! Bienvenido a nuestra barbería. "
            "¿En qué puedo ayudarte?"
        )

    else:
        response = (
            "Todavía no reconozco esa consulta. "
            "Puedes preguntar por servicios, horarios o reservas."
        )

    return {"response": response}

@app.post("/api/clientes", status_code=201)
def crear_cliente(request: ClienteRequest):
    nombre = request.nombre.strip()
    telefono = request.telefono.strip()
    correo = request.correo.strip() if request.correo else None

    if not nombre or not telefono:
        raise HTTPException(
            status_code=400,
            detail="El nombre y el teléfono son obligatorios.",
        )

    # Comprobar si el teléfono ya está registrado
    cliente_existente = buscar_cliente_por_telefono(telefono)

    if cliente_existente:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un cliente registrado con ese teléfono.",
        )

    try:
        cliente = registrar_cliente(nombre, telefono, correo)
        return {
            "mensaje": "Cliente registrado correctamente.",
            "cliente": cliente,
        }

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="No se pudo registrar: el teléfono ya existe.",
        )

@app.post("/api/auth/registro", status_code=201)
def registrar_cuenta(request: RegistroCuentaRequest):
    nombre = request.nombre.strip()
    correo = request.correo.strip().lower()
    telefono = request.telefono.strip()

    if not nombre or not telefono:
        raise HTTPException(
            status_code=400,
            detail="El nombre y el teléfono son obligatorios.",
        )

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
        raise HTTPException(
            status_code=422,
            detail="Introduce un correo electrónico válido.",
        )

    if buscar_cliente_por_correo(correo):
        raise HTTPException(
            status_code=409,
            detail="Ya existe una cuenta con ese correo.",
        )

    if buscar_cliente_por_telefono(telefono):
        raise HTTPException(
            status_code=409,
            detail=(
                "Ese teléfono ya está registrado. "
                "No se modificaron los datos existentes."
            ),
        )

    password_hash = password_hasher.hash(request.password)

    try:
        cliente = registrar_cliente(
            nombre=nombre,
            telefono=telefono,
            correo=correo,
            password_hash=password_hash,
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="El correo o el teléfono ya están registrados.",
        )

    return {
        "mensaje": "Cuenta creada correctamente. Ya puedes iniciar sesión.",
        "cliente": cliente,
    }


@app.post("/api/auth/login")
def iniciar_sesion(request: LoginRequest, response: Response):
    correo = request.correo.strip().lower()
    cliente = buscar_cliente_por_correo(correo)

    # Mensaje genérico para no revelar si un correo está registrado.
    if not cliente or not cliente.get("password_hash"):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos.",
        )

    if not password_hasher.verify(
        request.password,
        cliente["password_hash"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos.",
        )

    token = get_session_serializer().dumps(
        {"cliente_id": cliente["id"]}
    )

    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        secure=os.getenv("BARBERIA_COOKIE_SECURE", "0") == "1",
        samesite="lax",
        path="/",
    )

    return {
        "mensaje": "Sesión iniciada correctamente.",
        "cliente": {
            "id": cliente["id"],
            "nombre": cliente["nombre"],
            "correo": cliente["correo"],
        },
    }


@app.get("/api/auth/me")
def consultar_sesion(request: Request):
    cliente = obtener_cliente_autenticado(request)
    return {"autenticado": True, "cliente": cliente}


@app.post("/api/auth/logout")
def cerrar_sesion(response: Response):
    response.delete_cookie(
        key=SESSION_COOKIE,
        httponly=True,
        secure=os.getenv("BARBERIA_COOKIE_SECURE", "0") == "1",
        samesite="lax",
        path="/",
    )
    return {"mensaje": "Sesión cerrada correctamente."}

@app.post("/api/citas", status_code=201)
def crear_cita_endpoint(
    datos: CrearCitaRequest,
    request: Request
):
    cliente = obtener_cliente_autenticado(request)

    ahora = datetime.now()

    if datos.fecha_hora <= ahora:
        raise HTTPException(
            status_code=400,
            detail="La fecha y hora de la cita deben ser futuras."
        )

    fecha_hora = datos.fecha_hora.isoformat()

    if existe_cita_en_horario(fecha_hora):
        raise HTTPException(
            status_code=409,
            detail="Ese horario ya se encuentra reservado."
        )

    cita = crear_cita(
        cliente_id=cliente["id"],
        servicio=datos.servicio,
        fecha_hora=fecha_hora
    )

    return cita

@app.get("/api/citas")
def listar_mis_citas(request: Request):
    cliente = obtener_cliente_autenticado(request)

    return obtener_citas_cliente(cliente["id"])

@app.get("/api/prediccion-servicio")
def obtener_prediccion_servicio(request: Request):
    """
    Predice el próximo servicio probable del
    cliente autenticado utilizando su historial.
    """

    cliente = obtener_cliente_autenticado(request)

    historial = obtener_historial_servicios_cliente(
        cliente["id"]
    )

    if len(historial) < 2:
        return {
            "prediccion_disponible": False,
            "motivo": "Historial insuficiente",
            "cantidad_citas_utilizadas": len(historial),
        }

    try:
        resultado = predecir_servicio(
            historial
        )

    except ValueError as error:
        return {
            "prediccion_disponible": False,
            "motivo": str(error),
            "cantidad_citas_utilizadas": len(historial),
        }

    return {
        "prediccion_disponible": True,
        "servicio_predicho": resultado[
            "servicio_predicho"
        ],
        "probabilidad": resultado[
            "probabilidad"
        ],
        "probabilidades": resultado[
            "probabilidades"
        ],
        "cantidad_citas_utilizadas": resultado[
            "cantidad_citas_utilizadas"
        ],
    }