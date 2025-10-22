"""
Tests for FastAPI application
"""
import pytest
from fastapi.testclient import TestClient

from semantic_terminology_matcher.api import app, get_vector_store
from semantic_terminology_matcher.vector_store import VectorStore
from semantic_terminology_matcher.models import TerminologyEntry


# Skip tests that require embedding model
pytest_mark_skipif_no_model = pytest.mark.skipif(
    True,  # Skip by default in environments without internet access
    reason="Embedding model download requires internet access to huggingface.co"
)


@pytest.fixture
def client():
    """Create test client"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_entries():
    """Create sample entries"""
    return [
        TerminologyEntry(
            code="SNOMED:001",
            term="Myocardial infarction",
            description="Heart attack",
            category="Cardiology",
        ),
        TerminologyEntry(
            code="SNOMED:002",
            term="Diabetes mellitus",
            description="Diabetes",
            category="Endocrinology",
        ),
    ]


def test_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest_mark_skipif_no_model
def test_health_with_collection(client):
    """Test health endpoint with collection"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "collection_exists" in data


@pytest_mark_skipif_no_model
def test_search_post(client, sample_entries):
    """Test POST search endpoint"""
    # Add entries first
    store = get_vector_store()
    store.add_entries(sample_entries)
    
    # Search
    response = client.post(
        "/search",
        json={
            "query": "heart attack",
            "limit": 5,
        }
    )
    
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)


@pytest_mark_skipif_no_model
def test_search_get(client, sample_entries):
    """Test GET search endpoint"""
    # Add entries first
    store = get_vector_store()
    store.add_entries(sample_entries)
    
    # Search
    response = client.get("/search/diabetes?limit=5")
    
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)


@pytest_mark_skipif_no_model
def test_search_with_filters(client, sample_entries):
    """Test search with filters"""
    store = get_vector_store()
    store.add_entries(sample_entries)
    
    response = client.post(
        "/search",
        json={
            "query": "disease",
            "limit": 10,
            "score_threshold": 0.5,
            "category_filter": "Cardiology"
        }
    )
    
    assert response.status_code == 200
    results = response.json()
    
    # All results should be from Cardiology
    for result in results:
        if result["entry"]["category"]:
            assert result["entry"]["category"] == "Cardiology"


@pytest_mark_skipif_no_model
def test_get_stats(client):
    """Test stats endpoint"""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "collection" in data
    assert "exists" in data


@pytest_mark_skipif_no_model
def test_create_collection(client):
    """Test create collection endpoint"""
    response = client.post("/collection/create")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest_mark_skipif_no_model
def test_create_collection_recreate(client, sample_entries):
    """Test recreating collection"""
    # Add entries
    store = get_vector_store()
    store.add_entries(sample_entries)
    
    # Recreate
    response = client.post("/collection/create?recreate=true")
    assert response.status_code == 200
    
    # Check collection is empty
    stats = store.get_stats()
    assert stats["points_count"] == 0


@pytest_mark_skipif_no_model
def test_delete_collection(client):
    """Test delete collection endpoint"""
    response = client.delete("/collection")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
