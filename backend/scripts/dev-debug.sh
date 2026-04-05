#!/bin/bash
set -e

echo "Starting backend locally in DEBUG mode..."
.venv/bin/python -m debugpy --listen 0.0.0.0:5678 -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
