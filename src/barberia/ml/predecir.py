from collections import Counter
from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "models" / "modelo_servicio.joblib"

SERVICIOS = [
    "corte",
    "barba",
    "corte_barba",
    "corte_premium",
]

MAPEO_SERVICIOS = {
    # Corte
    "corte": "corte",
    "corte de cabello": "corte",

    # Barba
    "barba": "barba",

    # Corte + barba
    "corte_barba": "corte_barba",
    "corte barba": "corte_barba",
    "corte + barba": "corte_barba",
    "corte y barba": "corte_barba",

    # Corte premium
    "corte_premium": "corte_premium",
    "corte premium": "corte_premium",
}

COLUMNAS_MODELO = [
    "servicio_anterior",
    "cantidad_citas_previas",
    "racha_servicio_anterior",
    "proporcion_corte",
    "proporcion_barba",
    "proporcion_corte_barba",
    "proporcion_corte_premium",
    "recientes_corte",
    "recientes_barba",
    "recientes_corte_barba",
    "recientes_corte_premium",
]


def cargar_modelo():
    """
    Carga el pipeline entrenado desde disco.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo en: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def calcular_racha(servicios):
    """
    Calcula cuántas veces consecutivas aparece al final
    el último servicio solicitado.
    """
    if not servicios:
        return 0

    ultimo = servicios[-1]
    racha = 0

    for servicio in reversed(servicios):
        if servicio == ultimo:
            racha += 1
        else:
            break

    return racha


def normalizar_servicio(servicio):
    """
    Convierte los nombres utilizados por la aplicación
    a las etiquetas internas utilizadas por el modelo ML.
    """
    servicio_limpio = servicio.strip().lower()

    return MAPEO_SERVICIOS.get(
        servicio_limpio,
        servicio_limpio,
    )

def construir_caracteristicas(servicios):
    """
    Convierte el historial de servicios de un cliente
    en las mismas características utilizadas durante
    el entrenamiento.
    """
    if len(servicios) < 2:
        raise ValueError(
            "Se necesitan al menos 2 servicios históricos "
            "para realizar una predicción."
        )

    servicios = [
    normalizar_servicio(servicio)
    for servicio in servicios
]

    servicios_invalidos = [
        servicio
        for servicio in servicios
        if servicio not in SERVICIOS
    ]

    if servicios_invalidos:
        raise ValueError(
            "El historial contiene servicios no reconocidos: "
            + ", ".join(sorted(set(servicios_invalidos)))
        )

    cantidad = len(servicios)

    conteo_historico = Counter(servicios)
    servicios_recientes = servicios[-3:]
    conteo_reciente = Counter(servicios_recientes)

    caracteristicas = {
        "servicio_anterior": servicios[-1],
        "cantidad_citas_previas": cantidad,
        "racha_servicio_anterior": calcular_racha(servicios),
    }

    for servicio in SERVICIOS:
        caracteristicas[f"proporcion_{servicio}"] = (
            conteo_historico.get(servicio, 0)
            / cantidad
        )

    for servicio in SERVICIOS:
        caracteristicas[f"recientes_{servicio}"] = (
            conteo_reciente.get(servicio, 0)
        )

    return caracteristicas


def predecir_servicio(servicios):
    """
    Predice el próximo servicio probable utilizando
    el historial conocido del cliente.
    """
    caracteristicas = construir_caracteristicas(servicios)

    entrada = pd.DataFrame(
        [caracteristicas],
        columns=COLUMNAS_MODELO,
    )

    modelo = cargar_modelo()

    servicio_predicho = modelo.predict(entrada)[0]

    probabilidades = modelo.predict_proba(entrada)[0]

    clases = modelo.classes_

    probabilidades_por_servicio = {
        clase: float(probabilidad)
        for clase, probabilidad in zip(
            clases,
            probabilidades,
        )
    }

    probabilidad_prediccion = (
        probabilidades_por_servicio[
            servicio_predicho
        ]
    )

    return {
        "servicio_predicho": servicio_predicho,
        "probabilidad": probabilidad_prediccion,
        "probabilidades": probabilidades_por_servicio,
        "cantidad_citas_utilizadas": len(servicios),
    }


if __name__ == "__main__":
    historial_prueba = [
        "corte",
        "corte",
        "corte_barba",
        "corte_barba",
        "corte_barba",
    ]

    resultado = predecir_servicio(
        historial_prueba
    )

    print("Historial:")
    print(historial_prueba)

    print()
    print("Resultado:")
    print(resultado)