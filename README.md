# Semantic Terminology Matcher

A Python project for loading OMOP concepts from CSV files into a Qdrant vector store, with semantic search capabilities exposed through FastAPI and a CLI interface.

## Features

- **CSV Loading**: Import OMOP concepts with metadata from CSV files
- **Vector Store**: Store and index concepts using Qdrant with semantic embeddings
- **Semantic Search**: Find similar concepts using natural language queries
- **FastAPI**: RESTful API for all operations
- **CLI**: Command-line interface for easy interaction
- **Rich Output**: Beautiful terminal output using Rich library

## Architecture

```
SemanticTerminologyMatcher/
├── src/semantic_matcher/
│   ├── api/              # FastAPI application
│   ├── cli/              # CLI commands
│   ├── core/             # Core functionality
│   │   ├── csv_loader.py   # CSV loading logic
│   │   └── vector_store.py # Qdrant integration
│   ├── models/           # Pydantic models
│   └── config.py         # Configuration
├── data/                 # Sample data
├── tests/                # Tests
└── requirements.txt      # Dependencies
```

## Installation

### Prerequisites

- Python 3.8+
- Qdrant (running locally or remote)

### Install Qdrant

Using Docker:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Or follow the [official installation guide](https://qdrant.tech/documentation/quick-start/).

### Install the Package

```bash
# Clone the repository
git clone https://github.com/yourusername/SemanticTerminologyMatcher.git
cd SemanticTerminologyMatcher

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` to configure your settings:

```
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=omop_concepts
QDRANT_API_KEY=

EMBEDDING_MODEL=all-MiniLM-L6-v2

API_HOST=0.0.0.0
API_PORT=8000
```

## CSV Format

The CSV file should contain the following columns:

### Required Columns

- `concept_id` (int): Unique OMOP concept identifier
- `concept_name` (str): Name of the concept
- `definition_chunk` (str): Text definition used for generating embeddings

### Optional Columns

- `domain_id` (str): Domain identifier (e.g., "Condition", "Drug")
- `vocabulary_id` (str): Vocabulary identifier (e.g., "SNOMED", "RxNorm")
- `concept_class_id` (str): Concept class identifier
- `concept_code` (str): Concept code
- `metadata_payload` (str): JSON string with additional metadata

### Example CSV

See `data/sample_omop_concepts.csv` for a complete example.

## Usage

### CLI Commands

The CLI is available through the `semantic-matcher` command:

#### Upload CSV

```bash
# Upload concepts from CSV
semantic-matcher upload data/sample_omop_concepts.csv

# Upload and recreate collection
semantic-matcher upload data/sample_omop_concepts.csv --recreate

# Upload with custom batch size
semantic-matcher upload data/sample_omop_concepts.csv --batch-size 50
```

#### Search for Concepts

```bash
# Search for similar concepts
semantic-matcher search "diabetes treatment"

# Limit results
semantic-matcher search "high blood pressure" --limit 5

# Set minimum score threshold
semantic-matcher search "heart attack" --score-threshold 0.7
```

#### Get Specific Concept

```bash
# Retrieve concept by ID
semantic-matcher get 44054006
```

#### Collection Management

```bash
# Create collection
semantic-matcher create-collection

# Recreate collection (delete existing)
semantic-matcher create-collection --recreate

# Delete collection
semantic-matcher delete-collection

# View collection info
semantic-matcher info
```

#### Validate CSV

```bash
# Validate CSV without uploading
semantic-matcher validate data/sample_omop_concepts.csv
```

#### Start API Server

```bash
# Start the FastAPI server
semantic-matcher serve

# Custom host and port
semantic-matcher serve --host 0.0.0.0 --port 8080

# Enable auto-reload for development
semantic-matcher serve --reload
```

### FastAPI

#### Start the Server

```bash
semantic-matcher serve
```

Or using uvicorn directly:

```bash
uvicorn semantic_matcher.api.app:app --reload
```

#### API Endpoints

Access the interactive API documentation at `http://localhost:8000/docs`

**Main Endpoints:**

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /upload/csv` - Upload CSV file
- `POST /search` - Search for concepts
- `GET /concepts/{concept_id}` - Get specific concept
- `GET /collection/info` - Collection information
- `POST /collection/create` - Create collection
- `DELETE /collection` - Delete collection

#### Example API Usage

```bash
# Health check
curl http://localhost:8000/health

# Search for concepts
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "diabetes medication", "limit": 5}'

