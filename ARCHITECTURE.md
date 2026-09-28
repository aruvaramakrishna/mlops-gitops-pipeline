# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Developer Workflow                          │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    Push to main branch (GitHub)
                                  │
┌─────────────────────────────────────────────────────────────────────┐
│                       GitHub Actions (CI/CD)                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Job 1: Lint & Test                                            │  │
│  │  • Flake8 code quality check                                 │  │
│  │  • Pytest unit tests                                         │  │
│  │  • Fail fast on code issues                                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │ (needs: pass)                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Job 2: Train & Evaluate                                       │  │
│  │  • DVC pull (download dataset from Azure Blob)               │  │
│  │  • train.py → RandomForest classifier                        │  │
│  │  • MLflow logging (metrics, artifacts, registry)             │  │
│  │  • evaluate.py → Quality gate (accuracy ≥ 90%)              │  │
│  │  • Upload model-bundle GitHub artifact                       │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │ (needs: pass)                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Job 3: Build & Push                                           │  │
│  │  • Download model artifact                                    │  │
│  │  • Verify SHA-256 checksum                                   │  │
│  │  • Docker BuildKit → image with model embedded               │  │
│  │  • Trivy security scan                                        │  │
│  │  • Push to Azure Container Registry (ACR)                   │  │
│  │  • Tag MLflow model version with image digest                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │ (needs: pass)                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Job 4: GitOps Update                                          │  │
│  │  • Kustomize edit image tag                                  │  │
│  │  • Commit k8s/kustomization.yaml [skip ci]                  │  │
│  │  • Push to main branch                                        │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
         │                       │                         │
         │                       │                         │
    ┌────▼───────┐     ┌────────▼────────┐    ┌───────────▼────────┐
    │  DVC Remote │     │  MLflow Server  │    │  Azure Container   │
    │ (Azure Blob)│     │  (Tracking URI) │    │   Registry (ACR)   │
    │             │     │                 │    │                    │
    │ • Dataset   │     │ • Experiments   │    │ • Image layers     │
    │   versions  │     │ • Metrics       │    │ • Image digest     │
    │ • Data hash │     │ • Artifacts     │    │ • Tags/labels      │
    │ • Git linked│     │ • Model Registry│    │ • Security scans   │
    └─────────────┘     └─────────────────┘    └────────────────────┘
                                                          │
                                                          │
                                    ┌─────────────────────┴──────────────┐
                                    │                                    │
                    ┌───────────────────────────────────────────────────▼──┐
                    │               ArgoCD (GitOps)                        │
                    │  • Watches GitHub for kustomization changes         │
                    │  • Reconciles desired vs actual state               │
                    │  • Syncs manifests to AKS cluster                   │
                    └───────────────────────────────────────────────────┬──┘
                                                                        │
                    ┌───────────────────────────────────────────────────▼──┐
                    │             AKS Cluster (Kubernetes)                 │
                    │  ┌──────────────────────────────────────────────┐   │
                    │  │       ml-production namespace                │   │
                    │  │                                              │   │
                    │  │  ml-model-service Deployment (3 replicas)   │   │
                    │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │   │
                    │  │  │  Pod 1   │  │  Pod 2   │  │  Pod 3   │ │   │
                    │  │  │  Port    │  │  Port    │  │  Port    │ │   │
                    │  │  │  8000    │  │  8000    │  │  8000    │ │   │
                    │  │  │ /predict │  │ /predict │  │ /predict │ │   │
                    │  │  │ /health  │  │ /health  │  │ /health  │ │   │
                    │  │  └──────────┘  └──────────┘  └──────────┘ │   │
                    │  │                                              │   │
                    │  │  ClusterIP Service (ml-model-service:80)    │   │
                    │  │  → Distributes traffic to pods              │   │
                    │  └──────────────────────────────────────────────┘   │
                    │                                                       │
                    └───────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
            ┌───────▼──────────┐         ┌──────────▼───────┐
            │   Azure Monitor  │         │   Health Checks  │
            │                  │         │                  │
            │ • Pod metrics    │         │ • Readiness      │
            │ • Logs aggregated│         │ • Liveness       │
            │ • Alerts/dashboard         │ • Pod status     │
            └──────────────────┘         └──────────────────┘
```

---

## Components

### 1. **Data Layer** (DVC + Azure Blob)

```
┌────────────────────────────────────┐
│      Git Repository                │
├────────────────────────────────────┤
│ data/iris.csv.dvc (pointer)        │
│ .dvc/config (remote URL)           │
│ .dvcignore (ignore patterns)       │
└────────────────────────────────────┘
           │ (tracked by Git)
           │
           ▼
