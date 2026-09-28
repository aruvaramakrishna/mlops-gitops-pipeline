# 🚀 MLOps GitOps Pipeline: Production-Ready ML Deployment

**Complete end-to-end MLOps system** with data versioning, experiment tracking, automated quality gates, and GitOps deployment.

> 📊 **Interview-ready**: See [WORKFLOW.md](WORKFLOW.md) for flow diagrams | [ARCHITECTURE.md](ARCHITECTURE.md) for system design | [LINKEDIN.md](LINKEDIN.md) for talking points

## ⭐ Key Features

✅ **Data Versioning** — DVC tracks datasets in Azure Blob (reproducible training)  
✅ **Experiment Tracking** — MLflow logs all training runs, metrics, artifacts  
✅ **Quality Gates** — Accuracy >= 90% or deployment is blocked  
✅ **Automated CI/CD** — GitHub Actions with OIDC (no stored credentials)  
✅ **Security First** — Trivy scanning, checksum verification, non-root containers  
✅ **GitOps Deployment** — ArgoCD auto-syncs; `git revert` for instant rollback  
✅ **Zero-Downtime Updates** — Blue-green rolling deployments  
✅ **Full Lineage** — Pod → model → data → code completely traceable  
✅ **Production Hardened** — Kubernetes security context, resource limits, health probes  
✅ **Comprehensive Docs** — 8 markdown files covering every aspect  

---

## 📚 Documentation Hub

| Document | Purpose |
|----------|---------|
| **[WORKFLOW.md](WORKFLOW.md)** | 📊 Complete pipeline flow diagram + decision points + timing (12 min read) |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | 🏗️ System components, data flow, resilience patterns (15 min read) |
| **[STANDARDS.md](STANDARDS.md)** | ✅ Production standards, security practices, quality metrics (10 min read) |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | 🤝 How to contribute, code standards, PR process (5 min read) |
| **[SECURITY.md](SECURITY.md)** | 🔒 Security policy, incident response, best practices (8 min read) |
| **[LINKEDIN.md](LINKEDIN.md)** | 💼 Interview talking points, resume highlights, LinkedIn post template (10 min read) |
| **[CHANGELOG.md](CHANGELOG.md)** | 📝 Version history and release notes |

---

## 🎯 Quick Navigation

- **New to MLOps?** → Start with [ARCHITECTURE.md](ARCHITECTURE.md) (system overview)
- **Want to understand the pipeline?** → Read [WORKFLOW.md](WORKFLOW.md) (visual flow)
- **Preparing for interviews?** → Check [LINKEDIN.md](LINKEDIN.md) (talking points + Q&A)
- **Contributing code?** → See [CONTRIBUTING.md](CONTRIBUTING.md) (standards + process)
- **Need security info?** → Review [SECURITY.md](SECURITY.md) (practices + incident response)
- **Want to verify standards?** → Consult [STANDARDS.md](STANDARDS.md) (quality checklist)

Replace `yourregistryname` (in `k8s/`), `<org>` and `<repo>` (in `argocd-app.yaml`) before deploying.

## Flow
```
push to main -> lint+tests -> dvc pull -> train.py -> evaluate.py (>=90% or ValueError)
   -> upload model-bundle artifact (model.pkl, sha256, metadata.json, metrics.json)
   -> download bundle -> verify sha256 -> docker build (COPY model.pkl) -> Trivy scan
   -> push to ACR (tag = short SHA) -> tag MLflow model version with image digest
   -> kustomize edit set image -> commit [skip ci] -> ArgoCD syncs AKS
```

## Layout
```
.github/workflows/mlops-aks-pipeline.yml
src/{train.py, evaluate.py, app.py}     tests/test_app.py
k8s/{deployment.yaml, service.yaml, kustomization.yaml}
argocd-app.yaml  Dockerfile  .dockerignore
requirements.txt (CI)  requirements-serve.txt (image)
data/ (DVC pointers)  models/ (build output, git-ignored)
```

## Governance boundaries
| Tool | Owns | Never owns |
|---|---|---|
| Git | Code, pipeline, manifests, DVC pointers; audit trail of desired state | Datasets, model binaries |
| DVC | Dataset versions in Azure Blob, pinned by hash in `data/*.dvc` | Models, deploy state |
| MLflow | Experiments, metrics, registry versions, `champion` alias, image-digest tag per version | Cluster state |
| ArgoCD | Reconciling `k8s/` to AKS (sync, prune, self-heal) | Building or training |

