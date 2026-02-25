#!/bin/bash
set -e

echo "============================================"
echo "Deploying Iris Classifier to Minikube"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Minikube is running
if ! minikube status > /dev/null 2>&1; then
    echo -e "${RED}Error: Minikube is not running${NC}"
    echo "Please start Minikube first: make minikube-start"
    exit 1
fi

echo -e "${GREEN}✓ Minikube is running${NC}"

# Configure Docker to use Minikube's daemon
echo ""
echo "Configuring Docker environment..."
eval $(minikube docker-env)
echo -e "${GREEN}✓ Docker environment configured${NC}"

# Build Docker images
echo ""
echo "Building Docker images..."
echo "  - Building training image..."
docker build -q -f docker/Dockerfile.train -t iris-classifier-train:latest .
echo -e "${GREEN}  ✓ Training image built${NC}"

echo "  - Building serving image..."
docker build -q -f docker/Dockerfile.serve -t iris-classifier-serve:latest .
echo -e "${GREEN}  ✓ Serving image built${NC}"

# Verify images
echo ""
echo "Verifying images..."
docker images | grep iris-classifier
echo ""

# Deploy to Kubernetes
echo "Deploying to Kubernetes..."
echo ""

echo "  1. Creating namespace..."
kubectl apply -f k8s/local/namespace.yaml
echo -e "${GREEN}     ✓ Namespace created${NC}"

echo "  2. Creating ConfigMap..."
kubectl apply -f k8s/local/configmap.yaml
echo -e "${GREEN}     ✓ ConfigMap created${NC}"

echo "  3. Creating PersistentVolume and PVC..."
kubectl apply -f k8s/local/pv-local.yaml
echo -e "${GREEN}     ✓ Storage created${NC}"

echo "  4. Starting training job..."
kubectl apply -f k8s/local/training-job.yaml
echo -e "${GREEN}     ✓ Training job created${NC}"

echo "  5. Creating deployment..."
kubectl apply -f k8s/local/deployment.yaml
echo -e "${GREEN}     ✓ Deployment created${NC}"

echo "  6. Creating service..."
kubectl apply -f k8s/local/service.yaml
echo -e "${GREEN}     ✓ Service created${NC}"

echo ""
echo "============================================"
echo "Deployment initiated successfully!"
echo "============================================"
echo ""

# Wait for training job
echo "Waiting for training job to complete..."
kubectl wait --for=condition=complete --timeout=300s job/iris-training-job -n iris-ml || {
    echo -e "${YELLOW}Warning: Training job did not complete in time${NC}"
    echo "Check logs: kubectl logs job/iris-training-job -n iris-ml"
}

# Check training job status
JOB_STATUS=$(kubectl get job iris-training-job -n iris-ml -o jsonpath='{.status.conditions[?(@.type=="Complete")].status}')
if [ "$JOB_STATUS" == "True" ]; then
    echo -e "${GREEN}✓ Training job completed successfully!${NC}"
else
    echo -e "${YELLOW}⚠ Training job may still be running. Check: kubectl get jobs -n iris-ml${NC}"
fi

echo ""

# Wait for deployment
echo "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/iris-classifier -n iris-ml || {
    echo -e "${RED}Warning: Deployment did not become ready in time${NC}"
}

echo ""
echo "============================================"
echo "Deployment Status"
echo "============================================"
echo ""

# Show status
kubectl get all -n iris-ml

echo ""
echo "============================================"
echo "Access Information"
echo "============================================"
echo ""

# Get service URL
MINIKUBE_IP=$(minikube ip)
SERVICE_URL="http://${MINIKUBE_IP}:30080"

echo "Service URL: ${SERVICE_URL}"
echo ""
echo "Test the API:"
echo "  Health check:"
echo "    curl ${SERVICE_URL}/health"
echo ""
echo "  Make prediction:"
echo "    curl -X POST ${SERVICE_URL}/predict \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"sepal_length\": 5.1, \"sepal_width\": 3.5, \"petal_length\": 1.4, \"petal_width\": 0.2}'"
echo ""
echo "Open in browser:"
echo "  API docs: ${SERVICE_URL}/docs"
echo ""
echo "View logs:"
echo "  kubectl logs -f -l app=iris-classifier -n iris-ml"
echo ""
echo "Dashboard:"
echo "  minikube dashboard"
echo ""
echo -e "${GREEN}Deployment complete!${NC}"
