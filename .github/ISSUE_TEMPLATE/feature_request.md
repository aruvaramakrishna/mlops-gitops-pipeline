name: Feature Request
description: Suggest a new feature or enhancement
title: "[Feature] "
labels: ["enhancement"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Thanks for suggesting a feature! Please provide details about what you'd like to see.

  - type: textarea
    id: problem
    attributes:
      label: Problem Statement
      description: What problem does this solve?
      placeholder: "Currently, we can't track data drift in production models..."
    validations:
      required: true

  - type: textarea
    id: solution
    attributes:
      label: Proposed Solution
      description: How should this be implemented?
      placeholder: "Add data drift detection step in pipeline that compares test data distribution..."
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives Considered
      description: Other approaches to solving this
      placeholder: "Could use external service like Evidently AI..."

  - type: textarea
    id: impact
    attributes:
      label: Impact
      description: Who benefits and how?
      placeholder: "Data scientists can detect model degradation earlier, triggering retraining..."

  - type: textarea
    id: resources
    attributes:
      label: Additional Resources
      description: References, links, examples
      placeholder: "https://example.com/data-drift-detection"

  - type: checkboxes
    id: scope
    attributes:
      label: Scope
      description: What areas does this affect?
      options:
        - label: Data (DVC, datasets)
        - label: Training (train.py, MLflow)
        - label: Evaluation (evaluate.py)
        - label: Deployment (Docker, K8s)
        - label: Monitoring (health checks, metrics)
        - label: Documentation
        - label: Testing
        - label: CI/CD

