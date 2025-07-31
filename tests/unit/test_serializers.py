"""Unit tests for output serializers."""
import json
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from src.models import ASNResult, BatchResult
from src.serializers import CSVSerializer, JSONSerializer, ParquetSerializer


class TestJSONSerializer:
    """Test JSON serializer."""
    
    def test_serialize_to_string(self):
        """Test serializing to JSON string."""
        results = [
            ASNResult(ip="8.8.8.8", asn=15169, provider="pyipmeta"),
            ASNResult(ip="1.1.1.1", asn=13335, provider="pyipmeta"),
        ]
        batch = BatchResult(
            results=results,
            total=2,
            successful=2,
            lookup_date=datetime(2023, 1, 1)
        )
        
        json_str = JSONSerializer.serialize(batch)
        data = json.loads(json_str)
        
        assert len(data["results"]) == 2
        assert data["total"] == 2
        assert data["successful"] == 2
        assert data["results"][0]["ip"] == "8.8.8.8"
        assert data["results"][0]["asn"] == 15169
    
    def test_serialize_to_file(self):
        """Test serializing to JSON file."""
        results = [ASNResult(ip="8.8.8.8", asn=15169, provider="pyipmeta")]
        batch = BatchResult(
            results=results,
            total=1,
            successful=1,
            lookup_date=datetime(2023, 1, 1)
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            JSONSerializer.serialize(batch, temp_path)
            
            with open(temp_path, 'r') as f:
                data = json.load(f)
            
            assert len(data["results"]) == 1
            assert data["results"][0]["ip"] == "8.8.8.8"
        finally:
            Path(temp_path).unlink()


class TestCSVSerializer:
    """Test CSV serializer."""
    
    def test_serialize_to_string(self):
        """Test serializing to CSV string."""
        results = [
            ASNResult(ip="8.8.8.8", asn=15169, provider="pyipmeta"),
            ASNResult(ip="1.1.1.1", asn=13335, provider="pyipmeta"),
        ]
        batch = BatchResult(
            results=results,
            total=2,
            successful=2,
            lookup_date=datetime(2023, 1, 1)
        )
        
        csv_str = CSVSerializer.serialize(batch)
        lines = csv_str.strip().split('\n')
        
        assert len(lines) == 3  # Header + 2 rows
        assert "ip,asn,timestamp,provider" in lines[0]
        assert "8.8.8.8,15169" in lines[1]
        assert "1.1.1.1,13335" in lines[2]
    
    def test_serialize_to_file(self):
        """Test serializing to CSV file."""
        results = [ASNResult(ip="8.8.8.8", asn=15169, provider="pyipmeta")]
        batch = BatchResult(
            results=results,
            total=1,
            successful=1,
            lookup_date=datetime(2023, 1, 1)
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_path = f.name
        
        try:
            CSVSerializer.serialize(batch, temp_path)
            
            df = pd.read_csv(temp_path)
            assert len(df) == 1
            assert df.iloc[0]['ip'] == "8.8.8.8"
            assert df.iloc[0]['asn'] == 15169
        finally:
            Path(temp_path).unlink()


class TestParquetSerializer:
    """Test Parquet serializer."""
    
    def test_serialize_to_file(self):
        """Test serializing to Parquet file."""
        results = [
            ASNResult(ip="8.8.8.8", asn=15169, provider="pyipmeta"),
            ASNResult(ip="1.1.1.1", asn=13335, provider="pyipmeta"),
        ]
        batch = BatchResult(
            results=results,
            total=2,
            successful=2,
            lookup_date=datetime(2023, 1, 1)
        )
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet') as f:
            temp_path = f.name
        
        try:
            ParquetSerializer.serialize(batch, temp_path)
            
            df = pd.read_parquet(temp_path)
            assert len(df) == 2
            assert df.iloc[0]['ip'] == "8.8.8.8"
            assert df.iloc[0]['asn'] == 15169
            assert df.iloc[1]['ip'] == "1.1.1.1"
            assert df.iloc[1]['asn'] == 13335
        finally:
            Path(temp_path).unlink()
    
    def test_serialize_to_bytes(self):
        """Test serializing to bytes."""
        results = [ASNResult(ip="8.8.8.8", asn=15169, provider="pyipmeta")]
        batch = BatchResult(
            results=results,
            total=1,
            successful=1,
            lookup_date=datetime(2023, 1, 1)
        )
        
        parquet_bytes = ParquetSerializer.serialize(batch)
        assert isinstance(parquet_bytes, bytes)
        assert len(parquet_bytes) > 0