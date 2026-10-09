# Sistema web para la predicción del servicio de barbería y gestión de citas mediante aprendizaje automático

> **Documento vivo del proyecto.** Este archivo reúne la idea acordada, las decisiones tomadas, los contenidos vistos en clase, las alternativas técnicas y el estado del trabajo. Debe actualizarse cuando se tome una decisión o se complete una etapa para poder continuar en otro chat sin perder contexto.

## Estado actual del proyecto

- **Estado:** definición y consolidación de la idea; todavía no se ha comenzado la implementación.
- **Tipo de negocio definido:** barbería.
- **Usuario objetivo definido:** cualquier persona que desee recibir atención o reservar un servicio en la barbería.
- **Título profesional del proyecto:** Sistema web para la predicción del servicio de barbería y gestión de citas mediante aprendizaje automático.
- **Prioridad:** un proyecto de complejidad intermedia, realizable por estudiantes, que demuestre claramente el uso de Machine Learning y tenga una interfaz web funcional.
- **Problema principal de ML elegido provisionalmente:** predecir el servicio que probablemente elegirá un cliente en su próxima visita, a partir del historial disponible. La viabilidad queda sujeta a definir y validar el dataset.
- **Algoritmo inicial candidato:** `DecisionTreeClassifier`, por ser un tema trabajado en clase; no se considera validado hasta evaluar sus resultados.
- **Próximo paso técnico:** crear el repositorio compartido, preparar el entorno en Visual Studio Code y acordar el esquema de datos.
- **Importante:** las funcionalidades y tecnologías descritas son propuestas iniciales, no decisiones definitivas, salvo que se indiquen expresamente como definidas.

---

## 1. Propuesta del proyecto

### Título del proyecto

**Sistema web para la predicción del servicio de barbería y gestión de citas mediante aprendizaje automático**

### Nuestra idea

Desarrollar un asistente conversacional inteligente que interactúe con los clientes a través de una interfaz web, permita realizar operaciones básicas como agendar y cancelar citas, y sea capaz de aprender progresivamente de las preferencias y frecuencia de uso de cada cliente.

La idea no será únicamente construir un chatbot de respuestas predefinidas. El sistema deberá utilizar Machine Learning para analizar el historial de interacciones y comportamiento de los clientes, identificar patrones y generar recomendaciones personalizadas.

### Objetivo general

Desarrollar una aplicación web para una barbería que permita consultar servicios y gestionar citas, e incorpore un modelo de aprendizaje automático supervisado para predecir el servicio que probablemente elegirá un cliente a partir de su historial, siempre que los datos disponibles permitan entrenar y evaluar el modelo de forma razonable.

### Objetivos específicos

- Registrar clientes, servicios, historial de visitas y citas en una base de datos.
- Analizar el historial con Pandas, NumPy y Matplotlib.
- Definir una variable objetivo que represente el servicio elegido en una visita y construir características disponibles antes de esa elección.
- Entrenar un clasificador inicial, probablemente `DecisionTreeClassifier`, si el dataset lo permite.
- Evaluar el modelo con datos de prueba y métricas apropiadas.
- Mostrar la predicción como una sugerencia, sin impedir que el cliente elija otro servicio.
- Permitir consultar disponibilidad, reservar y cancelar citas mediante una interfaz web sencilla.
- Separar la lógica de negocio de reservas del componente de Machine Learning.

### Contexto del negocio definido

El sistema estará orientado a una **barbería**. El usuario objetivo es cualquier persona que quiera consultar servicios, conocer disponibilidad o gestionar una cita. No se presupone que la barbería tenga clientes registrados previamente: el diseño debe contemplar tanto a clientes nuevos como recurrentes.

El sistema debe evitar inventar disponibilidad. Los horarios ofrecidos deben consultarse en la base de datos y una cita solo se considerará reservada cuando haya sido guardada correctamente.

---

## 2. Funcionalidades propuestas

### 3.1. Funcionalidades principales (MVP)

