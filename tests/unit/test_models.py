"""Unit tests for Pydantic models."""
from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from src.models import (
    ASNResult,
    BatchResult,
    IPAddress,
    LookupConfig,
    OutputFormat,
    Provider,
)


class TestIPAddress:
    """Test IPAddress model."""
    
    def test_valid_ipv4(self):
        """Test valid IPv4 address."""
        ip = IPAddress(address="192.168.1.1")
        assert ip.address == "192.168.1.1"
    
    def test_valid_ipv6(self):
        """Test valid IPv6 address."""
        ip = IPAddress(address="2001:db8::1")
        assert ip.address == "2001:db8::1"
    
    def test_invalid_ip(self):
        """Test invalid IP address."""
        with pytest.raises(ValidationError):
            IPAddress(address="not.an.ip.address")


class TestASNResult:
    """Test ASNResult model."""
    
    def test_creation(self):
        """Test ASNResult creation."""
        result = ASNResult(
            ip="8.8.8.8",
            asn=15169,
            provider="pyipmeta"
        )
        assert result.ip == "8.8.8.8"
        assert result.asn == 15169
        assert result.provider == "pyipmeta"
        assert isinstance(result.timestamp, datetime)
    
    def test_zero_asn(self):
        """Test ASNResult with zero ASN (not found)."""
        result = ASNResult(
            ip="0.0.0.0",
            asn=0,
            provider="pyipmeta"
        )
        assert result.asn == 0


class TestBatchResult:
    """Test BatchResult model."""
    
    def test_creation(self):
        """Test BatchResult creation."""
        results = [
            ASNResult(ip="8.8.8.8", asn=15169, provider="pyipmeta"),
            ASNResult(ip="1.1.1.1", asn=13335, provider="pyipmeta"),
            ASNResult(ip="0.0.0.0", asn=0, provider="pyipmeta"),
        ]
        
        batch = BatchResult(
            results=results,
            total=3,
            successful=2,
            lookup_date=datetime.now()
        )
        
        assert len(batch.results) == 3
        assert batch.total == 3
        assert batch.successful == 2


class TestLookupConfig:
    """Test LookupConfig model."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = LookupConfig(input_file="test.txt")
        assert config.provider == Provider.PYIPMETA
        assert config.output_format == OutputFormat.JSON
        assert isinstance(config.snapshot_date, datetime)
    
    def test_single_ip_mode(self):
        """Test single IP configuration."""
        config = LookupConfig(single_ip="8.8.8.8")
        assert config.single_ip == "8.8.8.8"
        assert config.input_file is None
    
    def test_file_mode(self):
        """Test file input configuration."""
        config = LookupConfig(input_file="ips.txt")
        assert config.input_file == "ips.txt"
        assert config.single_ip is None
    
    def test_both_inputs_error(self):
        """Test error when both input modes are specified."""
        with pytest.raises(ValidationError) as exc_info:
            LookupConfig(input_file="test.txt", single_ip="8.8.8.8")
        assert "Cannot specify both" in str(exc_info.value)
    
    def test_no_input_error(self):
        """Test error when no input is specified."""
        with pytest.raises(ValidationError) as exc_info:
            LookupConfig()
        assert "Must specify either" in str(exc_info.value)
    
    def test_future_date_error(self):
        """Test error when snapshot date is in the future."""
        future_date = datetime.now() + timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            LookupConfig(input_file="test.txt", snapshot_date=future_date)
        assert "cannot be in the future" in str(exc_info.value)