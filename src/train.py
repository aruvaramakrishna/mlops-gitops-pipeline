"""Train the Iris model, log to MLflow, register it, and emit a model.pkl bundle.

Outputs (in models/), later shipped as a GitHub artifact and baked into the image:
  model.pkl, model.pkl.sha256, metadata.json
"""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, train_test_split

MODEL_NAME = "iris-classifier"
EXPERIMENT = "iris-training"
DATA_PATH = Path("data/iris.csv")
MODEL_DIR = Path("models")
PARAMS = {"n_estimators": 150, "max_depth": 5, "random_state": 42}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_split():
    """Deterministic split shared with evaluate.py."""
    df = pd.read_csv(DATA_PATH)
    x, y = df.drop(columns="target"), df["target"]
    return train_test_split(x, y, test_size=0.2, stratify=y, random_state=42)


def main():
    # Tracking URI and credentials come from MLFLOW_* environment variables.
    mlflow.set_experiment(EXPERIMENT)
    MODEL_DIR.mkdir(exist_ok=True)
    x_tr, _, y_tr, _ = load_split()
    git_sha = os.getenv("GITHUB_SHA", "local")

    with mlflow.start_run() as run:
        mlflow.set_tags({"git_sha": git_sha, "data_sha256": sha256(DATA_PATH)})
        mlflow.log_params(PARAMS)

        model = RandomForestClassifier(**PARAMS).fit(x_tr, y_tr)
        mlflow.log_metric("train_accuracy", model.score(x_tr, y_tr))
        mlflow.log_metric("cv_accuracy", cross_val_score(model, x_tr, y_tr, cv=5).mean())

        # 1) The deployable artifact: a plain pickle that goes into the image.
        pkl = MODEL_DIR / "model.pkl"
        joblib.dump(model, pkl)
        (MODEL_DIR / "model.pkl.sha256").write_text(f"{sha256(pkl)}  model.pkl\n")
        mlflow.log_artifact(str(pkl), artifact_path="pkl")

        # 2) The same model registered in the MLflow Model Registry (lineage).
        mlflow.sklearn.log_model(
            model, "model",
            signature=infer_signature(x_tr, model.predict(x_tr)),
            registered_model_name=MODEL_NAME,
        )
        client = MlflowClient()
        version = next(v.version for v in client.search_model_versions(f"name='{MODEL_NAME}'")
                       if v.run_id == run.info.run_id)

        metadata = {
            "model_name": MODEL_NAME,
            "model_version": version,
            "mlflow_run_id": run.info.run_id,
            "git_sha": git_sha,
            "data_sha256": sha256(DATA_PATH),
            "model_sha256": sha256(pkl),
            "params": PARAMS,
            "trained_at": datetime.now(timezone.utc).isoformat(),
        }
        (MODEL_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2))
        mlflow.log_artifact(str(MODEL_DIR / "metadata.json"), artifact_path="pkl")
        print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
