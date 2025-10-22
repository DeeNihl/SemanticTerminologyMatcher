"""Vector store implementation using Qdrant."""

import logging
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

from ..models.schemas import OMOPConcept, SearchResult
from ..config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages OMOP concepts in Qdrant vector store."""

    def __init__(
        self,
        collection_name: Optional[str] = None,
        embedding_model: Optional[str] = None,
    ):
        """
        Initialize vector store.

        Args:
            collection_name: Name of the Qdrant collection
            embedding_model: Name of the sentence transformer model
        """
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.embedding_model_name = embedding_model or settings.embedding_model

        # Initialize Qdrant client
        self.client = self._init_qdrant_client()

        # Initialize embedding model
        logger.info(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        self.vector_size = self.embedding_model.get_sentence_embedding_dimension()

        logger.info(f"VectorStore initialized with collection: {self.collection_name}")

    def _init_qdrant_client(self) -> QdrantClient:
        """
        Initialize Qdrant client.

        Returns:
            QdrantClient instance
        """
        if settings.qdrant_api_key:
            return QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                api_key=settings.qdrant_api_key,
            )
        else:
            return QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )

    def create_collection(self, recreate: bool = False) -> bool:
        """
        Create Qdrant collection if it doesn't exist.

        Args:
            recreate: If True, delete and recreate the collection

        Returns:
            True if collection was created, False if it already existed
        """
        try:
            if recreate and self.client.collection_exists(self.collection_name):
                logger.info(f"Deleting existing collection: {self.collection_name}")
                self.client.delete_collection(self.collection_name)

            if not self.client.collection_exists(self.collection_name):
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE,
                    ),
                )
                return True
            else:
                logger.info(f"Collection already exists: {self.collection_name}")
                return False

        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise

    def collection_exists(self) -> bool:
        """
        Check if collection exists.

        Returns:
            True if collection exists
        """
        return self.client.collection_exists(self.collection_name)

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.

        Returns:
            Dictionary with collection information
        """
        if not self.collection_exists():
            return {"exists": False}

        info = self.client.get_collection(self.collection_name)
        return {
            "exists": True,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status,
        }

    def upload_concepts(self, concepts: List[OMOPConcept], batch_size: int = 100) -> int:
        """
        Upload OMOP concepts to Qdrant.

        Args:
            concepts: List of OMOPConcept objects
            batch_size: Number of concepts to upload per batch

        Returns:
            Number of successfully uploaded concepts
        """
        if not concepts:
            logger.warning("No concepts to upload")
            return 0

        # Ensure collection exists
        if not self.collection_exists():
            self.create_collection()

        logger.info(f"Uploading {len(concepts)} concepts in batches of {batch_size}")

        # Prepare points for upload
        points = []
        for concept in concepts:
            # Generate embedding from definition_chunk
            embedding = self.embedding_model.encode(concept.definition_chunk).tolist()

            # Prepare payload
            payload = {
                "concept_id": concept.concept_id,
                "concept_name": concept.concept_name,
                "definition_chunk": concept.definition_chunk,
                "domain_id": concept.domain_id,
                "vocabulary_id": concept.vocabulary_id,
                "concept_class_id": concept.concept_class_id,
                "concept_code": concept.concept_code,
                "metadata_payload": concept.metadata_payload,
            }

            point = PointStruct(
                id=concept.concept_id,
                vector=embedding,
                payload=payload,
            )
            points.append(point)

        # Upload in batches
        uploaded_count = 0
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                )
                uploaded_count += len(batch)
                logger.info(f"Uploaded batch {i // batch_size + 1}: {len(batch)} points")
            except Exception as e:
                logger.error(f"Error uploading batch {i // batch_size + 1}: {e}")

        logger.info(f"Successfully uploaded {uploaded_count} concepts")
        return uploaded_count

    def search(
        self,
        query: str,
        limit: int = 10,
        score_threshold: Optional[float] = None,
    ) -> List[SearchResult]:
        """
        Search for similar concepts using semantic search.

        Args:
            query: Search query text
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of SearchResult objects
        """
        if not self.collection_exists():
            logger.warning("Collection does not exist")
            return []

        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()

        # Search in Qdrant
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
        )

        # Convert to SearchResult objects
        results = []
        for hit in search_result:
            result = SearchResult(
                concept_id=hit.payload["concept_id"],
                concept_name=hit.payload["concept_name"],
                definition_chunk=hit.payload["definition_chunk"],
                score=hit.score,
                metadata_payload=hit.payload.get("metadata_payload", {}),
            )
            results.append(result)

        return results

    def get_concept_by_id(self, concept_id: int) -> Optional[OMOPConcept]:
        """
        Retrieve a concept by its ID.

        Args:
            concept_id: The concept ID to retrieve

        Returns:
            OMOPConcept object or None if not found
        """
        if not self.collection_exists():
            return None

        try:
            point = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[concept_id],
            )

            if not point:
                return None

            payload = point[0].payload
            return OMOPConcept(
                concept_id=payload["concept_id"],
                concept_name=payload["concept_name"],
                definition_chunk=payload["definition_chunk"],
                domain_id=payload.get("domain_id"),
                vocabulary_id=payload.get("vocabulary_id"),
                concept_class_id=payload.get("concept_class_id"),
                concept_code=payload.get("concept_code"),
                metadata_payload=payload.get("metadata_payload", {}),
            )

        except Exception as e:
            logger.error(f"Error retrieving concept {concept_id}: {e}")
            return None

    def delete_collection(self) -> bool:
        """
        Delete the collection.

        Returns:
            True if successful
        """
        try:
            if self.collection_exists():
                self.client.delete_collection(self.collection_name)
                logger.info(f"Deleted collection: {self.collection_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise

    def health_check(self) -> Dict[str, Any]:
        """
        Check health of vector store connection.

        Returns:
            Dictionary with health status
        """
        try:
            # Check if we can connect to Qdrant
            collections = self.client.get_collections()

            collection_info = self.get_collection_info()

            return {
                "connected": True,
                "collection_exists": collection_info.get("exists", False),
                "total_points": collection_info.get("points_count", 0),
                "status": "healthy",
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "connected": False,
                "collection_exists": False,
                "total_points": 0,
                "status": f"error: {str(e)}",
            }
