#!/bin/bash
set -e

echo "Cleaning backend cache and dependencies..."
rm -rf .venv
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
echo "Backend clean complete."
