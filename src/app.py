"""FastAPI inference service serving the model.pkl baked into the image."""
import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

log = logging.getLogger("inference")
MODEL_DIR = Path(os.getenv("MODEL_DIR", "/app/model"))
COLS = ["sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"]
state = {"model": None, "metadata": {}}


@asynccontextmanager
async def lifespan(_app):
    try:
        state["model"] = joblib.load(MODEL_DIR / "model.pkl")
        state["metadata"] = json.loads((MODEL_DIR / "metadata.json").read_text())
        log.info("loaded model version %s", state["metadata"].get("model_version"))
    except Exception:
        log.exception("model load failed")  # /health returns 503 until fixed
    yield


app = FastAPI(title="ml-model-service", lifespan=lifespan)


class Features(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


def _require_model():
    if state["model"] is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    return state["model"]


@app.get("/health")
def health():
    _require_model()
    return {"status": "ok", "model_version": state["metadata"].get("model_version")}


@app.get("/version")
def version():
    _require_model()
    return state["metadata"]


@app.post("/predict")
def predict(f: Features):
    model = _require_model()
    row = pd.DataFrame([[f.sepal_length, f.sepal_width, f.petal_length, f.petal_width]],
                       columns=COLS)
    return {"class": int(model.predict(row)[0])}