## 🔗 How DVC & MLflow Connect

DVC and MLflow have separate responsibilities; the training pipeline connects them. DVC makes the exact dataset available to the job, and `train.py` records that dataset's SHA-256 in MLflow so each run can be traced back to its input data.

```mermaid
flowchart LR
  Git["Git commit\ncode + data/iris.csv.dvc"] -->|dvc pull| DVC["DVC remote\nAzure Blob dataset"]
  DVC -->|restores pinned data/iris.csv| Train["src/train.py"]
  Train -->|logs params, metrics, model, metadata| MLflow["MLflow Tracking\nexperiment run"]
  Train -->|registers model| Registry["MLflow Model Registry"]
  MLflow --> Eval["src/evaluate.py"]
  Eval -->|logs test accuracy; tags validation| Registry
  Registry -->|passing version gets champion alias| Bundle["Validated model bundle"]
  Bundle --> Image["Docker image in ACR"]
  Image -->|image digest recorded as model-version tag| Registry
```

### What happens at each handoff

1. **Git pins the data version.** Git tracks `data/iris.csv.dvc`, a small DVC pointer, rather than relying on a dataset copy inside the training code. The pointer identifies the data version stored in the configured DVC remote.
2. **DVC restores the data.** In CI, `dvc pull` uses that pointer and the Azure storage credentials supplied to the workflow to restore `data/iris.csv`.
3. **Training links the data to a run.** `src/train.py` reads `data/iris.csv`, computes its SHA-256, and logs it as the `data_sha256` MLflow run tag and in `models/metadata.json`. It also logs parameters, metrics, model artifacts, and registers the model.
4. **Evaluation records the quality decision.** `src/evaluate.py` evaluates the same model artifact, logs `test_accuracy`, and tags the registered version as passed or failed. Only a passing version gets the `champion` alias.
5. **Deployment lineage is attached.** The validated model bundle is built into an image. The workflow records the pushed image reference on the MLflow model version, connecting the registry entry to the deployed image.

**Hash detail:** the hash in a DVC pointer identifies DVC-managed content; `data_sha256` is a separate SHA-256 computed by `train.py` and logged for run lineage. They serve different purposes and should not be expected to match.

### How this project connects to MLflow

The MLflow Python client reads its connection settings from environment variables. In GitHub Actions, the workflow maps repository secrets to `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_USERNAME`, and `MLFLOW_TRACKING_PASSWORD`. `train.py` calls `mlflow.set_experiment("iris-training")` and starts a run; the client sends parameters, metrics, tags, and artifacts to that tracking server. `evaluate.py` creates an `MlflowClient` using the same tracking URI and adds the held-out test metric and model-version validation tag.

For local development, point the client at a running server:

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
# Set these only when the tracking server requires authentication.
export MLFLOW_TRACKING_USERNAME=your-username
export MLFLOW_TRACKING_PASSWORD=your-password
mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db
```

`mlflow-config.yaml` is a reference file; the Python scripts do not parse it. The active connection is made through MLflow's environment-variable configuration. For hosted tracking, configure the server's artifact store and registry backend as part of the server deployment; the client logs artifacts through the tracking server.

### Metrics currently logged

| Metric | Where it is calculated | Meaning |
|---|---|---|
| `train_accuracy` | `src/train.py` | Accuracy on the training split; useful for seeing fit on data used to train. |
| `cv_accuracy` | `src/train.py` | Mean accuracy from 5-fold cross-validation over the training split. |
| `test_accuracy` | `src/evaluate.py` | Accuracy on the held-out test split; compared with the `0.90` deployment threshold. |

All three are MLflow metrics attached to the training run. The test metric is logged before the quality gate raises an error on a failing score. `models/metrics.json` also records `threshold` and `passed`, but those two fields are currently written to the local/GitHub model bundle, not logged as MLflow metrics.

The run also stores parameters (`n_estimators`, `max_depth`, `random_state`) and lineage tags (`git_sha`, `data_sha256`). Those are **parameters and tags**, not metrics. The code does not currently calculate precision, recall, F1, a confusion matrix, per-class scores, inference latency, or data/model drift; add those explicitly if they are needed for evaluation or production monitoring.

In short: **DVC answers “which data version?”; MLflow answers “what happened when this version was trained and evaluated?”** The Git commit, DVC pointer, MLflow run ID, model version, and image reference form the traceability chain.

## Model tracking (how the .pkl is traced end to end)
- `train.py` writes `models/model.pkl`, its SHA-256, and `metadata.json` (MLflow run id, model version, git SHA, dataset hash, params). The pkl and metadata are also logged as MLflow artifacts, and the model is registered in the Model Registry.
- `evaluate.py` re-checks the checksum, scores that exact pkl, logs `test_accuracy` to the run, tags the version `validation=passed|failed`, and sets alias `champion` only on success.
- The bundle travels as the `model-bundle` GitHub artifact. The build job verifies the checksum, then `COPY models/model.pkl` bakes it into the image. Image labels carry git SHA, model name/version and MLflow run id.
- After the push, the MLflow model version gets an `image` tag holding the ACR digest. Any running pod maps back to its model, data and commit via `GET /version`.

## Quick Start (Local Development)

### Prerequisites
```bash
# Install DVC, MLflow, and dependencies
pip install -r requirements.txt

