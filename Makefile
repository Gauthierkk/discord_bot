.PHONY: run format lint check install help

# Default target
.DEFAULT_GOAL := help

# Run the Discord bot
run:
	@echo "Starting Discord bot..."
	python bot.py

# Format code with ruff
format:
	@echo "Formatting code with ruff..."
	ruff format .
	@echo "✓ Code formatted"

# Lint code with ruff
lint:
	@echo "Linting code with ruff..."
	ruff check .

# Check and auto-fix issues
check:
	@echo "Checking and fixing code issues..."
	ruff check . --fix
	@echo "✓ Issues fixed"

# Install dependencies
install:
	@echo "Installing dependencies with uv..."
	uv pip install -e .
	@echo "✓ Dependencies installed"

# Install dev dependencies
install-dev:
	@echo "Installing dev dependencies..."
	uv pip install -e . --group dev
	@echo "✓ Dev dependencies installed"

# Show help
help:
	@echo "Discord Bot - Available commands:"
	@echo ""
	@echo "  make run          - Run the Discord bot"
	@echo "  make format       - Format code with ruff"
	@echo "  make lint         - Lint code with ruff"
	@echo "  make check        - Check and auto-fix code issues"
	@echo "  make install      - Install dependencies"
	@echo "  make install-dev  - Install dev dependencies (including ruff)"
	@echo "  make help         - Show this help message"
	@echo ""
