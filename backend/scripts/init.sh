#!/bin/bash
set -e

echo "Initializing backend environment..."
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install debugpy
echo "Backend initialization complete."
