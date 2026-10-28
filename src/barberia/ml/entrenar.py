from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = PROJECT_ROOT / "data" / "citas_sinteticas.csv"
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "modelo_servicio.joblib"

SEMILLA = 42


def entrenar_modelo():
    # 1. Cargar dataset
    df = pd.read_csv(DATASET_PATH)

    print(f"Registros cargados: {len(df)}")

    # 2. Separar variables predictoras y objetivo
    X = df.drop(columns=["servicio_objetivo"])
    y = df["servicio_objetivo"]

    # 3. Identificar columnas
    columnas_categoricas = [
        "servicio_anterior",
        "servicio_frecuente",
    ]

    columnas_numericas = [
        "dia_semana",
        "hora",
        "mes",
        "cantidad_citas",
        "dias_desde_ultima_cita",
    ]

    # 4. Preprocesamiento
    preprocesador = ColumnTransformer(
        transformers=[
            (
                "categoricas",
                OneHotEncoder(handle_unknown="ignore"),
                columnas_categoricas,
            ),
            (
                "numericas",
                "passthrough",
                columnas_numericas,
            ),
        ]
    )

    # 5. Modelo
    clasificador = DecisionTreeClassifier(
        max_depth=8,
        min_samples_leaf=10,
        random_state=SEMILLA,
    )

    # 6. Pipeline
    pipeline = Pipeline(
        steps=[
            ("preprocesador", preprocesador),
            ("clasificador", clasificador),
        ]
    )

    # 7. Train / test
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=SEMILLA,
        stratify=y,
    )

    print(f"Entrenamiento: {len(X_train)} registros")
    print(f"Prueba: {len(X_test)} registros")

    # 8. Entrenar
    pipeline.fit(X_train, y_train)

    # 9. Predecir conjunto de prueba
    y_pred = pipeline.predict(X_test)

    # 10. Evaluación
    accuracy = accuracy_score(y_test, y_pred)

    print()
    print(f"Accuracy: {accuracy:.4f}")

    print()
    print("Reporte de clasificación:")
    print(
        classification_report(
            y_test,
            y_pred,
            digits=4,
        )
    )

    print("Matriz de confusión:")
    print(confusion_matrix(y_test, y_pred))

    # 11. Guardar modelo completo
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(pipeline, MODEL_PATH)

    print()
    print(f"Modelo guardado en: {MODEL_PATH}")


if __name__ == "__main__":
    entrenar_modelo()