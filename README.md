# Iris Classifier - MLOps with Kubernetes

A complete MLOps project demonstrating ML model training, containerization, and deployment using Kubernetes, Kubeflow, and CI/CD with GitHub Actions.

## Project Overview

This project builds a machine learning classifier for the Iris dataset and demonstrates modern MLOps practices:

- **ML Framework**: scikit-learn
- **API Framework**: FastAPI
- **Containerization**: Docker
- **Orchestration**: Kubernetes (Minikube locally, GKE for production)
- **ML Pipelines**: Kubeflow Pipelines
- **CI/CD**: GitHub Actions
- **Package Management**: Poetry
- **Development**: Dev Containers

## Project Structure

```
kubernetes-iris/
├── .devcontainer/          # VS Code dev container configuration
├── .github/workflows/      # GitHub Actions CI/CD pipelines
├── src/iris_classifier/    # Main application code
├── docker/                 # Dockerfiles for training and serving
├── k8s/                    # Kubernetes manifests
│   ├── local/             # Minikube configurations
│   └── gke/               # GKE configurations
├── kubeflow/              # Kubeflow pipeline definitions
├── tests/                 # Unit and integration tests
├── notebooks/             # Jupyter notebooks for exploration
├── scripts/               # Helper scripts
└── pyproject.toml         # Poetry dependencies
```

## Prerequisites

- Python 3.10+
- Poetry
- Docker
- kubectl
- Minikube (for local development)
- GCP account (for production deployment)
- VS Code with Dev Containers extension (recommended)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/YOUR_USERNAME/kubernetes-iris.git
cd kubernetes-iris

# Copy environment variables
cp .env.example .env

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### 2. Local Development

#### Train Model Locally

```bash
make run-train
```

#### Run API Server Locally

```bash
make run-serve
```

Test the API:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
```

### 3. Development with Dev Container

Open the project in VS Code and select "Reopen in Container" when prompted.

### 4. Testing

```bash
# Run all tests
make test

# Run linting
make lint

# Format code
make format
```

### 5. Docker Build

```bash
# Build Docker images
make docker-build

# Test training container
docker run --rm iris-classifier-train:latest

# Test serving container
docker run --rm -p 8000:8000 iris-classifier-serve:latest
```

### 6. Deploy to Minikube

```bash
# Start Minikube
make minikube-start

# Deploy application
make deploy-local

# Check deployment status
kubectl get all -n iris-ml

# Access the API
kubectl port-forward -n iris-ml svc/iris-classifier-service 8000:80
```

### 7. Deploy to GKE

```bash
# Set your GCP project
export GCP_PROJECT=your-gcp-project-id

# Create GKE cluster
make setup-gke

# Build and push images to GCR
make docker-build
make docker-push-gcr

# Deploy to GKE
make deploy-gke

# Get external IP
kubectl get svc -n iris-ml iris-classifier-service
```

## Development Workflow

1. **Feature Development**: Create feature branch
2. **Code**: Write code and tests
3. **Test Locally**: `make test && make lint`
4. **Build Docker**: `make docker-build`
5. **Test on Minikube**: `make deploy-local`
6. **Push**: Create PR
7. **CI/CD**: GitHub Actions runs tests and builds
8. **Deploy**: Merge to main triggers deployment to GKE

## API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /predict` - Make prediction
- `GET /metrics` - Prometheus metrics (optional)

## Technologies Used

- **Python 3.10**: Programming language
- **Poetry**: Dependency management
- **scikit-learn**: ML framework
- **FastAPI**: Web framework
- **Docker**: Containerization
- **Kubernetes**: Container orchestration
- **Kubeflow**: ML pipeline orchestration
- **GitHub Actions**: CI/CD
- **Google Cloud Platform**: Cloud infrastructure
- **MLflow**: Experiment tracking (optional)

## Project Phases

- [x] Phase 1: Project setup and structure
- [ ] Phase 2: ML code development
- [ ] Phase 3: Dockerization
- [ ] Phase 4: Local Kubernetes (Minikube)
- [ ] Phase 5: GitHub Actions CI
- [ ] Phase 6: GCP and GKE setup
- [ ] Phase 7: Kubeflow pipelines
- [ ] Phase 8: Complete CI/CD pipeline

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kubeflow Documentation](https://www.kubeflow.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Poetry Documentation](https://python-poetry.org/docs/)
