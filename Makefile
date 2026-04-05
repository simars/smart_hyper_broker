.PHONY: help init build dev dev-debug test up clean

.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make init       - Sets up local environment and installs dependencies"
	@echo "  make build      - Builds docker setup"
	@echo "  make up         - Runs application with docker-compose"
	@echo "  make dev        - Runs application locally without docker"
	@echo "  make dev-debug  - Runs application in debug mode"
	@echo "  make test       - Runs all tests"
	@echo "  make clean      - Cleans up local environments"

# Delegates to nested makefiles
init:
	$(MAKE) -C backend init
	$(MAKE) -C frontend init

# Builds docker setup
build:
	./scripts/build.sh

# Runs application locally without docker
dev:
	./scripts/run_local.sh

# Runs application in debug mode
dev-debug:
	./scripts/run_local_debug.sh

# Runs all tests
test:
	$(MAKE) -C backend test
	$(MAKE) -C frontend test

# Runs application with docker-compose
up:
	./scripts/dev.sh

# Cleans up local environments
clean:
	$(MAKE) -C backend clean
	$(MAKE) -C frontend clean
