"""Pydantic models for OMOP concepts and API responses."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OMOPConcept(BaseModel):
    """OMOP Concept model."""

    concept_id: int = Field(..., description="OMOP Concept ID")
    concept_name: str = Field(..., description="Concept name")
    domain_id: Optional[str] = Field(None, description="Domain ID")
    vocabulary_id: Optional[str] = Field(None, description="Vocabulary ID")
    concept_class_id: Optional[str] = Field(None, description="Concept class ID")
    concept_code: Optional[str] = Field(None, description="Concept code")
    definition_chunk: str = Field(..., description="Definition text for embedding")
    metadata_payload: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "concept_id": 123456,
                "concept_name": "Type 2 diabetes mellitus",
                "domain_id": "Condition",
                "vocabulary_id": "SNOMED",
                "concept_class_id": "Clinical Finding",
                "concept_code": "44054006",
                "definition_chunk": "A chronic metabolic disorder characterized by high blood glucose levels",
                "metadata_payload": {"source": "SNOMED CT", "version": "2023-01"},
            }
        }


class SearchResult(BaseModel):
    """Search result model."""

    concept_id: int
    concept_name: str
    score: float = Field(..., description="Similarity score")
    definition_chunk: str
    metadata_payload: Dict[str, Any] = Field(default_factory=dict)


class UploadResponse(BaseModel):
    """Response model for CSV upload."""

    message: str
    total_records: int
    successful_uploads: int
    failed_uploads: int = 0
    errors: List[str] = Field(default_factory=list)


class SearchRequest(BaseModel):
    """Search request model."""

    query: str = Field(..., description="Search query text")
    limit: int = Field(default=10, ge=1, le=100, description="Number of results")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    qdrant_connected: bool
    collection_exists: bool
    total_points: int = 0
