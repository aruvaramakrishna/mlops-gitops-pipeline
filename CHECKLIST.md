# Pre-Push Verification Checklist

Use this checklist before pushing to GitHub to ensure everything is production-ready.

---

## ✅ Code Quality

- [ ] **Flake8 passes**
  ```bash
  flake8 src tests
  # Should output nothing (no errors)
  ```

- [ ] **Tests pass**
  ```bash
  pytest -v
  # All tests should pass
  ```

- [ ] **Test coverage acceptable**
  ```bash
  pytest --cov=src tests/
  # Should show >= 80% coverage for critical paths
  ```

- [ ] **No hardcoded secrets**
  ```bash
  git diff HEAD --check
  grep -r "password\|api_key\|secret" src/ || echo "✅ No secrets found"
  ```

- [ ] **Docstrings present**
  - All functions have docstrings
  - All classes have docstrings
  - All public methods documented

- [ ] **Type hints added** (recommended)
  - Critical functions have type hints
  - Returns type documented

---

## 📝 Documentation

- [ ] **README.md is up to date**
  - Quick start section works
  - Setup instructions are accurate
  - Links are not broken

- [ ] **Code comments clear**
  - Non-obvious logic explained
  - "Why", not "what" documented
  - No commented-out code blocks

- [ ] **CHANGELOG.md updated**
  - New changes documented
  - Version bumped (if releasing)
  - Formatted correctly

- [ ] **Docstrings complete**
  ```bash
  python -m pydoc src.train
  python -m pydoc src.evaluate
  python -m pydoc src.app
  ```

---

## 🔒 Security

- [ ] **No secrets in code**
  ```bash
  grep -r "AZURE_\|MLFLOW_\|password=" src/ || echo "✅ Clean"
  ```

- [ ] **No debug code**
  ```bash
  grep -r "print(\|breakpoint(\|import pdb" src/ || echo "✅ Clean"
  ```

- [ ] **Dependencies pinned**
  ```bash
  cat requirements.txt | grep "=="
  # Should see exact versions, not >= or ~=
  ```

- [ ] **No vulnerable dependencies**
  ```bash
  safety check -r requirements.txt
  # Should pass (or known vulnerabilities documented)
  ```

- [ ] **.env.example has no real values**
  - All passwords are placeholders
  - No actual Azure credentials
  - No real MLflow URLs

- [ ] **.gitignore excludes sensitive files**
  - `*.pkl` (models)
  - `.env` (local config)
  - `mlruns/` (local MLflow)
  - `.dvc/config.local`

---

## 🧪 Testing

- [ ] **Unit tests cover critical paths**
  ```bash
  pytest tests/ -v
  # Check for:
  # - test_health_is_503_without_model ✅
  # - test_health_and_predict_with_model ✅
  # - Any error cases tested ✅
  ```

- [ ] **Mock external dependencies**
  - MLflow not called in unit tests
  - No real Azure calls in tests
  - No file I/O in unit tests

- [ ] **Tests are deterministic**
  ```bash
  pytest tests/ --count=10
  # Run multiple times, should always pass
  ```

- [ ] **No skipped tests**
  ```bash
  pytest tests/ -v 2>&1 | grep -i skip || echo "✅ No skips"
  ```

---

## 📦 Configuration

- [ ] **requirements.txt pinned**
  ```bash
  cat requirements.txt | head -5
  # Should see: scikit-learn==1.4.2 (not >=1.4)
  ```

- [ ] **requirements-serve.txt matches train**
  - Same versions for sklearn, pandas, joblib
  - No version conflicts

- [ ] **Dockerfile uses pinned images**
  ```bash
  grep "FROM " Dockerfile
  # Should be: python:3.10-slim (not python:3.10 or python:latest)
  ```

- [ ] **.flake8 configuration correct**
  ```bash
  cat .flake8
  # Should have max_line_length = 100
  ```

- [ ] **pytest.ini configured**
  ```bash
  cat pytest.ini
  # Should have testpaths and pythonpath
  ```

- [ ] **dvc.yaml pipeline defined**
  ```bash
  dvc dag
  # Should show train → evaluate pipeline
  ```