- Registro e identificación de clientes.
- Consulta de servicios disponibles.
- Consulta de horarios disponibles.
- Agendamiento de citas.
- Cancelación de citas.
- Consulta del historial del cliente.
- Registro de interacciones y comportamiento.
- Interpretación de las solicitudes habituales (mediante reglas, NLP o un modelo, según se decida).
- Registro del historial necesario para calcular preferencias.
- Una recomendación personalizada basada en datos, si se consigue un dataset suficiente y se define una evaluación válida.

### 3.2. Perfil inteligente del cliente

El sistema podrá construir un perfil a partir de los datos históricos:

```text
PERFIL DEL CLIENTE
------------------------------
Frecuencia:        Alta
Servicio frecuente: Corte
Horario preferido: 16:00 - 18:00
Día preferido:     Viernes
Intervalo promedio: 21 días
Última visita:     Fecha registrada
```

Este perfil se calculará a partir de los datos disponibles. Algunas estadísticas simples (por ejemplo, servicio más frecuente) pueden obtenerse directamente con consultas y agregaciones; no deben presentarse como Machine Learning si no interviene un modelo entrenado. Si el cliente tiene pocas visitas, el sistema deberá indicar que todavía no cuenta con suficiente historial.

### 3.3. Recomendación personalizada

El sistema podrá predecir o recomendar:

- Servicio con mayor probabilidad de interés.
- Horario preferido.
- Posible próxima visita.
- Opcionalmente, clientes con riesgo de inactividad.

Ejemplo:

```text
Cliente: 001

Historial:
- Corte
- Corte + barba
- Corte
- Corte + barba

Predicción:
Servicio recomendado: Corte + barba
Confianza: valor calculado por el modelo, si está disponible
```

### 3.4. Gestión de citas

Flujo esperado:

```text
Usuario
  ↓
"Quiero reservar una cita"
  ↓
Detección de intención
  ↓
Identificación de fecha/servicio
  ↓
Consulta de disponibilidad
  ↓
Recomendación según preferencias
  ↓
Selección del usuario
  ↓
Registro de cita en la base de datos
```

---

## 3. Componente de Inteligencia Artificial y Machine Learning

El proyecto deberá diferenciar claramente el chatbot de la parte de Machine Learning.

### 4.1. Procesamiento de lenguaje / chatbot

El sistema deberá interpretar solicitudes como:

```text
"Quiero reservar una cita"
→ AGENDAR_CITA

"¿Qué horarios tienen?"
→ CONSULTAR_HORARIOS

"Quiero cancelar mi cita"
→ CANCELAR_CITA

"¿Cuándo fue mi última cita?"
→ CONSULTAR_HISTORIAL
```

Para esta parte se podrá evaluar el uso de NLP tradicional o un modelo de lenguaje, dependiendo de los temas vistos en clase y de las herramientas permitidas.

### 4.2. Machine Learning propio

La parte de ML será responsable de aprender patrones del comportamiento del cliente.

Se evaluarán modelos sencillos y apropiados para el volumen de datos disponible, por ejemplo:

- **Decision Tree / DecisionTreeClassifier:** candidato inicial porque aparece entre los temas vistos en clase.
- Random Forest, KNN o Logistic Regression: alternativas que solo se evaluarán si se estudian y aportan valor.
- K-Means: posible alternativa si se decide agrupar clientes por comportamiento.

No se ha elegido todavía el algoritmo definitivo. La elección dependerá de la variable objetivo, los datos disponibles y las instrucciones del docente.

No se pretende entrenar un modelo de lenguaje desde cero.

### 4.3. Problema de Machine Learning seleccionado provisionalmente

**Pregunta predictiva:** dado el historial conocido de un cliente antes de una visita, ¿qué servicio elegirá en esa visita?

- **Tipo de tarea:** clasificación supervisada.
- **Variable objetivo (`y`):** categoría del servicio elegido en la visita que se desea predecir.
- **Características (`X`) candidatas:** cantidad de visitas previas, servicio de la visita anterior, frecuencias de servicios previos, días desde la última visita y otras variables conocidas antes de la elección. Solo se conservarán variables disponibles y justificables.
- **Algoritmo inicial:** `DecisionTreeClassifier` de Scikit-learn, por su relación directa con un ejercicio de clase.
- **Uso de la predicción:** sugerencia opcional en la interfaz; el cliente puede elegir un servicio distinto.

