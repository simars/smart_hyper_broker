#!/bin/bash
set -e

echo "Starting backend locally..."
.venv/bin/uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
