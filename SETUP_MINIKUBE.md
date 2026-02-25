# Minikube Setup Guide

This guide will help you install Minikube and kubectl on Linux to test the Iris Classifier locally.

## Prerequisites

- Docker installed and running
- At least 4GB of free RAM
- At least 20GB of free disk space
- Internet connection for downloading tools

## Installation Steps

### 1. Install kubectl

```bash
# Download the latest kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Make it executable
chmod +x kubectl

# Move to PATH
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client
```

### 2. Install Minikube

```bash
# Download Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Install Minikube
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify installation
minikube version
```

### 3. Start Minikube

```bash
# Start Minikube with recommended resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Or use the provided script
cd /home/ridu/Desktop/ri/kubernetes
make minikube-start
```

### 4. Verify Minikube is Running

```bash
# Check status
minikube status

# Check cluster info
kubectl cluster-info

# Check nodes
kubectl get nodes
```

## Deploy Iris Classifier

Once Minikube is running, deploy the application:

```bash
# Navigate to project directory
cd /home/ridu/Desktop/ri/kubernetes

# Deploy everything automatically
make deploy-local
```

This will:
1. Configure Docker to use Minikube's daemon
2. Build both Docker images
3. Deploy all Kubernetes resources
4. Wait for training to complete
5. Start the API service

## Access the API

After deployment completes:

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Test health endpoint
curl http://${MINIKUBE_IP}:30080/health

# Make a prediction
curl -X POST http://${MINIKUBE_IP}:30080/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }'

# Open API documentation in browser
xdg-open "http://${MINIKUBE_IP}:30080/docs"
```

## Useful Commands

### View Resources

```bash
# All resources in iris-ml namespace
kubectl get all -n iris-ml

# Watch pods
kubectl get pods -n iris-ml -w

# Deployment status
kubectl rollout status deployment/iris-classifier -n iris-ml
```

### View Logs

```bash
# Training job logs
kubectl logs job/iris-training-job -n iris-ml

# API logs (all pods)
kubectl logs -f -l app=iris-classifier,component=api -n iris-ml

# Specific pod
kubectl logs -f <pod-name> -n iris-ml
```

### Dashboard

```bash
# Open Kubernetes dashboard
minikube dashboard
```

### Troubleshooting

```bash
# Check events
kubectl get events -n iris-ml --sort-by='.lastTimestamp'

# Describe deployment
kubectl describe deployment iris-classifier -n iris-ml

# Describe pod
kubectl describe pod <pod-name> -n iris-ml

# Exec into pod
kubectl exec -it deployment/iris-classifier -n iris-ml -- /bin/bash
```

## Cleanup

```bash
# Delete namespace (removes all resources)
kubectl delete namespace iris-ml

# Or use make command
make undeploy-local

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

## Common Issues

### Issue: Minikube won't start

**Solution**:
```bash
# Delete and recreate
minikube delete
minikube start --cpus=4 --memory=8192 --driver=docker
```

### Issue: Docker images not found

**Solution**:
```bash
# Make sure to use Minikube's Docker daemon
eval $(minikube docker-env)

# Rebuild images
docker build -f docker/Dockerfile.train -t iris-classifier-train:latest .
docker build -f docker/Dockerfile.serve -t iris-classifier-serve:latest .
```

### Issue: Training job failed

**Solution**:
```bash
# Check logs
kubectl logs job/iris-training-job -n iris-ml

# Delete and recreate
kubectl delete job iris-training-job -n iris-ml
kubectl apply -f k8s/local/training-job.yaml
```

### Issue: Pods in CrashLoopBackOff

**Solution**:
```bash
# Check pod logs
kubectl logs <pod-name> -n iris-ml

# Check if model exists
kubectl exec -it deployment/iris-classifier -n iris-ml -- ls -la /app/models/

# May need to retrain model
kubectl delete job iris-training-job -n iris-ml
kubectl apply -f k8s/local/training-job.yaml
```

## Next Steps

After successfully deploying locally:

1. ✅ Verify all endpoints work
2. ✅ Test model predictions
3. ✅ Check logs for errors
4. ✅ Test pod scaling
5. ➡️ Proceed to GKE deployment for production

## Alternative: Kind (Kubernetes in Docker)

If Minikube doesn't work, you can use Kind as an alternative:

```bash
# Install Kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Create cluster
kind create cluster --name iris-classifier

# Load Docker images
kind load docker-image iris-classifier-train:latest --name iris-classifier
kind load docker-image iris-classifier-serve:latest --name iris-classifier

# Deploy
kubectl apply -f k8s/local/
```

## Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kubernetes Concepts](https://kubernetes.io/docs/concepts/)
