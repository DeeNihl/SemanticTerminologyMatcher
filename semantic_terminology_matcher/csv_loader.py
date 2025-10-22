"""
CSV loader for terminology data
"""
import pandas as pd
from typing import List, Dict, Any
import json
from pathlib import Path

from .models import TerminologyEntry


class CSVLoader:
    """Load terminology entries from CSV files"""
    
    def __init__(self):
        self.required_columns = {"code", "term"}
    
    def load_from_csv(self, file_path: str) -> List[TerminologyEntry]:
        """
        Load terminology entries from a CSV file.
        
        Expected columns:
        - code (required): The terminology code
        - term (required): The terminology term/label
        - description (optional): Description or definition
        - category (optional): Category or domain
        - metadata (optional): JSON string with additional metadata
        - Any other columns will be added to metadata
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of TerminologyEntry objects
            
        Raises:
            ValueError: If required columns are missing
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        # Read CSV
        df = pd.read_csv(file_path)
        
        # Check required columns
        missing_columns = self.required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Convert to entries
        entries = []
        for _, row in df.iterrows():
            entry_data = self._row_to_entry(row)
            entries.append(TerminologyEntry(**entry_data))
        
        return entries
    
    def _row_to_entry(self, row: pd.Series) -> Dict[str, Any]:
        """Convert a DataFrame row to entry dictionary"""
        entry_data = {
            "code": str(row["code"]),
            "term": str(row["term"]),
        }
        
        # Add optional fields
        if "description" in row and pd.notna(row["description"]):
            entry_data["description"] = str(row["description"])
        
        if "category" in row and pd.notna(row["category"]):
            entry_data["category"] = str(row["category"])
        
        # Handle metadata
        metadata = {}
        
        # If there's a metadata column, parse it
        if "metadata" in row and pd.notna(row["metadata"]):
            try:
                metadata.update(json.loads(row["metadata"]))
            except json.JSONDecodeError:
                # If it's not JSON, just store as string
                metadata["metadata"] = str(row["metadata"])
        
        # Add any extra columns to metadata
        extra_columns = set(row.index) - {"code", "term", "description", "category", "metadata"}
        for col in extra_columns:
            if pd.notna(row[col]):
                metadata[col] = row[col]
        
        if metadata:
            entry_data["metadata"] = metadata
        
        return entry_data
