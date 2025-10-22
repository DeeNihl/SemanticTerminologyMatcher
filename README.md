# Semantic Terminology Matcher

A tool for loading medical/clinical terminology from CSV files into a Qdrant vector store and providing semantic search capabilities via CLI and FastAPI REST APIs.

## Features

- **CSV Loading**: Load terminology entries (codes, terms, descriptions, metadata) from CSV files
- **Vector Storage**: Store terminology in Qdrant vector database with semantic embeddings
- **Semantic Search**: Find similar terms using natural language queries
- **CLI**: Command-line interface for loading data and searching
- **REST API**: FastAPI-based REST API for integration with other systems

## Installation

### Prerequisites

- Python 3.9 or higher
- Qdrant (optional - can use in-memory mode for testing)
- Internet access to download sentence-transformers models from HuggingFace on first run

**Note**: The embedding model (`sentence-transformers/all-MiniLM-L6-v2`) will be downloaded automatically on first use. This requires access to huggingface.co. In restricted environments, you can pre-download the model or use a local model cache.

### Install from source

```bash
# Clone the repository
git clone https://github.com/DeeNihl/SemanticTerminologyMatcher.git
cd SemanticTerminologyMatcher

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running Qdrant (optional)

For production use, run Qdrant in a Docker container:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

For testing, you can use in-memory mode (no installation needed).

## CSV Format

Your CSV file should have the following columns:

- `code` (required): The terminology code (e.g., "SNOMED:12345", "ICD10:E11")
- `term` (required): The term or label (e.g., "Diabetes mellitus")
- `description` (optional): Description or definition
- `category` (optional): Category or domain (e.g., "Cardiology", "Endocrinology")
- `metadata` (optional): JSON string with additional metadata
- Any other columns will be included in metadata

Example CSV:
```csv
code,term,description,category
SNOMED:22298006,Myocardial infarction,Heart attack,Cardiology
ICD10:E11,Type 2 diabetes,Non-insulin dependent diabetes,Endocrinology
```

See `examples/sample_terminology.csv` for a complete example.

## Usage

### Command Line Interface (CLI)

#### Load terminology from CSV

```bash
# Load into in-memory Qdrant (for testing)
stm load examples/sample_terminology.csv --memory

# Load into Qdrant server
stm load examples/sample_terminology.csv --host localhost --port 6333

# Recreate collection if it exists
stm load examples/sample_terminology.csv --recreate --memory
```

#### Search for terminology

```bash
# Basic search
stm search "heart attack" --memory

# Search with filters
stm search "diabetes" --limit 5 --threshold 0.7 --category Endocrinology --memory

# Search in Qdrant server
stm search "high blood pressure" --host localhost --port 6333
```

#### Show collection statistics

```bash
stm stats --memory
```

### FastAPI REST API

#### Start the API server

```bash
# Start server (default: http://localhost:8000)
python -m semantic_terminology_matcher.api

# Or with custom settings
uvicorn semantic_terminology_matcher.api:app --host 0.0.0.0 --port 8000
```

#### API Endpoints

**Health Check**
```bash
curl http://localhost:8000/health
```

**Search (POST)**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "heart attack",
    "limit": 5,
    "score_threshold": 0.7
  }'
```

**Search (GET)**
```bash
curl "http://localhost:8000/search/diabetes?limit=5&score_threshold=0.7&category=Endocrinology"
```

**Collection Statistics**
```bash
curl http://localhost:8000/stats
```

**Create Collection**
```bash
curl -X POST "http://localhost:8000/collection/create?recreate=false"
```

**Delete Collection**
```bash
curl -X DELETE http://localhost:8000/collection
```

#### Interactive API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation.

## Configuration

Configuration can be set via environment variables with `STM_` prefix:

```bash
# Qdrant settings
export STM_QDRANT_HOST=localhost
export STM_QDRANT_PORT=6333
export STM_QDRANT_COLLECTION=terminology
export STM_QDRANT_USE_MEMORY=false

# Embedding model
export STM_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# API settings
export STM_API_HOST=0.0.0.0
export STM_API_PORT=8000
```

Or create a `.env` file in the project root.

## Development

### Install development dependencies

```bash
pip install -r requirements-dev.txt
```

### Run tests

```bash
pytest
```

### Format code

```bash
black semantic_terminology_matcher tests
```

### Lint code

```bash
flake8 semantic_terminology_matcher tests
```

## Architecture

- **CSV Loader**: Parses CSV files and converts to structured terminology entries
- **Vector Store**: Manages Qdrant collection and embeddings using Sentence Transformers
- **Embedding Model**: Uses `sentence-transformers/all-MiniLM-L6-v2` (384-dim) for semantic embeddings
- **CLI**: Click-based command-line interface
- **API**: FastAPI REST endpoints for programmatic access

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
