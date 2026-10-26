# Memoria del proyecto: Sistema web para la predicción del servicio de barbería y gestión de citas

**Última actualización:** 2026-10-23  
**Estado:** base de datos existente preservada; migración de autenticación confirmada en la comprobación previa; interfaz de registro/login/chat preparada en los tres archivos incluidos en este paquete. La integración y las pruebas locales aún están pendientes. El backend presenta un error Pydantic por la ubicación/indentación de `password_hasher`.

## Proyecto y entorno

Ruta local: `D:\U\Semestre_08\MACHINE_LEARNING\sistema-prediccion-servicios-barberia`. Se trabaja en Windows, VS Code y `.venv`.

```text
sistema-prediccion-servicios-barberia/
├── barberia.db
├── frontend/index.html
├── frontend/styles.css
├── frontend/script.js
└── src/barberia/{main.py,database.py}
```

`database.py` es un archivo, no una carpeta. Arranque desde la raíz:

```powershell
python -m uvicorn src.barberia.main:app --reload
```

Web: `http://127.0.0.1:8000`; documentación: `http://127.0.0.1:8000/docs`.

## Base de datos

SQLite `barberia.db` está en la raíz. Tablas de negocio: `clientes` y `citas`. En la comprobación anterior había 2 clientes; la migración agregó `password_hash` y el índice único `idx_clientes_correo_unico`. No borrar ni recrear la DB. Teléfono es único; los registros antiguos sin hash no podrán entrar hasta contar con un flujo seguro para crear contraseña. La cuenta de prueba `Cliente Prueba`, teléfono `900123456`, correo `prueba@example.com`, puede estar ocupada.

Consulta de usuarios desde la raíz:

```powershell
python -c "import sqlite3; conn=sqlite3.connect('barberia.db'); print(*conn.execute('SELECT id, nombre, telefono, correo, creado_en FROM clientes').fetchall(), sep='\n'); conn.close()"
```

## Backend y error actual

El chatbot existente `POST /api/chat` usa reglas/keywords; aún no es un modelo ML. Dependencias de auth instaladas/indicadas: `pwdlib[argon2]` e `itsdangerous`. La variable de entorno prevista para firmar sesiones es `BARBERIA_SESSION_SECRET`.

Error más reciente:
`PydanticUserError: A non-annotated attribute was detected: password_hasher = <pwdlib._hash.PasswordHash ...>`.

Causa probable: `password_hasher = PasswordHash.recommended()` está indentado dentro de una clase Pydantic (`BaseModel`). Debe quedar al nivel superior del módulo, fuera de todas las clases. Corregir antes de probar interfaz y ejecutar:

```powershell
python -m py_compile src/barberia/main.py src/barberia/database.py
python -m uvicorn src.barberia.main:app --reload
```

Rutas de autenticación que el frontend espera: `POST /api/auth/registro`, `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout`. Hay que confirmar que existen y que devuelven los datos esperados antes de considerar funcional el login. En producción se requiere HTTPS y cookie `Secure`; también falta evaluar protección CSRF y limitación de intentos.

## Interfaz incluida en este paquete

- `index.html`: página principal, navegación, tarjetas de servicios, chat y modal de autenticación.
- `styles.css`: diseño adaptable para escritorio y móvil.
- `script.js`: alternancia entre login/registro, envío a las rutas de autenticación, comprobación de sesión, logout y chat.
- Registro: nombre, correo obligatorio, teléfono, contraseña y confirmación.
- Login: correo y contraseña.
- El chat sigue siendo público. Si un visitante escribe una intención de reserva, el frontend conserva el mensaje en memoria mientras abre el login; tras autenticarse, vuelve a enviarlo al chat.

**Antes de copiar los archivos al proyecto:** guardar una copia de `frontend/index.html`, `frontend/styles.css` y `frontend/script.js`. Estos archivos se prepararon aquí y aún no se han ejecutado contra el backend local. El JS tolera varias claves de respuesta (`respuesta`, `response`, `reply`, `mensaje`, `message`, `answer`); revisar la respuesta real de `/api/chat` si aparece texto de respaldo.

## Límites importantes

- El frontend no registra citas por sí mismo. No afirmar que una reserva quedó guardada hasta que exista un endpoint backend que la persista y confirme.
- La API de citas futura debe verificar sesión en backend y asociar `cliente_id` al usuario autenticado; ocultar botones no es seguridad.
- No guardar contraseñas en `localStorage` ni en el chat.
- Pedir correo no significa que haya recordatorios: todavía no están implementados.
- La detección de intención de reserva es aproximada y puede detectar preguntas informativas con la palabra “cita”.
- La corrección de hora de Lima sigue pendiente; SQLite `CURRENT_TIMESTAMP` usa UTC, conviene convertir a `America/Lima` al mostrar.

## Próximos pasos

1. Corregir la indentación de `password_hasher` en `src/barberia/main.py`.
2. Ejecutar `py_compile` y levantar Uvicorn sin errores.
3. Respaldar los tres archivos frontend actuales e integrar los archivos de este paquete.
4. Probar carga de la web, CSS/JS, chat anónimo, registro con correo/teléfono nuevos, validación de contraseñas, login, login inválido, `/api/auth/me`, logout y reserva pendiente.
5. Corregir la integración según errores reales; no tocar ni recrear la DB.
6. Implementar endpoint de citas protegido antes de prometer reservas reales.
7. Después, implementar recordatorios por correo y el modelo ML.

## ML futuro

El modelo no está implementado. Objetivo previsto: predecir el servicio probable para un cliente a partir de historial de citas. Dos clientes no bastan para entrenar y evaluar un modelo fiable. Recopilar historial etiquetado; luego evaluar `DecisionTreeClassifier` u otro modelo del curso, con división train/test y métricas explicadas. El chatbot por palabras clave no es ML.

## Preferencias de trabajo

Responder en español, avanzar paso a paso y explicar los cambios. Preservar datos y código existente. Actualizar y compartir este Markdown al cerrar etapas o cuando se acerque el límite de contexto.
