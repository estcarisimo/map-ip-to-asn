"""JSON serializer for ASN lookup results."""
import json
from typing import Optional

from ..models import BatchResult


class JSONSerializer:
    """Serialize results to JSON format."""
    
    @staticmethod
    def serialize(result: BatchResult, output_file: Optional[str] = None) -> str:
        """Serialize BatchResult to JSON.
        
        Args:
            result: The batch result to serialize.
            output_file: Optional path to write the output to.
            
        Returns:
            The JSON string representation.
        """
        json_str = result.model_dump_json(indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_str)
        
        return json_str