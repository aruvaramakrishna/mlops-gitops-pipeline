"""MLflow Utilities

Helpers for logging, model management, and tracking integration.
Used by train.py and evaluate.py for experiment tracking.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import mlflow
from mlflow.tracking import MlflowClient


def configure_mlflow(
    tracking_uri: Optional[str] = None,
    experiment_name: str = "default",
    backend_store_uri: Optional[str] = None,
):
    """Configure MLflow tracking server connection.
    
    Args:
        tracking_uri: MLflow server URI (env MLFLOW_TRACKING_URI)
        experiment_name: Experiment to log runs to
        backend_store_uri: Backend store for model registry persistence
    """
    if not tracking_uri:
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    
    if backend_store_uri:
        client = MlflowClient(tracking_uri)
        # Configure if needed


def log_model_metadata(
    model_dir: Path,
    model_name: str,
    model_version: str,
    run_id: str,
    git_sha: str,
    data_sha: str,
    model_sha: str,
    params: Dict[str, Any],
):
    """Write model metadata JSON file.
    
    Metadata is:
    - Logged as MLflow artifact
    - Baked into Docker image
    - Used for audit trail and reproducibility
    """
    from datetime import datetime, timezone
    
    metadata = {
        "model_name": model_name,
        "model_version": model_version,
        "mlflow_run_id": run_id,
        "git_sha": git_sha,
        "data_sha256": data_sha,
        "model_sha256": model_sha,
        "params": params,
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    
    metadata_file = model_dir / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2))
    mlflow.log_artifact(str(metadata_file), artifact_path="model")
    
    return metadata


def get_champion_model_version(model_name: str) -> Optional[str]:
    """Fetch the 'champion' model version from registry.
    
    Returns: Version number or None if not set
    """
    try:
        client = MlflowClient()
        model = client.get_registered_model(model_name)
        
        for alias in model.aliases:
            if alias.alias == "champion":
                return alias.version
    except Exception as e:
        print(f"Could not fetch champion model: {e}")
    
    return None


def set_model_alias(
    model_name: str,
    version: str,
    alias_name: str = "champion",
):
    """Set or update a model alias (e.g., 'champion', 'staging').
    
    Used for promoting model versions through the ML lifecycle.
    """
    client = MlflowClient()
    client.set_registered_model_alias(model_name, alias_name, version)
    print(f"Set {alias_name} -> version {version}")


def tag_model_version(
    model_name: str,
    version: str,
    tag: str,
    value: str,
):
    """Tag a model version for governance and tracking.
    
    Examples:
      - validation: passed | failed
      - env: development | staging | production
      - approval: pending | approved | rejected
    """
    client = MlflowClient()
    client.set_model_version_tag(model_name, version, tag, value)
    print(f"Tagged version {version}: {tag}={value}")
