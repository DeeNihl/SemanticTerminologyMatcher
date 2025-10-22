"""
Tests for FastAPI application
"""
import pytest
from fastapi.testclient import TestClient

from semantic_terminology_matcher.api import app, get_vector_store
from semantic_terminology_matcher.vector_store import VectorStore
from semantic_terminology_matcher.models import TerminologyEntry


@pytest.fixture
def client():
    """Create test client"""
    # Override vector store to use in-memory
    def override_get_vector_store():
        store = VectorStore(use_memory=True)
        store.create_collection(recreate=True)
        return store
    
    app.dependency_overrides[get_vector_store] = override_get_vector_store
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


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
    assert "collection_exists" in data


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


def test_get_stats(client):
    """Test stats endpoint"""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "collection" in data
    assert "exists" in data


def test_create_collection(client):
    """Test create collection endpoint"""
    response = client.post("/collection/create")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


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


def test_delete_collection(client):
    """Test delete collection endpoint"""
    response = client.delete("/collection")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
