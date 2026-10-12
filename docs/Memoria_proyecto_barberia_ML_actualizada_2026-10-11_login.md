# Memoria del proyecto: Sistema web para la predicción del servicio de barbería y gestión de citas

**Última actualización:** 2026-10-11  
**Estado:** registro básico de clientes probado en la API y en el formulario web. Próxima etapa: cuentas con contraseña, login y reservas protegidas, manteniendo la conversación del chat.

## 1. Contexto

- Curso: Sistemas Inteligentes y Machine Learning.
- Proyecto: sistema web para barbería con chatbot, registro de clientes, citas y futura predicción del servicio que probablemente elegirá un cliente.
- Título provisional: **Sistema web para la predicción del servicio de barbería y gestión de citas mediante aprendizaje automático**.
- Modelo ML candidato por evaluar: `DecisionTreeClassifier`.
- El usuario quiere avanzar paso a paso, entender los archivos y poder explicar/defender el proyecto.
- El usuario conoce HTML, CSS y JavaScript; explicar especialmente Python, FastAPI, SQLite y ML.
- Este archivo sirve como memoria de continuidad. Actualizarlo y compartirlo cuando se cierre una etapa o se acerque el límite de contexto.

## 2. Entorno

Carpeta local: `D:\\U\\Semestre_08\\MACHINE_LEARNING\\sistema-prediccion-servicios-barberia`

Repositorio GitHub: `sistema-prediccion-servicios-barberia`. Se usa Windows, VS Code y `.venv`.

Ejecutar desde la raíz:

```bash
python -m uvicorn src.barberia.main:app --reload
```

- Web: `http://127.0.0.1:8000`
- FastAPI docs: `http://127.0.0.1:8000/docs`

## 3. Estructura real conocida

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

**Importante:** `src/barberia/database.py` es un archivo, no una carpeta. No asumir una estructura distinta sin revisar el proyecto.

## 4. Estado de la base de datos

SQLite: `barberia.db` en la raíz.

Tablas verificadas:
- `clientes`: `id`, `nombre`, `telefono`, `correo`, `creado_en`.
- `citas`: `id`, `cliente_id`, `servicio`, `fecha_hora`, `estado`, `creado_en`.
- `sqlite_sequence`: tabla interna.

Esquema actual:
- `clientes.telefono` es `NOT NULL UNIQUE`.
- `clientes.correo` es opcional actualmente; no se ha confirmado que sea `UNIQUE`.
- No existe todavía columna para contraseña ni hash.
- `citas.cliente_id` referencia `clientes.id`.
- `creado_en DEFAULT CURRENT_TIMESTAMP` usa UTC en SQLite.
- La conexión activa `PRAGMA foreign_keys = ON`.

**No borrar ni recrear la base de datos para cambiar el esquema.** Preparar una migración compatible y explicar el impacto antes de aplicarla.

## 5. Backend y frontend existentes

`src/barberia/main.py` usa FastAPI, sirve `frontend/index.html`, monta los archivos estáticos en `/static` y expone `POST /api/chat`. El chatbot actual responde con reglas de palabras clave para saludos, servicios, horarios, reservas, cancelaciones y agradecimientos. **Preservar esta ruta y el chat existente.**

`src/barberia/database.py` contiene la conexión SQLite y las funciones de inicialización; se añadieron `buscar_cliente_por_telefono(telefono)` y `registrar_cliente(nombre, telefono, correo=None)`. El archivo completo más reciente no se ha revisado; comprobarlo antes de modificarlo.

`frontend/index.html` contiene el encabezado, el botón flotante, la ventana del chat y un formulario de registro básico de cliente.

`frontend/script.js` abre/cierra el chat, añade mensajes, envía mensajes a `/api/chat` y envía el formulario de registro a `/api/clientes`.

`frontend/styles.css` contiene los estilos del sitio, el chat y el formulario.

### Pruebas confirmadas

En `/docs`, `POST /api/clientes` con datos de prueba devolvió `201 Created` la primera vez; el registro apareció en el visor SQLite. Repetir el teléfono devolvió `409 Conflict`.

Datos de prueba usados:

```json
{
  "nombre": "Cliente Prueba",
  "telefono": "900123456",
  "correo": "prueba@example.com"
}
```

El usuario confirmó que el formulario web también registra correctamente. Ese teléfono ya existe en la base de datos; no tratarlo como nuevo.

## 6. Nueva decisión: chat libre, reserva con login obligatorio

Flujo deseado:
1. El visitante puede conversar con el chatbot sin iniciar sesión.
2. Puede consultar servicios, precios y horarios como visitante.
3. Al solicitar una cita, el sistema exige iniciar sesión o crear una cuenta.
4. Login/registro aparece en una ventana modal dentro de la misma página, sin redirigir ni recargarla.
5. La conversación no se pierde mientras se autentica.
6. Tras autenticarse, la conversación y el flujo de reserva continúan donde quedaron.
7. También debe existir una opción para iniciar sesión antes de abrir el chat.
8. La cita guardada se asocia al `cliente_id` de la cuenta autenticada en backend; no confiar en un ID de cliente enviado libremente desde el navegador.