# For local Azure CLI (if using real Azure backend)
# az login
```

### 1. Initialize DVC & MLflow Locally

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings:
# - For local dev: MLFLOW_TRACKING_URI=http://localhost:5000
# - For Azure: set AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_CONNECTION_STRING
source .env

# Start MLflow tracking server locally (in a separate terminal)
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db

# Initialize DVC (already done, but here's the pattern)
# dvc init
```

### 2. Run the Training Pipeline

```bash
# Option A: Run individual scripts (development)
python src/train.py          # Trains model, logs to MLflow, outputs model.pkl + metadata.json
python src/evaluate.py       # Quality gate: checks accuracy >= 90%, tags model as champion

# Option B: Run full DVC pipeline (reproducibility)
dvc repro                    # Executes stages defined in dvc.yaml

# View the pipeline DAG
dvc dag

# View metrics
dvc metrics show models/metrics.json

# View the experiment in MLflow UI
# Open: http://localhost:5000
```

### 3. Serve Predictions Locally

```bash
# Set model directory for the app
export MODEL_DIR=models

# Start the FastAPI server
python -m uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload

# Test a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'

# Check model version
curl http://localhost:8000/version
```

---

## Production Setup (Azure)

### 1. Provision storage, attach DVC, track data
```bash
RG=rg-mlops; LOC=westeurope; SA=stmlopsdvc$RANDOM; CONT=dvc
az group create -n $RG -l $LOC
az storage account create -n $SA -g $RG -l $LOC --sku Standard_LRS \
  --min-tls-version TLS1_2 --allow-blob-public-access false
az storage container create --account-name $SA -n $CONT --auth-mode login

dvc init
dvc remote add -d azremote azure://$CONT/dvcstore
dvc remote modify azremote account_name $SA
export AZURE_STORAGE_CONNECTION_STRING=$(az storage account show-connection-string -n $SA -g $RG -o tsv)

# Update .env with credentials
sed -i "s|stmlopsdvc123|$SA|" .env
sed -i "s|DefaultEndpointsProtocol=...|$AZURE_STORAGE_CONNECTION_STRING|" .env

# Load sample iris data
python -c "from sklearn.datasets import load_iris; load_iris(as_frame=True).frame.to_csv('data/iris.csv', index=False)"

# Track with DVC
dvc add data/iris.csv
git add data/iris.csv.dvc data/.gitignore .dvc .dvcignore .dvcignore
git commit -m "track iris dataset with DVC" 

# Push to Azure Blob Storage
dvc push

# Verify
dvc status
```

## 2. MLflow Setup (Experiment Tracking & Model Registry)

### Option A: Local MLflow (Development)
```bash
# Start server with SQLite backend (local only)
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db

# In train.py and evaluate.py, env var auto-connects:
export MLFLOW_TRACKING_URI=http://localhost:5000

# View UI: http://localhost:5000
```

### Option B: Cloud MLflow (Production - Azure ML or hosted)

