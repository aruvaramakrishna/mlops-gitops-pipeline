# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of MLOps pipeline
- DVC integration for data versioning
- MLflow experiment tracking and model registry
- GitHub Actions CI/CD workflow
- ArgoCD GitOps deployment
- Kubernetes manifests with security best practices
- Trivy vulnerability scanning
- OIDC authentication (no stored credentials)
- Comprehensive documentation (ARCHITECTURE.md, WORKFLOW.md)
- Unit tests with pytest
- Code quality checks with flake8
- Health endpoints and model versioning API

### Security
- Non-root container user
- Read-only root filesystem
- Dropped Linux capabilities
- SHA-256 checksum verification
- Encrypted GitHub Secrets
- OIDC federated credentials

### Infrastructure
- AKS Kubernetes cluster deployment
- Azure Container Registry integration
- Azure Blob Storage for datasets
- MLflow tracking server
- Blue-green deployment strategy
- Zero-downtime rolling updates

---

## [1.0.0] - Initial Release (Template)

### Added
- MLOps pipeline scaffold
- DVC data versioning setup
- MLflow experiment tracking
- GitHub Actions workflow
- Kubernetes deployment manifests
- ArgoCD GitOps configuration
- Model quality gates
- Security scanning (Trivy)
- Comprehensive documentation

### Features
- Reproducible ML pipeline (code + data version pinned)
- Automated model evaluation (accuracy gate)
- Container scanning (vulnerability detection)
- Git-based rollback capability
- Production-ready Kubernetes setup
- Health checks and monitoring

---

## Release Notes

### How to Release

1. Update `CHANGELOG.md` with new version and changes
2. Update version in any version files (if applicable)
3. Create annotated git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub Release with notes
6. Announce on social media / team channels

### Version Naming

- `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes (0 → 1, requires migration guide)
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes (backwards compatible)

Example releases:
- `v0.1.0` — Initial development version
- `v1.0.0` — First stable release
- `v1.1.0` — Added feature X (backwards compatible)
- `v1.1.1` — Fixed bug Y
- `v2.0.0` — Major refactor (breaking changes)

---

## Archive

This is where old entries are moved as the project evolves.
Keeping current changelog focused on recent changes.

