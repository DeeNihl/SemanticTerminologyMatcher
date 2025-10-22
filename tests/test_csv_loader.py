"""
Tests for CSV loader
"""
import pytest
import pandas as pd
from pathlib import Path
import tempfile
import json

from semantic_terminology_matcher.csv_loader import CSVLoader
from semantic_terminology_matcher.models import TerminologyEntry


@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file for testing"""
    csv_content = """code,term,description,category
SNOMED:12345,Myocardial infarction,Heart attack,Cardiology
ICD10:E11,Type 2 diabetes,Diabetes mellitus,Endocrinology
LOINC:2093-3,Cholesterol,Total cholesterol,Laboratory"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink()


@pytest.fixture
def csv_with_metadata():
    """Create CSV with metadata column"""
    csv_content = """code,term,description,category,metadata,source
SNOMED:12345,Test term,Test description,Test category,"{""version"": ""2023""}",TestSource"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name
    
    yield temp_path
    
    Path(temp_path).unlink()


def test_load_from_csv_basic(sample_csv_file):
    """Test basic CSV loading"""
    loader = CSVLoader()
    entries = loader.load_from_csv(sample_csv_file)
    
    assert len(entries) == 3
    assert all(isinstance(e, TerminologyEntry) for e in entries)
    
    # Check first entry
    entry = entries[0]
    assert entry.code == "SNOMED:12345"
    assert entry.term == "Myocardial infarction"
    assert entry.description == "Heart attack"
    assert entry.category == "Cardiology"


def test_load_from_csv_with_metadata(csv_with_metadata):
    """Test CSV loading with metadata"""
    loader = CSVLoader()
    entries = loader.load_from_csv(csv_with_metadata)
    
    assert len(entries) == 1
    entry = entries[0]
    
    # Check metadata was parsed
    assert "version" in entry.metadata
    assert entry.metadata["version"] == "2023"
    
    # Check extra column was added to metadata
    assert "source" in entry.metadata
    assert entry.metadata["source"] == "TestSource"


def test_load_missing_file():
    """Test loading from non-existent file"""
    loader = CSVLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_from_csv("nonexistent.csv")


def test_load_missing_required_columns():
    """Test CSV with missing required columns"""
    csv_content = """term,description
    Test term,Test description"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name
    
    try:
        loader = CSVLoader()
        with pytest.raises(ValueError, match="Missing required columns"):
            loader.load_from_csv(temp_path)
    finally:
        Path(temp_path).unlink()


def test_row_to_entry_minimal():
    """Test converting minimal row to entry"""
    loader = CSVLoader()
    row = pd.Series({"code": "TEST:001", "term": "Test Term"})
    
    entry_data = loader._row_to_entry(row)
    
    assert entry_data["code"] == "TEST:001"
    assert entry_data["term"] == "Test Term"
    assert "description" not in entry_data
    assert "category" not in entry_data


def test_row_to_entry_full():
    """Test converting full row to entry"""
    loader = CSVLoader()
    row = pd.Series({
        "code": "TEST:001",
        "term": "Test Term",
        "description": "Test Description",
        "category": "Test Category",
        "extra_field": "Extra Value"
    })
    
    entry_data = loader._row_to_entry(row)
    
    assert entry_data["code"] == "TEST:001"
    assert entry_data["term"] == "Test Term"
    assert entry_data["description"] == "Test Description"
    assert entry_data["category"] == "Test Category"
    assert entry_data["metadata"]["extra_field"] == "Extra Value"
