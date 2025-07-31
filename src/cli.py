"""Command-line interface for IP to ASN mapping."""
import argparse
import sys
from datetime import datetime
from typing import Optional

from .lookup import lookup_ips, read_ips_from_file
from .models import LookupConfig, OutputFormat, Provider
from .serializers import CSVSerializer, JSONSerializer, ParquetSerializer


def parse_date(date_str: str) -> datetime:
    """Parse date string in YYYY-MM-DD format.
    
    Args:
        date_str: Date string to parse.
        
    Returns:
        Parsed datetime object.
        
    Raises:
        argparse.ArgumentTypeError: If date format is invalid.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI.
    
    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="map-ip-to-asn",
        description="Map IP addresses to Autonomous System Numbers (ASNs) using CAIDA data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Lookup a single IP
  %(prog)s --ip 8.8.8.8
  
  # Process IPs from a file
  %(prog)s --file ips.txt --format csv --output results.csv
  
  # Use a specific date for the RouteViews snapshot
  %(prog)s --file ips.txt --date 2023-01-01 --format parquet
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--ip",
        dest="single_ip",
        help="Single IP address to lookup"
    )
    input_group.add_argument(
        "--file",
        dest="input_file",
        help="Path to file containing IP addresses (one per line)"
    )
    
    # Output options
    parser.add_argument(
        "--format",
        dest="output_format",
        type=str,
        choices=[f.value for f in OutputFormat],
        default=OutputFormat.JSON.value,
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--output",
        dest="output_file",
        help="Path to output file (default: stdout)"
    )
    
    # Provider options (hidden since only one provider is available)
    parser.add_argument(
        "--provider",
        type=str,
        choices=[p.value for p in Provider],
        default=Provider.PYIPMETA.value,
        help=argparse.SUPPRESS  # Hide this option since only pyipmeta is available
    )
    
    # Date option
    parser.add_argument(
        "--date",
        type=parse_date,
        default=datetime.now(),
        help="RouteViews snapshot date in YYYY-MM-DD format (default: today)"
    )
    
    return parser


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Create configuration
        config = LookupConfig(
            provider=Provider(args.provider),
            snapshot_date=args.date,
            output_format=OutputFormat(args.output_format),
            input_file=args.input_file,
            single_ip=args.single_ip,
            output_file=args.output_file
        )
        
        # Get IPs to process
        if config.single_ip:
            ips = [config.single_ip]
        else:
            ips = read_ips_from_file(config.input_file)
        
        # Perform lookups
        print(f"Looking up {len(ips)} IP address(es) using {config.provider.value} provider...", 
              file=sys.stderr)
        results = lookup_ips(ips, config)
        
        # Serialize output
        if config.output_format == OutputFormat.JSON:
            output = JSONSerializer.serialize(results, config.output_file)
        elif config.output_format == OutputFormat.CSV:
            output = CSVSerializer.serialize(results, config.output_file)
        elif config.output_format == OutputFormat.PARQUET:
            ParquetSerializer.serialize(results, config.output_file)
            output = None  # Parquet is binary, don't print to stdout
        
        # Print to stdout if no output file specified
        if not config.output_file and output:
            print(output)
        
        # Print summary
        print(f"\nProcessed {results.total} IPs: {results.successful} found, "
              f"{results.total - results.successful} not found", file=sys.stderr)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()