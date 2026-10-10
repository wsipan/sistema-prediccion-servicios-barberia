
const chatToggle = document.getElementById("chat-toggle");
const chatWindow = document.getElementById("chat-window");
const chatClose = document.getElementById("chat-close");

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");

// Abrir y cerrar el chat
function openChat() {
    chatWindow.hidden = false;
    chatToggle.setAttribute("aria-expanded", "true");
    chatInput.focus();
}

function closeChat() {
    chatWindow.hidden = true;
    chatToggle.setAttribute("aria-expanded", "false");
}

chatToggle.addEventListener("click", () => {
    if (chatWindow.hidden) {
        openChat();
    } else {
        closeChat();
    }
});

chatClose.addEventListener("click", closeChat);

// Agregar mensajes a la conversación
function addMessage(text, sender) {
    const message = document.createElement("div");

    message.classList.add("message", `${sender}-message`);
    message.textContent = text;

    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Normalizar texto para reconocer distintas formas de escribir
function normalizeText(text) {
    return text
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[¿?¡!.,;:]/g, "")
        .trim();
}

// Detectar la intención del usuario y generar una respuesta
function getBotResponse(message) {
    const text = normalizeText(message);

    if (
        text.includes("hola") ||
        text.includes("buenos dias") ||
        text.includes("buenas tardes") ||
        text.includes("buenas noches")
    ) {
        return "¡Hola! Bienvenido a nuestra barbería. ¿Qué te gustaría hacer?";
    }

    if (
        text.includes("servicio") ||
        text.includes("corte") ||
        text.includes("barba") ||
        text.includes("precio") ||
        text.includes("precios")
    ) {
        return "Puedes consultar nuestros servicios de corte de cabello, arreglo de barba y corte más barba. Próximamente conectaremos este chat con el catálogo y los precios reales de la barbería.";
    }

    if (
        text.includes("reservar") ||
        text.includes("agendar") ||
        text.includes("cita") ||
        text.includes("disponibilidad")
    ) {
        return "¡Claro! Vamos a preparar tu reserva. Primero necesitaremos conocer el servicio que deseas, la fecha y la hora. En esta versión todavía no podemos confirmar ni guardar citas.";
    }

    if (
        text.includes("cancelar") ||
        text.includes("anular")
    ) {
        return "Puedo ayudarte a iniciar una cancelación. Cuando conectemos la base de datos, verificaremos tu cita antes de modificarla.";
    }

    if (
        text.includes("horario") ||
        text.includes("abren") ||
        text.includes("cierran") ||
        text.includes("atienden")
    ) {
        return "Todavía no tenemos configurados los horarios reales de atención. Más adelante consultaremos el horario de la barbería desde el backend.";
    }

    if (
        text.includes("gracias") ||
        text.includes("muchas gracias")
    ) {
        return "¡Con gusto! Estoy aquí para ayudarte. ¿Necesitas algo más?";
    }

    return "No he identificado tu consulta todavía. Puedes preguntarme por servicios, precios, horarios o reservas.";
}

// Enviar el mensaje

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const text = chatInput.value.trim();

    if (!text) return;

    addMessage(text, "user");

    chatInput.value = "";
    chatInput.disabled = true;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: text
            })
        });

        if (!response.ok) {
            throw new Error("Error al consultar el asistente");
        }

        const data = await response.json();

        addMessage(data.response, "bot");

    } catch (error) {
        console.error("Error de comunicación:", error);

        addMessage(
            "No pude comunicarme con el servidor. Inténtalo nuevamente.",
            "bot"
        );
    } finally {
        chatInput.disabled = false;
        chatInput.focus();
    }
});