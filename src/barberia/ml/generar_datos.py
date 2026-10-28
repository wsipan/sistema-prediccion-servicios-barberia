from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
import random

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"

HISTORIAL_PATH = DATA_DIR / "historial_sintetico.csv"
DATASET_PATH = DATA_DIR / "dataset_ml.csv"

SEMILLA = 42
CANTIDAD_CLIENTES = 300

SERVICIOS = [
    "corte",
    "barba",
    "corte_barba",
    "corte_premium",
]


def elegir_servicio_distinto(servicio_actual):
    opciones = [
        servicio
        for servicio in SERVICIOS
        if servicio != servicio_actual
    ]

    return random.choice(opciones)


def generar_secuencia_cliente(cantidad_citas):
    """
    Genera una secuencia de servicios para un cliente sintético.

    Se simulan tres comportamientos:
    - estable
    - cambio de preferencia
    - variable
    """

    tipo_cliente = random.choices(
        population=[
            "estable",
            "cambio_preferencia",
            "variable",
        ],
        weights=[
            0.45,
            0.35,
            0.20,
        ],
        k=1,
    )[0]

    preferencia_inicial = random.choice(SERVICIOS)
    preferencia_actual = preferencia_inicial

    # Para clientes que cambian de preferencia,
    # determinamos aproximadamente cuándo ocurre.
    punto_cambio = None

    if tipo_cliente == "cambio_preferencia":
        punto_cambio = random.randint(
            max(2, cantidad_citas // 3),
            max(3, (cantidad_citas * 2) // 3),
        )

    servicios = []

    for indice in range(cantidad_citas):

        if (
            tipo_cliente == "cambio_preferencia"
            and indice == punto_cambio
        ):
            preferencia_actual = elegir_servicio_distinto(
                preferencia_actual
            )

        if tipo_cliente == "estable":
            # Alta tendencia a mantener su preferencia.
            if random.random() < 0.75:
                servicio = preferencia_actual
            else:
                servicio = random.choice(SERVICIOS)

        elif tipo_cliente == "cambio_preferencia":
            # Antes y después del cambio existe una
            # preferencia dominante, pero no absoluta.
            if random.random() < 0.72:
                servicio = preferencia_actual
            else:
                servicio = random.choice(SERVICIOS)

        else:
            # Cliente más variable.
            # El servicio anterior tiene cierta influencia,
            # pero existe mayor diversidad.
            if servicios and random.random() < 0.45:
                servicio = servicios[-1]
            else:
                servicio = random.choice(SERVICIOS)

        servicios.append(servicio)

    return tipo_cliente, servicios


def generar_historial():
    random.seed(SEMILLA)

    registros = []

    fecha_inicio = datetime(2024, 1, 1, 10, 0)

    for cliente_id in range(1, CANTIDAD_CLIENTES + 1):

        cantidad_citas = random.randint(8, 20)

        tipo_cliente, servicios = generar_secuencia_cliente(
            cantidad_citas
        )

        fecha_actual = fecha_inicio + timedelta(
            days=random.randint(0, 120)
        )

        for numero_cita, servicio in enumerate(
            servicios,
            start=1,
        ):
            registros.append(
                {
                    "cliente_id": cliente_id,
                    "numero_cita": numero_cita,
                    "fecha_hora": fecha_actual.isoformat(),
                    "servicio": servicio,
                    "tipo_cliente_sintetico": tipo_cliente,
                }
            )

            dias_hasta_siguiente = random.randint(14, 56)
            hora = random.randint(9, 19)

            fecha_actual = (
                fecha_actual
                + timedelta(days=dias_hasta_siguiente)
            ).replace(
                hour=hora,
                minute=0,
                second=0,
                microsecond=0,
            )

    return pd.DataFrame(registros)


def calcular_racha(servicios):
    """
    Calcula cuántas veces consecutivas aparece al final
    el último servicio.
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


def construir_dataset_ml(historial):
    ejemplos = []

    for cliente_id, citas_cliente in historial.groupby(
        "cliente_id"
    ):
        citas_cliente = citas_cliente.sort_values(
            "numero_cita"
        ).reset_index(drop=True)

        # Necesitamos al menos dos citas previas para
        # construir características más útiles.
        for indice in range(2, len(citas_cliente)):

            historial_previo = citas_cliente.iloc[:indice]
            cita_objetivo = citas_cliente.iloc[indice]

            servicios_previos = historial_previo[
                "servicio"
            ].tolist()

            servicio_anterior = servicios_previos[-1]

            cantidad_citas_previas = len(
                servicios_previos
            )

            conteo_historico = Counter(
                servicios_previos
            )

            # Ventana reciente: últimas 3 citas.
            servicios_recientes = servicios_previos[-3:]

            conteo_reciente = Counter(
                servicios_recientes
            )

            ejemplo = {
                "cliente_id": cliente_id,
                "servicio_anterior": servicio_anterior,
                "cantidad_citas_previas": (
                    cantidad_citas_previas
                ),
                "racha_servicio_anterior": calcular_racha(
                    servicios_previos
                ),
            }

            # Proporción histórica de cada servicio.
            for servicio in SERVICIOS:
                ejemplo[
                    f"proporcion_{servicio}"
                ] = (
                    conteo_historico.get(servicio, 0)
                    / cantidad_citas_previas
                )

            # Número de apariciones en las últimas 3 citas.
            for servicio in SERVICIOS:
                ejemplo[
                    f"recientes_{servicio}"
                ] = conteo_reciente.get(
                    servicio,
                    0,
                )

            ejemplo["servicio_objetivo"] = (
                cita_objetivo["servicio"]
            )

            ejemplos.append(ejemplo)

    return pd.DataFrame(ejemplos)


def generar_datos():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    historial = generar_historial()

    dataset_ml = construir_dataset_ml(
        historial
    )

    historial.to_csv(
        HISTORIAL_PATH,
        index=False,
        encoding="utf-8",
    )

    dataset_ml.to_csv(
        DATASET_PATH,
        index=False,
        encoding="utf-8",
    )

    print("GENERACIÓN V2 FINALIZADA")
    print("-" * 50)

    print(
        f"Clientes sintéticos: "
        f"{historial['cliente_id'].nunique()}"
    )

    print(
        f"Citas generadas: "
        f"{len(historial)}"
    )

    print(
        f"Ejemplos para ML: "
        f"{len(dataset_ml)}"
    )

    print()
    print("Tipos de clientes sintéticos:")

    tipos_por_cliente = (
        historial[
            [
                "cliente_id",
                "tipo_cliente_sintetico",
            ]
        ]
        .drop_duplicates()
        ["tipo_cliente_sintetico"]
        .value_counts()
    )

    print(tipos_por_cliente)

    print()
    print("Distribución del objetivo:")
    print(
        dataset_ml[
            "servicio_objetivo"
        ].value_counts()
    )

    print()
    print(f"Historial: {HISTORIAL_PATH}")
    print(f"Dataset ML: {DATASET_PATH}")


if __name__ == "__main__":
    generar_datos()