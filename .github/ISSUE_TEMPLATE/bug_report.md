name: Bug Report
description: Report a bug or issue
title: "[Bug] "
labels: ["bug"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Thank you for reporting a bug! Please fill in as much detail as possible.

  - type: input
    id: title
    attributes:
      label: Title
      description: Brief description of the bug
      placeholder: "Model fails to load in production pods"
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Detailed description of the bug
      placeholder: "When deploying version X, pods fail to start with error..."
    validations:
      required: true

  - type: textarea
    id: steps
    attributes:
      label: Steps to Reproduce
      description: How to reproduce the issue
      placeholder: |
        1. Train model with parameters X
        2. Deploy to AKS
        3. Pod fails with error
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What should happen
      placeholder: "Pod should start and respond to /health"
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
      description: What actually happened
      placeholder: "Pod crashes with OOMKilled"
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Logs
      description: Relevant error logs or stack traces
      render: bash
      placeholder: |
        ERROR: model load failed
        FileNotFoundError: /app/model/model.pkl

  - type: input
    id: version
    attributes:
      label: Version
      description: Affected version (git SHA or release tag)
      placeholder: "abc123def456 or v1.0.0"
    validations:
      required: true

  - type: textarea
    id: environment
    attributes:
      label: Environment
      description: Affected environment details
      placeholder: |
        - OS: Ubuntu 22.04 / macOS 13.4 / Windows 11
        - Python: 3.10
        - AKS: v1.27.0
        - Kubernetes: 1.27

  - type: textarea
    id: context
    attributes:
      label: Additional Context
      description: Any other relevant information
      placeholder: "This started after updating dependencies"

