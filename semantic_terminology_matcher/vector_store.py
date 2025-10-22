"""
Qdrant vector store integration
"""
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from sentence_transformers import SentenceTransformer
import uuid

from .models import TerminologyEntry, SearchResult
from .config import settings


class VectorStore:
    """Qdrant vector store for terminology entries"""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: Optional[str] = None,
        embedding_model: Optional[str] = None,
        use_memory: Optional[bool] = None,
    ):
        """
        Initialize vector store.
        
        Args:
            host: Qdrant host (default from settings)
            port: Qdrant port (default from settings)
            collection_name: Collection name (default from settings)
            embedding_model: Embedding model name (default from settings)
            use_memory: Use in-memory storage (default from settings)
        """
        self.host = host or settings.qdrant_host
        self.port = port or settings.qdrant_port
        self.collection_name = collection_name or settings.qdrant_collection
        self.embedding_model_name = embedding_model or settings.embedding_model
        self.use_memory = use_memory if use_memory is not None else settings.qdrant_use_memory
        
        # Initialize Qdrant client
        if self.use_memory:
            self.client = QdrantClient(":memory:")
        else:
            self.client = QdrantClient(host=self.host, port=self.port)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
    
    def create_collection(self, recreate: bool = False) -> None:
        """
        Create the collection in Qdrant.
        
        Args:
            recreate: If True, delete existing collection and create new one
        """
        if recreate and self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)
        
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        return self.embedding_model.encode(text).tolist()
    
    def add_entries(self, entries: List[TerminologyEntry], batch_size: int = 100) -> int:
        """
        Add terminology entries to the vector store.
        
        Args:
            entries: List of terminology entries
            batch_size: Number of entries to upload at once
            
        Returns:
            Number of entries added
        """
        points = []
        
        for entry in entries:
            # Create text for embedding (combine term and description)
            text_parts = [entry.term]
            if entry.description:
                text_parts.append(entry.description)
            text = " ".join(text_parts)
            
            # Generate embedding
            embedding = self._generate_embedding(text)
            
            # Create payload
            payload = {
                "code": entry.code,
                "term": entry.term,
            }
            if entry.description:
                payload["description"] = entry.description
            if entry.category:
                payload["category"] = entry.category
            if entry.metadata:
                payload["metadata"] = entry.metadata
            
            # Create point
            point_id = str(uuid.uuid4())
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload,
            )
            points.append(point)
            
            # Upload in batches
            if len(points) >= batch_size:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points,
                )
                points = []
        
        # Upload remaining points
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
        
        return len(entries)
    
    def search(
        self,
        query: str,
        limit: int = 10,
        score_threshold: Optional[float] = None,
        category_filter: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Search for similar terminology entries.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            category_filter: Filter by category
            
        Returns:
            List of search results with scores
        """
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        
        # Build filter
        query_filter = None
        if category_filter:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="category",
                        match=MatchValue(value=category_filter),
                    )
                ]
            )
        
        # Search
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            query_filter=query_filter,
            score_threshold=score_threshold,
        )
        
        # Convert to SearchResult objects
        results = []
        for hit in search_results:
            entry = TerminologyEntry(
                code=hit.payload["code"],
                term=hit.payload["term"],
                description=hit.payload.get("description"),
                category=hit.payload.get("category"),
                metadata=hit.payload.get("metadata", {}),
            )
            result = SearchResult(entry=entry, score=hit.score)
            results.append(result)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        if not self.client.collection_exists(self.collection_name):
            return {"exists": False}
        
        info = self.client.get_collection(self.collection_name)
        return {
            "exists": True,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
        }
    
    def delete_collection(self) -> None:
        """Delete the collection"""
        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)
