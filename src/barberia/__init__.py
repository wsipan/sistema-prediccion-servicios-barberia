
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel


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