Cada fila de entrenamiento debe representar una predicción posible y utilizar únicamente información conocida antes de la visita objetivo. No se deben incluir como entrada el servicio que se intenta predecir ni datos que solo se conocen después de esa elección (fuga de información o *data leakage*).

La evaluación debe separar correctamente los ejemplos de entrenamiento y prueba. Si un cliente aporta múltiples filas, habrá que evitar que registros casi duplicados del mismo cliente aparezcan en ambos conjuntos cuando eso produzca una evaluación demasiado optimista. Si se dispone de fechas, también se puede considerar una separación temporal.

El problema sigue sujeto a la viabilidad del dataset: si no hay suficientes ejemplos representativos, se documentará la limitación y se presentará el modelo como experimento académico, no como predictor fiable para un negocio real. No se mostrarán porcentajes de confianza inventados.

---

## 4. Arquitectura propuesta

```text
                    ┌─────────────────────────┐
                    │       INTERFAZ WEB      │
                    │   Chatbot + información │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     CHATBOT / NLP       │
                    │ Comprensión de intención│
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
       ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
       │ Base de     │   │ Machine      │   │ Gestión de   │
       │ datos       │   │ Learning     │   │ citas        │
       └──────┬──────┘   └──────┬───────┘   └──────┬───────┘
              │                 │                  │
              └─────────────────┼──────────────────┘
                                ▼
                       ┌─────────────────┐
                       │ Perfil y        │
                       │ recomendaciones │
                       └─────────────────┘
```

---

## 5. Herramientas y tecnologías

### Herramientas ya consideradas

- **Python**: lenguaje principal.
- **Google Colab**: exploración de datos, experimentación y entrenamiento de modelos.
- **Base de datos**: inicialmente SQLite por su facilidad de implementación.

### Herramientas recomendadas

- **Scikit-learn**: entrenamiento y evaluación de modelos de Machine Learning.
- **Pandas**: manipulación y análisis de datos.
- **NumPy**: operaciones numéricas.
- **Matplotlib**: visualización de datos y resultados.
- **FastAPI**: backend y API del sistema.
- **HTML + CSS + JavaScript**: interfaz web.
- **SQLite**: almacenamiento inicial de clientes, citas, servicios e interacciones.

### Herramientas opcionales

- PostgreSQL, si posteriormente se requiere una base de datos más robusta.
- Un modelo de lenguaje mediante API, si está permitido y resulta conveniente para mejorar la conversación.
- Docker, únicamente si resulta útil para facilitar el despliegue.

La selección final de herramientas se realizará después de revisar los contenidos y restricciones del curso.

---

## 6. Estructura inicial de la base de datos

Se propone comenzar con las siguientes entidades:

### clientes

- id_cliente
- nombre
- fecha_registro
- frecuencia_visitas

### servicios

- id_servicio
- nombre
- descripción
- duración

### citas

- id_cita
- id_cliente
- id_servicio
- fecha
- hora
- estado

### interacciones

- id_interaccion
- id_cliente
- fecha
- mensaje
- intención_detectada

### preferencias

- id_preferencia
- id_cliente
- servicio_preferido
- horario_preferido
- día_preferido
- frecuencia_estimada

La estructura podrá modificarse cuando se defina el caso de uso y el algoritmo de ML.

---

## 7. Datos para Machine Learning

Se deberá definir un conjunto de datos que represente el historial de comportamiento de los clientes.

Variables potenciales:

- Edad, si resulta pertinente y permitido.
- Número de visitas.
- Días desde la última visita.
- Servicio utilizado.
- Número de veces utilizado cada servicio.
- Día de la semana habitual.
- Hora habitual.
- Intervalo promedio entre visitas.
- Frecuencia de cancelaciones.
- Servicio elegido en la última visita.

El conjunto de datos podrá ser:

1. Datos sintéticos creados por el equipo.
2. Dataset público adaptado al problema, si se encuentra uno adecuado.
3. Una combinación de ambos, si es necesario.

