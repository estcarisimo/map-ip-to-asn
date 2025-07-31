"""Core IP to ASN lookup functionality."""
from datetime import datetime
from typing import List, Optional

from .models import ASNResult, BatchResult, LookupConfig, Provider
from .providers import BaseProvider, PyIPMetaProvider


def get_provider(provider_type: Provider, snapshot_date: datetime) -> BaseProvider:
    """Get the appropriate provider instance.
    
    Args:
        provider_type: The type of provider to use.
        snapshot_date: The date for which to fetch the RouteViews snapshot.
        
    Returns:
        An initialized provider instance.
        
    Raises:
        ValueError: If the provider type is not supported.
    """
    if provider_type == Provider.PYIPMETA:
        return PyIPMetaProvider(snapshot_date)
    else:
        raise ValueError(f"Unsupported provider: {provider_type}")


def lookup_ips(ips: List[str], config: LookupConfig) -> BatchResult:
    """Perform IP to ASN lookups for a list of IPs.
    
    Args:
        ips: List of IP addresses to lookup.
        config: Configuration for the lookup operation.
        
    Returns:
        BatchResult containing all lookup results.
    """
    provider = get_provider(config.provider, config.snapshot_date)
    provider.initialize()
    
    results = []
    for ip in ips:
        asn = provider.lookup(ip)
        result = ASNResult(
            ip=ip,
            asn=asn,
            provider=provider.provider_name
        )
        results.append(result)
    
    return BatchResult(
        results=results,
        total=len(results),
        successful=sum(1 for r in results if r.asn != 0),
        lookup_date=config.snapshot_date
    )


def read_ips_from_file(file_path: str) -> List[str]:
    """Read IP addresses from a file (one per line).
    
    Args:
        file_path: Path to the file containing IP addresses.
        
    Returns:
        List of IP addresses.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file is empty.
    """
    try:
        with open(file_path, 'r') as f:
            ips = [line.strip() for line in f if line.strip()]
        
        if not ips:
            raise ValueError(f"No IP addresses found in {file_path}")
        
        return ips
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {file_path}")