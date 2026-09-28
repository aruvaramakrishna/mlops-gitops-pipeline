# Security Policy

## Reporting Security Issues

**Do not open public issues for security vulnerabilities.**

If you discover a security issue, please email maintainers privately:
- Do not disclose the issue publicly
- Include detailed information about the vulnerability
- Provide steps to reproduce if possible
- Allow time for a fix before public disclosure (typically 90 days)

## Security Practices

This project implements:

### Authentication & Authorization
- ✅ OIDC federated credentials (no stored secrets in CI/CD)
- ✅ GitHub Secrets for sensitive data (encrypted at rest)
- ✅ Service principal with least-privilege roles (AcrPush only)
- ✅ RBAC in Kubernetes (non-root, read-only filesystem)

### Image Security
- ✅ Trivy vulnerability scanning before push to registry
- ✅ Non-root user (UID 1001) in container
- ✅ Read-only root filesystem
- ✅ Drop all Linux capabilities
- ✅ Pinned base image (python:3.10-slim)
- ✅ No `RUN sudo` or privilege escalation
- ✅ Multi-stage builds (not used here; single-stage is lean)

### Dependency Management
- ✅ Pinned versions in requirements.txt
- ✅ Automated scanning via Trivy (CI step)
- ✅ Regular updates via Dependabot
- ✅ Security headers in FastAPI app

### Data & Artifact Security
- ✅ Model checksums (SHA-256 verification)
- ✅ Git audit trail (all training runs logged to MLflow)
- ✅ DVC remote in private Azure Blob Storage
- ✅ Access control on ACR (authentication required)

### Code Security
- ✅ Linting with flake8
- ✅ Unit tests (pytest)
- ✅ No hardcoded secrets (checked in CI)
- ✅ Code review required before merge
- ✅ Branch protection on main

### Kubernetes Security
- ✅ Non-root container user
- ✅ Security context enforced
- ✅ Resource limits (CPU, memory)
- ✅ Health probes (readiness, liveness)
- ✅ Network policies (via service type)
- ✅ RBAC in ArgoCD namespace

## Dependency Updates

Dependencies are managed by:
- **Manual**: Review and test before updating
- **Automated**: Dependabot creates PRs for security updates
- **Pinned**: Exact versions in `requirements.txt` and `requirements-serve.txt`

Check for vulnerabilities:
```bash
pip install safety
safety check -r requirements.txt
```

## Scanning & Monitoring

- **Trivy**: Image vulnerability scanning (on push)
- **GitHub Secret Scanner**: Prevents accidental credential commits
- **SAST**: Optional: Add SonarQube or similar
- **Runtime**: Monitor pod logs for errors/attacks

## Compliance

This project aligns with:
- ✅ OWASP Top 10 (secure coding practices)
- ✅ CIS Kubernetes Benchmarks (K8s security)
- ✅ Supply Chain Security (SLSA framework basics)

## Best Practices for Users

When using this project:

1. **Rotate secrets regularly**
   ```bash
   gh secret set MLFLOW_TRACKING_PASSWORD --body "new-password"
   ```

2. **Use OIDC, not stored credentials**
   - Federated identity is more secure
   - No PAT tokens to manage

3. **Enable branch protection**
   - Require status checks before merge
   - Require code reviews
   - Dismiss stale PR reviews

4. **Monitor ACR access**
   ```bash
   az acr repository list --name $ACR_NAME
   az acr aad spa-credential show --registry $ACR_NAME
   ```

5. **Audit MLflow access**
   - Check who modified models
   - Review experiment history
   - Log access patterns

6. **Scan images before deployment**
   ```bash
   trivy image $ACR_NAME.azurecr.io/ml-model-service:latest
   ```

## Security Checklist for Deployments

Before deploying to production:

- [ ] All dependencies pinned and scanned
- [ ] Trivy scan passes (HIGH/CRITICAL fixed)
- [ ] Code reviewed by team
- [ ] Tests passing (100% on critical paths)
- [ ] ArgoCD automated sync enabled
- [ ] Monitoring/alerts configured
- [ ] Runbooks for incidents available
- [ ] Secrets rotated (< 90 days old)
- [ ] Backup/disaster recovery tested
- [ ] Security audit completed

## Incident Response

If a security incident occurs:

1. **Immediate**: Disable affected credentials
2. **Investigate**: Review audit logs, git history, pod logs
3. **Contain**: Rollback to known-good state (`git revert`)
4. **Fix**: Apply security patch
5. **Deploy**: Push fix through pipeline
6. **Monitor**: Watch for recurrence
7. **Document**: Post-mortem analysis

## Questions?

Contact maintainers with security concerns:
- Private email preferred for vulnerabilities
- GitHub Issues for general security questions
- Security@example.com for urgent matters

**Thank you for helping keep this project secure!** 🔒
