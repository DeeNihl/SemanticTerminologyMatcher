"""
Simplified integration test that verifies code structure without needing model downloads
"""
import pytest
from semantic_terminology_matcher.models import TerminologyEntry, SearchRequest
from semantic_terminology_matcher.csv_loader import CSVLoader
from semantic_terminology_matcher.config import settings


def test_models_can_be_instantiated():
    """Test that models can be created"""
    entry = TerminologyEntry(
        code="TEST:001",
        term="Test Term",
        description="Test Description",
        category="Test Category"
    )
    assert entry.code == "TEST:001"
    assert entry.term == "Test Term"


def test_search_request_validation():
    """Test search request validation"""
    request = SearchRequest(
        query="test query",
        limit=5,
        score_threshold=0.7
    )
    assert request.query == "test query"
    assert request.limit == 5
    assert request.score_threshold == 0.7


def test_config_loads():
    """Test that configuration loads"""
    assert settings.qdrant_collection == "terminology"
    assert settings.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"


def test_csv_loader_exists():
    """Test CSV loader is importable"""
    loader = CSVLoader()
    assert loader.required_columns == {"code", "term"}