#### Using Azure ML Workspace
```bash
# Create Azure ML workspace
az ml workspace create -n ml-ops-ws -g $RG -l $LOC

# Get MLflow URI (auto-generated)
MLFLOW_URI=$(az ml workspace show -n ml-ops-ws -g $RG --query mlflow_tracking_uri -o tsv)
echo "MLflow Tracking URI: $MLFLOW_URI"

# Set in GitHub Secrets
gh secret set MLFLOW_TRACKING_URI --body "$MLFLOW_URI"
gh secret set MLFLOW_TRACKING_USERNAME --body "your-username"
gh secret set MLFLOW_TRACKING_PASSWORD --body "your-password"
```

#### Using Self-Hosted MLflow (PostgreSQL + S3/Azure Blob)
```bash
# Backend store (persistent runs/models)
az postgres server create -n mlflow-db -g $RG -u dbadmin -p SecurePassword123!

# Artifact store (model files)
az storage container create --account-name $SA -n mlflow-artifacts --auth-mode login

# Start MLflow with remote backends
export MLFLOW_BACKEND_STORE_URI="postgresql://user:password@mlflow-db:5432/mlflow"
export MLFLOW_DEFAULT_ARTIFACT_ROOT="azure://mlflow-artifacts"

mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri $MLFLOW_BACKEND_STORE_URI \
  --default-artifact-root $MLFLOW_DEFAULT_ARTIFACT_ROOT
```

### How train.py Logs to MLflow
```python
# Automatic via environment variables (in CI/CD)
import mlflow
mlflow.set_experiment("iris-training")

with mlflow.start_run() as run:
    # Log parameters
    mlflow.log_params({"n_estimators": 150, "max_depth": 5})
    
    # Log metrics
    mlflow.log_metric("accuracy", 0.96)
    
    # Register model in registry
    mlflow.sklearn.log_model(model, "model", registered_model_name="iris-classifier")
    
    # Log artifacts (model.pkl, metadata.json)
    mlflow.log_artifact("models/model.pkl")
    mlflow.log_artifact("models/metadata.json")
    
    print(f"Run ID: {run.info.run_id}")
```

### How evaluate.py Tags & Promotes Models
```python
# Quality gate: only passing versions get champion alias
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Tag version with validation result
client.set_model_version_tag(
    "iris-classifier", 
    version="1", 
    tag="validation", 
    value="passed"
)

# Promote to production (champion alias)
client.set_registered_model_alias(
    "iris-classifier", 
    alias="champion", 
    version="1"
)

# Fail the job if accuracy < threshold (blocks image build)
if accuracy < THRESHOLD:
    raise ValueError(f"Accuracy {accuracy} below {THRESHOLD}")
```

---

## 2. GitHub Configuration (CI/CD)

Secrets to configure in GitHub (Settings → Secrets and variables → Actions):
- [ ] `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` (OIDC; federated credential for `repo:<org>/<repo>:ref:refs/heads/main`; role `AcrPush` on the registry)
- [ ] `MLFLOW_TRACKING_URI` (e.g., `https://your-workspace.eastus.inference.ml.azure.com`)
- [ ] `MLFLOW_TRACKING_USERNAME` (Service principal username or token)
- [ ] `MLFLOW_TRACKING_PASSWORD` (Service principal password or token)
- [ ] `DVC_AZURE_STORAGE_CONNECTION_STRING` (From `az storage account show-connection-string`)

Repository variables:
- [ ] `ACR_NAME` (registry name without `.azurecr.io`)

Optional: create environment `production` with required reviewers for manual release gate.

### GitHub Actions Workflow
See `.github/workflows/mlops-aks-pipeline.yml` (not included; create from template below):

