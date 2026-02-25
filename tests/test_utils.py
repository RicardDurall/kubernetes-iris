"""Tests for utility functions."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from iris_classifier.utils import (
    convert_numpy_to_python,
    ensure_dir,
    format_prediction_response,
    save_metrics,
    load_metrics,
)


def test_ensure_dir() -> None:
    """Test directory creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_path = Path(tmpdir) / "test" / "nested" / "dir"
        result = ensure_dir(test_path)
        assert result.exists()
        assert result.is_dir()


def test_convert_numpy_to_python() -> None:
    """Test numpy to Python type conversion."""
    # Test numpy array
    arr = np.array([1, 2, 3])
    result = convert_numpy_to_python(arr)
    assert isinstance(result, list)
    assert result == [1, 2, 3]

    # Test numpy int
    num = np.int64(42)
    result = convert_numpy_to_python(num)
    assert isinstance(result, int)
    assert result == 42

    # Test numpy float
    num = np.float64(3.14)
    result = convert_numpy_to_python(num)
    assert isinstance(result, float)
    assert abs(result - 3.14) < 0.01

    # Test dict with numpy values
    data = {"array": np.array([1, 2]), "num": np.int32(5)}
    result = convert_numpy_to_python(data)
    assert isinstance(result["array"], list)
    assert isinstance(result["num"], int)


def test_save_and_load_metrics() -> None:
    """Test saving and loading metrics."""
    metrics = {
        "accuracy": 0.95,
        "confusion_matrix": [[10, 0], [1, 9]],
        "nested": {"precision": 0.96},
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "metrics.json"
        save_metrics(metrics, filepath)

        assert filepath.exists()

        loaded = load_metrics(filepath)
        assert loaded["accuracy"] == metrics["accuracy"]
        assert loaded["confusion_matrix"] == metrics["confusion_matrix"]
        assert loaded["nested"]["precision"] == metrics["nested"]["precision"]


def test_format_prediction_response() -> None:
    """Test prediction response formatting."""
    prediction = 0
    probabilities = np.array([0.8, 0.15, 0.05])
    class_names = ["setosa", "versicolor", "virginica"]

    result = format_prediction_response(prediction, probabilities, class_names)

    assert result["prediction"] == "setosa"
    assert result["prediction_index"] == 0
    assert abs(result["confidence"] - 0.8) < 0.01
    assert "probabilities" in result
    assert len(result["probabilities"]) == 3
    assert abs(result["probabilities"]["setosa"] - 0.8) < 0.01
