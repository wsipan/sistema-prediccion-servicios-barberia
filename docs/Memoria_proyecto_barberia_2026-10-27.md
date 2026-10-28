# Memoria técnica y guía de ejecución --- Sistema inteligente de barbería

**Actualizado:** 27 de octubre de 2026\
**Estado:** Fase experimental de Machine Learning completada. Siguiente
paso: integración SQLite → ML → FastAPI → chatbot.

## 1. Objetivo

Desarrollar un sistema inteligente para una barbería que prediga el
próximo servicio probable de un cliente mediante Machine Learning usando
su historial.

Flujo objetivo:

``` text
Usuario → Frontend/Chatbot → FastAPI → SQLite + módulo ML
                                      ↓
                            modelo_servicio.joblib
                                      ↓
                         predicción/recomendación
```

## 2. Estructura relevante

``` text
sistema-prediccion-servicios-barberia/
├── barberia.db
├── data/
│   ├── citas_sinteticas_v1.csv
│   ├── historial_sintetico_v1.csv
│   ├── dataset_ml_v1.csv
│   ├── historial_sintetico.csv
│   └── dataset_ml.csv
├── models/
│   └── modelo_servicio.joblib
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── src/barberia/
    ├── main.py
    ├── database.py
    └── ml/
        ├── __init__.py
        ├── generar_datos.py
        ├── entrenar.py
        └── predecir.py
```

**No borrar ni recrear `barberia.db`.**

## 3. Entorno utilizado

Python 3.13.5. Paquetes principales: FastAPI 0.143.0, Uvicorn 0.54.0,
pandas 2.3.3, scikit-learn 1.9.1, numpy 2.5.3, scipy 1.18.1, joblib
1.6.0, matplotlib 3.11.2, pwdlib 0.3.1, itsdangerous 2.2.0,
python-dotenv 1.2.4 y pytest 8.4.2.

Instalación:

``` powershell
python -m pip install -r requirements.txt
```

Si hace falta generar `requirements.txt` desde el equipo funcional:

``` powershell
python -m pip freeze > requirements.txt
```

## 4. Ejecutar la aplicación

Desde la raíz:

``` powershell
python -m uvicorn src.barberia.main:app --reload
```

Aplicación: `http://127.0.0.1:8000`\
Swagger: `http://127.0.0.1:8000/docs`

## 5. Estado FastAPI / SQLite

La aplicación ya tiene registro, login, logout, sesión firmada,
`/api/auth/me`, chat público antes del login y autenticación para
reservar.

La tabla `clientes` incluye `password_hash`. La tabla `citas` permite
crear/listar citas. Se validaron fechas futuras y rechazo de un horario
exacto duplicado.

## 6. Objetivo de Machine Learning

Predecir el próximo servicio probable usando únicamente historial
previo.

Clases:

``` text
corte
barba
corte_barba
corte_premium
```

## 7. Experimento V1

Resultados conservados como primer experimento:

``` text
Baseline F1       = 0.8239
Decision Tree F1  = 0.8152
Random Forest F1  = 0.8183
```

La baseline dominaba debido a cómo estaba diseñado el primer generador.
No son los resultados finales.

## 8. Dataset V2 actual

`src/barberia/ml/generar_datos.py` simula clientes estables, con cambio
de preferencia y variables. `tipo_cliente_sintetico` se usa para la
simulación, pero NO como predictor.

Características del dataset:

``` text
cliente_id
servicio_anterior
cantidad_citas_previas
racha_servicio_anterior
proporcion_corte
proporcion_barba
proporcion_corte_barba
proporcion_corte_premium
recientes_corte
recientes_barba
recientes_corte_barba
recientes_corte_premium
servicio_objetivo
```

Estado confirmado:

``` text
Clientes sintéticos: 300
Ejemplos ML: 3623
Columnas: 13
Nulos: 0
```

Regenerar:

``` powershell
python -m py_compile src/barberia/ml/generar_datos.py
python -m src.barberia.ml.generar_datos
```

Inspeccionar:

``` powershell
python -c "import pandas as pd; df=pd.read_csv('data/dataset_ml.csv'); print(df.head(10).to_string(index=False)); print('Forma:', df.shape); print(df.isnull().sum())"
```

## 9. Entrenamiento V2

`src/barberia/ml/entrenar.py` compara:

1.  servicio históricamente más frecuente;
2.  último servicio;
3.  Decision Tree;
4.  Random Forest.

La separación es por cliente con `GroupShuffleSplit`.

Resultado confirmado:

``` text
Registros: 3623
Clientes: 300
Clientes entrenamiento: 240
Clientes prueba: 60
Clientes compartidos: 0
Registros entrenamiento: 2911
Registros prueba: 712
```

Resultados:

  Método                                 Accuracy     F1 macro
  ---------------------------------- ------------ ------------
  Baseline: servicio más frecuente         0.6236       0.6228
  Baseline: último servicio                0.6447       0.6438
  Decision Tree                            0.6685       0.6668
  Random Forest                        **0.6756**   **0.6741**

Random Forest supera la mejor baseline en **+0.0303 F1 macro** y es el
modelo seleccionado.

Entrenar:

``` powershell
python -m py_compile src/barberia/ml/entrenar.py
python -m src.barberia.ml.entrenar
```

Debe aparecer `Clientes compartidos: 0`.