```yaml
name: MLOps Pipeline

on:
  push:
    branches: [main]

jobs:
  train-and-build:
    runs-on: ubuntu-latest
    environment: production
    
    permissions:
      id-token: write
      contents: read
    
    steps:
      - uses: actions/checkout@v4
      
      # Authenticate to Azure using OIDC (no stored credentials)
      - uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      # Lint & test
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          pip install -r requirements.txt
          flake8 src/ tests/
          pytest tests/
      
      # DVC: pull latest data
      - run: |
          dvc pull
        env:
          DVC_AZURE_STORAGE_CONNECTION_STRING: ${{ secrets.DVC_AZURE_STORAGE_CONNECTION_STRING }}
      
      # Train & evaluate with MLflow
      - run: |
          python src/train.py
          python src/evaluate.py
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
          MLFLOW_TRACKING_USERNAME: ${{ secrets.MLFLOW_TRACKING_USERNAME }}
          MLFLOW_TRACKING_PASSWORD: ${{ secrets.MLFLOW_TRACKING_PASSWORD }}
          GITHUB_SHA: ${{ github.sha }}
      
      # Upload model artifact
      - uses: actions/upload-artifact@v3
        with:
          name: model-bundle
          path: models/
      
      # Docker build & push
      - run: |
          docker buildx build --push \
            -t ${{ vars.ACR_NAME }}.azurecr.io/ml-model-service:${{ github.sha }} \
            -t ${{ vars.ACR_NAME }}.azurecr.io/ml-model-service:latest \
            .
      
      # Update k8s deployment (triggers ArgoCD sync)
      - run: |
          git config user.email "actions@github.com"
          git config user.name "GitHub Actions"
          
          kustomize edit set image ml-model-service=${{ vars.ACR_NAME }}.azurecr.io/ml-model-service:${{ github.sha }}
          
          git add k8s/kustomization.yaml
          git commit -m "Update image: ${{ github.sha }} [skip ci]"
          git push
        working-directory: k8s
```

## 3. Connect Git to ArgoCD
```bash
kubectl create namespace argocd
kubectl apply -n argocd --server-side -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Add GitHub repo
argocd repo add https://github.com/<org>/<repo>.git \
  --username <user> \
  --password <PAT>   # private repos only

# Deploy the app
kubectl apply -f argocd-app.yaml

# Monitor
argocd app get ml-model-service
argocd app logs ml-model-service --follow
```

---

## Architecture: How Data & Models Flow Through the System

### 1. **Data Versioning with DVC** 🔄
```
git push → dvc.yaml (pipeline definition)
           ↓
         dvc repro → load data/iris.csv (tracked by DVC)
           ↓
         DVC checks metadata: is data up-to-date?
           ↓
         (if needed) dvc pull → download from Azure Blob via .dvc pointer
```

**Files involved:**
- `data/iris.csv` — Raw dataset (git-ignored, stored in Azure Blob)
- `data/iris.csv.dvc` — DVC pointer & metadata (tracked in Git)
- `.dvc/config` — Remote storage config (Azure Blob)
- `dvc.yaml` — Pipeline DAG (train stage → evaluate stage)

**Benefits:**
- Reproducible: exact data version pinned by hash
- Efficient: don't re-download unchanged data
- Auditable: all data versions in Azure Blob; lineage in Git

### 2. **Model Training & Experiment Tracking with MLflow** 📊

```
src/train.py
├── Load data/iris.csv
├── Train RandomForestClassifier
├── mlflow.start_run()
│   ├── Log params: n_estimators=150, max_depth=5
│   ├── Log metrics: train_accuracy=0.986, cv_accuracy=0.973
│   ├── Log artifacts: model.pkl, metadata.json
│   └── Register model: iris-classifier v1
│
└── Output files:
    ├── models/model.pkl (the serialized model)
    ├── models/model.pkl.sha256 (for verification)
    └── models/metadata.json (lineage: run_id, git_sha, data_sha, etc.)
```

**MLflow tracks:**
- Parameters: hyperparameters that control training
- Metrics: accuracy, loss, etc. (updated during training)
- Artifacts: model.pkl, plots, datasets
- Metadata: git commit, data hash, timestamp (in metadata.json)

### 3. **Quality Gate with evaluate.py** ✅

```
src/evaluate.py
├── Load models/model.pkl (exact file from train.py)
├── Re-verify SHA-256 checksum (ensure no corruption)
├── Score on held-out test set
│
├── If accuracy >= 90%: PASS ✅
│   ├── Log test_accuracy to MLflow
│   ├── Tag model version: validation=passed
│   └── Set alias: champion=v1 (production-ready)
│
└── If accuracy < 90%: FAIL ❌
    ├── Log test_accuracy to MLflow
    ├── Tag model version: validation=failed
    └── Raise ValueError → fail CI/CD job
       (prevents image build & deployment)
```

### 4. **Docker Image Build** 🐳

```
Dockerfile
├── FROM python:3.11-slim
├── COPY requirements-serve.txt
├── RUN pip install -r requirements-serve.txt
│
├── COPY models/model.pkl /app/model/  ← Bake the exact .pkl
├── COPY models/metadata.json /app/model/
│
├── LABEL model_version="1"
├── LABEL mlflow_run_id="a1b2c3d4..."
├── LABEL git_sha="abc123..."
│
└── CMD ["uvicorn", "app:app"]
```

