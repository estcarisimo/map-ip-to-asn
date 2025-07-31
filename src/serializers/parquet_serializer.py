"""Parquet serializer for ASN lookup results."""
from typing import Optional

import pandas as pd

from ..models import BatchResult


class ParquetSerializer:
    """Serialize results to Parquet format."""
    
    @staticmethod
    def serialize(result: BatchResult, output_file: Optional[str] = None) -> bytes:
        """Serialize BatchResult to Parquet.
        
        Args:
            result: The batch result to serialize.
            output_file: Optional path to write the output to.
            
        Returns:
            The Parquet bytes representation.
        """
        # Convert results to DataFrame
        df = pd.DataFrame([
            {
                'ip': r.ip,
                'asn': r.asn,
                'timestamp': r.timestamp,
                'provider': r.provider
            }
            for r in result.results
        ])
        
        if output_file:
            df.to_parquet(output_file, index=False, engine='pyarrow')
            # Read back to return bytes
            with open(output_file, 'rb') as f:
                return f.read()
        else:
            # Return as bytes
            return df.to_parquet(index=False, engine='pyarrow')