"""Utility functions for the Iris Classifier."""

import json
import logging
from pathlib import Path
from typing import Any, Dict

import numpy as np


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Set up logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("iris_classifier")


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists, create if it doesn't.

    Args:
        path: Directory path

    Returns:
        The path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_metrics(metrics: Dict[str, Any], filepath: Path) -> None:
    """Save metrics to a JSON file.

    Args:
        metrics: Dictionary of metrics to save
        filepath: Path to save the metrics
    """
    # Convert numpy arrays to lists for JSON serialization
    metrics_serializable = convert_numpy_to_python(metrics)

    ensure_dir(filepath.parent)
    with open(filepath, "w") as f:
        json.dump(metrics_serializable, f, indent=2)


def load_metrics(filepath: Path) -> Dict[str, Any]:
    """Load metrics from a JSON file.

    Args:
        filepath: Path to the metrics file

    Returns:
        Dictionary of metrics
    """
    with open(filepath, "r") as f:
        return json.load(f)


def convert_numpy_to_python(obj: Any) -> Any:
    """Recursively convert numpy types to Python native types.

    Args:
        obj: Object to convert

    Returns:
        Converted object
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_numpy_to_python(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_python(item) for item in obj]
    else:
        return obj


def format_prediction_response(
    prediction: int, probabilities: np.ndarray, class_names: list[str]
) -> Dict[str, Any]:
    """Format prediction results into a structured response.

    Args:
        prediction: Predicted class index
        probabilities: Prediction probabilities for all classes
        class_names: List of class names

    Returns:
        Formatted prediction response
    """
    return {
        "prediction": class_names[prediction],
        "prediction_index": int(prediction),
        "confidence": float(probabilities[prediction]),
        "probabilities": {
            class_name: float(prob)
            for class_name, prob in zip(class_names, probabilities)
        },
    }
