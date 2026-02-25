#!/bin/bash
set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set defaults if not in .env
GCP_PROJECT=${GCP_PROJECT_ID:-"your-gcp-project-id"}
GCP_REGION=${GCP_REGION:-"us-central1"}
GCP_ZONE=${GCP_ZONE:-"us-central1-a"}
CLUSTER_NAME=${CLUSTER_NAME:-"iris-classifier-cluster"}

echo "Setting up GKE cluster..."
echo "Project: $GCP_PROJECT"
echo "Region: $GCP_REGION"
echo "Cluster: $CLUSTER_NAME"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Set project
echo "Setting GCP project..."
gcloud config set project $GCP_PROJECT

# Enable required APIs
echo "Enabling required GCP APIs..."
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Create GKE cluster
echo "Creating GKE cluster (this may take 5-10 minutes)..."
gcloud container clusters create $CLUSTER_NAME \
    --region=$GCP_REGION \
    --num-nodes=2 \
    --machine-type=e2-standard-4 \
    --disk-size=50 \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=5 \
    --enable-autorepair \
    --enable-autoupgrade \
    --addons=HorizontalPodAutoscaling,HttpLoadBalancing \
    --workload-pool=$GCP_PROJECT.svc.id.goog \
    || echo "Cluster might already exist, continuing..."

# Get cluster credentials
echo "Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --region=$GCP_REGION

# Create namespace
echo "Creating Kubernetes namespace..."
kubectl create namespace iris-ml --dry-run=client -o yaml | kubectl apply -f -

# Configure Docker for GCR
echo "Configuring Docker authentication for GCR..."
gcloud auth configure-docker

echo "✓ GKE setup complete!"
echo ""
echo "Cluster info:"
gcloud container clusters describe $CLUSTER_NAME --region=$GCP_REGION --format="value(endpoint,currentMasterVersion)"
echo ""
echo "Next steps:"
echo "  1. Build Docker images: make docker-build"
echo "  2. Push to GCR: make docker-push-gcr GCP_PROJECT=$GCP_PROJECT"
echo "  3. Deploy: make deploy-gke"
