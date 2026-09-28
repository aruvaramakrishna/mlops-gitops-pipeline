FROM python:3.10-slim

# Traceability: injected by CI, exposed as OCI labels on the image.
ARG GIT_SHA=unknown
ARG MODEL_NAME=unknown
ARG MODEL_VERSION=unknown
ARG MLFLOW_RUN_ID=unknown
LABEL org.opencontainers.image.revision=$GIT_SHA \
      org.opencontainers.image.title="ml-model-service" \
      ml.model.name=$MODEL_NAME \
      ml.model.version=$MODEL_VERSION \
      ml.mlflow.run_id=$MLFLOW_RUN_ID

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MODEL_DIR=/app/model
WORKDIR /app

# Dependency layer first: cached unless requirements-serve.txt changes.
COPY requirements-serve.txt .
RUN pip install --no-cache-dir -r requirements-serve.txt

COPY src/app.py ./src/app.py
# The validated artifact built and gated earlier in the pipeline (see build job).
COPY models/model.pkl models/metadata.json ./model/

RUN useradd -r -u 1001 app
USER 1001
EXPOSE 8000
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
