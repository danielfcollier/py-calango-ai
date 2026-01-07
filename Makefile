# Makefile
.PHONY: install clean clean-all format lint run test check

# Variables
VENV_BIN = .venv/bin
UV = uv

# --- Install & Setup ---
install: ## Install dependencies and setup the environment
	$(UV) sync --group dev
	$(UV) pip install -e .

# --- Development ---
format: ## Format code using Ruff
	$(UV) run ruff format .

lint: ## Run linting checks (Ruff & Mypy)
	$(UV) run ruff check . --fix
	$(UV) run mypy src

check: format lint ## Run both format and lint

test: ## Run tests with pytest
	$(UV) run pytest

# --- Execution ---
run: ## Run the Streamlit app
	$(UV) run streamlit run src/app.py

# --- Cleaning ---
clean: ## Remove cache files and artifacts
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf **/__pycache__
	rm -rf dist
	rm -rf build

clean-all: clean ## Deep clean (removes venv and database)
	rm -rf .venv
	rm -f mystique.json

# --- Help ---
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'