import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    """Schéma de validation pour les prédictions."""
    heure: int = Field(ge=0, le=23, default=14, description="Heure de l'accident")
    lum: int = Field(ge=1, le=5, default=1, description="Luminosité")
    atm: int = Field(ge=1, le=6, default=1, description="Conditions météo")
    age: float = Field(ge=0, le=120, default=30, description="Âge du conducteur")
    catr: int = Field(ge=1, le=4, default=3, description="Type de route")
    agg: int = Field(ge=1, le=2, default=2, description="Localisation")
    sexe: int = Field(ge=1, le=2, default=1, description="Sexe")
    catv: int = Field(ge=1, le=33, default=7, description="Type de véhicule")

app = FastAPI(title="API Prédiction Accidents")

try:
    model = joblib.load("model_pred/model_logistic_regression.pkl")
    columns = joblib.load("model_pred/model_columns.pkl")
except FileNotFoundError as err:
    raise RuntimeError("Modèle non trouvé") from err

@app.get("/")
def home() -> dict:
    """Point d'entrée de l'API."""
    return {"message": "API marche", "status": "OK"}

@app.get("/health")
def health() -> dict:
    """Vérification de l'état de santé de l'API."""
    return {"status": "healthy", "model": "Logistic Regression"}

@app.post("/predict")
def predict(input: PredictionInput) -> dict:
    """
    Prédit la gravité d'un accident routier.

    Args:
        input: Données de l'accident

    Returns:
        Prédiction avec gravité et probabilités
    """
    data: dict[str, float] = dict.fromkeys(columns, 0.0)

    data['heure'] = input.heure
    data['lum'] = input.lum
    data['atm'] = input.atm
    data['age'] = input.age
    data['catr'] = input.catr
    data['agg'] = input.agg
    data['sexe'] = input.sexe
    data['catv'] = input.catv

    data['nuit'] = (
        1.0 if (input.heure >= 22 or input.heure <= 6)
        else 0.0
    )
    data['jeune_conducteur'] = 1.0 if input.age < 25 else 0.0
    data['conditions_dangereuses'] = (
        1.0 if (input.atm in [2,3,4,5,6] or input.lum in [3,4])
        else 0.0
    )

    df = pd.DataFrame([data])[columns]

    prediction = int(model.predict(df)[0])
    proba = model.predict_proba(df)[0]

    return {
        "gravite": "Grave" if prediction == 1 else "Non grave",
        "probabilite_grave": round(float(proba[1]) * 100, 1),
        "probabilite_non_grave": round(float(proba[0]) * 100, 1)
    }
