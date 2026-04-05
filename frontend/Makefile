.PHONY: help init dev dev-debug test clean

.DEFAULT_GOAL := help

help:
	@echo "Available frontend commands:"
	@echo "  make init       - Installs node modules"
	@echo "  make dev        - Runs Next.js development server"
	@echo "  make dev-debug  - Runs Next.js with --inspect"
	@echo "  make test       - Runs frontend tests"
	@echo "  make clean      - Removes node modules and .next build"

init:
	npm install

dev:
	npm run dev

dev-debug:
	NODE_OPTIONS='--inspect' npm run dev

test:
	npm run test --if-present

clean:
	rm -rf node_modules
	rm -rf .next
