.PHONY: help install install-dev test coverage lint format typecheck check clean sync

# Default target
help:
	@echo "git-gud-samaritans Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      Install package with uv"
	@echo "  make install-dev  Install with development dependencies"
	@echo "  make sync         Sync environment from lockfile"
	@echo ""
	@echo "Testing:"
	@echo "  make test         Run tests with pytest"
	@echo "  make coverage     Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         Run linter (ruff check)"
	@echo "  make format       Format code (ruff format)"
	@echo "  make typecheck    Run type checker (mypy)"
	@echo "  make check        Run all checks (lint + typecheck + test)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        Remove build artifacts and cache"
	@echo ""

# Install package
install:
	uv pip install -e .

# Install with dev dependencies
install-dev:
	uv pip install -e ".[dev]"
	uv run pre-commit install

# Sync from lockfile (preferred for reproducible builds)
sync:
	uv sync --all-extras

# Run tests
test:
	uv run pytest tests/ -v

# Run tests with coverage
coverage:
	uv run pytest tests/ --cov=src/git_gud_samaritans --cov-report=term-missing --cov-report=html
	@echo "HTML coverage report: htmlcov/index.html"

# Run linter
lint:
	uv run ruff check src/ tests/
	@echo "Lint check passed!"

# Format code
format:
	uv run ruff check --fix src/ tests/
	uv run ruff format src/ tests/
	@echo "Code formatted!"

# Run type checker
typecheck:
	uv run mypy src/
	@echo "Type check passed!"

# Run all checks (CI simulation)
check: lint typecheck test
	@echo ""
	@echo "All checks passed!"

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned!"
