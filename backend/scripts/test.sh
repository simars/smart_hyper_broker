#!/bin/bash
set -e

echo "Running backend test suite..."
PYTHONPATH=. .venv/bin/pytest tests/
