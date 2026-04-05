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
	./scripts/init.sh

dev:
	./scripts/dev.sh

dev-debug:
	./scripts/dev-debug.sh

test:
	./scripts/test.sh

clean:
	./scripts/clean.sh
