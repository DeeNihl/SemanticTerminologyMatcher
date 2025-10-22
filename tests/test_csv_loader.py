"""Tests for CSV loader."""

import pytest
from pathlib import Path
from semantic_matcher.core.csv_loader import CSVLoader


def test_csv_loader_initialization():
    """Test CSV loader can be initialized."""
    loader = CSVLoader()
    assert loader is not None


def test_validate_sample_csv():
    """Test validation of sample CSV."""
    loader = CSVLoader()
    csv_path = Path(__file__).parent.parent / "data" / "sample_omop_concepts.csv"

    if csv_path.exists():
        result = loader.validate_csv(str(csv_path))
        assert result["valid"] is True
        assert result["total_rows"] > 0
        assert "concept_id" in result["columns"]
        assert "concept_name" in result["columns"]
        assert "definition_chunk" in result["columns"]


def test_load_sample_csv():
    """Test loading sample CSV."""
    loader = CSVLoader()
    csv_path = Path(__file__).parent.parent / "data" / "sample_omop_concepts.csv"

    if csv_path.exists():
        concepts = loader.load_from_csv(str(csv_path))
        assert len(concepts) > 0
        assert concepts[0].concept_id is not None
        assert concepts[0].concept_name is not None
        assert concepts[0].definition_chunk is not None
