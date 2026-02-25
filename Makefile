.PHONY: install test lint format docker-build deploy-local deploy-gke clean help

# Variables
GCP_PROJECT ?= your-gcp-project-id
GCP_REGION ?= us-central1
CLUSTER_NAME ?= iris-classifier-cluster
IMAGE_TAG ?= latest

help:
	@echo "Available commands:"
	@echo "  make install          - Install dependencies with Poetry"
	@echo "  make test            - Run tests with coverage"
	@echo "  make lint            - Run linters (ruff, mypy)"
	@echo "  make format          - Format code with black and ruff"
	@echo "  make docker-build    - Build Docker images"
	@echo "  make docker-push-gcr - Push images to GCR"
	@echo "  make minikube-start  - Start Minikube cluster"
	@echo "  make deploy-local    - Deploy to Minikube"
	@echo "  make setup-gke       - Create GKE cluster"
	@echo "  make deploy-gke      - Deploy to GKE"
	@echo "  make run-train       - Run training locally"
	@echo "  make run-serve       - Run serving API locally"
	@echo "  make clean           - Clean cache and artifacts"

# Development
install:
	poetry install

test:
	poetry run pytest tests/ -v --cov=iris_classifier

lint:
	poetry run ruff check src/ tests/
	poetry run mypy src/

format:
	poetry run black src/ tests/
	poetry run ruff check --fix src/ tests/

# Docker
docker-build:
	docker build -f docker/Dockerfile.train -t iris-classifier-train:$(IMAGE_TAG) .
	docker build -f docker/Dockerfile.serve -t iris-classifier-serve:$(IMAGE_TAG) .

docker-push-gcr:
	docker tag iris-classifier-train:$(IMAGE_TAG) gcr.io/$(GCP_PROJECT)/iris-classifier-train:$(IMAGE_TAG)
	docker tag iris-classifier-serve:$(IMAGE_TAG) gcr.io/$(GCP_PROJECT)/iris-classifier-serve:$(IMAGE_TAG)
	docker push gcr.io/$(GCP_PROJECT)/iris-classifier-train:$(IMAGE_TAG)
	docker push gcr.io/$(GCP_PROJECT)/iris-classifier-serve:$(IMAGE_TAG)

# Local Kubernetes (Minikube)
minikube-start:
	bash scripts/setup_minikube.sh

deploy-local:
	bash scripts/deploy_local.sh

deploy-local-manual:
	kubectl apply -f k8s/local/

undeploy-local:
	kubectl delete -f k8s/local/

logs-local:
	kubectl logs -f -l app=iris-classifier -n iris-ml

status-local:
	kubectl get all -n iris-ml

describe-local:
	kubectl describe deployment iris-classifier -n iris-ml

# GKE
setup-gke:
	bash scripts/setup_gke.sh

deploy-gke:
	kubectl apply -f k8s/gke/

undeploy-gke:
	kubectl delete -f k8s/gke/

# Local development
run-train:
	poetry run python src/iris_classifier/train.py

run-serve:
	poetry run uvicorn iris_classifier.serve:app --reload --host 0.0.0.0 --port 8000

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
