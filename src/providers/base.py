"""Abstract base class for IP to ASN lookup providers."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional


class BaseProvider(ABC):
    """Abstract base class for IP to ASN lookup providers."""
    
    def __init__(self, snapshot_date: datetime) -> None:
        """Initialize the provider with a snapshot date.
        
        Args:
            snapshot_date: The date for which to fetch the RouteViews snapshot.
        """
        self.snapshot_date = snapshot_date
        self._cache: Dict[str, int] = {}
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the provider with necessary resources."""
        pass
    
    @abstractmethod
    def _lookup_uncached(self, ip: str) -> int:
        """Perform the actual IP to ASN lookup without caching.
        
        Args:
            ip: The IP address to lookup.
            
        Returns:
            The ASN for the IP address, or 0 if not found.
        """
        pass
    
    def lookup(self, ip: str) -> int:
        """Lookup the ASN for an IP address with caching.
        
        Args:
            ip: The IP address to lookup.
            
        Returns:
            The ASN for the IP address, or 0 if not found.
        """
        if ip not in self._cache:
            self._cache[ip] = self._lookup_uncached(ip)
        return self._cache[ip]
    
    def clear_cache(self) -> None:
        """Clear the lookup cache."""
        self._cache.clear()
    
    @property
    def provider_name(self) -> str:
        """Return the name of this provider."""
        return self.__class__.__name__.replace("Provider", "").lower()