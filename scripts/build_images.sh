#!/bin/bash
set -e

IMAGE_TAG=${1:-latest}

echo "Building Docker images with tag: $IMAGE_TAG"

# Build training image
echo "Building training image..."
docker build -f docker/Dockerfile.train -t iris-classifier-train:$IMAGE_TAG .

# Build serving image
echo "Building serving image..."
docker build -f docker/Dockerfile.serve -t iris-classifier-serve:$IMAGE_TAG .

echo "✓ Docker images built successfully!"
echo ""
echo "Images:"
docker images | grep iris-classifier
