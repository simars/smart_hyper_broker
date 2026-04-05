#!/bin/bash
set -e

echo "Building Production Docker Images..."

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Docker Compose is not installed."
    exit 1
fi

echo "Spinning up production build..."
if docker compose version &> /dev/null; then
  docker compose -f docker-compose.prod.yml build
else
  docker-compose -f docker-compose.prod.yml build
fi

echo "Build successful! To test locally, run:"
echo "docker-compose -f docker-compose.prod.yml up"
