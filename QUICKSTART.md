# Quick Start Guide

Get started with Semantic Terminology Matcher in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Docker (for running Qdrant)

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/SemanticTerminologyMatcher.git
cd SemanticTerminologyMatcher

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## Step 2: Start Qdrant

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# OR using Docker directly
docker run -p 6333:6333 qdrant/qdrant
```

Verify Qdrant is running:
```bash
curl http://localhost:6333
```

## Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env if needed (defaults work for local development)
```

## Step 4: Upload Sample Data

```bash
# Upload the sample OMOP concepts
semantic-matcher upload data/sample_omop_concepts.csv

# Verify the upload
semantic-matcher info
```

Expected output:
```
✓ Loaded 10 concepts from CSV
✓ Collection created
Uploading 10 concepts...
✓ Successfully uploaded 10 concepts
```

## Step 5: Try Semantic Search

```bash
# Search for diabetes-related concepts
semantic-matcher search "high blood sugar"

# Get specific concept
semantic-matcher get 44054006
```

## Step 6: Start the API Server

```bash
# Start the FastAPI server
semantic-matcher serve

# Or with auto-reload for development
semantic-matcher serve --reload
```

Visit http://localhost:8000/docs to see the interactive API documentation.

## Step 7: Try the API

Open another terminal and try these commands:

```bash
# Health check
curl http://localhost:8000/health

# Search via API
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "diabetes medication", "limit": 3}'

# Get concept by ID
curl http://localhost:8000/concepts/44054006
```

## Next Steps

### Upload Your Own Data

Create a CSV file with these required columns:
- `concept_id` - Unique integer ID
- `concept_name` - Name of the concept
- `definition_chunk` - Text description for semantic search

Optional columns:
- `domain_id`, `vocabulary_id`, `concept_class_id`, `concept_code`
- `metadata_payload` - JSON string with additional metadata

Then upload:
```bash
semantic-matcher upload your_data.csv
```

### Explore CLI Commands

```bash
# Validate CSV before uploading
semantic-matcher validate your_data.csv

# Recreate collection (delete existing data)
semantic-matcher upload data/sample_omop_concepts.csv --recreate

# Search with filters
semantic-matcher search "heart disease" --limit 5 --score-threshold 0.7

# View collection information
semantic-matcher info

# Delete collection
semantic-matcher delete-collection
```

### Use Different Embedding Models

Edit `.env` and change the embedding model:

```env
# Fast and efficient (default)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Higher quality
EMBEDDING_MODEL=all-mpnet-base-v2

# Optimized for Q&A
EMBEDDING_MODEL=multi-qa-mpnet-base-dot-v1
```

Then recreate the collection:
```bash
semantic-matcher create-collection --recreate
semantic-matcher upload data/sample_omop_concepts.csv
```

### Integrate with Your Application

```python
from semantic_matcher.core import CSVLoader, VectorStore

# Initialize
vector_store = VectorStore()

# Search
results = vector_store.search("diabetes", limit=5)
for result in results:
    print(f"{result.concept_name}: {result.score:.4f}")
```

## Common Commands

```bash
# Using Makefile shortcuts
make qdrant-up          # Start Qdrant
make dev-install        # Install in dev mode
make test               # Run tests
make format             # Format code
make run-api            # Start API server

# Manual commands
semantic-matcher --help          # Show all commands
semantic-matcher upload --help   # Help for specific command
```

## Troubleshooting

**Qdrant connection failed:**
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Restart Qdrant
docker-compose restart
```

**Module not found:**
```bash
# Reinstall in development mode
pip install -e .
```

**Model download slow:**
The first run downloads the embedding model (~80-400MB depending on the model). This is a one-time download.

## Production Deployment

For production use:

1. Use a persistent Qdrant instance (not Docker)
2. Set `QDRANT_API_KEY` in `.env`
3. Use a production ASGI server:
   ```bash
   gunicorn semantic_matcher.api.app:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
4. Set up proper logging and monitoring
5. Use HTTPS for API endpoints

## More Help

- Full documentation: See [README.md](README.md)
- API documentation: http://localhost:8000/docs (when server is running)
- Qdrant docs: https://qdrant.tech/documentation/
- Issues: https://github.com/yourusername/SemanticTerminologyMatcher/issues