### Campos de cuenta

Registro:
- Nombre completo.
- Correo electrónico.
- Teléfono.
- Contraseña.

Login:
- Correo electrónico.
- Contraseña.

El correo debe ser único. El teléfono debe seguir evitando duplicados. La cuenta autenticada debe verificarse en el backend para cualquier endpoint protegido.

### Seguridad obligatoria

- Nunca guardar contraseñas en texto plano: guardar un hash seguro, por ejemplo Argon2 mediante una biblioteca adecuada.
- Verificar contraseñas con la función de verificación de la biblioteca.
- Nunca devolver el hash en respuestas de API.
- No guardar contraseñas en `localStorage`, el historial del chat, JavaScript ni el repositorio.
- No guardar credenciales de correo ni otros secretos en el código; usar variables de entorno y excluir `.env` de Git.
- Elegir antes de implementar un mecanismo de autenticación claro (sesión/cookie segura o tokens validados). No improvisar un mecanismo propio.
- Validar los datos también en el backend. Ocultar un botón en frontend no protege una API.
- Usar datos ficticios en pruebas.

### Conservar el chat

No redirigir ni recargar la página para mostrar el login. Mostrar un modal y mantener el historial de mensajes en la página. Guardar también el estado de la reserva pendiente (por ejemplo, intención de reservar y servicio elegido) para continuar preguntando fecha y hora después de iniciar sesión.

Si más adelante se requiere conservar el chat tras actualizar/cerrar la página, evaluar persistencia adicional. Nunca guardar contraseñas en el estado persistente del navegador.

## 7. Próximos pasos técnicos, en orden

1. Revisar el contenido actual de `database.py`, `main.py`, `index.html`, `script.js` y `styles.css`.
2. Diseñar una migración de SQLite que permita cuentas: correo requerido y único para nuevas cuentas y una columna para el hash de contraseña. No borrar datos. Los clientes antiguos, incluido `Cliente Prueba`, no tienen contraseña: tendrán que establecer una antes de poder iniciar sesión; no asignar contraseñas predeterminadas.
3. Implementar registro de cuenta en backend, validando correo/teléfono duplicados y guardando el hash.
4. Implementar login y sesión/autenticación validada por backend.
5. Añadir controles visibles “Iniciar sesión” y “Crear cuenta” al frontend, preferiblemente con modal sin recarga.
6. Mantener el chat público; si el usuario solicita reservar sin sesión, mostrar el modal sin perder historial ni datos de reserva.
7. Después del login/registro, continuar el flujo de reserva.
8. Crear el endpoint de citas protegido: verificar sesión, obtener el cliente autenticado del contexto de autenticación, validar servicio, fecha, hora y disponibilidad, y asociar correctamente `cliente_id`.
9. Probar chat anónimo, registro, login válido/inválido, duplicados, reserva sin sesión, conservación del chat, creación de cita y cierre de sesión.
10. Luego implementar recordatorios por correo y el modelo de ML.

## 8. Recordatorios por correo (futuro)

Todavía no están implementados. Primero estabilizar cuentas y citas. Luego:
- Definir cuándo se envían y qué ocurre si una cita cambia o se cancela.
- Enviar desde backend mediante SMTP o proveedor de correo.
- Guardar credenciales en variables de entorno, nunca en frontend ni Git.
- En desarrollo, usar pruebas o destinatarios controlados.
- No indicar que un correo se envió hasta recibir confirmación del proveedor.

## 9. Pendiente: hora de Lima

El usuario observó que `creado_en` no coincide con la hora local. La causa probable es `CURRENT_TIMESTAMP` en SQLite, que genera UTC; Perú usa UTC−5. No se ha implementado la corrección.

Preferencia técnica: guardar timestamps en UTC y convertirlos a `America/Lima` al mostrarlos. Aplicar una política consistente a clientes y citas. No modificar registros históricos sin explicar el efecto.

## 10. ML futuro

El modelo aún no está implementado. Primero estabilizar registro, autenticación y citas para estructurar datos. Se pueden usar datos sintéticos claramente identificados como ficticios. Evaluar el árbol de decisión u otro modelo visto en clase y explicar variables, entrenamiento, evaluación y limitaciones.

## 11. Preferencias de trabajo

- Responder en español.
- Avanzar paso a paso y explicar el propósito de cada archivo/cambio.
- No reescribir todo el proyecto cuando basta un cambio localizado.
- Revisar archivos reales antes de proponer reemplazos extensos.
- Preservar el chat y `POST /api/chat`.
- No asumir carpetas no confirmadas.
- No borrar la base de datos ni registros como solución rápida.
- Actualizar y compartir este Markdown al cerrar etapas o cuando se acerque el límite de contexto.
