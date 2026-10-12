import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


from .database import (
    buscar_cliente_por_telefono,
    registrar_cliente,
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