┌────────────────────────────────────┐
│   Azure Blob Storage               │
├────────────────────────────────────┤
│ dvc/dvcstore/                      │
│ ├─ ab/cdef123... (v1 dataset)      │
│ ├─ 12/3456789... (v2 dataset)      │
│ └─ ...                              │
└────────────────────────────────────┘

Key:
- DVC uses content-addressable storage (hash-based)
- `dvc pull` downloads dataset matching .dvc file hash
- Versions tracked by git commits to .dvc files
- Reproducible: same commit = same data
```

**Benefits:**
- Datasets never in Git (storage efficient)
- Version control without duplicating large files
- Easy rollback to previous data versions
- Audit trail via git history

---

### 2. **Training Layer** (Python + MLflow)

```
┌─────────────────────────────────────────────┐
│         training/ci-cd environment          │
├─────────────────────────────────────────────┤
│ src/train.py                                │
│  ├─ Load data/iris.csv (via DVC)            │
│  ├─ Train RandomForestClassifier            │
│  ├─ mlflow.start_run()                      │
│  │  ├─ Log params: n_estimators=150        │
│  │  ├─ Log metrics: accuracy=0.96          │
│  │  ├─ Log artifacts: model.pkl            │
│  │  └─ Register model: iris-classifier v1  │
│  └─ Output: models/model.pkl               │
│             models/metadata.json           │
│                                              │
│ src/evaluate.py (quality gate)              │
│  ├─ Load models/model.pkl                   │
│  ├─ Verify SHA-256 checksum                 │
│  ├─ Score on test set                       │
│  ├─ If accuracy >= 90%:                     │
│  │   ├─ Log test_accuracy to MLflow        │
│  │   ├─ Tag: validation=passed             │
│  │   └─ Set alias: champion=v1             │
│  └─ If accuracy < 90%: raise ValueError    │
│       (fails job, blocks deployment)        │
└─────────────────────────────────────────────┘
           │ (on success)
           ▼
┌─────────────────────────────────────────────┐
│     MLflow Tracking Server                  │
├─────────────────────────────────────────────┤
│ Experiment: iris-training                   │
│  ├─ Run 1 (2024-03-15 10:30)               │
│  │  ├─ Params: n_estimators=150            │
│  │  ├─ Metrics: accuracy=0.96              │
│  │  ├─ Artifacts: model.pkl, metadata.json │
│  │  ├─ Tags: validation=passed, image=...  │
│  │  └─ Status: completed                   │
│  └─ Model Registry:                        │
│     ├─ iris-classifier                    │
│     │  ├─ Version 1 (champion) ⭐         │
│     │  │  ├─ Source: run-id-1             │
│     │  │  └─ Tags: validation=passed      │
│     │  └─ Version 2 (candidate)            │
```

**Why MLflow?**
- Experiment tracking (compare runs)
- Model registry (central versioning)
- Artifact storage (model files, plots)
- Lineage tracking (reproducibility)
- Champion alias (production-ready marker)

---

### 3. **Container Layer** (Docker + ACR)

```
GitHub Actions (CI/CD)
        │
        ▼