No se utilizarán datos personales reales de clientes sin autorización.

---

## 8. Evaluación del modelo

La evaluación dependerá del problema de ML seleccionado.

Para clasificación se podrán considerar:

- Accuracy.
- Precision.
- Recall.
- F1-score.
- Matriz de confusión.

Para predicción o recomendación se definirán métricas adecuadas al modelo seleccionado.

También se deberá comparar, cuando sea viable, más de un algoritmo para justificar técnicamente la elección del modelo final.

---

## 9. Alcance del proyecto

### Nivel obligatorio

- Chatbot funcional.
- Interfaz web.
- Base de datos.
- Gestión básica de citas.
- Registro de historial.
- Modelo de Machine Learning.
- Predicción o recomendación personalizada.
- Evaluación del modelo.

### Nivel recomendado

- Perfil inteligente del cliente.
- Dashboard con estadísticas.
- Comparación de algoritmos.
- Visualización de preferencias aprendidas.
- Predicción de próxima visita o servicio.

### Nivel opcional

Estas funcionalidades solo se implementarán si el tiempo lo permite:

- Predicción de inactividad.
- Análisis de sentimiento.
- Interacción mediante voz.
- Notificaciones.
- Integración con servicios externos.
- Modelos más avanzados.

No se añadirá complejidad tecnológica que no aporte directamente al objetivo académico del proyecto.

---

## 10. Relación entre los temas vistos en clase y el proyecto

Los siguientes temas fueron compartidos como contenidos trabajados hasta el momento. Esta sección registra cómo podrían aprovecharse; no significa que todos deban convertirse en funcionalidades del proyecto.

### 11.1. Sistemas expertos basados en reglas

**Tema visto:** base de conocimiento, reglas y motor de inferencia usando `if`, `elif` y `else` para recomendar una acción según condiciones.

**Posible aplicación en el sistema:** utilizar reglas explícitas para procesos que no requieren entrenamiento, por ejemplo:

- No ofrecer horarios que ya estén ocupados.
- No permitir reservar en una fecha u hora pasada.
- Pedir los datos que falten para completar una reserva.
- Mostrar servicios y duración según el catálogo configurado.

Estas reglas son lógica de negocio o un sistema basado en reglas; por sí solas **no constituyen Machine Learning**. Se pueden combinar con el modelo ML, manteniendo separadas ambas responsabilidades.

### 11.2. Análisis y visualización de datos con Pandas, NumPy y Matplotlib

**Temas vistos:** lectura de CSV/Excel, DataFrames, identificación de variables, análisis exploratorio, cálculos estadísticos y gráficos.

**Aplicación prevista:** crear o cargar un dataset de visitas y servicios de la barbería, revisar valores faltantes, explorar la distribución de servicios y horarios, calcular frecuencias e intervalos entre visitas y visualizar resultados. Estas herramientas también servirán para preparar los datos antes de entrenar el modelo.

### 11.3. Machine Learning supervisado con DecisionTreeClassifier

**Tema visto:** separar características `X` y variable objetivo `y`, entrenar un `DecisionTreeClassifier` de Scikit-learn y realizar predicciones.

**Aplicación elegida provisionalmente:** utilizar un árbol de decisión para predecir la categoría del servicio elegido en la próxima visita a partir de características derivadas del historial anterior. Primero se definirá el formato de cada fila y se comprobará si hay suficientes ejemplos etiquetados.

El pequeño dataset de ejemplo usado en clase para aprobar/desaprobar sirve para aprender el procedimiento, pero **no es un dataset adecuado para entrenar el sistema de la barbería**. Tampoco bastará por sí solo para evaluar un modelo fiable. La elección de la predicción debe ajustarse a los datos disponibles.

### 11.4. Decisión provisional sobre los temas

- **Pandas, NumPy y Matplotlib:** se consideran herramientas útiles para la exploración y preparación de datos.
- **DecisionTreeClassifier:** primer algoritmo candidato para experimentar, porque ya se ha trabajado en clase.
- **Reglas e inferencia:** se pueden utilizar para gestionar las reglas de reserva y disponibilidad.
- **NLP o LLM:** no consta todavía que se haya estudiado en clase; no se asume como requisito y se decidirá más adelante.

