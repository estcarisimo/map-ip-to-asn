"""PyIPMeta provider for IP to ASN lookups."""
import sys
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base import BaseProvider


def find_routeviews_snapshot_url(date: datetime) -> tuple[str, datetime]:
    """Retrieves the URL for a RouteViews prefix-to-AS snapshot from CAIDA's data repository.
    
    If the exact date is not found, searches for the closest available snapshot within the same month,
    then tries previous months up to 6 months back.
    
    Args:
        date: The date of the RouteViews prefix-to-AS snapshot to be downloaded.
    
    Returns:
        Tuple of (URL to the RouteViews snapshot, actual date found).
        
    Raises:
        SystemExit: If no snapshot can be found within 6 months.
    """
    from datetime import timedelta
    import re
    
    def get_snapshots_for_month(year: int, month: int) -> list[tuple[str, datetime]]:
        """Get all available snapshots for a given month."""
        base_url = f"http://data.caida.org/datasets/routing/routeviews-prefix2as/{year}/{month:02d}/"
        
        try:
            response = requests.get(base_url)
            response.raise_for_status()
        except requests.RequestException:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        snapshots = []
        
        for link in links:
            # Look for files with date pattern YYYYMMDD
            match = re.search(r'(\d{8})', link.text)
            if match:
                date_str = match.group(1)
                try:
                    snapshot_date = datetime.strptime(date_str, '%Y%m%d')
                    snapshots.append((f"{base_url}{link.text}", snapshot_date))
                except ValueError:
                    continue
        
        return snapshots
    
    # Try to find exact date first
    base_url = f"http://data.caida.org/datasets/routing/routeviews-prefix2as/{date.year}/{date.month:02d}/"
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        
        for link in links:
            if date.strftime('%Y%m%d') in link.text:
                file_name = link.text
                return f"{base_url}{file_name}", date
    except requests.RequestException:
        pass
    
    print(f"Exact date {date.strftime('%Y-%m-%d')} not found, searching backwards for closest available snapshot...", file=sys.stderr)
    
    # Search for closest date within 6 months, going backwards only
    best_snapshot = None
    best_date_diff = None
    closest_date = None
    
    current_date = date
    for _ in range(6):  # Search up to 6 months back
        snapshots = get_snapshots_for_month(current_date.year, current_date.month)
        
        for snapshot_url, snapshot_date in snapshots:
            # Only consider dates that are on or before the requested date (backwards only)
            if snapshot_date <= date:
                date_diff = (date - snapshot_date).days
                
                if best_snapshot is None or date_diff < best_date_diff:
                    best_snapshot = snapshot_url
                    best_date_diff = date_diff
                    closest_date = snapshot_date
        
        # Move to previous month safely
        if current_date.month == 1:
            current_date = current_date.replace(year=current_date.year - 1, month=12, day=1)
        else:
            # Use day=1 to avoid "day out of range" errors when moving between months
            current_date = current_date.replace(month=current_date.month - 1, day=1)
    
    if best_snapshot:
        print(f"Using closest available snapshot from {closest_date.strftime('%Y-%m-%d')} ({best_date_diff} days difference)", file=sys.stderr)
        return best_snapshot, closest_date
    
    raise SystemExit(f"No RouteViews snapshot found within 6 months of {date.strftime('%Y-%m-%d')}")


class PyIPMetaProvider(BaseProvider):
    """PyIPMeta-based provider for IP to ASN lookups."""
    
    def __init__(self, snapshot_date: datetime) -> None:
        """Initialize the PyIPMeta provider.
        
        Args:
            snapshot_date: The date for which to fetch the RouteViews snapshot.
        """
        super().__init__(snapshot_date)
        self._ip_meta = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize PyIPMeta with the RouteViews snapshot."""
        if self._initialized:
            return
            
        try:
            import _pyipmeta
        except ImportError:
            raise SystemExit(
                "PyIPMeta is not installed. Please install it from: "
                "https://github.com/CAIDA/pyipmeta"
            )
        
        self._ip_meta = _pyipmeta.IpMeta()
        provider = self._ip_meta.get_provider_by_name("pfx2as")
        url_routeviews_snapshot, actual_date = find_routeviews_snapshot_url(self.snapshot_date)
        
        if url_routeviews_snapshot:
            self._ip_meta.enable_provider(provider, f"-f {url_routeviews_snapshot}")
            # Update our snapshot date to the actual date found
            self.snapshot_date = actual_date
            self._initialized = True
        else:
            raise SystemExit(f"No snapshot found for date: {self.snapshot_date}")
    
    def _lookup_uncached(self, ip: str) -> int:
        """Perform the actual IP to ASN lookup using PyIPMeta.
        
        Args:
            ip: The IP address to lookup.
            
        Returns:
            The ASN for the IP address, or 0 if not found.
        """
        if not self._initialized:
            self.initialize()
            
        lookup_result = self._ip_meta.lookup(ip)
        if lookup_result:
            (result,) = lookup_result
            return result.get('asns')[-1] if result.get('asns') else 0
        return 0