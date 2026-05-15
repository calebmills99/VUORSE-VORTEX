.PHONY: help install install-dev sync test test-cov lint format typecheck clean docker-build docker-run

# ── Meta ───────────────────────────────────────────────────────────────────

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Installation ───────────────────────────────────────────────────────────

install: ## Install production dependencies via UV
	uv sync

install-dev: ## Install all dependencies including dev extras
	uv sync --extra dev

sync: ## Sync all dependencies (alias for install-dev)
	uv sync --all-extras

# ── Testing ────────────────────────────────────────────────────────────────

test: ## Run the test suite
	uv run pytest tests/ -q

test-cov: ## Run tests with coverage report
	uv run pytest tests/ --cov=src/vuorse_vortex --cov-report=term-missing --cov-report=html

test-fast: ## Run tests excluding slow integration tests
	uv run pytest tests/ -q -m "not integration"

# ── Code Quality ───────────────────────────────────────────────────────────

lint: ## Run ruff linter
	uv run ruff check src/ tests/

lint-fix: ## Run ruff linter with auto-fix
	uv run ruff check --fix src/ tests/

format: ## Run ruff formatter
	uv run ruff format src/ tests/

format-check: ## Check formatting without making changes
	uv run ruff format --check src/ tests/

typecheck: ## Run mypy type checker
	uv run mypy src/

check: lint format-check typecheck ## Run all code quality checks

# ── CLI ────────────────────────────────────────────────────────────────────

gpu-status: ## Check GPU/CUDA availability
	uv run vortex gpu-status

validate-sample: ## Validate the sample JSONL manifest
	uv run vortex validate manifests/sample_synthetic_memory.jsonl

enrich-sample: ## Generate sample synthetic memories
	uv run vortex enrich "Hooplehopper displacement event" --count 3

# ── Docker ─────────────────────────────────────────────────────────────────

docker-build: ## Build the Docker image
	docker build -t vuorse-vortex:latest .

docker-run: ## Run the CLI in the Docker container
	docker run --rm --gpus all vuorse-vortex:latest --help

# ── Cleanup ────────────────────────────────────────────────────────────────

clean: ## Remove build artifacts and caches
	rm -rf dist/ build/ .pytest_cache/ htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# ── Environment ────────────────────────────────────────────────────────────

env-setup: ## Copy .env.example to .env (if .env doesn't exist)
	@if [ ! -f .env ]; then cp .env.example .env; echo ".env created from .env.example"; \
	else echo ".env already exists — skipping"; fi