┌──────────────────────────────────┐
│    Docker Build                  │
├──────────────────────────────────┤
│ FROM python:3.10-slim            │
│ RUN pip install -r ...           │
│ COPY src/app.py ./               │
│ COPY models/model.pkl ./         │  ◄─── Model embedded here
│ COPY models/metadata.json ./     │
│ USER 1001 (non-root)             │
│ CMD ["uvicorn", "src.app:app"]   │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│    Trivy Scan                    │
│    (vulnerability detection)     │
│                                  │
│    ✅ No HIGH/CRITICAL CVEs      │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  Docker Push to ACR              │
├──────────────────────────────────┤
│ acr.azurecr.io/                  │
│  ml-model-service:abc123...      │
│                                  │
│ Image digest:                    │
│ sha256:f1f2f3f4f5f6f7...        │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│   Tag MLflow Model Version       │
│   with Image Digest              │
│                                  │
│   set_model_version_tag(         │
│    "iris-classifier",            │
│    version="1",                  │
│    tag="image",                  │
│    value="sha256:f1f2...")       │
└──────────────────────────────────┘
```

**Key Design Decisions:**
- Model embedded in image (immutable deployment)
- Non-root user (security)
- Read-only filesystem (prevent tampering)
- Image digest = unique version identifier
- Trivy scan = security gate

---

### 4. **Kubernetes Layer** (AKS)

```
┌────────────────────────────────────────────────┐
│         AKS Cluster (Azure)                    │
├────────────────────────────────────────────────┤
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │  Namespace: ml-production                │ │
│  │                                          │ │
│  │  Deployment: ml-model-service (3 pods)  │ │
│  │  ├─ Pod 1: Running                      │ │
│  │  ├─ Pod 2: Running                      │ │
│  │  └─ Pod 3: Running                      │ │
│  │                                          │ │
│  │  Service: ml-model-service (80:8000)    │ │
│  │  ├─ Type: ClusterIP                     │ │
│  │  └─ Distributes traffic to pods         │ │
│  │                                          │ │
│  │  Security:                              │ │
│  │  ├─ Non-root user (1001)               │ │
│  │  ├─ Read-only filesystem               │ │
│  │  ├─ Drop capabilities (no root)        │ │
│  │  ├─ Resource limits (CPU, memory)      │ │
│  │  └─ Network policy (if configured)     │ │
│  │                                          │ │
│  │  Health Checks:                         │ │
│  │  ├─ Readiness: GET /health            │ │
│  │  │  (is pod ready for traffic?)        │ │
│  │  └─ Liveness: GET /health             │ │
│  │     (is pod still alive?)              │ │
│  └──────────────────────────────────────────┘ │
│                                                │
└────────────────────────────────────────────────┘
```

**Deployment Strategy:**
- RollingUpdate: maxUnavailable=0, maxSurge=1
- Result: Zero-downtime updates
- 1 new pod at a time, old pod replaced after health check passes

---

### 5. **GitOps Layer** (ArgoCD)

```
GitHub Repository
├─ main branch
│  ├─ src/ (application code)
│  ├─ k8s/
│  │  ├─ deployment.yaml (desired state)
│  │  ├─ service.yaml
│  │  └─ kustomization.yaml (image tag)
│  └─ ...

     │ (CI/CD commits image tag change)
     │
     ▼
ArgoCD Application
├─ Source: https://github.com/<org>/<repo>
├─ Path: k8s/
├─ Destination: AKS cluster
│
├─ Sync Policy:
│  ├─ automated: true
│  ├─ selfHeal: true (revert manual changes)
│  └─ prune: true (delete removed resources)
│
└─ Status:
   ├─ Synced ✅ (desired state matches cluster)
   └─ OutOfSync (cluster differs from repo)

Key Insight:
- Git repo = source of truth
- ArgoCD constantly reconciles
- Any repo change auto-syncs to cluster
- Manual cluster changes are reverted
- Rollback = git revert = easy
```

---

## Data Flow Example: End-to-End

```
1. Developer: git push to main
              │
              ▼
2. GitHub: Trigger workflow
           │
           ├─→ DVC pull (data/iris.csv via .dvc pointer)
           │
           ├─→ train.py:
           │    Input: data/iris.csv
           │    Output: models/model.pkl, metadata.json
           │    Log: MLflow experiment
           │
           ├─→ evaluate.py:
           │    Input: models/model.pkl
           │    Check: accuracy >= 90%?
           │    Output: validation=passed, champion alias
           │
           ├─→ Docker build:
           │    COPY models/model.pkl
           │    Push to ACR:abc123
           │    Image digest: sha256:f1f2f3f4...
           │
           ├─→ Tag MLflow model version:
           │    version 1 → image digest sha256:f1f2f3f4
           │
           ├─→ Kustomize update:
           │    image: acr/ml-model-service:abc123
           │    git commit & push [skip ci]
           │
           ▼
3. Git: Manifest updated on main
        │
        ▼
4. ArgoCD: Detects change
           │
           ├─→ diffs kustomization.yaml
           │
           ├─→ Applies to AKS:
           │    kubectl set image deployment/ml-model-service \
           │    ml-model-service=acr:abc123
           │
           └─→ Monitors pod readiness
               │
               ├─→ Old pod (abc000) terminating
               ├─→ New pod (abc123) starting
               └─→ Health check passes → traffic routed to new pod
                  │
                  ▼
5. Production: 
   Pod running model.pkl (embedded in image)
   │
   ├─→ GET /version
   │   Returns: model_version=1, mlflow_run_id=..., git_sha=...
   │
   ├─→ POST /predict
   │   Loads model.pkl → inference
   │   Returns: {"class": 1}
   │
   └─→ Metrics collected:
       latency, accuracy, throughput