---

## 11. Apuntes y ejercicios originales de clase

```
Caso: Sistema experto para recomendar mantenimiento de una máquina
Una empresa textil desea implementar un sistema experto basado en reglas para
determinar el tipo de mantenimiento que debe realizarse a una máquina de producción.
Se tienen las siguientes condiciones:
• Si la temperatura de la máquina es mayor a 80 °C y la vibración es alta, se
recomienda mantenimiento inmediato.
• Si la temperatura es mayor a 80 °C y la vibración es normal, se recomienda revisión
de temperatura.
• Si la temperatura está entre 60 y 80 °C y la vibración es alta, se recomienda revisión
de vibración.
• Si la temperatura es menor o igual a 60 °C y la vibración es normal, se recomienda
funcionamiento normal.
Actividad
Desarrolle un programa en Python que:
1. Solicite al usuario la temperatura de la máquina.
2. Solicite el nivel de vibración (alta o normal).
3. Utilice una base de conocimiento representada mediante reglas.
4. Implemente un motor de inferencia utilizando estructuras if, elif y else.
5. Muestre la decisión obtenida.
6. Muestre una explicación de la decisión, indicando qué condiciones se
cumplieron.
```

```
Caso. Análisis de ventas utilizando Pandas, NumPy y Matplotlib
Una empresa desea analizar las ventas mensuales de cuatro productos textiles.
Crear el siguiente dataset y guárdelo con Excel o csv:
Producto Ventas Precio Stock
Polo 150 35 20
Pantalón 120 60 15
Casaca 80 120 5
Camisa 200 45 30
Falda 90 50 10
Actividad
Desarrolle un programa que:
1. Obtener los datos del Excel o csv
2. Cree el DataFrame.
3. Muestre las primeras filas.
4. Calcule:
o promedio de ventas;
o promedio de precios;
o venta máxima;
o venta mínima.
5. Determine cuál es el producto con mayor cantidad de ventas.
6. Genere un gráfico con matplotlib que muestre los datos
Temas evaluados:
Pandas → NumPy → DataFrame → identificación de variables → análisis exploratorio →
preparación de datos->Matplotlib
```

```
Caso: Predicción de aprobación de un estudiante
La UPN desea desarrollar un pequeño modelo de Machine Learning que permita predecir
si un estudiante tiene alta probabilidad de aprobar o desaprobar su curso de “Sistemas
Inteligentes y Machine Learning”.
Para ello, se dispone de información histórica de estudiantes. Se consideran como
características:
• Horas de estudio por semana
• Porcentaje de asistencia
La variable objetivo indica:
• 0 = Desaprobado
• 1 = Aprobado
Datos históricos
Estudiante Horas de estudio/semana Asistencia (%) Resultado
1 2 60 0
2 3 65 0
3 4 70 0
4 5 75 1
5 6 80 1
6 7 85 1
7 8 90 1
8 4 85 1
Actividad
Desarrolle un programa en Python utilizando la librería Scikit-learn que permita:
1. Importar DecisionTreeClassifier desde sklearn.tree.
2. Crear la matriz X con las variables:
o horas de estudio;
o porcentaje de asistencia.
3. Crear el vector y con los resultados históricos.
4. Crear un modelo utilizando DecisionTreeClassifier.
5. Obviamente no debe usar if sino solo el modelo
6. Entrenar el modelo con los datos proporcionados.
7. Considerar para su prueba, un nuevo estudiante con las siguientes
características:
Horas de estudio/semana Asistencia (%)
6 82
8. Utilizar el modelo entrenado para realizar la predicción.
9. Mostrar mediante print() un mensaje indicando si el modelo predice:
o "Aprobado", o
o "Desaprobado".
```

---

## 12. Plan de trabajo y próximos pasos

Se avanzará en etapas pequeñas, validando cada una antes de añadir complejidad.

