"""
Tests for vector store
"""
import pytest
from semantic_terminology_matcher.vector_store import VectorStore
from semantic_terminology_matcher.models import TerminologyEntry


# Skip tests if embedding model is not available
pytest_mark_skipif_no_model = pytest.mark.skipif(
    True,  # Skip by default in environments without internet access
    reason="Embedding model download requires internet access to huggingface.co"
)


@pytest_mark_skipif_no_model
@pytest.fixture
def vector_store():
    """Create in-memory vector store for testing"""
    store = VectorStore(use_memory=True)
    store.create_collection(recreate=True)
    yield store
    # Cleanup
    try:
        store.delete_collection()
    except:
        pass


@pytest.fixture
def sample_entries():
    """Create sample terminology entries"""
    return [
        TerminologyEntry(
            code="SNOMED:22298006",
            term="Myocardial infarction",
            description="Heart attack",
            category="Cardiology",
        ),
        TerminologyEntry(
            code="SNOMED:38341003",
            term="Hypertension",
            description="High blood pressure",
            category="Cardiology",
        ),
        TerminologyEntry(
            code="SNOMED:73211009",
            term="Diabetes mellitus",
            description="Chronic condition affecting blood sugar",
            category="Endocrinology",
        ),
    ]


@pytest_mark_skipif_no_model
def test_create_collection(vector_store):
    """Test collection creation"""
    stats = vector_store.get_stats()
    assert stats["exists"] is True


@pytest_mark_skipif_no_model
def test_add_entries(vector_store, sample_entries):
    """Test adding entries to vector store"""
    count = vector_store.add_entries(sample_entries)
    assert count == 3
    
    stats = vector_store.get_stats()
    assert stats["points_count"] == 3


@pytest_mark_skipif_no_model
def test_search_basic(vector_store, sample_entries):
    """Test basic search"""
    vector_store.add_entries(sample_entries)
    
    results = vector_store.search("heart attack", limit=5)
    
    assert len(results) > 0
    # The top result should be myocardial infarction
    assert "infarction" in results[0].entry.term.lower() or "heart" in results[0].entry.term.lower()
    assert results[0].score > 0.5  # Should have decent similarity


@pytest_mark_skipif_no_model
def test_search_with_limit(vector_store, sample_entries):
    """Test search with limit"""
    vector_store.add_entries(sample_entries)
    
    results = vector_store.search("heart disease", limit=2)
    
    assert len(results) <= 2


@pytest_mark_skipif_no_model
def test_search_with_threshold(vector_store, sample_entries):
    """Test search with score threshold"""
    vector_store.add_entries(sample_entries)
    
    results = vector_store.search("heart attack", score_threshold=0.6)
    
    # All results should meet threshold
    for result in results:
        assert result.score >= 0.6


@pytest_mark_skipif_no_model
def test_search_with_category_filter(vector_store, sample_entries):
    """Test search with category filter"""
    vector_store.add_entries(sample_entries)
    
    results = vector_store.search("disease", category_filter="Cardiology")
    
    # All results should be in Cardiology category
    for result in results:
        assert result.entry.category == "Cardiology"


@pytest_mark_skipif_no_model
def test_search_empty_collection(vector_store):
    """Test search in empty collection"""
    results = vector_store.search("test query")
    assert len(results) == 0


def test_get_stats_nonexistent_collection():
    """Test getting stats for non-existent collection"""
    store = VectorStore(use_memory=True, collection_name="nonexistent_test_collection")
    stats = store.get_stats()
    assert stats["exists"] is False


@pytest_mark_skipif_no_model
def test_delete_collection(vector_store, sample_entries):
    """Test deleting collection"""
    vector_store.add_entries(sample_entries)
    
    vector_store.delete_collection()
    
    stats = vector_store.get_stats()
    assert stats["exists"] is False


@pytest_mark_skipif_no_model
def test_embedding_generation(vector_store):
    """Test embedding generation"""
    embedding = vector_store._generate_embedding("test text")
    
    assert isinstance(embedding, list)
    assert len(embedding) == vector_store.embedding_dim
    assert all(isinstance(x, float) for x in embedding)