```

---

## Traceability: Pod ↔ Model ↔ Data ↔ Code

```
Running Pod (AKS)
├─ Image: acr/ml-model-service@sha256:f1f2f3f4...
│  │
│  └─→ Dockerfile labels:
│      git_sha = abc123def456...
│      model_version = 1
│      mlflow_run_id = a1b2c3d4...
│
├─ GET /version endpoint
│  └─→ metadata.json (baked in image):
│      {
│        "model_version": "1",
│        "mlflow_run_id": "a1b2c3d4...",
│        "git_sha": "abc123def456...",
│        "data_sha256": "3f2f3f3f...",
│        "model_sha256": "e5e5e5e5...",
│        "trained_at": "2024-03-15T10:30:45Z"
│      }
│
└─→ MLflow tracking server:
    Run: a1b2c3d4e5f6g7h8
    ├─ Params: n_estimators=150, max_depth=5
    ├─ Metrics: accuracy=0.96
    ├─ Tags: git_sha=abc123, data_sha=3f2f3f3f
    ├─ Artifacts:
    │  ├─ model.pkl
    │  └─ metadata.json
    └─ Model: iris-classifier
       └─ Version: 1 (champion)
          ├─ Artifact path: runs/a1b2c3d4/model/model.pkl
          └─ Image tag: sha256:f1f2f3f4...

To trace: Query MLflow with mlflow_run_id → get git_sha + data_sha
          → Query GitHub for commit abc123 (source code)
          → Query DVC for data version 3f2f3f3f (training dataset)
          → Complete reproducibility!
```

---

## Resilience & Recovery

### Scenario 1: Model Accuracy Degrades
```
Monitoring alerts: accuracy < 90%
                  │
                  ▼
Developer: git revert HEAD
           │
           ▼
CI/CD: Build previous model again
       Deploy previous image
       │
       ▼
ArgoCD: Sync k8s/ manifest
        └─ Pod rolls back to previous image
           (includes old model.pkl)
           │
           ▼
Production: Serving previous model immediately
            Accuracy restored
```

### Scenario 2: Pod Crash
```
Pod dies / health check fails
            │
            ▼
Kubernetes: Detects pod unhealthy
            │
            ├─→ Auto-restart pod (liveness probe)
            │
            ├─→ If persistent: replace with new pod
            │   (deployment maintains 3 replicas)
            │
            └─→ Traffic rerouted to healthy pods
                (zero downtime)
```

### Scenario 3: Data Corruption
```
DVC detects file mismatch
                │
                ▼
Pipeline fails: dvc pull fails
                │
                ▼
CI/CD: Notify & stop
       Manual investigation
       │
       ├─→ Restore from Azure Blob backup
       ├─→ Regenerate DVC cache
       ├─→ Re-push corrected data
       │
       └─→ Retry training pipeline
```

---

## Monitoring & Observability

```
┌──────────────────────────────┐
│  Azure Monitor               │
├──────────────────────────────┤
│ • Pod metrics (CPU, memory)  │
│ • HTTP request latency       │
│ • Error rates                │
│ • Custom metrics (accuracy)  │
│ • Logs aggregation           │
│ • Alerts (on threshold)      │
│ • Dashboards                 │
└──────────────────────────────┘
            │
            ├─→ Prometheus (optional)
            │
            └─→ Grafana dashboards
                ├─ Pod health
                ├─ Model performance
                ├─ API latency
                └─ Error rates
```

---

## Scaling

**Horizontal (add pods):**
```yaml
# deployment.yaml
spec:
  replicas: 3  # → change to 5 for more capacity
  
# Or use HPA (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-model-service
spec:
  scaleTargetRef:
    kind: Deployment
    name: ml-model-service
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

**Vertical (bigger pods):**
```yaml
# deployment.yaml
resources:
  requests:
    cpu: 250m → 500m
    memory: 512Mi → 1Gi
  limits:
    cpu: 1 → 2
    memory: 1Gi → 2Gi
```

**Geographic (multi-region):**
```
Not covered in this doc, but possible via:
- Replicate ACR to multiple regions
- Deploy AKS in multiple regions
- Traffic Manager for routing
```

---

## Development Workflow

```
Local Development:
├─ git clone repo
├─ dvc pull (get data)
├─ python src/train.py (train locally)
├─ python -m pytest tests/ (test)
├─ python -m uvicorn src.app:app (serve)
└─ Iterate...

CI/CD Pipeline:
├─ git push
├─ GitHub Actions triggers
├─ All steps automated
├─ Results in production deployment
└─ No manual intervention

Production:
├─ Pod serving predictions
├─ Health checks passing
├─ Metrics collected
├─ Logs aggregated
└─ Ready to scale
```