1. Consolidar el caso de uso de la barbería y las operaciones que tendrá el asistente.
2. Revisar los contenidos restantes del curso y cualquier restricción del docente.
3. Definir **un problema principal de Machine Learning**, su variable objetivo y cómo se medirá el éxito.
4. Diseñar las columnas del dataset y decidir si se utilizarán datos sintéticos, datos autorizados o una fuente pública apropiada.
5. Realizar análisis exploratorio con Pandas y gráficos.
6. Crear una primera línea base y probar `DecisionTreeClassifier` si encaja con el problema elegido.
7. Evaluar el modelo con una separación de datos y métricas apropiadas; evitar conclusiones fuertes con pocos datos.
8. Diseñar la base de datos para clientes, servicios, horarios, citas e interacciones.
9. Implementar las reglas de negocio y las operaciones de reserva.
10. Construir el backend y la interfaz web.
11. Integrar el modelo con el sistema de atención y recomendaciones.
12. Probar casos normales y errores (horario ocupado, datos incompletos, cliente nuevo, etc.).
13. Registrar en este archivo las decisiones tomadas, resultados, problemas y tareas siguientes.

**No es necesario implementar todo a la vez.** Primero se debe demostrar un flujo pequeño de extremo a extremo y después incorporar la personalización basada en ML.

---

## 13. Decisiones pendientes y cuestiones por resolver

### Ya definido

- **Tipo de negocio:** barbería.
- **Usuario objetivo:** cualquier persona que quiera recibir atención en la barbería.
- **Idea central:** asistente conversacional web para consultar servicios, gestionar citas y personalizar recomendaciones a partir del historial.
- **Herramientas de análisis conocidas en clase:** Pandas, NumPy y Matplotlib.
- **Algoritmo de ML visto en clase:** `DecisionTreeClassifier`.
- **Tema de sistemas inteligentes visto:** reglas y motor de inferencia.

### Pendiente de decidir

- **Dataset:** formato, tamaño, variables, etiquetas y procedencia. El problema elegido es la predicción del servicio, pero aún no se ha seleccionado ni validado un dataset.
- **Definición exacta de cada ejemplo:** cómo se construye una fila por visita objetivo sin incluir información futura.
- **Categorías de servicio:** catálogo inicial y criterio para agrupar servicios poco frecuentes.
- **Estrategia de evaluación:** separación de entrenamiento/prueba que evite fuga de información y métricas acordes al número de ejemplos por categoría.
- **Datos para pruebas:** se puede empezar con datos sintéticos, claramente identificados como tales, y diseñar escenarios realistas.
- **Alcance del chatbot:** respuestas mediante reglas/NLP tradicional o integración con un LLM. No se ha decidido y no es obligatorio añadir un LLM.
- **Tecnologías definitivas:** Python y las herramientas de clase son el punto de partida; FastAPI, SQLite y HTML/CSS/JavaScript son recomendaciones pendientes de confirmar.
- **Agenda:** horario de apertura, duración de servicios, disponibilidad por barbero y reglas de cancelación.
- **Requisitos del docente:** entregables, algoritmos obligatorios, restricciones de APIs, tamaño esperado del proyecto y criterios de evaluación.
- **Integrantes y reparto de tareas:** pendiente de confirmar los nombres y disponibilidad del equipo; se propone un flujo de trabajo con Git y GitHub en la sección 15.

### Criterios para tomar decisiones

1. Priorizar los conceptos vistos en clase y las restricciones del docente.
2. Escoger una tarea de ML que pueda formularse claramente como clasificación, regresión o agrupamiento.
3. No afirmar que el sistema “aprende” si solo aplica reglas o cuenta frecuencias.
4. No mostrar porcentajes de confianza inventados ni presentar datos sintéticos como datos reales.
5. Mantener el proyecto realizable: un modelo bien definido, una agenda funcional y una interfaz demostrable valen más que muchas funciones incompletas.

---

## 14. Estructura inicial del proyecto en Visual Studio Code

Se propone una estructura modular y sencilla. El repositorio contendrá el código compartido y documentación; los entornos virtuales, secretos, bases de datos locales y datos privados no se subirán a Git.

