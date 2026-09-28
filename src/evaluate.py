"""Quality gate on the exact model.pkl that will be shipped.

Raises ValueError below the accuracy threshold, which fails the job and therefore
blocks the Docker build. Only passing versions get the `champion` alias.
"""
import json
import os

import joblib
from mlflow.tracking import MlflowClient
from sklearn.metrics import accuracy_score

from train import MODEL_DIR, sha256, load_split

THRESHOLD = 0.90


def main():
    meta = json.loads((MODEL_DIR / "metadata.json").read_text())
    pkl = MODEL_DIR / "model.pkl"
    if sha256(pkl) != meta["model_sha256"]:
        raise ValueError("model.pkl does not match metadata checksum")

    _, x_te, _, y_te = load_split()
    acc = float(accuracy_score(y_te, joblib.load(pkl).predict(x_te)))
    passed = acc >= THRESHOLD
    metrics = {"test_accuracy": acc, "threshold": THRESHOLD, "passed": passed}
    (MODEL_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))

    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as fh:
            fh.write(f"### Model gate\nversion `{meta['model_version']}` "
                     f"accuracy **{acc:.4f}** (threshold {THRESHOLD}) "
                     f"{'PASSED' if passed else 'FAILED'}\n")

    client = MlflowClient()
    client.log_metric(meta["mlflow_run_id"], "test_accuracy", acc)
    client.set_model_version_tag(meta["model_name"], meta["model_version"],
                                 "validation", "passed" if passed else "failed")
    if not passed:
        raise ValueError(f"Accuracy {acc:.4f} below {THRESHOLD}; blocking image build.")
    client.set_registered_model_alias(meta["model_name"], "champion", meta["model_version"])


if __name__ == "__main__":
    main()
