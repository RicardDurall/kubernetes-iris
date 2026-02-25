"""Training script for the Iris classifier."""

import sys
from pathlib import Path

from iris_classifier.config import settings
from iris_classifier.model import IrisClassifier
from iris_classifier.utils import ensure_dir, save_metrics, setup_logging

# Set up logging
logger = setup_logging()


def train_model() -> None:
    """Train the Iris classifier and save it to disk."""
    logger.info("Starting training process...")
    logger.info(f"Configuration: random_state={settings.random_state}, "
                f"test_size={settings.test_size}, n_estimators={settings.n_estimators}")

    # Initialize model
    classifier = IrisClassifier(
        n_estimators=settings.n_estimators,
        max_depth=settings.max_depth,
        random_state=settings.random_state,
    )

    # Load and split data
    logger.info("Loading Iris dataset...")
    X_train, X_test, y_train, y_test = classifier.load_data()
    logger.info(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")

    # Train model
    logger.info("Training model...")
    classifier.train(X_train, y_train)
    logger.info("Training completed!")

    # Evaluate model
    logger.info("Evaluating model on test set...")
    metrics = classifier.evaluate(X_test, y_test)
    logger.info(f"Test Accuracy: {metrics['accuracy']:.4f}")

    # Print detailed metrics
    logger.info("\nClassification Report:")
    for class_name, class_metrics in metrics["classification_report"].items():
        if isinstance(class_metrics, dict):
            logger.info(f"  {class_name}:")
            logger.info(f"    Precision: {class_metrics.get('precision', 0):.4f}")
            logger.info(f"    Recall: {class_metrics.get('recall', 0):.4f}")
            logger.info(f"    F1-score: {class_metrics.get('f1-score', 0):.4f}")

    # Save model
    model_path = settings.get_model_path()
    ensure_dir(model_path.parent)
    logger.info(f"Saving model to {model_path}...")
    classifier.save(str(model_path))

    # Save metrics
    metrics_path = model_path.parent / "metrics.json"
    logger.info(f"Saving metrics to {metrics_path}...")
    save_metrics(metrics, metrics_path)

    logger.info("✓ Training pipeline completed successfully!")


def main() -> None:
    """Main entry point for the training script."""
    try:
        train_model()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
