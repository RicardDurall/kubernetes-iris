# Local Kubernetes Deployment (Minikube)

This directory contains Kubernetes manifests for deploying the Iris Classifier locally using Minikube.

## Architecture

```
┌─────────────────────────────────────────┐
│          Minikube Cluster               │
│  ┌───────────────────────────────────┐  │
│  │     Namespace: iris-ml            │  │
│  │                                   │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │  Training Job (one-time)    │  │  │
│  │  │  - Trains model             │  │  │
│  │  │  - Saves to PVC             │  │  │
│  │  └─────────────────────────────┘  │  │
│  │              ↓                    │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │  PersistentVolumeClaim      │  │  │
│  │  │  - Shared model storage     │  │  │
│  │  └─────────────────────────────┘  │  │
│  │              ↓                    │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │  Deployment (2 replicas)    │  │  │
│  │  │  - Serves predictions       │  │  │
│  │  │  - Reads model from PVC     │  │  │
│  │  └─────────────────────────────┘  │  │
│  │              ↓                    │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │  Service (NodePort)         │  │  │
│  │  │  - Exposes API externally   │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Prerequisites

1. **Minikube** installed and running
2. **kubectl** configured to use Minikube
3. **Docker images** built locally

## Quick Start

### 1. Start Minikube

```bash
# From project root
make minikube-start

# Or manually:
minikube start --cpus=4 --memory=8192
```

### 2. Build Docker Images

**Important**: Build images using Minikube's Docker daemon so they're available in the cluster:

```bash
# Configure shell to use Minikube's Docker
eval $(minikube docker-env)

# Build images
docker build -f docker/Dockerfile.train -t iris-classifier-train:latest .
docker build -f docker/Dockerfile.serve -t iris-classifier-serve:latest .

# Verify images
docker images | grep iris-classifier
```

### 3. Deploy to Minikube

```bash
# Deploy all manifests
kubectl apply -f k8s/local/

# Or step by step:
kubectl apply -f k8s/local/namespace.yaml
kubectl apply -f k8s/local/configmap.yaml
kubectl apply -f k8s/local/pv-local.yaml
kubectl apply -f k8s/local/training-job.yaml
kubectl apply -f k8s/local/deployment.yaml
kubectl apply -f k8s/local/service.yaml
```

### 4. Verify Deployment

```bash
# Check all resources
kubectl get all -n iris-ml

# Watch training job
kubectl logs -f job/iris-training-job -n iris-ml

# Check if training completed
kubectl get jobs -n iris-ml

# Check deployment
kubectl get pods -n iris-ml
kubectl describe deployment iris-classifier -n iris-ml
```

### 5. Access the API

```bash
# Get Minikube IP
minikube ip

# Get service URL
minikube service iris-classifier-service -n iris-ml --url

# Or access via NodePort
curl http://$(minikube ip):30080/health

# Make a prediction
curl -X POST http://$(minikube ip):30080/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }'
```

## Components

### namespace.yaml
Creates the `iris-ml` namespace for all resources.

### configmap.yaml
Contains environment variables for model configuration:
- `RANDOM_STATE`: Random seed (42)
- `TEST_SIZE`: Test split ratio (0.2)
- `N_ESTIMATORS`: Number of trees (100)
- `MODEL_PATH`: Path to save model

### pv-local.yaml
Creates:
- **PersistentVolume**: 1Gi storage at `/tmp/iris-models`
- **PersistentVolumeClaim**: Shared between training and serving

### training-job.yaml
Kubernetes Job that:
- Runs the training container once
- Saves model to PVC
- Auto-cleans up after 1 hour

### deployment.yaml
Kubernetes Deployment with:
- 2 replicas for high availability
- Health checks (liveness + readiness probes)
- Resource limits
- Mounts model from PVC

### service.yaml
NodePort Service exposing the API on port 30080.

## Troubleshooting

### Training Job Failed

```bash
# Check logs
kubectl logs job/iris-training-job -n iris-ml

# Describe job
kubectl describe job iris-training-job -n iris-ml

# Delete and retry
kubectl delete job iris-training-job -n iris-ml
kubectl apply -f k8s/local/training-job.yaml
```

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n iris-ml

# Describe pod
kubectl describe pod <pod-name> -n iris-ml

# Check events
kubectl get events -n iris-ml --sort-by='.lastTimestamp'

# Check if images are available
eval $(minikube docker-env)
docker images | grep iris-classifier
```

### Model Not Found in Serving Pods

```bash
# Check PVC
kubectl describe pvc iris-model-pvc -n iris-ml

# Check if training job completed
kubectl get jobs -n iris-ml

# Exec into pod and check
kubectl exec -it deployment/iris-classifier -n iris-ml -- ls -la /app/models/
```

### Service Not Accessible

```bash
# Check service
kubectl get svc -n iris-ml
kubectl describe svc iris-classifier-service -n iris-ml

# Get URL
minikube service iris-classifier-service -n iris-ml --url

# Port forward as alternative
kubectl port-forward -n iris-ml svc/iris-classifier-service 8000:80
```

## Updating the Deployment

### Rebuild and Redeploy

```bash
# Use Minikube's Docker
eval $(minikube docker-env)

# Rebuild images
docker build -f docker/Dockerfile.serve -t iris-classifier-serve:latest .

# Restart deployment
kubectl rollout restart deployment/iris-classifier -n iris-ml

# Watch rollout
kubectl rollout status deployment/iris-classifier -n iris-ml
```

### Retrain Model

```bash
# Delete old job
kubectl delete job iris-training-job -n iris-ml

# Create new job
kubectl apply -f k8s/local/training-job.yaml

# Watch logs
kubectl logs -f job/iris-training-job -n iris-ml
```

## Cleanup

```bash
# Delete all resources in namespace
kubectl delete namespace iris-ml

# Or delete individually
kubectl delete -f k8s/local/

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

## Monitoring

### View Logs

```bash
# Training job logs
kubectl logs -f job/iris-training-job -n iris-ml

# API logs (all pods)
kubectl logs -f -l app=iris-classifier,component=api -n iris-ml

# Specific pod
kubectl logs -f <pod-name> -n iris-ml
```

### Dashboard

```bash
# Open Kubernetes dashboard
minikube dashboard

# Or just get URL
minikube dashboard --url
```

### Resource Usage

```bash
# Top pods
kubectl top pods -n iris-ml

# Top nodes
kubectl top nodes
```

## Next Steps

After successful local deployment:
1. Test the API endpoints thoroughly
2. Verify model persistence across pod restarts
3. Test scaling: `kubectl scale deployment iris-classifier --replicas=3 -n iris-ml`
4. Proceed to GKE deployment for production
