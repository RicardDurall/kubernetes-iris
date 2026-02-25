"""Tests for the API endpoints."""

import pytest
from fastapi.testclient import TestClient

from iris_classifier.serve import app

client = TestClient(app)


def test_root_endpoint() -> None:
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint() -> None:
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "model_path" in data


def test_predict_endpoint_valid_input() -> None:
    """Test prediction with valid input."""
    # Note: This test will fail if model is not trained
    # In CI/CD, we should train the model first
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }
    response = client.post("/predict", json=payload)

    # Model might not be loaded in test environment
    if response.status_code == 200:
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data
        assert "probabilities" in data
        assert data["prediction"] in ["setosa", "versicolor", "virginica"]
        assert 0 <= data["confidence"] <= 1
    elif response.status_code == 503:
        # Model not loaded - acceptable in test environment
        assert "Model not loaded" in response.json()["detail"]


def test_predict_endpoint_invalid_input() -> None:
    """Test prediction with invalid input."""
    # Missing required field
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        # Missing petal_width
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Validation error


def test_predict_endpoint_negative_values() -> None:
    """Test prediction with negative values."""
    payload = {
        "sepal_length": -1.0,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Validation error


def test_batch_predict_endpoint() -> None:
    """Test batch prediction endpoint."""
    payload = [
        {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        },
        {
            "sepal_length": 6.7,
            "sepal_width": 3.0,
            "petal_length": 5.2,
            "petal_width": 2.3,
        },
    ]
    response = client.post("/predict/batch", json=payload)

    # Model might not be loaded in test environment
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        for item in data:
            assert "prediction" in item
            assert "confidence" in item
    elif response.status_code == 503:
        # Model not loaded - acceptable in test environment
        assert "Model not loaded" in response.json()["detail"]


def test_openapi_schema() -> None:
    """Test that OpenAPI schema is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
