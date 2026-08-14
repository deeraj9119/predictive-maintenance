import pickle
from pathlib import Path
from typing import Literal

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "predictive_maintenance_model.pkl"

app = FastAPI(title="Predictive Maintenance API", version="1.0")


class MaintenanceInput(BaseModel):
    Type: Literal["L", "M", "H"] = Field(..., description="Product quality type")
    air_temperature_k: float = Field(..., ge=250, le=350)
    process_temperature_k: float = Field(..., ge=250, le=400)
    rotational_speed_rpm: float = Field(..., ge=0)
    torque_nm: float = Field(..., ge=0)
    tool_wear_min: float = Field(..., ge=0)


def load_model_bundle():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found at {MODEL_PATH}. Run the notebook first to create the pickle model."
        )

    with open(MODEL_PATH, "rb") as file:
        bundle = pickle.load(file)

    if isinstance(bundle, dict) and "model" in bundle:
        return bundle

    return {
        "model_name": "Unknown model",
        "model": bundle,
        "selection_metric": "unknown",
        "test_metrics": {},
    }


model_bundle = load_model_bundle()
model = model_bundle["model"]


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "model_name": model_bundle.get("model_name"),
        "selection_metric": model_bundle.get("selection_metric"),
    }


@app.post("/predict")
def predict_failure(payload: MaintenanceInput):
    try:
        # Column names must match the training notebook exactly.
        input_df = pd.DataFrame(
            [
                {
                    "Type": payload.Type,
                    "Air temperature [K]": payload.air_temperature_k,
                    "Process temperature [K]": payload.process_temperature_k,
                    "Rotational speed [rpm]": payload.rotational_speed_rpm,
                    "Torque [Nm]": payload.torque_nm,
                    "Tool wear [min]": payload.tool_wear_min,
                }
            ]
        )

        prediction = int(model.predict(input_df)[0])
        probability = None
        if hasattr(model, "predict_proba"):
            probability = float(model.predict_proba(input_df)[0][1])

        return {
            "prediction": prediction,
            "prediction_label": "Failure" if prediction == 1 else "No Failure",
            "failure_probability": probability,
            "model_name": model_bundle.get("model_name"),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
