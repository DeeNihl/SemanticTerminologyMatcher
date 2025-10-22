"""
FastAPI application for Semantic Terminology Matcher
"""
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
import uvicorn

from .models import TerminologyEntry, SearchResult, SearchRequest
from .vector_store import VectorStore
from .csv_loader import CSVLoader
from .config import settings


app = FastAPI(
    title="Semantic Terminology Matcher API",
    description="REST API for semantic search of terminology entries using Qdrant vector store",
    version="0.1.0",
)

# Global vector store instance
vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create vector store instance"""
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
    return vector_store


@app.on_event("startup")
async def startup_event():
    """Initialize vector store on startup"""
    get_vector_store()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Semantic Terminology Matcher API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    store = get_vector_store()
    stats = store.get_stats()
    return {
        "status": "healthy",
        "collection": settings.qdrant_collection,
        "collection_exists": stats.get("exists", False),
        "points_count": stats.get("points_count", 0),
    }


@app.post("/search", response_model=List[SearchResult])
async def search(request: SearchRequest):
    """
    Search for terminology entries using semantic similarity.
    
    Args:
        request: Search request with query and parameters
        
    Returns:
        List of matching entries with similarity scores
    """
    try:
        store = get_vector_store()
        results = store.search(
            query=request.query,
            limit=request.limit,
            score_threshold=request.score_threshold,
            category_filter=request.category_filter,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/{query}", response_model=List[SearchResult])
async def search_get(
    query: str,
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    score_threshold: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum score"),
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """
    Search for terminology entries using GET request.
    
    Args:
        query: Search query text
        limit: Maximum number of results
        score_threshold: Minimum similarity score
        category: Filter by category
        
    Returns:
        List of matching entries with similarity scores
    """
    try:
        store = get_vector_store()
        results = store.search(
            query=query,
            limit=limit,
            score_threshold=score_threshold,
            category_filter=category,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """
    Get collection statistics.
    
    Returns:
        Collection statistics including count of entries
    """
    try:
        store = get_vector_store()
        stats = store.get_stats()
        return {
            "collection": settings.qdrant_collection,
            **stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/collection/create")
async def create_collection(recreate: bool = Query(False, description="Recreate if exists")):
    """
    Create the Qdrant collection.
    
    Args:
        recreate: If True, delete existing collection and create new one
        
    Returns:
        Success message
    """
    try:
        store = get_vector_store()
        store.create_collection(recreate=recreate)
        return {"message": "Collection created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/collection")
async def delete_collection():
    """
    Delete the Qdrant collection.
    
    Returns:
        Success message
    """
    try:
        store = get_vector_store()
        store.delete_collection()
        return {"message": "Collection deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_server(
    host: str = settings.api_host,
    port: int = settings.api_port,
    reload: bool = False,
):
    """Run the FastAPI server"""
    uvicorn.run(
        "semantic_terminology_matcher.api:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    run_server()
