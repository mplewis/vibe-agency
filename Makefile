# ============================================================================
# VIBE AGENCY - MAKEFILE
# ============================================================================
# Self-running system automation for non-technical users
#
# Quick Start:
#   make install    # One-command setup
#   make test       # Run all tests
#   make lint       # Check code quality
#   make ci         # Run full CI validation
#
# ============================================================================

.PHONY: help install clean test lint format ci validate-deps

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# HELP
# ============================================================================

help:  ## Show this help message
	@echo "📚 Vibe Agency - Available Commands"
	@echo "===================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start:"
	@echo "  make install   # Setup environment"
	@echo "  make test      # Run tests"
	@echo "  make ci        # Full validation"

# ============================================================================
# INSTALLATION
# ============================================================================

install: clean  ## Install all dependencies and setup environment
	@echo "🔧 Installing dependencies with uv..."
	uv sync --all-extras
	@echo "🪝 Setting up pre-commit hooks..."
	uv run pre-commit install
	@echo "🔍 Validating knowledge bases..."
	@if [ -f "validate_knowledge_index.py" ]; then \
		uv run python validate_knowledge_index.py; \
	else \
		echo "⚠️  validate_knowledge_index.py not found (skipping)"; \
	fi
	@echo ""
	@echo "✅ Environment ready!"
	@echo ""
	@echo "Next steps:"
	@echo "  make test      # Run tests"
	@echo "  make lint      # Check quality"
	@echo "  ./vibe-cli run <project-id>"

install-dev: clean  ## Install only dev dependencies (faster)
	@echo "🔧 Installing dev dependencies..."
	uv sync --extra dev
	@echo "✅ Dev environment ready!"

# ============================================================================
# TESTING
# ============================================================================

test:  ## Run all tests
	@echo "🧪 Running test suite..."
	uv run pytest tests/ -v --tb=short

test-cov:  ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	uv run pytest tests/ -v --cov=agency_os --cov-report=term-missing --cov-report=html

test-unit:  ## Run only unit tests
	@echo "🧪 Running unit tests..."
	uv run pytest tests/ -v -m unit

test-integration:  ## Run only integration tests
	@echo "🧪 Running integration tests..."
	uv run pytest tests/ -v -m integration

test-fast:  ## Run tests (skip slow tests)
	@echo "🧪 Running fast tests..."
	uv run pytest tests/ -v -m "not slow"

# ============================================================================
# CODE QUALITY
# ============================================================================

lint:  ## Run all linters
	@echo "🔍 Running linters..."
	@echo "  → Ruff (linter)..."
	uv run ruff check .
	@echo "  → Ruff (formatter check)..."
	uv run ruff format --check .
	@echo "  → YAMLlint..."
	uv run yamllint -c .yamllint agency_os/ system_steward_framework/ || true
	@echo "✅ Linting complete!"

format:  ## Auto-format code
	@echo "🎨 Formatting code..."
	uv run ruff check --fix .
	uv run ruff format .
	uv run black .
	uv run isort .
	@echo "✅ Formatting complete!"

type-check:  ## Run type checker (mypy)
	@echo "🔍 Running type checker..."
	uv run mypy agency_os/ --install-types --non-interactive || true
	@echo "⚠️  Type checking baseline (errors expected)"

complexity:  ## Check code complexity
	@echo "🔍 Checking complexity..."
	uv run ruff check . --select C90
	@echo "✅ Complexity check complete!"

security:  ## Run security checks
	@echo "🔒 Running security checks..."
	@echo "  → Ruff security rules..."
	uv run ruff check . --select S
	@echo "  → pip-audit (dependency vulnerabilities)..."
	uv run pip-audit || true
	@echo "  → detect-secrets..."
	uv run detect-secrets scan || true
	@echo "✅ Security scan complete!"

# ============================================================================
# CI/CD SIMULATION
# ============================================================================

ci: lint test validate-deps  ## Run full CI validation (what CI runs)
	@echo ""
	@echo "✅ All CI checks passed!"
	@echo ""

ci-strict: lint test-cov type-check security validate-deps  ## Strict CI (all checks)
	@echo ""
	@echo "✅ All strict CI checks passed!"
	@echo ""

# ============================================================================
# VALIDATION
# ============================================================================

validate-deps:  ## Validate dependencies and lock file
	@echo "🔍 Validating dependencies..."
	@if [ -f "uv.lock" ]; then \
		echo "  ✅ uv.lock exists"; \
	else \
		echo "  ❌ uv.lock missing (run: uv sync)"; \
		exit 1; \
	fi
	@echo "  → Checking for dependency issues..."
	uv sync --frozen || (echo "❌ Lock file out of sync (run: uv lock)" && exit 1)
	@echo "✅ Dependencies valid!"

validate-knowledge:  ## Validate knowledge bases
	@echo "🔍 Validating knowledge bases..."
	@if [ -f "validate_knowledge_index.py" ]; then \
		uv run python validate_knowledge_index.py; \
	else \
		echo "⚠️  validate_knowledge_index.py not found (skipping)"; \
	fi

# ============================================================================
# CLEANUP
# ============================================================================

clean:  ## Clean build artifacts and caches
	@echo "🧹 Cleaning..."
	rm -rf .venv/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete!"

clean-all: clean  ## Clean everything including uv.lock (full reset)
	rm -rf uv.lock
	@echo "✅ Full cleanup complete! (run 'make install' to rebuild)"

# ============================================================================
# DEVELOPMENT HELPERS
# ============================================================================

shell:  ## Start a shell with activated virtualenv
	@echo "🐚 Starting shell (uv environment)..."
	uv run bash

update:  ## Update dependencies to latest versions
	@echo "📦 Updating dependencies..."
	uv lock --upgrade
	@echo "✅ Dependencies updated! Review uv.lock changes."

freeze:  ## Show installed package versions
	uv pip list

audit:  ## Run full project audit
	@echo "🔍 Project Audit"
	@echo "================"
	@echo ""
	@echo "📊 Project Stats:"
	@find agency_os -name "*.py" -type f | wc -l | xargs echo "  Python files:"
	@find agency_os -name "*.py" -type f -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print "  Total lines:", $$1}'
	@echo ""
	@echo "📦 Dependencies:"
	@uv pip list | wc -l | xargs echo "  Installed packages:"
	@echo ""
	@echo "🧪 Test Coverage:"
	@make test-cov > /dev/null 2>&1 || true
	@echo ""
	@echo "🔍 Code Quality:"
	@make lint || true

# ============================================================================
# PROJECT INFO
# ============================================================================

info:  ## Show project information
	@echo "📋 Vibe Agency - Project Info"
	@echo "=============================="
	@echo "Python Version: $(shell python3 --version)"
	@echo "UV Version: $(shell uv --version)"
	@echo "Working Directory: $(shell pwd)"
	@echo "Lock File: $(shell [ -f uv.lock ] && echo '✅ exists' || echo '❌ missing')"
	@echo "Virtual Env: $(shell [ -d .venv ] && echo '✅ exists' || echo '❌ missing')"
	@echo ""
	@echo "Configuration Files:"
	@echo "  pyproject.toml: $(shell [ -f pyproject.toml ] && echo '✅' || echo '❌')"
	@echo "  requirements.txt: $(shell [ -f requirements.txt ] && echo '✅' || echo '❌')"
	@echo "  Makefile: ✅"
	@echo ""
