"""CSV serializer for ASN lookup results."""
import csv
from io import StringIO
from typing import Optional

from ..models import BatchResult


class CSVSerializer:
    """Serialize results to CSV format."""
    
    @staticmethod
    def serialize(result: BatchResult, output_file: Optional[str] = None) -> str:
        """Serialize BatchResult to CSV.
        
        Args:
            result: The batch result to serialize.
            output_file: Optional path to write the output to.
            
        Returns:
            The CSV string representation.
        """
        output = StringIO()
        writer = csv.DictWriter(
            output, 
            fieldnames=['ip', 'asn', 'timestamp', 'provider'],
            quoting=csv.QUOTE_MINIMAL
        )
        
        writer.writeheader()
        for r in result.results:
            writer.writerow({
                'ip': r.ip,
                'asn': r.asn,
                'timestamp': r.timestamp.isoformat(),
                'provider': r.provider
            })
        
        csv_str = output.getvalue()
        
        if output_file:
            with open(output_file, 'w', newline='') as f:
                f.write(csv_str)
        
        return csv_str