---

## 🚀 Deployment Files

- [ ] **k8s/deployment.yaml**
  - [ ] Image placeholder is correct
  - [ ] Replicas set to 3
  - [ ] Resource limits defined (CPU, memory)
  - [ ] Health probes configured (readiness + liveness)
  - [ ] Security context enforced (non-root, read-only)
  - [ ] Environment variables set (MODEL_DIR)

- [ ] **k8s/service.yaml**
  - [ ] Service type is ClusterIP
  - [ ] Port 80 maps to 8000
  - [ ] Selector matches labels

- [ ] **k8s/kustomization.yaml**
  - [ ] Namespace set
  - [ ] Image placeholder ready for CI update
  - [ ] Resources listed

- [ ] **argocd-app.yaml**
  - [ ] repoURL updated to your repo
  - [ ] targetPath is k8s
  - [ ] namespace is ml-production
  - [ ] syncPolicy: automated enabled
  - [ ] selfHeal: true (revert manual changes)
  - [ ] prune: true (delete resources)

- [ ] **Dockerfile**
  - [ ] Non-root user (UID 1001)
  - [ ] Read-only filesystem
  - [ ] Capabilities dropped
  - [ ] OCI labels with metadata
  - [ ] MODEL_DIR environment variable

---

## 🔧 GitHub Configuration