```text
sistema-prediccion-servicios-barberia/
├── README.md                    # Presentación y pasos de instalación
├── requirements.txt             # Dependencias de Python
├── .gitignore                   # Archivos que Git no debe versionar
├── .env.example                 # Plantilla de variables; nunca secretos reales
├── docs/
│   ├── memoria_proyecto.md      # Este documento
│   └── decisiones_tecnicas.md   # Acuerdos y cambios importantes
├── data/
│   ├── raw/                     # Datos originales autorizados (no subir datos privados)
│   ├── processed/               # Datos limpios generados localmente
│   └── README.md                # Origen y esquema de datos, sin datos sensibles
├── notebooks/
│   └── 01_analisis_exploratorio.ipynb
├── src/
│   └── barberia/
│       ├── __init__.py
│       ├── main.py              # Punto de entrada inicial
│       ├── data/                # Carga y validación de datos
│       ├── features/            # Construcción de características X
│       ├── models/              # Entrenamiento, evaluación y predicción
│       ├── database/            # Acceso a SQLite cuando se implemente
│       └── services/             # Reglas de negocio y citas
└── tests/                       # Pruebas automáticas
```

La estructura es una base de partida, no significa que todas las carpetas deban tener código desde el primer día. Se irán incorporando módulos cuando exista una necesidad real.

### Entorno de desarrollo compartido

1. Instalar Python (misma versión menor recomendada por el equipo), Git y Visual Studio Code en cada computadora.
2. Clonar el repositorio de GitHub y abrir esa carpeta desde VS Code.
3. Crear un entorno virtual local llamado `.venv` y activarlo.
4. Instalar las dependencias desde `requirements.txt`.
5. Seleccionar el intérprete Python de `.venv` en VS Code.
6. Ejecutar las pruebas y el punto de entrada siguiendo el README.

Comandos habituales en Windows PowerShell:

```powershell
git clone https://github.com/USUARIO/sistema-prediccion-servicios-barberia.git
cd sistema-prediccion-servicios-barberia
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
code .
```

En macOS/Linux, la creación y activación normalmente se hace con `python3 -m venv .venv` y `source .venv/bin/activate`. La URL del repositorio se reemplazará por la URL real que cree el equipo.

### Datos y archivos que no deben subirse

- `.venv/`, cachés y archivos temporales.
- Credenciales, tokens y archivos `.env` reales.
- Bases de datos locales con información personal.
- Datos de clientes identificables sin autorización.
- Modelos entrenados grandes, salvo que el equipo acuerde explícitamente cómo versionarlos.

Los datos sintéticos para ejercicios deben identificarse claramente como sintéticos. Si se usa una base SQLite compartida durante el desarrollo, conviene generar una base local de prueba para cada integrante en lugar de versionar la base de datos activa.

---

## 15. Repositorio GitHub y trabajo en equipo

No se debe asumir que el repositorio remoto ya existe: un integrante deberá crearlo en GitHub y compartir su URL con el equipo. El repositorio será la fuente común del código y la documentación; cada integrante tendrá una copia local en su computadora.

### Creación inicial del repositorio

1. Elegir un integrante responsable de crear un repositorio **privado** en GitHub (si el docente no exige otra visibilidad).
2. Usar un nombre claro, por ejemplo `sistema-prediccion-servicios-barberia`.
3. Añadir una descripción basada en el título profesional del proyecto.
4. Como ya se tendrá un README y `.gitignore` en el proyecto inicial, evitar generar archivos duplicados al crear el repositorio remoto; luego conectar la carpeta local al repositorio remoto siguiendo las instrucciones de GitHub.
5. Añadir a los integrantes como colaboradores con los permisos necesarios.
6. Compartir la URL y confirmar que cada integrante puede clonar el proyecto.

### Flujo de trabajo recomendado

- `main`: versión estable que debe poder ejecutarse.
- `feature/nombre-tarea`: rama individual para una tarea concreta, por ejemplo `feature/analisis-datos` o `feature/modelo-decision-tree`.
- Cada integrante trabaja en su rama, realiza commits pequeños y descriptivos, sube la rama y abre un Pull Request hacia `main`.
- Otro integrante revisa los cambios y ejecuta las pruebas antes de aprobar la integración.
- No trabajar todos editando simultáneamente el mismo archivo si puede dividirse el trabajo por módulos.
- Antes de empezar una tarea, actualizar la rama con los cambios recientes de `main`.
- Nunca compartir contraseñas ni subir claves de API.