Salida:

``` text
models/modelo_servicio.joblib
```

## 10. Predictor

`src/barberia/ml/predecir.py` carga el pipeline, reconstruye las mismas
características, ejecuta `predict()` y `predict_proba()` y devuelve
servicio, probabilidad, probabilidades por clase y cantidad de citas
usadas.

Requiere mínimo **2 servicios históricos**.

Prueba:

``` powershell
python -m py_compile src/barberia/ml/predecir.py
python -m src.barberia.ml.predecir
```

Resultados confirmados:

``` text
[corte, corte, corte_barba, corte_barba, corte_barba]
→ corte_barba
→ probabilidad 0.7064601164699658

[corte, corte, corte, corte, corte]
→ corte
→ probabilidad 0.7821461123100085

[barba, barba, corte_barba, corte_barba, corte_barba]
→ corte_barba
→ probabilidad 0.6583425333520468
```

Pruebas manuales:

``` powershell
python -c "from src.barberia.ml.predecir import predecir_servicio; print(predecir_servicio(['corte','corte','corte','corte','corte']))"
```

``` powershell
python -c "from src.barberia.ml.predecir import predecir_servicio; print(predecir_servicio(['barba','barba','corte_barba','corte_barba','corte_barba']))"
```

## 11. Estado actual

Completado:

``` text
[OK] FastAPI / SQLite
[OK] autenticación y sesiones
[OK] citas
[OK] dataset sintético V1 y experimento V1
[OK] dataset sintético V2
[OK] ingeniería de características V2
[OK] split por cliente
[OK] dos baselines
[OK] Decision Tree
[OK] Random Forest
[OK] evaluación y selección
[OK] modelo_servicio.joblib
[OK] predecir.py
[OK] predict_proba()
```

Pendiente:

``` text
[PENDIENTE] SQLite → historial del cliente → ML
[PENDIENTE] GET /api/prediccion-servicio
[PENDIENTE] integración localizada con chatbot/frontend
[PENDIENTE] datos/clientes controlados para demostración
[PENDIENTE] mínimo 2 escenarios formales de validación
[PENDIENTE] consolidar resultados/gráficos
[PENDIENTE] Capítulo V
[PENDIENTE] matriz antecedentes vs resultados
```

## 12. Próximo paso EXACTO

Implementar:

``` text
cliente autenticado
        ↓
cliente["id"]
        ↓
tabla citas
        ↓
historial cronológico de servicios
        ↓
predecir_servicio(historial)
        ↓
GET /api/prediccion-servicio
```

Respuesta objetivo con historial:

``` json
{
  "prediccion_disponible": true,
  "servicio_predicho": "corte_barba",
  "probabilidad": 0.68,
  "cantidad_citas_utilizadas": 5
}
```

Sin historial suficiente:

``` json
{
  "prediccion_disponible": false,
  "motivo": "Historial insuficiente"
}
```

Primero se valida el endpoint. **No tocar todavía el frontend.**

## 13. Validación prevista

**Escenario 1:** cliente autenticado con historial suficiente → modelo
genera recomendación.

**Escenario 2:** cliente con 0 o 1 cita → sistema responde historial
insuficiente sin inventar predicción.

**Escenario 3 recomendado:** predicción → reserva → persistencia en
SQLite.

## 14. Ruta hasta Capítulo V

``` text
FASE 1 Datos                 [COMPLETADA]
FASE 2 Machine Learning      [COMPLETADA]
FASE 3 Integración           [SIGUIENTE]
FASE 4 Validación            [PENDIENTE]
FASE 5 Resultados            [PENDIENTE]
CAPÍTULO V                   [PENDIENTE]
```

## 15. Reglas del equipo

1.  No borrar `barberia.db`.
2.  No recrear tablas que funcionan.
3.  No reemplazar el frontend completo; hacer cambios localizados.
4.  Mantener chat público.
5.  Usar autenticación para acciones personales.
6.  `cliente_id` NO es predictor.
7.  Mantener train/test separados por cliente.
8.  No usar información futura.
9.  No alterar datos sintéticos para inflar métricas.
10. Conservar V1 y V2 como evidencia experimental.
11. Probar cada componente antes de avanzar.

## 16. Guía rápida para otro integrante

Desde su copia del proyecto:

``` powershell
cd RUTA\AL\sistema-prediccion-servicios-barberia
python -m pip install -r requirements.txt
python -m src.barberia.ml.predecir
python -m uvicorn src.barberia.main:app --reload
```

Si falta el `.joblib`:

``` powershell
python -m src.barberia.ml.entrenar
```

Si falta también `dataset_ml.csv`:

``` powershell
python -m src.barberia.ml.generar_datos
python -m src.barberia.ml.entrenar
```

Pipeline reproducible:

``` text
generar_datos.py
      ↓
dataset_ml.csv
      ↓
entrenar.py
      ↓
modelo_servicio.joblib
      ↓
predecir.py
      ↓
FastAPI
```

## 17. Punto de reanudación

> Continuar implementando SQLite → ML → FastAPI. Obtener de `citas` el
> historial cronológico de servicios del cliente autenticado, pasarlo a
> `predecir_servicio()` y crear `GET /api/prediccion-servicio`. Probar
> un cliente con al menos 2 citas y otro con historial insuficiente. No
> modificar todavía el frontend.