**Why embed model.pkl in image:**
- Model is immutable once container runs
- Version = Docker image digest
- Easy rollback: just point to previous image tag
- Fast startup (no download latency)

### 5. **Push to Registry & Tag with Model Metadata** 🏗️

```
docker push acr.azurecr.io/ml-model-service:abc123...
              ↓
Image digest: sha256:f1f2f3f4f5f6...

# Tag MLflow model version with image digest
mlflow.tracking.MlflowClient().set_model_version_tag(
    "iris-classifier",
    version="1",
    tag="image",
    value="sha256:f1f2f3f4f5f6..."
)

# Now the model registry knows: v1 → image digest → container → running pod
```

### 6. **GitOps Deployment with ArgoCD** 🚀

```
GitHub (kustomization.yaml)
├── image: acr.azurecr.io/ml-model-service:abc123
│
ArgoCD (watches repo)
├── Detects change → syncs to AKS
├── Pulls image from ACR
├── Deploys new pods
├── Old pods → terminated (blue-green rollout)
│
Running pod
├── Loads /app/model/model.pkl (embedded in image)
├── Responds to HTTP /predict requests
├── Returns model_version via GET /version
│   (maps pod → model version → image digest → training run)
```

**Traceability:** `pod → image digest → metadata.json → mlflow_run_id → training data hash → DVC pointer → Azure Blob`

---

## Governance Boundaries

| Tool | Owns | Never owns |
|---|---|---|
| **Git** | Code, pipeline, manifests, DVC pointers, metadata; audit trail of desired state | Datasets, model binaries |
| **DVC** | Dataset versions in Azure Blob, pinned by hash in `data/*.dvc` | Models, deploy state |
| **MLflow** | Experiments, metrics, registry versions, `champion` alias, image-digest tag | Cluster state |
| **ArgoCD** | Reconciling `k8s/` to AKS (sync, prune, self-heal) | Building or training |

---

## Troubleshooting

### DVC Issues
```bash
# Check DVC status
dvc status

# Show DAG
dvc dag

# Inspect .dvc file
cat data/iris.csv.dvc

# Re-download data
dvc pull --verbose

# List remote storage contents
dvc remote list-cache
```

### MLflow Issues
```bash
# Check tracking server connection
curl $MLFLOW_TRACKING_URI/api/2.0/health

# View experiments
mlflow experiments search

# View a specific run
mlflow runs describe --experiment-name iris-training --run-id <run_id>

# Check model registry
mlflow models search

# List versions of a model
mlflow models versions-search --name iris-classifier
```

### Model Loading in App
```python
# Debug model loading (src/app.py lifespan)
import joblib
import json
from pathlib import Path

MODEL_DIR = Path("/app/model")
print("Files:", list(MODEL_DIR.glob("*")))

model = joblib.load(MODEL_DIR / "model.pkl")
print("Model loaded:", model)

metadata = json.loads((MODEL_DIR / "metadata.json").read_text())
print("Metadata:", metadata)
```

## Best Practices Included
- **Least-privilege** permissions per job; OIDC (no stored Azure credentials)
- **Pinned dependencies**, actions and kustomize for reproducibility
- **Identical sklearn/joblib versions** in CI and image (pickle compatibility)
- **Checksum-verified artifact** (model.pkl.sha256) — corruption detected immediately
- **Quality gate** on shipped file (evaluate.py blocks build if accuracy < threshold)
- **Trivy scan** before push to registry (vulnerability detection)
- **BuildKit cache** and provenance for faster, traceable builds
- **Non-root** read-only container with health probes and zero-downtime rollout
- **Concurrency lock** and rebase-before-push on manifest commit (prevent race conditions)
- **[skip ci]** tag and path filters (avoid training on manifest-only changes)
- **Rollback**: `git revert` the promotion commit → ArgoCD restores previous image → model + data
- **Data versioning**: DVC tracks exact dataset; train/eval always use same split (seeded)
- **Model lineage**: metadata.json embeds git_sha, data_sha, mlflow_run_id → full audit trail
- **Champion alias**: MLflow marks production-ready model version → app fetches automatically