Comandos Git habituales:

```bash
git switch main
git pull origin main
git switch -c feature/nombre-tarea
# editar y probar los archivos
git add ruta/del/archivo
git commit -m "Agrega analisis exploratorio de visitas"
git push -u origin feature/nombre-tarea
```

Después se abre un Pull Request en GitHub. Tras su revisión y aprobación, se integra la rama en `main`. Los comandos exactos pueden variar si GitHub crea la rama principal o si el equipo usa otra política.

### Reparto de responsabilidades sugerido

El reparto se ajustará al número de integrantes; una persona puede cubrir más de una función:

- **Datos y análisis:** define el esquema del dataset, documenta su procedencia, limpia los datos y prepara gráficos exploratorios.
- **Machine Learning:** define `X` e `y`, entrena el árbol de decisión, evalúa métricas y documenta limitaciones.
- **Backend y base de datos:** implementa el catálogo de servicios, la persistencia y las reglas de disponibilidad/citas.
- **Interfaz y documentación/integración:** prepara la experiencia de usuario, integra los módulos, mantiene el README y verifica que los pasos funcionen en una computadora limpia.

Aunque existan responsables, todo el equipo debe comprender la pregunta predictiva, los datos, la evaluación y el flujo principal del sistema para poder defender el proyecto.

### Acuerdos para evitar problemas de integración

1. Acordar nombres de columnas, formatos de fecha, categorías de servicios y convenciones antes de que varias personas implementen módulos dependientes.
2. Mantener un único `requirements.txt` y actualizarlo cuando se añadan dependencias.
3. Documentar en el README cómo instalar, ejecutar y probar el proyecto desde cero.
4. Cada Pull Request debe explicar qué cambia y cómo se probó.
5. Probar periódicamente en al menos dos computadoras distintas.
6. Mantener `docs/memoria_proyecto.md` actualizado con las decisiones definitivas y el siguiente paso pendiente.

---

## 16. Memoria de continuidad para futuros chats

Este bloque resume el contexto esencial para retomar el proyecto en otra conversación. Al cambiar de etapa, actualizarlo.

- **Curso:** Sistemas Inteligentes y Machine Learning.
- **Título del proyecto:** Sistema web para la predicción del servicio de barbería y gestión de citas mediante aprendizaje automático.
- **Negocio:** barbería.
- **Público:** cualquier persona que quiera consultar servicios o gestionar citas.
- **Objetivo:** construir una aplicación web para consultar servicios y gestionar citas, con un modelo supervisado que prediga el servicio que probablemente elegirá un cliente a partir de su historial.
- **Requisito académico clave:** debe existir un componente de Machine Learning identificable, entrenado y evaluado; el chatbot por sí solo no satisface ese objetivo.
- **Contenidos vistos:** sistemas expertos/reglas con `if`/`elif`/`else`; análisis de datos con Pandas, NumPy y Matplotlib; entrenamiento básico supervisado con Scikit-learn y `DecisionTreeClassifier`.
- **Herramientas sugeridas, aún por confirmar:** Python, Google Colab, Pandas, NumPy, Matplotlib, Scikit-learn, SQLite, FastAPI y HTML/CSS/JavaScript.
- **Pendiente:** dataset y columnas definitivas, categorías de servicio, estrategia de evaluación, detalles de agenda, interfaz final y requisitos específicos del docente.
- **Próxima acción recomendada:** crear el repositorio compartido y el esqueleto de carpetas; después definir el dataset de visitas y ejecutar un primer análisis exploratorio antes de entrenar el modelo.
- **Estado actual:** planificación. No se ha implementado código del proyecto ni se han obtenido resultados experimentales.

Cuando se retome este documento, leer primero este bloque y las secciones 10, 12, 13, 14 y 15. No asumir que las opciones técnicas todavía pendientes ya fueron aprobadas.
