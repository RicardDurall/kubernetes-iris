"""Configuration management for the Iris Classifier."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Project paths
    project_root: Path = Path(__file__).parent.parent.parent
    model_path: Path = Field(default=Path("models/iris_model.joblib"))
    data_path: Path = Field(default=Path("data"))

    # Model configuration
    random_state: int = Field(default=42, description="Random seed for reproducibility")
    test_size: float = Field(default=0.2, ge=0.0, le=1.0, description="Test set size")
    n_estimators: int = Field(default=100, ge=1, description="Number of trees in RandomForest")
    max_depth: Optional[int] = Field(default=None, description="Max depth of trees")

    # API configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_title: str = Field(default="Iris Classifier API")
    api_version: str = Field(default="0.1.0")

    # MLflow configuration
    mlflow_tracking_uri: str = Field(default="", description="MLflow tracking server URI")
    mlflow_experiment_name: str = Field(default="iris-classifier")

    # GCP configuration
    gcp_project_id: str = Field(default="")
    gcp_region: str = Field(default="us-central1")
    gcp_zone: str = Field(default="us-central1-a")
    gcs_bucket: str = Field(default="")

    # Kubernetes configuration
    k8s_namespace: str = Field(default="iris-ml")
    cluster_name: str = Field(default="iris-classifier-cluster")

    # Model version
    model_version: str = Field(default="v1")

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env

    def get_model_path(self) -> Path:
        """Get absolute path to model file."""
        if self.model_path.is_absolute():
            return self.model_path
        return self.project_root / self.model_path

    def get_data_path(self) -> Path:
        """Get absolute path to data directory."""
        if self.data_path.is_absolute():
            return self.data_path
        return self.project_root / self.data_path


# Global settings instance
settings = Settings()
