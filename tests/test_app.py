from fastapi.testclient import TestClient

import app as service

client = TestClient(service.app)  # no lifespan: model state is set manually


class DummyModel:
    def predict(self, _x):
        return [1]


def test_health_is_503_without_model():
    service.state["model"] = None
    assert client.get("/health").status_code == 503


def test_health_and_predict_with_model():
    service.state["model"] = DummyModel()
    service.state["metadata"] = {"model_version": "7"}
    assert client.get("/health").json() == {"status": "ok", "model_version": "7"}
    body = {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}
    assert client.post("/predict", json=body).json() == {"class": 1}