# Get specific concept
curl http://localhost:8000/concepts/44054006

# Upload CSV
curl -X POST http://localhost:8000/upload/csv \
  -F "file=@data/sample_omop_concepts.csv"
```

### Python API

```python
from semantic_matcher.core import CSVLoader, VectorStore
from semantic_matcher.config import settings

# Initialize components
loader = CSVLoader()
vector_store = VectorStore()

# Load concepts from CSV
concepts = loader.load_from_csv("data/sample_omop_concepts.csv")

# Create collection
vector_store.create_collection()

# Upload concepts
vector_store.upload_concepts(concepts)

# Search
results = vector_store.search("diabetes treatment", limit=5)
for result in results:
    print(f"{result.concept_name}: {result.score:.4f}")

# Get specific concept
concept = vector_store.get_concept_by_id(44054006)
print(concept.concept_name)
```

## Examples

### Complete Workflow

```bash
# 1. Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# 2. Validate CSV
semantic-matcher validate data/sample_omop_concepts.csv

# 3. Upload concepts
semantic-matcher upload data/sample_omop_concepts.csv

# 4. View collection info
semantic-matcher info

# 5. Search for concepts
semantic-matcher search "high blood sugar"

# 6. Start API server
semantic-matcher serve
```

### Search Examples

```bash
# Find diabetes-related concepts
semantic-matcher search "high blood sugar diabetes"

# Find cardiovascular procedures
semantic-matcher search "heart surgery bypass"

# Find medications
semantic-matcher search "blood pressure medication"

# Find lab tests
semantic-matcher search "glucose test blood"
```

## Development

### Run Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

## Project Structure Details

### Core Modules

- **csv_loader.py**: Handles loading and parsing CSV files
- **vector_store.py**: Manages Qdrant vector store operations and embeddings
- **config.py**: Configuration management using Pydantic Settings
- **models/schemas.py**: Pydantic models for data validation

### API Module

- **api/app.py**: FastAPI application with all endpoints

### CLI Module

- **cli/main.py**: Click-based CLI commands with Rich output

## Configuration Options

All settings can be configured via environment variables:

- `QDRANT_HOST`: Qdrant server host (default: localhost)
- `QDRANT_PORT`: Qdrant server port (default: 6333)
- `QDRANT_COLLECTION_NAME`: Collection name (default: omop_concepts)
- `QDRANT_API_KEY`: Qdrant API key (optional)
- `EMBEDDING_MODEL`: Sentence transformer model (default: all-MiniLM-L6-v2)
- `API_HOST`: FastAPI host (default: 0.0.0.0)
- `API_PORT`: FastAPI port (default: 8000)

## Embedding Models

The project uses [sentence-transformers](https://www.sbert.net/) for generating embeddings. You can use any model from the library:

- `all-MiniLM-L6-v2` (default): Fast and efficient, 384 dimensions
- `all-mpnet-base-v2`: Higher quality, 768 dimensions
- `multi-qa-mpnet-base-dot-v1`: Optimized for question-answering

Change the model in `.env`:

```
EMBEDDING_MODEL=all-mpnet-base-v2
```

## Troubleshooting

### Qdrant Connection Error

Ensure Qdrant is running:
```bash
docker ps  # Check if Qdrant container is running
curl http://localhost:6333/collections  # Test connection
```

### Model Download Issues

The first run will download the embedding model. Ensure you have internet access and sufficient disk space.

### Memory Issues

For large CSV files, adjust the batch size:
```bash
semantic-matcher upload data/large_file.csv --batch-size 50
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Acknowledgments

- [OMOP Common Data Model](https://ohdsi.github.io/CommonDataModel/)
- [Qdrant Vector Database](https://qdrant.tech/)
- [Sentence Transformers](https://www.sbert.net/)
- [FastAPI](https://fastapi.tiangolo.com/)
