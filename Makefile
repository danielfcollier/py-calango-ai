# Makefile
.PHONY: install clean clean-all format lint run test check build security help lock coverage spell-check setup-ollama

# --- Variables ---
UV := uv
PYTHON := $(UV) run python
SRC_DIR := src
DOCS_DIR := docs
CSPELL_VERSION := latest

# Colors
GREEN := \033[0;32m
NC := \033[0m # No Color

# --- Install & Setup ---
setup-ollama: ## Run Ollama inside a Docker container (Port 11434)
	@echo "🐳 Starting Ollama in Docker..."
	@# 1. Check if container exists and remove it to start fresh
	@docker rm -f calango-ollama 2>/dev/null || true
	
	@# 2. Run container
	@# -v ollama:/root/.ollama: Persist models
	@# -p 11434:11434: Expose port
	@docker run -d --name calango-ollama \
		-v ollama:/root/.ollama \
		-p 11434:11434 \
		ollama/ollama
	
	@echo "⏳ Waiting for Ollama to boot..."
	@sleep 3
	
	@echo "📥 Pulling default model (Llama 3)..."
	@docker exec calango-ollama ollama pull llama3
	
	@echo "✅ Ollama is ready at http://localhost:11434"

install: ## Install dependencies using uv
	@echo "$(GREEN)>>> Installing dependencies...$(NC)"
	@$(UV) sync --group dev
	@$(UV) pip install -e .
	@$(UV) run pre-commit install
	@echo "$(GREEN)>>> Installation complete. Tip: Run 'make setup-ollama' to enable local models.$(NC)"

lock: ## Update the lock file for dependencies.
	@echo "$(GREEN)>>> Updating lock file...$(NC)"
	@$(UV) lock
	@echo "$(GREEN)>>> Lock file updated.$(NC)"

# --- Development & Quality ---

lint: ## Check code style and errors with Ruff.
	@echo "$(GREEN)>>> Running Ruff linter...$(NC)"
	@$(UV) run ruff check $(SRC_DIR)

format: ## Format code with Ruff formatter.
	@echo "$(GREEN)>>> Running Ruff formatter...$(NC)"
	@$(UV) run ruff format $(SRC_DIR)
	@$(UV) run ruff check $(SRC_DIR) --fix

security: ## Run CVE security scan using pip-audit
	@echo "$(GREEN)>>> Running security audit...$(NC)"
	@$(UV) run pip-audit

spell-check: ## Spell check project.
	@echo "$(GREEN)*** Checking project for misspellings... ***$(NC)"
	@grep . cspell.txt 2>/dev/null | sort -u > .cspell.txt && mv .cspell.txt cspell.txt || true
	@docker run --quiet -v $$(pwd):/workdir ghcr.io/streetsidesoftware/cspell:$(CSPELL_VERSION) lint -c cspell.json --no-progress --unique $(SRC_DIR) $(DOCS_DIR) || exit 0  
	@echo "$(GREEN)*** Spell check complete! ***$(NC)"

# --- Testing ---
# ... existing variables ...

test: ## Run unit tests only (excludes integration and e2e)
	@echo "$(GREEN)>>> Running unit tests...$(NC)"
	@$(UV) run pytest -m "not integration and not e2e"

test-integration: ## Run integration tests only
	@echo "$(GREEN)>>> Running integration tests...$(NC)"
	@$(UV) run pytest -m "integration"

test-e2e: ## Run E2E tests only
	@echo "$(GREEN)>>> Running E2E tests...$(NC)"
	@$(UV) run pytest -m "e2e"

test-all: ## Run everything
	@echo "$(GREEN)>>> Running all tests...$(NC)"
	@$(UV) run pytest

coverage: ## Run tests and generate coverage report.
	@echo "$(GREEN)>>> Running tests with coverage...$(NC)"
	@$(UV) run pytest --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html


# --- CI/CD Check ---

check: format lint test ## Run format, lint, and unit tests (Recommended for pre-commit).
	@echo  "$(GREEN)>>> All checks passed.$(NC)"

# --- Execution ---
run: ## Run the Streamlit app
	$(UV) run streamlit run src/app.py

# --- Build ---
build: ## Build the executable using PyInstaller
	$(UV) run pyinstaller calango.spec --clean --noconfirm

# --- Cleaning ---
clean: ## Remove cache files and artifacts
	@rm -rf .pytest_cache
	@rm -rf .ruff_cache
	@rm -rf .mypy_cache
	@rm -rf **/__pycache__
	@rm -rf dist
	@rm -rf build
	@rm -rf htmlcov
	@rm -f .coverage

clean-all: clean ## Deep clean (removes venv and database)
	@rm -rf .venv
	@rm -f calango.json

# --- Help ---
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'