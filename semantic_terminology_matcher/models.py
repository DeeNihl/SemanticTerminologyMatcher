"""
Data models for terminology entries
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class TerminologyEntry(BaseModel):
    """A terminology entry with code and metadata"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "SNOMED:12345",
                "term": "Acute myocardial infarction",
                "description": "Heart attack",
                "category": "Cardiology",
                "metadata": {"source": "SNOMED CT", "version": "2023"}
            }
        }
    )
    
    code: str = Field(..., description="The terminology code")
    term: str = Field(..., description="The terminology term/label")
    description: Optional[str] = Field(None, description="Description or definition")
    category: Optional[str] = Field(None, description="Category or domain")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SearchResult(BaseModel):
    """Search result with similarity score"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entry": {
                    "code": "SNOMED:12345",
                    "term": "Acute myocardial infarction",
                    "description": "Heart attack",
                    "category": "Cardiology",
                    "metadata": {}
                },
                "score": 0.95
            }
        }
    )
    
    entry: TerminologyEntry
    score: float = Field(..., description="Similarity score (0-1)")


class SearchRequest(BaseModel):
    """Search request parameters"""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "heart attack",
                "limit": 5,
                "score_threshold": 0.7,
                "category_filter": "Cardiology"
            }
        }
    )
    
    query: str = Field(..., description="Search query text")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    score_threshold: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Minimum similarity score"
    )
    category_filter: Optional[str] = Field(None, description="Filter by category")
