# Makefile for Meetup-FastAPI project

.PHONY: help test lint format check_format run

# Show available targets
help:
	@echo "Available commands:"
	@echo "  make test            - Run all tests with coverage"
	@echo "  make lint            - Check code with flake8 for linting issues"
	@echo "  make format          - Format code with black"
	@echo "  make check_format    - Check if code adheres to black formatting"
	@echo "  make run             - Run the FastAPI application"

# Run tests with coverage report
test:
	pytest --cov=app --cov-report=html

# Lint the code using flake8
lint:
	flake8 app tests

# Format code with black
format:
	black app tests

# Check code formatting without making changes
check_format:
	black --check app tests

# Run the FastAPI application
run:
	uvicorn app.main:app --reload
