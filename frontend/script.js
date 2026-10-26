(() => {
  "use strict";

  const $ = (selector) => document.querySelector(selector);

  const elements = {
    navLogin: $("#nav-login"),
    navRegister: $("#nav-register"),
    navLogout: $("#nav-logout"),
    greeting: $("#user-greeting"),

    heroRegister: $("#hero-register"),
    heroChat: $("#hero-chat"),

    chatToggle: $("#chat-toggle"),
    chatToggleIcon: $("#chat-toggle-icon"),
    chatWindow: $("#chat-window"),
    chatClose: $("#chat-close"),
    chatMessages: $("#chat-messages"),
    chatForm: $("#chat-form"),
    chatInput: $("#chat-input"),

    authOverlay: $("#auth-overlay"),
    authClose: $("#auth-close"),
    showLogin: $("#show-login"),
    showRegister: $("#show-register"),

    loginForm: $("#login-form"),
    registerForm: $("#register-form"),

    loginMessage: $("#login-message"),
    registerMessage: $("#register-message"),
    loginEmail: $("#login-correo"),
  };

  let authenticated = false;
  let pendingReservationMessage = null;
  let sendingMessage = false;

  // Mostrar mensajes de error o éxito en los formularios.
  function setMessage(element, message = "", kind = "") {
    element.textContent = message;
    element.className = `form-message${kind ? ` ${kind}` : ""}`;
  }

  // Leer los errores que devuelve FastAPI.
  function explainApiError(data, fallback) {
    if (typeof data?.detail === "string") {
      return data.detail;
    }

    if (Array.isArray(data?.detail)) {
      return data.detail
        .map((item) => item.msg || "Dato inválido")
        .join(" ");
    }

    return fallback;
  }

  // Función común para llamar a la API.
  async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
      credentials: "same-origin",
      ...options,
      headers: {
        ...(options.body
          ? { "Content-Type": "application/json" }
          : {}),
        ...(options.headers || {}),
      },
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(
        explainApiError(data, `La solicitud falló (${response.status}).`)
      );
    }

    return data;
  }

  // Actualizar los botones según la sesión.
  function updateAuthUI(user) {
    const isAuthenticated = Boolean(user);

    authenticated = isAuthenticated;

    elements.navLogin.hidden = isAuthenticated;
    elements.navRegister.hidden = isAuthenticated;
    elements.navLogout.hidden = !isAuthenticated;
    elements.greeting.hidden = !isAuthenticated;

    elements.greeting.textContent = isAuthenticated
      ? `Hola, ${(user.nombre || "cliente").split(" ")[0]}`
      : "";
  }

  // Abrir y cerrar el chat.
  function openChat() {
    elements.chatWindow.hidden = false;
    elements.chatToggle.setAttribute("aria-expanded", "true");
    elements.chatToggleIcon.textContent = "×";
    elements.chatInput.focus();
  }

  function closeChat() {
    elements.chatWindow.hidden = true;
    elements.chatToggle.setAttribute("aria-expanded", "false");
    elements.chatToggleIcon.textContent = "✦";
  }

  // Abrir y cerrar el modal de autenticación.
  function openAuth(screen = "login") {
    elements.authOverlay.hidden = false;
    showAuthScreen(screen);
    document.body.classList.add("modal-open");

    const target = screen === "register"
      ? $("#register-nombre")
      : elements.loginEmail;

    target.focus();
  }

  function closeAuth() {
    elements.authOverlay.hidden = true;
    document.body.classList.remove("modal-open");
  }

  // Cambiar entre el formulario de login y el de registro.
  function showAuthScreen(screen) {
    const login = screen === "login";

    elements.loginForm.hidden = !login;
    elements.registerForm.hidden = login;

    elements.showLogin.classList.toggle("active", login);
    elements.showRegister.classList.toggle("active", !login);

    elements.showLogin.setAttribute("aria-selected", String(login));
    elements.showRegister.setAttribute("aria-selected", String(!login));

    $("#auth-title").textContent = login
      ? "Tu cuenta, tu estilo"
      : "Crea tu cuenta";

    setMessage(elements.loginMessage);
    setMessage(elements.registerMessage);
  }

  // Agregar un mensaje al historial visible del chat.
  function addMessage(text, sender = "bot") {
    const wrapper = document.createElement("div");

    wrapper.className = sender === "user"
      ? "message user-message"
      : "message bot-message";

    const paragraph = document.createElement("p");
    paragraph.textContent = text;

    wrapper.appendChild(paragraph);
    elements.chatMessages.appendChild(wrapper);

    elements.chatMessages.scrollTop =
      elements.chatMessages.scrollHeight;
  }

  // Detección inicial de mensajes relacionados con una reserva.
  function isReservationIntent(message) {
    return /\b(reservar|reserva|reservas|agendar|agenda|cita|citas|disponibilidad)\b/i
      .test(message);
  }

  // Adaptarse al nombre del campo de respuesta del chatbot.
  function getChatReply(data) {
    return data.respuesta
      || data.response
      || data.reply
      || data.message
      || data.mensaje
      || data.answer
      || "Recibí tu mensaje, pero no encontré una respuesta del servidor.";
  }

  // Enviar mensajes al endpoint del chat existente.
  async function sendChatMessage(message, showUserMessage = true) {
    if (sendingMessage) return;

    sendingMessage = true;

    if (showUserMessage) {
      addMessage(message, "user");
    }

    const submitButton =
      elements.chatForm.querySelector("button[type='submit']");

    submitButton.disabled = true;

    try {
      const data = await apiRequest("/api/chat", {
        method: "POST",
        body: JSON.stringify({ message }),
      });

      addMessage(String(getChatReply(data)), "bot");
    } catch (error) {
      addMessage(
        `No pude conectar con el asistente: ${error.message}`,
        "bot"
      );
    } finally {
      sendingMessage = false;
      submitButton.disabled = false;
      elements.chatInput.focus();
    }
  }

  // Botones principales.
  elements.navLogin.addEventListener("click", () => {
    openAuth("login");
  });

  elements.navRegister.addEventListener("click", () => {
    openAuth("register");
  });

  elements.heroRegister.addEventListener("click", () => {
    openAuth("register");
  });

  elements.heroChat.addEventListener("click", () => {
    openChat();
  });

  elements.chatToggle.addEventListener("click", () => {
    if (elements.chatWindow.hidden) {
      openChat();
    } else {
      closeChat();
    }
  });

  elements.chatClose.addEventListener("click", closeChat);
  elements.authClose.addEventListener("click", closeAuth);

  elements.showLogin.addEventListener("click", () => {
    showAuthScreen("login");
  });

  elements.showRegister.addEventListener("click", () => {
    showAuthScreen("register");
  });

  document.querySelectorAll("[data-switch]").forEach((button) => {
    button.addEventListener("click", () => {
      showAuthScreen(button.dataset.switch);
    });
  });

  // Cerrar el modal al hacer clic fuera de su contenido.
  elements.authOverlay.addEventListener("click", (event) => {
    if (event.target === elements.authOverlay) {
      closeAuth();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape"
      && !elements.authOverlay.hidden
    ) {
      closeAuth();
    }
  });

  // REGISTRO DE CUENTA.
  elements.registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    setMessage(elements.registerMessage);

    const form = new FormData(elements.registerForm);

    const nombre = String(form.get("nombre") || "").trim();
    const correo = String(form.get("correo") || "").trim();
    const telefono = String(form.get("telefono") || "").trim();
    const password = String(form.get("password") || "");
    const confirmPassword =
      String(form.get("confirm_password") || "");

    if (password !== confirmPassword) {
      setMessage(
        elements.registerMessage,
        "Las contraseñas no coinciden.",
        "error"
      );
      return;
    }

    if (password.length < 8) {
      setMessage(
        elements.registerMessage,
        "La contraseña debe tener al menos 8 caracteres.",
        "error"
      );
      return;
    }

    const submitButton =
      elements.registerForm.querySelector("button[type='submit']");

    submitButton.disabled = true;
    submitButton.textContent = "Creando cuenta…";

    try {
      await apiRequest("/api/auth/registro", {
        method: "POST",
        body: JSON.stringify({
          nombre,
          correo,
          telefono,
          password,
        }),
      });

      // Después del registro, pasar al login.
      elements.loginEmail.value = correo;
      elements.registerForm.reset();

      showAuthScreen("login");

      setMessage(
        elements.loginMessage,
        "Cuenta creada. Ahora inicia sesión.",
        "success"
      );
    } catch (error) {
      setMessage(
        elements.registerMessage,
        error.message,
        "error"
      );
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Crear mi cuenta";
    }
  });

  // INICIO DE SESIÓN.
  elements.loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    setMessage(elements.loginMessage);

    const form = new FormData(elements.loginForm);
    const correo = String(form.get("correo") || "").trim();
    const password = String(form.get("password") || "");

    const submitButton =
      elements.loginForm.querySelector("button[type='submit']");

    submitButton.disabled = true;
    submitButton.textContent = "Ingresando…";

    try {
      await apiRequest("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ correo, password }),
      });

      // Consultar el usuario asociado a la sesión.
      let user;

      try {
        user = await apiRequest("/api/auth/me");
      } catch (_) {
        user = { nombre: correo.split("@")[0], correo };
      }

      updateAuthUI(user);
      elements.loginForm.reset();
      closeAuth();

      addMessage("Has iniciado sesión correctamente.", "bot");

      // Recuperar el mensaje de reserva pendiente.
      if (pendingReservationMessage) {
        const pending = pendingReservationMessage;
        pendingReservationMessage = null;

        addMessage(
          "Retomemos tu consulta. El registro real de citas debe estar habilitado en el sistema.",
          "bot"
        );

        await sendChatMessage(pending, false);
      }
    } catch (error) {
      setMessage(
        elements.loginMessage,
        error.message,
        "error"
      );
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Entrar a mi cuenta";
    }
  });

  // CERRAR SESIÓN.
  elements.navLogout.addEventListener("click", async () => {
    try {
      await apiRequest("/api/auth/logout", {
        method: "POST",
      });

      updateAuthUI(null);
      addMessage("Has cerrado sesión.", "bot");
    } catch (error) {
      window.alert(
        `No se pudo cerrar la sesión: ${error.message}`
      );
    }
  });

  // ENVÍO DE MENSAJES DEL CHAT.
  elements.chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = elements.chatInput.value.trim();

    if (!message || sendingMessage) return;

    elements.chatInput.value = "";
    openChat();

    // Si intenta reservar sin sesión, conservar el mensaje.
    if (isReservationIntent(message) && !authenticated) {
      addMessage(message, "user");

      pendingReservationMessage = message;

      addMessage(
        "Para continuar con una reserva, inicia sesión o crea una cuenta. Mantendré este mensaje mientras te identificas.",
        "bot"
      );

      openAuth("login");
      return;
    }

    await sendChatMessage(message, true);
  });

  // Comprobar si existe una sesión activa al cargar la página.
  async function checkSession() {
    try {
      const user = await apiRequest("/api/auth/me");
      updateAuthUI(user);
    } catch (_) {
      updateAuthUI(null);
    }
  }

  checkSession();
})();