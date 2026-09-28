# Production Standards & Best Practices

This document outlines the standards and best practices implemented in this MLOps project.

## 🏆 Code Quality Standards

### Python Code Style (PEP 8)
- ✅ **Max line length**: 100 characters (enforced by flake8)
- ✅ **Indentation**: 4 spaces (never tabs)
- ✅ **Naming conventions**: snake_case for functions/variables, PascalCase for classes
- ✅ **Docstrings**: All functions include docstrings with parameters and returns
- ✅ **Type hints**: Encouraged for public APIs
- ✅ **Comments**: Explain "why", not "what"

**Checked by**: `flake8 src tests`

### Testing Standards
- ✅ **Minimum coverage**: 80% for critical code paths
- ✅ **Test framework**: pytest with fixtures
- ✅ **Unit tests**: All functions tested independently
- ✅ **Integration tests**: Full workflow tested
- ✅ **Mock external services**: MLflow, storage mocked in tests
- ✅ **Fast tests**: < 1 second per test

**Checked by**: `pytest -v --cov=src`

### Commit Message Standards
- ✅ **Format**: [Conventional Commits](https://www.conventionalcommits.org/)
  - `type(scope): description`
  - Types: feat, fix, docs, test, refactor, chore, perf
- ✅ **Description**: Clear, concise, actionable
- ✅ **Linking issues**: `Fixes #123` in PR description
- ✅ **Atomic commits**: One logical change per commit

**Examples:**
- `feat(train): add hyperparameter tuning`
- `fix(app): handle missing model gracefully`
- `docs(README): clarify DVC setup`
- `test(evaluate): add accuracy gate tests`

---

## 🔒 Security Standards

### Container Security
- ✅ **Non-root user**: UID 1001 (never root)
- ✅ **Read-only filesystem**: Prevents runtime tampering
- ✅ **Dropped capabilities**: ALL dropped (zero privilege escalation)
- ✅ **Resource limits**: CPU and memory constrained
- ✅ **Image scanning**: Trivy scan on every push (fail on HIGH/CRITICAL CVEs)
- ✅ **Base image**: Pinned version (python:3.10-slim, not latest)

**Verified by**: Dockerfile inspection, Trivy scan

### Secrets Management
- ✅ **No hardcoded secrets**: Git hooks detect private keys
- ✅ **GitHub Secrets**: All credentials encrypted at rest
- ✅ **Environment variables**: Injected at runtime
- ✅ **OIDC**: Federated credentials (temporary tokens)
- ✅ **No PAT tokens**: Service principal with minimal scope
- ✅ **Rotation**: Secrets rotated every 90 days

**Verified by**: GitHub Secret Scanner, manual review

### Data Security
- ✅ **Encryption in transit**: HTTPS/TLS for all connections
- ✅ **Encryption at rest**: Azure Storage with encryption enabled
- ✅ **Access control**: RBAC on Azure resources
- ✅ **Audit logging**: All access logged
- ✅ **Checksums**: SHA-256 verification of artifacts

**Verified by**: Azure compliance settings, DVC checksums

### Supply Chain Security
- ✅ **Dependency pinning**: Exact versions (no ~= or >=)
- ✅ **Automated scanning**: Dependabot for updates
- ✅ **Build provenance**: Docker provenance enabled
- ✅ **Artifact verification**: Checksum validation before deployment
- ✅ **SLSA basics**: Reproducible builds, audit trail, access control

**Verified by**: requirements.txt review, Trivy scan, BuildKit provenance

---

## 🚀 Performance Standards

### Pipeline Speed
- ✅ **Lint & test**: < 2 minutes
- ✅ **Training**: 5-10 minutes (depends on data size)
- ✅ **Evaluation**: < 1 minute
- ✅ **Docker build & push**: 3-7 minutes
- ✅ **ArgoCD sync**: < 5 minutes
- ✅ **Total pipeline**: ~14.5 minutes
- ✅ **Caching**: Docker layer caching for faster rebuilds
- ✅ **Parallel jobs**: Code quality checks run in parallel

**Measured by**: GitHub Actions logs, timing in workflow

### Container Performance
- ✅ **Startup time**: < 10 seconds
- ✅ **Memory**: < 512 MB requests, 1 GB limits
- ✅ **CPU**: 250m requests, 1 core limits
- ✅ **Inference latency**: < 100ms (P95)
- ✅ **Throughput**: > 100 requests/sec per pod

**Measured by**: Kubernetes metrics, application telemetry

### Scalability
- ✅ **Horizontal**: Replicas configurable (3 by default)
- ✅ **Auto-scaling**: HPA ready (no configuration needed)
- ✅ **Data versioning**: DVC handles terabytes
- ✅ **Model registry**: MLflow handles thousands of versions
- ✅ **No single points of failure**: Multiple replicas, load-balanced

**Verified by**: Kubernetes configuration, architecture review

---

## 📊 Observability Standards

### Logging
- ✅ **Application logs**: Structured logging to stdout/stderr
- ✅ **Aggregation**: Azure Monitor collects all pod logs
- ✅ **Retention**: 90 days (configurable)
- ✅ **Searchability**: Filterable by pod, namespace, labels
- ✅ **Error tracking**: Stack traces captured

**Tools**: Azure Monitor, kubectl logs

### Metrics
- ✅ **Application metrics**: Exposed via Prometheus format (if configured)
- ✅ **Kubernetes metrics**: CPU, memory, network I/O
- ✅ **Business metrics**: Accuracy, latency, throughput
- ✅ **Alerts**: Thresholds for anomalies
- ✅ **Dashboards**: Visualized in Azure Monitor or Grafana

**Tools**: Prometheus, Azure Monitor, Grafana (optional)

### Health Checks
- ✅ **Readiness probe**: Is pod ready for traffic? (GET /health)
- ✅ **Liveness probe**: Is pod alive? (GET /health)
- ✅ **Startup probe**: Ready to accept traffic after startup? (optional)
- ✅ **Failure handling**: Restart policy, pod disruption budgets

**Verified by**: Kubernetes deployment.yaml configuration

### Traceability
- ✅ **Model lineage**: metadata.json embeds git_sha, data_sha, run_id
- ✅ **Request tracing**: Request IDs propagated through logs (if configured)
- ✅ **Audit trail**: All changes in Git history
- ✅ **Deployment history**: ArgoCD tracks syncs
- ✅ **Model history**: MLflow tracks all runs

**Tools**: Git, MLflow, ArgoCD, Azure Monitor

---

## 🧪 Testing Standards

### Unit Tests
- ✅ **Coverage**: Minimum 80% for critical paths
- ✅ **Isolation**: Mocked external dependencies
- ✅ **Deterministic**: No flaky tests, deterministic seeding
- ✅ **Fast**: All tests run in < 10 seconds
- ✅ **Clear names**: Test names describe what they test

### Integration Tests
- ✅ **End-to-end**: Full workflow from data to prediction
- ✅ **Realistic data**: Uses actual sample data
- ✅ **Failure cases**: Tests error handling
- ✅ **Timeout guards**: Prevents hanging tests

### Quality Gates
- ✅ **Linting**: flake8 must pass (no style violations)
- ✅ **Testing**: pytest must pass (no test failures)
- ✅ **Type checking**: mypy optional (for type hints)
- ✅ **Security**: No hardcoded secrets
- ✅ **Model accuracy**: >= 90% (blocks deployment if lower)

**Verified by**: GitHub Actions checks (required before merge)

---

## 📚 Documentation Standards

### Code Documentation
- ✅ **Docstrings**: All functions/classes have docstrings
- ✅ **Type hints**: Public APIs include type hints
- ✅ **Comments**: Explain non-obvious logic
- ✅ **Examples**: Complex functions have usage examples

### Project Documentation
- ✅ **README**: Overview, quick start, setup instructions
- ✅ **ARCHITECTURE.md**: System design, data flow, components
- ✅ **WORKFLOW.md**: Pipeline visualization, decision points, timing
- ✅ **CONTRIBUTING.md**: How to contribute, code standards
- ✅ **SECURITY.md**: Security practices, incident response
- ✅ **CHANGELOG.md**: Versioning, release notes

### API Documentation
- ✅ **OpenAPI/Swagger**: FastAPI auto-generates from docstrings
- ✅ **Endpoint docs**: All endpoints documented with examples
- ✅ **Error codes**: HTTP status codes and error messages defined

---

## 🔄 Deployment Standards

### Kubernetes Configuration
- ✅ **Security context**: Non-root, read-only filesystem, dropped caps
- ✅ **Resource limits**: CPU and memory defined
- ✅ **Health probes**: Readiness and liveness configured
- ✅ **Replica strategy**: Blue-green rolling updates
- ✅ **Namespace**: Isolated namespace (ml-production)
- ✅ **Labels & selectors**: Consistent naming for identification

### GitOps Standards
- ✅ **Declarative**: k8s manifests describe desired state
- ✅ **Version control**: All manifests in Git
- ✅ **Automated sync**: ArgoCD reconciles desired vs actual
- ✅ **Self-healing**: Auto-revert manual changes
- ✅ **Audit trail**: All changes tracked in Git history
- ✅ **Rollback**: Simple `git revert` for instant rollback

### Dockerfile Best Practices
- ✅ **Multi-stage**: Not applicable (single-stage is lean)
- ✅ **Layer caching**: Dependency layer before code
- ✅ **Minimal base**: python:3.10-slim (not latest, not bloated)
- ✅ **Build context**: .dockerignore excludes unnecessary files
- ✅ **Security**: No RUN sudo, no privilege escalation
- ✅ **Labels**: OCI labels with metadata

---

## 📋 Compliance Standards

### Data Governance
- ✅ **Versioning**: All data versions tracked (DVC)
- ✅ **Lineage**: Complete audit trail (git + MLflow)
- ✅ **Validation**: Quality gates prevent bad data
- ✅ **Retention**: Policies defined in DVC remote
- ✅ **Access control**: Role-based access to datasets

### Model Governance
- ✅ **Registry**: Central model registry (MLflow)
- ✅ **Versioning**: All models versioned
- ✅ **Promotion**: Champion alias for production
- ✅ **Tagging**: Validation status tags
- ✅ **Lineage**: Training run linked to model version
- ✅ **Metrics**: Historical metrics for all versions

### Audit Trail
- ✅ **Git history**: Every change is a commit
- ✅ **MLflow tracking**: Every training run logged
- ✅ **ArgoCD syncs**: Deployment history tracked
- ✅ **Kubernetes events**: Pod lifecycle events
- ✅ **Azure Monitor**: Access logs and metrics

---

## 🎯 Quality Metrics

### Stability
- ✅ **Uptime**: Target 99.5% (3 replicas + auto-restart)
- ✅ **Error rate**: < 0.1% (SLO)
- ✅ **Deployment success**: > 95% (failures caught early)

### Performance
- ✅ **P50 latency**: < 50ms
- ✅ **P95 latency**: < 100ms
- ✅ **P99 latency**: < 500ms
- ✅ **Throughput**: > 100 req/sec per pod

### Reliability
- ✅ **Mean time to recovery**: < 5 minutes (git revert)
- ✅ **Mean time between failures**: > 30 days (no crashes)
- ✅ **Test coverage**: 80%+ for critical paths

### Security
- ✅ **CVEs in production**: 0 (Trivy scanning)
- ✅ **Secret leaks**: 0 (GitHub Secret Scanner)
- ✅ **Unauthorized access**: 0 (RBAC enforced)
- ✅ **Data breaches**: 0 (encryption enabled)

---

## 📝 Checklist for New Features

Before committing new code:

- [ ] Flake8 passes: `flake8 src tests`
- [ ] Tests pass: `pytest -v --cov=src`
- [ ] Test coverage >= 80%
- [ ] Docstrings added
- [ ] No hardcoded secrets
- [ ] Type hints added (recommended)
- [ ] Comments explain "why"
- [ ] Commit message follows convention
- [ ] No large files committed (> 5MB)
- [ ] .gitignore updated if needed

Before merging to main:

- [ ] Code review approved
- [ ] All CI checks passing
- [ ] Tests passing
- [ ] Linting passing
- [ ] No breaking changes (or documented)
- [ ] Documentation updated
- [ ] PR description is clear
- [ ] Related issues linked

Before deploying to production:

- [ ] Training accuracy >= 90%
- [ ] Model artifact checksums verified
- [ ] Container security scan passed
- [ ] All health checks configured
- [ ] Monitoring/alerts ready
- [ ] Runbooks documented
- [ ] Team notified
- [ ] Rollback plan prepared

---

## 🔗 Related Standards

- **PEP 8**: Python Enhancement Proposal 8 (style guide)
- **Semantic Versioning**: MAJOR.MINOR.PATCH versioning
- **Conventional Commits**: Standardized commit messages
- **OWASP Top 10**: Security best practices
- **CIS Kubernetes Benchmarks**: Kubernetes hardening
- **SLSA Framework**: Supply chain security
- **Keep a Changelog**: Changelog standards

