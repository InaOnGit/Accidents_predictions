import time
from contextlib import asynccontextmanager
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator

from metrics import (
    predictions_total, 
    http_errors_total, 
    probability_histogram, 
    app_uptime_seconds, 
    model_inference_duration_seconds
)

startup_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global startup_time
    startup_time = time.time()
    yield

instrumentator = Instrumentator(
    should_group_status_codes = False,
    should_ignore_untemplated = True,
    should_respect_env_var = True,
    should_instrument_requests_inprogress = True,
    excluded_handlers = [".*admin.*", "/metrics"],
    env_var_name = "ENABLE_METRICS",
    inprogress_name = "http_requests_inprogress",
    inprogress_labels = True,
)

try:
    model = joblib.load("model_pred/model_logistic_regression.pkl")
    columns = joblib.load("model_pred/model_columns.pkl")
except FileNotFoundError as err:
    raise RuntimeError("Modèle non trouvé") from err

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

app = FastAPI( 
    title="API Prédiction Accidents",
    description="Prédiction de la gravité des accidents routiers",
    version="1.0.0",
    lifespan=lifespan 
)

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/metrics")

@app.get("/")
def home() -> dict:
    """Point d'entrée de l'API."""
    return {"message": "API marche", "status": "OK"}

@app.get("/health")
def health() -> dict:
    """Endpoint de health check."""
    app_uptime_seconds.set(time.time() - startup_time)
    return {"status": "healthy", "model": "Logistic Regression", 
            "uptime_seconds": time.time() - startup_time
    }

@app.post("/predict")
def predict(input: PredictionInput) -> dict:
    """
    Prédit la gravité d'un accident routier.

    Args:
        input: Données de l'accident

    Returns:
        Prédiction avec gravité et probabilités
    """
    try:
        start_time = time.time()

        data: dict[str, float] = {col: 0.0 for col in columns}

        data["heure"] = float(input.heure)
        data["lum"] = float(input.lum)
        data["atm"] = float(input.atm)
        data["age"] = float(input.age)
        data["catr"] = float(input.catr)
        data["agg"] = float(input.agg)
        data["sexe"] = float(input.sexe)
        data["catv"] = float(input.catv)
        data["nuit"] = 1.0 if (input.heure >= 22 or input.heure <= 6) else 0.0
        data["jeune_conducteur"] = 1.0 if input.age < 25 else 0.0
        data["conditions_dangereuses"] = (
            1.0 if (input.atm in [2, 3, 4, 5, 6] or input.lum in [3, 4]) else 0.0
        )

        df = pd.DataFrame([data])[columns]
        prediction = int(model.predict(df)[0])
        probabilities = model.predict_proba(df)[0]

        inference_duration = time.time() - start_time
        model_inference_duration_seconds.observe(inference_duration)

        gravite = "Grave" if prediction == 1 else "Non grave"
        proba_grave = round(float(probabilities[1]) * 100, 1)
        proba_non_grave = round(float(probabilities[0]) * 100, 1)

        predictions_total.labels(gravite=gravite).inc()
        probability_histogram.labels(gravite=gravite).observe(probabilities[1])

        return {
            "gravite": gravite,
            "probabilite_grave": proba_grave,
            "probabilite_non_grave": proba_non_grave,
        }
    
    except ValueError as e:
        http_errors_total.labels(error_type="validation", endpoint="/predict").inc()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        http_errors_total.labels(error_type="server_error", endpoint="/predict").inc()
        raise HTTPException(status_code=500, detail=str(e))
