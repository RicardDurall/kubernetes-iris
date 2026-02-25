"""FastAPI serving application for the Iris classifier."""

import sys
from pathlib import Path
from typing import List

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from iris_classifier.config import settings
from iris_classifier.model import IrisClassifier
from iris_classifier.utils import format_prediction_response, setup_logging

# Set up logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="API for Iris flower classification using machine learning",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
model: IrisClassifier | None = None


class IrisFeatures(BaseModel):
    """Input features for Iris classification."""

    sepal_length: float = Field(..., ge=0, description="Sepal length in cm")
    sepal_width: float = Field(..., ge=0, description="Sepal width in cm")
    petal_length: float = Field(..., ge=0, description="Petal length in cm")
    petal_width: float = Field(..., ge=0, description="Petal width in cm")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2,
            }
        }


class PredictionResponse(BaseModel):
    """Response model for predictions."""

    prediction: str = Field(..., description="Predicted class name")
    prediction_index: int = Field(..., description="Predicted class index")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")
    probabilities: dict[str, float] = Field(..., description="Class probabilities")


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    model_loaded: bool
    model_path: str


@app.on_event("startup")
async def load_model() -> None:
    """Load the trained model on application startup."""
    global model
    model_path = settings.get_model_path()

    logger.info(f"Loading model from {model_path}...")

    if not model_path.exists():
        logger.error(f"Model file not found at {model_path}")
        logger.error("Please train the model first using: poetry run train")
        return

    try:
        model = IrisClassifier.load(str(model_path))
        logger.info("✓ Model loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load model: {e}", exc_info=True)


@app.get("/", response_model=dict)
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "Iris Classifier API",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        model_path=str(settings.get_model_path()),
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict(features: IrisFeatures) -> PredictionResponse:
    """Make a prediction for given iris features.

    Args:
        features: Iris flower measurements

    Returns:
        Prediction results with probabilities

    Raises:
        HTTPException: If model is not loaded
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check server logs.",
        )

    # Convert input to numpy array
    X = np.array(
        [[
            features.sepal_length,
            features.sepal_width,
            features.petal_length,
            features.petal_width,
        ]]
    )

    # Make prediction
    try:
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]

        # Format response
        result = format_prediction_response(
            prediction=prediction,
            probabilities=probabilities,
            class_names=IrisClassifier.CLASS_NAMES,
        )

        logger.info(f"Prediction: {result['prediction']} "
                   f"(confidence: {result['confidence']:.4f})")

        return PredictionResponse(**result)

    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=List[PredictionResponse])
async def predict_batch(features_list: List[IrisFeatures]) -> List[PredictionResponse]:
    """Make predictions for multiple samples.

    Args:
        features_list: List of iris flower measurements

    Returns:
        List of prediction results

    Raises:
        HTTPException: If model is not loaded
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check server logs.",
        )

    # Convert inputs to numpy array
    X = np.array([
        [f.sepal_length, f.sepal_width, f.petal_length, f.petal_width]
        for f in features_list
    ])

    # Make predictions
    try:
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)

        results = [
            PredictionResponse(
                **format_prediction_response(
                    prediction=pred,
                    probabilities=probs,
                    class_names=IrisClassifier.CLASS_NAMES,
                )
            )
            for pred, probs in zip(predictions, probabilities)
        ]

        logger.info(f"Batch prediction completed for {len(results)} samples")
        return results

    except Exception as e:
        logger.error(f"Batch prediction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Batch prediction failed: {str(e)}"
        )


def main() -> None:
    """Main entry point for running the server."""
    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
