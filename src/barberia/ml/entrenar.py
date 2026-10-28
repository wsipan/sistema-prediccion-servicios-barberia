from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = PROJECT_ROOT / "data" / "dataset_ml.csv"
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "modelo_servicio.joblib"

SEMILLA = 42

SERVICIOS = [
    "barba",
    "corte",
    "corte_barba",
    "corte_premium",
]

COLUMNAS_CATEGORICAS = [
    "servicio_anterior",
]

COLUMNAS_NUMERICAS = [
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

COLUMNAS_MODELO = (
    COLUMNAS_CATEGORICAS
    + COLUMNAS_NUMERICAS
)


def crear_preprocesador():
    return ColumnTransformer(
        transformers=[
            (
                "categoricas",
                OneHotEncoder(handle_unknown="ignore"),
                COLUMNAS_CATEGORICAS,
            ),
            (
                "numericas",
                "passthrough",
                COLUMNAS_NUMERICAS,
            ),
        ]
    )


def crear_pipeline(clasificador):
    return Pipeline(
        steps=[
            ("preprocesador", crear_preprocesador()),
            ("clasificador", clasificador),
        ]
    )


def servicio_mas_frecuente(fila):
    proporciones = {
        "corte": fila["proporcion_corte"],
        "barba": fila["proporcion_barba"],
        "corte_barba": fila["proporcion_corte_barba"],
        "corte_premium": fila["proporcion_corte_premium"],
    }

    return max(
        proporciones,
        key=proporciones.get,
    )


def evaluar_predicciones(
    nombre,
    y_real,
    y_pred,
    mostrar_detalle=False,
):
    accuracy = accuracy_score(
        y_real,
        y_pred,
    )

    f1_macro = f1_score(
        y_real,
        y_pred,
        average="macro",
    )

    print()
    print("=" * 65)
    print(nombre)
    print("=" * 65)

    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1 macro: {f1_macro:.4f}")

    if mostrar_detalle:
        print()
        print("Reporte de clasificación:")

        print(
            classification_report(
                y_real,
                y_pred,
                labels=SERVICIOS,
                digits=4,
                zero_division=0,
            )
        )

        print("Matriz de confusión:")

        print(
            confusion_matrix(
                y_real,
                y_pred,
                labels=SERVICIOS,
            )
        )

    return {
        "nombre": nombre,
        "accuracy": accuracy,
        "f1_macro": f1_macro,
    }


def entrenar_y_evaluar(
    nombre,
    modelo,
    X_train,
    y_train,
    X_test,
    y_test,
):
    modelo.fit(
        X_train,
        y_train,
    )

    predicciones = modelo.predict(
        X_test
    )

    resultado = evaluar_predicciones(
        nombre,
        y_test,
        predicciones,
        mostrar_detalle=True,
    )

    resultado["modelo"] = modelo

    return resultado


def entrenar_modelos():

    # --------------------------------------------------
    # 1. Cargar datos
    # --------------------------------------------------

    df = pd.read_csv(
        DATASET_PATH
    )

    print(
        f"Registros cargados: {len(df)}"
    )

    print(
        f"Clientes: "
        f"{df['cliente_id'].nunique()}"
    )

    # --------------------------------------------------
    # 2. Separación POR CLIENTES
    # --------------------------------------------------

    separador = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=SEMILLA,
    )

    indice_train, indice_test = next(
        separador.split(
            df,
            groups=df["cliente_id"],
        )
    )

    train = df.iloc[
        indice_train
    ].copy()

    test = df.iloc[
        indice_test
    ].copy()

    clientes_train = set(
        train["cliente_id"]
    )

    clientes_test = set(
        test["cliente_id"]
    )

    clientes_compartidos = (
        clientes_train
        .intersection(clientes_test)
    )

    print()
    print(
        f"Clientes entrenamiento: "
        f"{len(clientes_train)}"
    )

    print(
        f"Clientes prueba: "
        f"{len(clientes_test)}"
    )

    print(
        f"Clientes compartidos: "
        f"{len(clientes_compartidos)}"
    )

    print()
    print(
        f"Registros entrenamiento: "
        f"{len(train)}"
    )

    print(
        f"Registros prueba: "
        f"{len(test)}"
    )

    # --------------------------------------------------
    # 3. X / y
    # --------------------------------------------------

    X_train = train[
        COLUMNAS_MODELO
    ]

    y_train = train[
        "servicio_objetivo"
    ]

    X_test = test[
        COLUMNAS_MODELO
    ]

    y_test = test[
        "servicio_objetivo"
    ]

    # --------------------------------------------------
    # 4. BASELINE 1
    # Servicio históricamente más frecuente
    # --------------------------------------------------

    baseline_frecuente = test.apply(
        servicio_mas_frecuente,
        axis=1,
    )

    resultado_baseline_frecuente = (
        evaluar_predicciones(
            "BASELINE 1: SERVICIO MÁS FRECUENTE",
            y_test,
            baseline_frecuente,
        )
    )

    # --------------------------------------------------
    # 5. BASELINE 2
    # Repetir último servicio
    # --------------------------------------------------

    baseline_ultimo = test[
        "servicio_anterior"
    ]

    resultado_baseline_ultimo = (
        evaluar_predicciones(
            "BASELINE 2: ÚLTIMO SERVICIO",
            y_test,
            baseline_ultimo,
        )
    )

    # --------------------------------------------------
    # 6. DECISION TREE
    # --------------------------------------------------

    arbol = crear_pipeline(
        DecisionTreeClassifier(
            max_depth=8,
            min_samples_leaf=10,
            random_state=SEMILLA,
        )
    )

    resultado_arbol = entrenar_y_evaluar(
        "DECISION TREE",
        arbol,
        X_train,
        y_train,
        X_test,
        y_test,
    )

    # --------------------------------------------------
    # 7. RANDOM FOREST
    # --------------------------------------------------

    bosque = crear_pipeline(
        RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            min_samples_leaf=5,
            random_state=SEMILLA,
            n_jobs=-1,
        )
    )

    resultado_bosque = entrenar_y_evaluar(
        "RANDOM FOREST",
        bosque,
        X_train,
        y_train,
        X_test,
        y_test,
    )

    # --------------------------------------------------
    # 8. Resumen
    # --------------------------------------------------

    resultados = [
        resultado_baseline_frecuente,
        resultado_baseline_ultimo,
        resultado_arbol,
        resultado_bosque,
    ]

    print()
    print("=" * 65)
    print("RESUMEN COMPARATIVO")
    print("=" * 65)

    for resultado in resultados:
        print(
            f"{resultado['nombre']:<38} "
            f"Accuracy={resultado['accuracy']:.4f} | "
            f"F1={resultado['f1_macro']:.4f}"
        )

    # --------------------------------------------------
    # 9. Selección entre modelos ML
    # --------------------------------------------------

    modelos_ml = [
        resultado_arbol,
        resultado_bosque,
    ]

    mejor_modelo = max(
        modelos_ml,
        key=lambda resultado: resultado["f1_macro"],
    )

    mejor_baseline = max(
        [
            resultado_baseline_frecuente,
            resultado_baseline_ultimo,
        ],
        key=lambda resultado: resultado["f1_macro"],
    )

    diferencia = (
        mejor_modelo["f1_macro"]
        - mejor_baseline["f1_macro"]
    )

    print()
    print("=" * 65)
    print("SELECCIÓN")
    print("=" * 65)

    print(
        f"Mejor baseline: "
        f"{mejor_baseline['nombre']}"
    )

    print(
        f"F1 mejor baseline: "
        f"{mejor_baseline['f1_macro']:.4f}"
    )

    print()
    print(
        f"Mejor modelo ML: "
        f"{mejor_modelo['nombre']}"
    )

    print(
        f"F1 mejor modelo ML: "
        f"{mejor_modelo['f1_macro']:.4f}"
    )

    print(
        f"Diferencia ML vs baseline: "
        f"{diferencia:+.4f}"
    )

    # --------------------------------------------------
    # 10. Guardar modelo
    # --------------------------------------------------

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        mejor_modelo["modelo"],
        MODEL_PATH,
    )

    print()
    print(
        f"Modelo ML guardado en: "
        f"{MODEL_PATH}"
    )


if __name__ == "__main__":
    entrenar_modelos()