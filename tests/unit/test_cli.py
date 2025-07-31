"""Unit tests for CLI module."""
from datetime import datetime

import pytest

from src.cli import create_parser, parse_date


class TestCLI:
    """Test CLI functionality."""
    
    def test_parse_date_valid(self):
        """Test parsing valid date strings."""
        date = parse_date("2023-01-15")
        assert date == datetime(2023, 1, 15)
    
    def test_parse_date_invalid(self):
        """Test parsing invalid date strings."""
        with pytest.raises(Exception) as exc_info:
            parse_date("2023-13-01")  # Invalid month
        assert "Invalid date format" in str(exc_info.value)
        
        with pytest.raises(Exception) as exc_info:
            parse_date("not-a-date")
        assert "Invalid date format" in str(exc_info.value)
    
    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        assert parser.prog == "map-ip-to-asn"
    
    def test_single_ip_args(self):
        """Test parsing single IP arguments."""
        parser = create_parser()
        args = parser.parse_args(["--ip", "8.8.8.8"])
        assert args.single_ip == "8.8.8.8"
        assert args.input_file is None
        assert args.output_format == "json"
        assert args.provider == "pyipmeta"
    
    def test_file_input_args(self):
        """Test parsing file input arguments."""
        parser = create_parser()
        args = parser.parse_args([
            "--file", "ips.txt",
            "--format", "csv",
            "--output", "results.csv"
        ])
        assert args.input_file == "ips.txt"
        assert args.single_ip is None
        assert args.output_format == "csv"
        assert args.output_file == "results.csv"
    
    def test_all_options(self):
        """Test parsing all options."""
        parser = create_parser()
        args = parser.parse_args([
            "--file", "ips.txt",
            "--format", "parquet",
            "--output", "results.parquet",
            "--provider", "pyipmeta",
            "--date", "2023-01-01"
        ])
        assert args.input_file == "ips.txt"
        assert args.output_format == "parquet"
        assert args.output_file == "results.parquet"
        assert args.provider == "pyipmeta"
        assert args.date == datetime(2023, 1, 1)
    
    def test_mutually_exclusive_inputs(self):
        """Test that --ip and --file are mutually exclusive."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--ip", "8.8.8.8", "--file", "ips.txt"])
    
    def test_required_input(self):
        """Test that either --ip or --file is required."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--format", "json"])