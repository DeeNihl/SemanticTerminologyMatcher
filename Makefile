.PHONY: help install dev-install qdrant-up qdrant-down test clean format lint run-api

help:
	@echo "Available commands:"
	@echo "  make install       - Install package and dependencies"
	@echo "  make dev-install   - Install package in development mode"
	@echo "  make qdrant-up     - Start Qdrant using Docker Compose"
	@echo "  make qdrant-down   - Stop Qdrant"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make format        - Format code with black"
	@echo "  make lint          - Lint code with flake8"
	@echo "  make run-api       - Start the FastAPI server"

install:
	pip install -r requirements.txt
	pip install .

dev-install:
	pip install -r requirements.txt
	pip install -e .

qdrant-up:
	docker-compose up -d
	@echo "Qdrant is running at http://localhost:6333"

qdrant-down:
	docker-compose down

test:
	pytest tests/ -v

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

format:
	black src/

lint:
	flake8 src/

run-api:
	semantic-matcher serve --reload
