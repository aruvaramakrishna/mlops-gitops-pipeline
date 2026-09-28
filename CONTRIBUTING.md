# Contributing to ml-gitops

Thank you for your interest in contributing! This document outlines the process and standards we follow.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on ideas, not personalities

## Development Setup

```bash
# Clone the repo
git clone https://github.com/<org>/<repo>.git
cd ml-gitops

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run linting & tests locally
flake8 src tests
pytest -v
```

## Making Changes

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Code Standards

- **Python**: Follow PEP 8 (checked by flake8)
- **Line length**: Max 100 characters (see `.flake8`)
- **Type hints**: Encouraged for public APIs
- **Docstrings**: Required for functions/classes
- **Comments**: Explain "why", not "what"

### 3. Testing Requirements

- All new code must include tests
- Minimum 80% test coverage
- Run tests locally: `pytest -v`
- Tests must pass in CI before merge

```bash
# Run tests with coverage
pytest --cov=src tests/
```

### 4. Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): short description

Longer explanation if needed.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `perf`

**Examples:**
- `feat(train): add hyperparameter tuning`
- `fix(app): handle missing model gracefully`
- `docs(README): clarify DVC setup`

### 5. Pull Request Process

1. Fork the repo (if external contributor)
2. Create a feature branch
3. Make changes & commit with clear messages
4. Push to your fork
5. Open PR with description of changes
6. Link related issues with `Fixes #123`
7. Pass all CI checks (lint, test, build)
8. Code review by maintainers
9. Merge when approved

**PR Title Format:**
```
[Type] Brief description

Example: [Feature] Add hyperparameter tuning to training pipeline
```

## ML/Data Changes

When modifying training code or data:

- **DVC**: If changing datasets, update `data/*.dvc` and push to remote
- **MLflow**: Log experiments; document parameter changes
- **evaluate.py**: Update accuracy threshold if it changes
- **Requirements**: Pin versions if adding/updating dependencies
- **WORKFLOW.md**: Update if adding new pipeline stages

## Security

- Never commit secrets (API keys, credentials, passwords)
- Use `.env.example` for example configs
- Report security issues to maintainers privately
- See [SECURITY.md](SECURITY.md)

## Review Checklist

Before requesting review, verify:
- [ ] Code passes `flake8` (run `flake8 src tests`)
- [ ] Tests pass (`pytest -v`)
- [ ] New tests added for new code
- [ ] No hardcoded secrets
- [ ] Docstrings/comments added
- [ ] Commit messages follow convention
- [ ] PR description is clear
- [ ] No merge conflicts

## Reporting Issues

Use GitHub Issues to report:
- Bugs: Clear description, steps to reproduce, expected vs actual behavior
- Features: Use case, proposed solution, any alternatives
- Questions: Detailed context and what you've already tried

**Issue Title Format:**
```
[Bug] Short description
[Feature] What you'd like to add
[Question] What you're trying to understand
```

## Release Process

Releases follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

Releases are created by maintainers with:
- Merged PRs since last release
- Updated `CHANGELOG.md`
- Git tag with version

## Questions?

- Open an issue for general questions
- Start a discussion for ideas
- Contact maintainers for sensitive topics

**Happy contributing!** 🎉
