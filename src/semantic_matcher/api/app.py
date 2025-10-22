"""FastAPI application for OMOP concept vector store."""

import logging
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse

from ..core.csv_loader import CSVLoader
from ..core.vector_store import VectorStore
from ..models.schemas import (
    SearchRequest,
    SearchResult,
    UploadResponse,
    HealthResponse,
    OMOPConcept,
)
from ..config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="OMOP Concept Vector Store API",
    description="API for managing and searching OMOP concepts using semantic similarity",
    version="0.1.0",
)

# Initialize components
vector_store = VectorStore()
csv_loader = CSVLoader()


@app.on_event("startup")
async def startup_event():
    """Initialize vector store on startup."""
    logger.info("Starting up OMOP Concept Vector Store API")
    # Ensure collection exists
    if not vector_store.collection_exists():
        logger.info("Collection does not exist, creating it...")
        vector_store.create_collection()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "OMOP Concept Vector Store API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Check the health status of the API and vector store.

    Returns:
        Health status including Qdrant connection and collection info
    """
    health = vector_store.health_check()

    return HealthResponse(
        status="healthy" if health["connected"] else "unhealthy",
        qdrant_connected=health["connected"],
        collection_exists=health["collection_exists"],
        total_points=health["total_points"],
    )


@app.post("/upload/csv", response_model=UploadResponse, tags=["Upload"])
async def upload_csv(
    file: UploadFile = File(...),
    recreate_collection: bool = Query(
        False, description="Recreate collection before upload"
    ),
):
    """
    Upload OMOP concepts from a CSV file.

    Expected CSV columns:
    - concept_id (required): Integer concept ID
    - concept_name (required): Name of the concept
    - definition_chunk (required): Text definition for embedding
    - domain_id (optional): Domain identifier
    - vocabulary_id (optional): Vocabulary identifier
    - concept_class_id (optional): Concept class identifier
    - concept_code (optional): Concept code
    - metadata_payload (optional): JSON string with additional metadata

    Args:
        file: CSV file to upload
        recreate_collection: If True, recreate the collection before uploading

    Returns:
        Upload status and statistics
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        # Save uploaded file temporarily
        temp_path = Path("/tmp") / file.filename
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Load concepts from CSV
        logger.info(f"Loading concepts from {file.filename}")
        concepts = csv_loader.load_from_csv(str(temp_path))

        if not concepts:
            raise HTTPException(
                status_code=400, detail="No valid concepts found in CSV"
            )

        # Recreate collection if requested
        if recreate_collection:
            logger.info("Recreating collection...")
            vector_store.create_collection(recreate=True)

        # Upload to vector store
        logger.info(f"Uploading {len(concepts)} concepts to vector store")
        uploaded_count = vector_store.upload_concepts(concepts)

        # Clean up temp file
        temp_path.unlink()

        return UploadResponse(
            message="Successfully uploaded concepts",
            total_records=len(concepts),
            successful_uploads=uploaded_count,
            failed_uploads=len(concepts) - uploaded_count,
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/search", response_model=List[SearchResult], tags=["Search"])
async def search_concepts(request: SearchRequest):
    """
    Search for OMOP concepts using semantic similarity.

    Args:
        request: Search request with query and limit

    Returns:
        List of matching concepts with similarity scores
    """
    try:
        results = vector_store.search(
            query=request.query,
            limit=request.limit,
        )
        return results

    except Exception as e:
        logger.error(f"Error searching concepts: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/concepts/{concept_id}", response_model=OMOPConcept, tags=["Concepts"])
async def get_concept(concept_id: int):
    """
    Retrieve a specific OMOP concept by ID.

    Args:
        concept_id: The concept ID to retrieve

    Returns:
        OMOP concept details
    """
    concept = vector_store.get_concept_by_id(concept_id)

    if concept is None:
        raise HTTPException(status_code=404, detail=f"Concept {concept_id} not found")

    return concept


@app.delete("/collection", tags=["Collection"])
async def delete_collection():
    """
    Delete the entire collection.

    Returns:
        Deletion status
    """
    try:
        deleted = vector_store.delete_collection()
        if deleted:
            return {"message": "Collection deleted successfully"}
        else:
            return {"message": "Collection did not exist"}

    except Exception as e:
        logger.error(f"Error deleting collection: {e}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@app.post("/collection/create", tags=["Collection"])
async def create_collection(recreate: bool = Query(False)):
    """
    Create the collection (optionally recreate if it exists).

    Args:
        recreate: If True, delete and recreate the collection

    Returns:
        Creation status
    """
    try:
        created = vector_store.create_collection(recreate=recreate)
        if created:
            return {"message": "Collection created successfully"}
        else:
            return {"message": "Collection already exists"}

    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise HTTPException(status_code=500, detail=f"Creation failed: {str(e)}")


@app.get("/collection/info", tags=["Collection"])
async def get_collection_info():
    """
    Get information about the collection.

    Returns:
        Collection statistics and status
    """
    try:
        info = vector_store.get_collection_info()
        return info

    except Exception as e:
        logger.error(f"Error getting collection info: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get collection info: {str(e)}"
        )
