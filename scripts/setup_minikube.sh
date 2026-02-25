#!/bin/bash
set -e

echo "Setting up Minikube for Iris Classifier..."

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "Error: Minikube is not installed. Please install it first."
    exit 1
fi

# Start Minikube if not running
if ! minikube status &> /dev/null; then
    echo "Starting Minikube..."
    minikube start \
        --cpus=4 \
        --memory=8192 \
        --driver=docker \
        --kubernetes-version=v1.28.0
else
    echo "Minikube is already running."
fi

# Enable addons
echo "Enabling Minikube addons..."
minikube addons enable metrics-server
minikube addons enable dashboard
minikube addons enable ingress

# Configure Docker to use Minikube's Docker daemon
echo "Configuring Docker environment..."
eval $(minikube docker-env)

# Create namespace
echo "Creating Kubernetes namespace..."
kubectl create namespace iris-ml --dry-run=client -o yaml | kubectl apply -f -

echo "✓ Minikube setup complete!"
echo ""
echo "Useful commands:"
echo "  minikube dashboard        - Open Kubernetes dashboard"
echo "  minikube service list     - List all services"
echo "  eval \$(minikube docker-env) - Use Minikube's Docker daemon"
echo "  kubectl get all -n iris-ml - Check deployed resources"
