"""Tests for the model module."""

from pathlib import Path

import numpy as np
import pytest

from iris_classifier.model import IrisClassifier


def test_model_initialization() -> None:
    """Test model initialization."""
    classifier = IrisClassifier(n_estimators=50, random_state=42)
    assert classifier.model is not None
    assert classifier.random_state == 42
    assert not classifier.is_trained


def test_load_data() -> None:
    """Test data loading."""
    classifier = IrisClassifier()
    X_train, X_test, y_train, y_test = classifier.load_data()

    assert len(X_train) > 0
    assert len(X_test) > 0
    assert len(y_train) == len(X_train)
    assert len(y_test) == len(X_test)
    assert X_train.shape[1] == 4  # 4 features


def test_training(trained_classifier: IrisClassifier) -> None:
    """Test model training."""
    assert trained_classifier.is_trained
    assert trained_classifier.model is not None


def test_prediction(
    trained_classifier: IrisClassifier, sample_features: np.ndarray
) -> None:
    """Test single prediction."""
    prediction = trained_classifier.predict(sample_features)
    assert len(prediction) == 1
    assert 0 <= prediction[0] <= 2  # Valid class index


def test_prediction_proba(
    trained_classifier: IrisClassifier, sample_features: np.ndarray
) -> None:
    """Test prediction probabilities."""
    probabilities = trained_classifier.predict_proba(sample_features)
    assert probabilities.shape == (1, 3)  # 1 sample, 3 classes
    assert np.allclose(probabilities.sum(axis=1), 1.0)  # Probabilities sum to 1


def test_batch_prediction(
    trained_classifier: IrisClassifier, sample_batch_features: np.ndarray
) -> None:
    """Test batch prediction."""
    predictions = trained_classifier.predict(sample_batch_features)
    assert len(predictions) == 3
    assert all(0 <= pred <= 2 for pred in predictions)


def test_prediction_before_training() -> None:
    """Test that prediction fails before training."""
    classifier = IrisClassifier()
    with pytest.raises(ValueError, match="Model must be trained"):
        classifier.predict(np.array([[5.1, 3.5, 1.4, 0.2]]))


def test_evaluate(trained_classifier: IrisClassifier) -> None:
    """Test model evaluation."""
    _, X_test, _, y_test = trained_classifier.load_data()
    metrics = trained_classifier.evaluate(X_test, y_test)

    assert "accuracy" in metrics
    assert "confusion_matrix" in metrics
    assert "classification_report" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0


def test_save_and_load(
    trained_classifier: IrisClassifier, temp_model_path: Path
) -> None:
    """Test model saving and loading."""
    # Save model
    trained_classifier.save(str(temp_model_path))
    assert temp_model_path.exists()

    # Load model
    loaded_classifier = IrisClassifier.load(str(temp_model_path))
    assert loaded_classifier.is_trained

    # Test that loaded model works
    sample = np.array([[5.1, 3.5, 1.4, 0.2]])
    original_pred = trained_classifier.predict(sample)
    loaded_pred = loaded_classifier.predict(sample)
    assert original_pred == loaded_pred

    # Cleanup
    temp_model_path.unlink()


def test_save_untrained_model() -> None:
    """Test that saving untrained model raises error."""
    classifier = IrisClassifier()
    with pytest.raises(ValueError, match="Cannot save an untrained model"):
        classifier.save("dummy_path.joblib")


def test_class_names() -> None:
    """Test class names constant."""
    assert len(IrisClassifier.CLASS_NAMES) == 3
    assert "setosa" in IrisClassifier.CLASS_NAMES
    assert "versicolor" in IrisClassifier.CLASS_NAMES
    assert "virginica" in IrisClassifier.CLASS_NAMES


def test_feature_names() -> None:
    """Test feature names constant."""
    assert len(IrisClassifier.FEATURE_NAMES) == 4
    assert "sepal_length" in IrisClassifier.FEATURE_NAMES
    assert "petal_width" in IrisClassifier.FEATURE_NAMES
