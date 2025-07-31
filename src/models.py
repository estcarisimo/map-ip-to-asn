"""Pydantic models for data validation and serialization."""
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator, IPvAnyAddress


class OutputFormat(str, Enum):
    """Supported output formats."""
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"


class Provider(str, Enum):
    """Available lookup providers."""
    PYIPMETA = "pyipmeta"


class IPAddress(BaseModel):
    """Validated IP address model."""
    address: IPvAnyAddress = Field(..., description="IP address to lookup")
    
    @field_validator('address')
    @classmethod
    def validate_ip(cls, v: IPvAnyAddress) -> str:
        """Convert IPvAnyAddress to string."""
        return str(v)


class ASNResult(BaseModel):
    """Result of an IP to ASN lookup."""
    ip: str = Field(..., description="The queried IP address")
    asn: int = Field(..., description="The Autonomous System Number (0 if not found)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Lookup timestamp")
    provider: str = Field(..., description="Provider used for lookup")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BatchResult(BaseModel):
    """Collection of ASN lookup results."""
    results: List[ASNResult] = Field(..., description="List of lookup results")
    total: int = Field(..., description="Total number of lookups")
    successful: int = Field(..., description="Number of successful lookups (ASN != 0)")
    lookup_date: datetime = Field(..., description="RouteViews snapshot date used")
    
    @field_validator('successful')
    @classmethod
    def calculate_successful(cls, v: int) -> int:
        """Calculate successful lookups if not provided."""
        return v


class LookupConfig(BaseModel):
    """Configuration for IP lookup operations."""
    provider: Provider = Field(default=Provider.PYIPMETA, description="Lookup provider to use")
    snapshot_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="RouteViews snapshot date")
    output_format: OutputFormat = Field(default=OutputFormat.JSON, description="Output format")
    input_file: Optional[str] = Field(None, description="Path to input file with IPs")
    single_ip: Optional[str] = Field(None, description="Single IP address to lookup")
    output_file: Optional[str] = Field(None, description="Path to output file")
    
    @field_validator('snapshot_date')
    @classmethod
    def validate_date(cls, v: datetime) -> datetime:
        """Ensure snapshot date is not in the future."""
        # Convert naive datetime to UTC for comparison
        if v.tzinfo is None:
            v_utc = v.replace(tzinfo=timezone.utc)
        else:
            v_utc = v.astimezone(timezone.utc)
        
        if v_utc > datetime.now(timezone.utc):
            raise ValueError("Snapshot date cannot be in the future")
        return v
    
    @model_validator(mode='after')
    def validate_input_options(self) -> 'LookupConfig':
        """Ensure either input_file or single_ip is provided, not both."""
        if self.single_ip and self.input_file:
            raise ValueError("Cannot specify both input_file and single_ip")
        if not self.single_ip and not self.input_file:
            raise ValueError("Must specify either input_file or single_ip")
        return self