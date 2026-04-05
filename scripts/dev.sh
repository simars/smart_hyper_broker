#!/bin/bash
set -e

echo "Starting Local Development Environment..."

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Docker Compose is not installed."
    exit 1
fi

echo "Spinning up Docker Compose..."
if docker compose version &> /dev/null; then
  docker compose -f docker-compose.yml -f docker-compose.override.yml up --build -d
else
  docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build -d
fi

echo "Waiting for services to become healthy..."
echo "Frontend available at http://localhost:3000"
echo "Backend available at http://localhost:8000"
echo ""
echo "To tail logs, run: docker-compose logs -f"
