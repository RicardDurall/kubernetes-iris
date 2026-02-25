"""Machine learning model definition and utilities."""

from typing import Any, Dict, Tuple

import joblib
import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from iris_classifier.config import settings


class IrisClassifier:
    """Wrapper class for Iris classification model."""

    # Class names for the Iris dataset
    CLASS_NAMES = ["setosa", "versicolor", "virginica"]

    # Feature names
    FEATURE_NAMES = ["sepal_length", "sepal_width", "petal_length", "petal_width"]

    def __init__(
        self,
        n_estimators: int = settings.n_estimators,
        max_depth: int | None = settings.max_depth,
        random_state: int = settings.random_state,
    ) -> None:
        """Initialize the Iris classifier.

        Args:
            n_estimators: Number of trees in the random forest
            max_depth: Maximum depth of trees
            random_state: Random seed for reproducibility
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
        )
        self.random_state = random_state
        self.is_trained = False

    def load_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Load and split the Iris dataset.

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        iris = load_iris()
        X, y = iris.data, iris.target

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=settings.test_size, random_state=self.random_state
        )

        return X_train, X_test, y_train, y_test

    def train(
        self, X_train: np.ndarray, y_train: np.ndarray
    ) -> "IrisClassifier":
        """Train the model.

        Args:
            X_train: Training features
            y_train: Training labels

        Returns:
            Self for method chaining
        """
        self.model.fit(X_train, y_train)
        self.is_trained = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions.

        Args:
            X: Features to predict on

        Returns:
            Predicted class labels
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities.

        Args:
            X: Features to predict on

        Returns:
            Prediction probabilities for each class
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        return self.model.predict_proba(X)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Evaluate the model.

        Args:
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary with evaluation metrics
        """
        y_pred = self.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)
        class_report = classification_report(
            y_test, y_pred, target_names=self.CLASS_NAMES, output_dict=True
        )

        return {
            "accuracy": accuracy,
            "confusion_matrix": conf_matrix.tolist(),
            "classification_report": class_report,
        }

    def save(self, filepath: str) -> None:
        """Save the model to disk.

        Args:
            filepath: Path to save the model
        """
        if not self.is_trained:
            raise ValueError("Cannot save an untrained model")
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "IrisClassifier":
        """Load a model from disk.

        Args:
            filepath: Path to the saved model

        Returns:
            Loaded IrisClassifier instance
        """
        return joblib.load(filepath)
