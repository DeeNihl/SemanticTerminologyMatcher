# Testing Guide

## Running Tests

### Quick Test (No Model Download Required)

These tests validate core functionality without requiring the embedding model:

```bash
pytest tests/test_csv_loader.py tests/test_integration_basic.py tests/test_api.py::test_root tests/test_api.py::test_health -v
```

### Full Test Suite (Requires Model Download)

To run all tests including vector store and search tests, you need:
1. Internet access to huggingface.co for model download
2. The first run will download ~90MB for the embedding model

```bash
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_vector_store.py -v
pytest tests/test_api.py -v
```

## Test Organization

- `test_csv_loader.py`: Tests for CSV parsing and loading (no model required)
- `test_integration_basic.py`: Basic integration tests (no model required)
- `test_api.py`: FastAPI endpoint tests (some require model)
- `test_vector_store.py`: Vector store and search tests (requires model)

## Skipped Tests

Tests that require the embedding model are marked with `@pytest_mark_skipif_no_model` and will be skipped in environments without internet access to huggingface.co.

## Test Coverage

Current test coverage includes:
- CSV loading from files
- Data model validation
- Configuration loading
- API endpoint availability
- (Conditional) Vector store operations
- (Conditional) Semantic search functionality

## Development

To run tests during development:

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests with coverage (if installed)
pytest --cov=semantic_terminology_matcher tests/

# Run tests with output
pytest -v -s

# Run specific test
pytest tests/test_csv_loader.py::test_load_from_csv_basic -v
```

## Continuous Integration

For CI/CD pipelines in restricted environments, use:

```bash
# Run only tests that don't require model downloads
pytest tests/test_csv_loader.py tests/test_integration_basic.py -v
```

For CI/CD with HuggingFace access:

```bash
# Run full test suite
pytest tests/ -v
```
