"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from iris_classifier.model import IrisClassifier


@pytest.fixture
def sample_features() -> np.ndarray:
    """Sample iris features for testing."""
    return np.array([[5.1, 3.5, 1.4, 0.2]])


@pytest.fixture
def sample_batch_features() -> np.ndarray:
    """Sample batch of iris features for testing."""
    return np.array([
        [5.1, 3.5, 1.4, 0.2],
        [6.7, 3.0, 5.2, 2.3],
        [5.9, 3.0, 4.2, 1.5],
    ])


@pytest.fixture
def trained_classifier() -> IrisClassifier:
    """Create a trained classifier for testing."""
    classifier = IrisClassifier(n_estimators=10, random_state=42)
    X_train, _, y_train, _ = classifier.load_data()
    classifier.train(X_train, y_train)
    return classifier


@pytest.fixture
def temp_model_path() -> Path:
    """Create a temporary path for model saving."""
    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
        return Path(f.name)