- [ ] **.github/workflows/mlops-aks-pipeline.yml**
  - [ ] Triggered on push to main
  - [ ] All 4 jobs present (lint, train, build, deploy)
  - [ ] Needs dependencies correct
  - [ ] Permissions minimal (only what's needed)
  - [ ] Concurrency lock prevents race conditions
  - [ ] Timeout values reasonable

- [ ] **.github/CODEOWNERS**
  - [ ] Update usernames to your team
  - [ ] Critical areas have reviewers assigned

- [ ] **.github/dependabot.yml**
  - [ ] Scheduled for weekly checks
  - [ ] GitHub token configured

- [ ] **.github/pull_request_template.md**
  - [ ] Clear sections for description
  - [ ] Checklist items relevant

- [ ] **Issue templates**
  - [ ] bug_report.md present
  - [ ] feature_request.md present

---

## 📊 Git Repository

- [ ] **Commit messages follow convention**
  ```bash
  git log --oneline -5
  # Should see: feat(...), fix(...), docs(...), chore(...)
  # Not: random messages or "update"
  ```

- [ ] **No accidental commits**
  - No venv/, __pycache__, .pyc files committed
  - No models/ directory committed
  - No .env file committed
  - No IDE files (.vscode, .idea)

- [ ] **Branch is clean**
  ```bash
  git status
  # Should show: "On branch main" and "nothing to commit"
  ```

- [ ] **All changes are staged**
  ```bash
  git status
  # Should be clean, no "Changes not staged"
  ```

---

## 📋 Pre-Deployment Checks

- [ ] **Local test run successful**
  ```bash
  python src/train.py
  python src/evaluate.py
  # Both should complete without errors
  ```

- [ ] **Model files generated**
  ```bash
  ls -la models/
  # Should have: model.pkl, model.pkl.sha256, metadata.json
  ```

- [ ] **Metadata looks correct**
  ```bash
  cat models/metadata.json | jq .
  # Should have all required fields
  ```

- [ ] **Checksum verifies**
  ```bash
  cd models && sha256sum -c model.pkl.sha256
  # Should output: model.pkl: OK
  ```

- [ ] **App runs locally**
  ```bash
  export MODEL_DIR=models
  python -m uvicorn src.app:app
  # Should start without errors
  ```

- [ ] **Health endpoint responds**
  ```bash
  curl http://localhost:8000/health
  # Should return: {"status": "ok", "model_version": "..."}
  ```

---

## 🔐 Secrets & Environment

- [ ] **GitHub Secrets configured**
  - [ ] `AZURE_CLIENT_ID`
  - [ ] `AZURE_TENANT_ID`
  - [ ] `AZURE_SUBSCRIPTION_ID`
  - [ ] `MLFLOW_TRACKING_URI`
  - [ ] `MLFLOW_TRACKING_USERNAME`
  - [ ] `MLFLOW_TRACKING_PASSWORD`
  - [ ] `DVC_AZURE_STORAGE_CONNECTION_STRING`

- [ ] **GitHub Variables configured**
  - [ ] `ACR_NAME` (repository variable)

- [ ] **No secrets in repo**
  ```bash
  git log -p | grep -i "password\|api_key" || echo "✅ Clean"
  ```

---

## 📝 Documentation Check

Before publicizing, verify:

- [ ] **README.md**
  - [ ] Quick start works
  - [ ] All links are valid
  - [ ] Code examples are correct
  - [ ] Setup instructions complete

- [ ] **WORKFLOW.md**
  - [ ] Diagrams render correctly
  - [ ] Interview questions answered
  - [ ] Timeline realistic

- [ ] **ARCHITECTURE.md**
  - [ ] System diagrams clear
  - [ ] All components documented
  - [ ] Data flow explained

- [ ] **CONTRIBUTING.md**
  - [ ] Setup steps work
  - [ ] Standards are clear
  - [ ] Review process defined

- [ ] **SECURITY.md**
  - [ ] Security practices documented
  - [ ] Incident response clear

- [ ] **STANDARDS.md**
  - [ ] All standards listed
  - [ ] Verification methods shown
  - [ ] Checklist items clear

---

## 🎬 Final Checks Before Push

```bash
# Run full verification
echo "🔍 Checking code quality..."
flake8 src tests || exit 1

echo "✅ Running tests..."
pytest -v || exit 1

echo "✅ Checking coverage..."
pytest --cov=src tests/ || exit 1

echo "✅ Checking for secrets..."
git diff HEAD | grep -i "password\|api_key\|secret" && exit 1 || echo "✅ Clean"

echo "✅ Checking git status..."
git status --porcelain || echo "✅ Clean"

echo "✅ Validating YAML..."
python -c "import yaml; yaml.safe_load(open('.github/workflows/mlops-aks-pipeline.yml'))"
python -c "import yaml; yaml.safe_load(open('k8s/deployment.yaml'))"

echo "✅ All checks passed! Ready to push 🚀"
```

---

## 🚀 Push to GitHub

```bash
# Add changes
git add .

# Commit with clear message
git commit -m "feat: production-ready MLOps pipeline

- Add DVC data versioning
- Add MLflow experiment tracking
- Add quality gates (accuracy >= 90%)
- Add GitHub Actions CI/CD workflow
- Add Kubernetes deployment manifests
- Add ArgoCD GitOps configuration
- Add comprehensive documentation
- Add security hardening
- Add unit tests"

# Push to main
git push origin main

# Verify CI/CD ran successfully
# → Visit: https://github.com/<org>/<repo>/actions
# → All checks should be green ✅
```

---

## 💼 After Push: LinkedIn Strategy

### 1. Create LinkedIn Post
Use template from [LINKEDIN.md](LINKEDIN.md)

### 2. Timing
- Post on Tuesday-Thursday (higher engagement)
- Post in morning (8-10 AM) in your timezone
- Add relevant hashtags

### 3. Follow-up Actions
- Share in relevant communities (r/MachineLearning, etc.)
- Update resume with link
- Share with network/recruiters
- Prepare talking points from [LINKEDIN.md](LINKEDIN.md)

### 4. Expected Engagement
- Comments will ask questions
- Be ready with detailed answers (see LINKEDIN.md)
- Share knowledge generously
- Build your professional brand

---

## 🎯 Verification Summary

| Category | Status | Notes |
|----------|--------|-------|
| Code Quality | ⬜ | Run flake8 & pytest |
| Testing | ⬜ | 80%+ coverage |
| Security | ⬜ | No secrets, dependencies pinned |
| Documentation | ⬜ | All 8 markdown files complete |
| Configuration | ⬜ | All YAML files validated |
| Deployment | ⬜ | All K8s manifests ready |
| Git | ⬜ | Clean commit history |
| GitHub | ⬜ | Secrets & variables configured |

**Total Time**: ~30 minutes to complete all checks  
**Estimated Success Rate**: 98% (if all checks pass)

Good luck! 🍀

