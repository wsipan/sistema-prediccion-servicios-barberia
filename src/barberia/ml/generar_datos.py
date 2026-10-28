from pathlib import Path
import random

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
DATASET_PATH = DATA_DIR / "citas_sinteticas.csv"

SEMILLA = 42
CANTIDAD_REGISTROS = 3000

SERVICIOS = [
    "corte",
    "barba",
    "corte_barba",
    "corte_premium",
]


def elegir_servicio_objetivo(
    servicio_anterior,
    servicio_frecuente,
):
    """
    Genera patrones simulados para que exista una relación
    aprendible entre el historial y el próximo servicio.

    Estos datos son sintéticos y solamente se utilizan
    para desarrollo y demostración del modelo.
    """

    probabilidad = random.random()

    # La preferencia histórica tiene bastante influencia.
    if probabilidad < 0.55:
        return servicio_frecuente

    # El servicio anterior también influye.
    if probabilidad < 0.80:
        return servicio_anterior

    # Introducimos variabilidad para evitar un dataset
    # completamente determinista.
    return random.choice(SERVICIOS)


def generar_dataset():
    random.seed(SEMILLA)

    registros = []

    for _ in range(CANTIDAD_REGISTROS):
        dia_semana = random.randint(0, 5)
        hora = random.randint(9, 19)
        mes = random.randint(1, 12)

        servicio_anterior = random.choice(SERVICIOS)
        servicio_frecuente = random.choice(SERVICIOS)

        cantidad_citas = random.randint(1, 20)
        dias_desde_ultima_cita = random.randint(7, 60)

        servicio_objetivo = elegir_servicio_objetivo(
            servicio_anterior,
            servicio_frecuente,
        )

        registros.append(
            {
                "dia_semana": dia_semana,
                "hora": hora,
                "mes": mes,
                "servicio_anterior": servicio_anterior,
                "servicio_frecuente": servicio_frecuente,
                "cantidad_citas": cantidad_citas,
                "dias_desde_ultima_cita": dias_desde_ultima_cita,
                "servicio_objetivo": servicio_objetivo,
            }
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    dataframe = pd.DataFrame(registros)
    dataframe.to_csv(
        DATASET_PATH,
        index=False,
        encoding="utf-8",
    )

    print(f"Dataset generado: {DATASET_PATH}")
    print(f"Registros: {len(dataframe)}")
    print()
    print("Distribución del servicio objetivo:")
    print(dataframe["servicio_objetivo"].value_counts())


if __name__ == "__main__":
    generar_dataset()