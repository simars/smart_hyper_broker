.PHONY: init dev dev-debug test clean

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
