.PHONY: help init dev dev-debug test clean

.DEFAULT_GOAL := help

help:
	@echo "Available backend commands:"
	@echo "  make init       - Creates venv and installs python dependencies"
	@echo "  make dev        - Runs FastAPI via uvicorn locally"
	@echo "  make dev-debug  - Runs FastAPI with debugpy on port 5678"
	@echo "  make test       - Runs pytest suites"
	@echo "  make clean      - Removes .venv and cache files"

init:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install debugpy

dev:
	.venv/bin/uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

dev-debug:
	.venv/bin/python -m debugpy --listen 0.0.0.0:5678 -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	PYTHONPATH=. .venv/bin/pytest tests/

clean:
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
