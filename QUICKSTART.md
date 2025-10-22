# Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/DeeNihl/SemanticTerminologyMatcher.git
cd SemanticTerminologyMatcher

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode (optional)
pip install -e .
```

## Basic Usage

### 1. Prepare Your CSV File

Create a CSV file with your terminology data. Minimum required columns are `code` and `term`:

```csv
code,term,description,category
SNOMED:22298006,Myocardial infarction,Heart attack,Cardiology
ICD10:E11,Type 2 diabetes,Non-insulin dependent diabetes,Endocrinology
```

See `examples/sample_terminology.csv` for a complete example.

### 2. Load Data into Qdrant

**Option A: Using In-Memory Mode (for testing)**

```bash
# Load CSV into in-memory vector store
stm load examples/sample_terminology.csv --memory
```

**Option B: Using Qdrant Server**

First, start Qdrant:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

Then load your data:
```bash
stm load examples/sample_terminology.csv --host localhost --port 6333
```

### 3. Search for Terms

```bash
# Basic search
stm search "heart attack" --memory

# Search with filters
stm search "diabetes" --limit 5 --threshold 0.7 --category Endocrinology --memory
```

### 4. Start the API Server

```bash
# Start the FastAPI server
python -m semantic_terminology_matcher.api

# Or using uvicorn directly
uvicorn semantic_terminology_matcher.api:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

### 5. Use the REST API

```bash
# Health check
curl http://localhost:8000/health

# Search via GET
curl "http://localhost:8000/search/heart%20attack?limit=5"

# Search via POST
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "heart attack", "limit": 5}'
```

## Common Tasks

### Loading Data with Custom Collection Name

```bash
stm load my_data.csv --collection my_terminology --memory
```

### Recreating a Collection

```bash
stm load my_data.csv --recreate --memory
```

### Checking Collection Statistics

```bash
stm stats --memory
```

## Environment Configuration

Create a `.env` file in the project root:

```bash
STM_QDRANT_HOST=localhost
STM_QDRANT_PORT=6333
STM_QDRANT_COLLECTION=terminology
STM_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Troubleshooting

### Model Download Issues

On first run, the embedding model (~90MB) will be downloaded from HuggingFace. If you're behind a firewall or proxy:

1. Pre-download the model on a machine with internet access
2. Copy the cached model from `~/.cache/huggingface/` to your target machine
3. Or use a local mirror/proxy for HuggingFace

### Qdrant Connection Issues

If using Qdrant server mode:
- Ensure Qdrant is running: `curl http://localhost:6333/`
- Check firewall settings
- Use `--memory` flag for testing without Qdrant server

## Next Steps

- See [README.md](README.md) for complete documentation
- See [TESTING.md](TESTING.md) for testing guide
- Check `/docs` endpoint when API is running for interactive documentation
