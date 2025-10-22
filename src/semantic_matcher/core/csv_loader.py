"""CSV loader for OMOP concepts."""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

from ..models.schemas import OMOPConcept

logger = logging.getLogger(__name__)


class CSVLoader:
    """Loads OMOP concepts from CSV files."""

    def __init__(self):
        """Initialize CSV loader."""
        self.logger = logger

    def load_from_csv(self, file_path: str) -> List[OMOPConcept]:
        """
        Load OMOP concepts from a CSV file.

        Expected CSV columns:
        - concept_id (required): Integer concept ID
        - concept_name (required): Name of the concept
        - domain_id (optional): Domain identifier
        - vocabulary_id (optional): Vocabulary identifier
        - concept_class_id (optional): Concept class identifier
        - concept_code (optional): Concept code
        - definition_chunk (required): Text definition for embedding
        - metadata_payload (optional): JSON string with additional metadata

        Args:
            file_path: Path to the CSV file

        Returns:
            List of OMOPConcept objects

        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If required columns are missing
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        self.logger.info(f"Loading CSV from {file_path}")
        df = pd.read_csv(file_path)

        # Validate required columns
        required_columns = {"concept_id", "concept_name", "definition_chunk"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        self.logger.info(f"Found {len(df)} records in CSV")

        concepts = []
        errors = []

        for idx, row in df.iterrows():
            try:
                concept = self._parse_row(row)
                concepts.append(concept)
            except Exception as e:
                error_msg = f"Error parsing row {idx}: {str(e)}"
                self.logger.warning(error_msg)
                errors.append(error_msg)

        self.logger.info(
            f"Successfully parsed {len(concepts)} concepts ({len(errors)} errors)"
        )

        if errors:
            self.logger.warning(f"Errors encountered: {errors[:5]}")  # Show first 5

        return concepts

    def _parse_row(self, row: pd.Series) -> OMOPConcept:
        """
        Parse a single CSV row into an OMOPConcept.

        Args:
            row: Pandas Series representing a CSV row

        Returns:
            OMOPConcept object
        """
        # Parse metadata_payload if it exists
        metadata_payload = {}
        if "metadata_payload" in row and pd.notna(row["metadata_payload"]):
            try:
                if isinstance(row["metadata_payload"], str):
                    metadata_payload = json.loads(row["metadata_payload"])
                elif isinstance(row["metadata_payload"], dict):
                    metadata_payload = row["metadata_payload"]
            except json.JSONDecodeError:
                self.logger.warning(
                    f"Failed to parse metadata_payload for concept_id {row['concept_id']}"
                )

        # Build concept data
        concept_data = {
            "concept_id": int(row["concept_id"]),
            "concept_name": str(row["concept_name"]),
            "definition_chunk": str(row["definition_chunk"]),
            "metadata_payload": metadata_payload,
        }

        # Add optional fields if they exist and are not null
        optional_fields = [
            "domain_id",
            "vocabulary_id",
            "concept_class_id",
            "concept_code",
        ]
        for field in optional_fields:
            if field in row and pd.notna(row[field]):
                concept_data[field] = str(row[field])

        return OMOPConcept(**concept_data)

    def validate_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Validate a CSV file without loading all data.

        Args:
            file_path: Path to the CSV file

        Returns:
            Dictionary with validation results
        """
        path = Path(file_path)
        if not path.exists():
            return {"valid": False, "error": f"File not found: {file_path}"}

        try:
            # Read only first few rows for validation
            df = pd.read_csv(file_path, nrows=5)

            required_columns = {"concept_id", "concept_name", "definition_chunk"}
            missing_columns = required_columns - set(df.columns)

            if missing_columns:
                return {
                    "valid": False,
                    "error": f"Missing required columns: {missing_columns}",
                    "found_columns": list(df.columns),
                }

            # Get total row count
            total_rows = sum(1 for _ in open(file_path)) - 1  # Subtract header

            return {
                "valid": True,
                "total_rows": total_rows,
                "columns": list(df.columns),
                "sample_data": df.head().to_dict("records"),
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}
