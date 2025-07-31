# IP to ASN Mapper

A minimal, maintainable CLI tool for mapping IP addresses to Autonomous System Numbers (ASNs) using CAIDA's infrastructure.

## Key Features

- **CLI Interface**: Support for single IP lookups and batch processing from files
- **Multiple Output Formats**: JSON, CSV, and Parquet output formats
- **CAIDA PyIPMeta Integration**: Leverages CAIDA's pyipmeta for accurate IP to ASN mappings
- **Daily RouteViews Snapshots**: Uses daily snapshots from RouteViews' prefix-to-AS dataset
- **Historical Analysis**: Specify past dates for retrospective studies
- **Docker Support**: Fully containerized with all dependencies included
- **Type Safety**: Built with Pydantic for robust data validation

## Installation

### Using UV (Recommended)

UV is a fast Python package manager written in Rust. Install UV first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install the project:

```bash
# Clone the repository
git clone https://github.com/estcarisimo/map-ip-to-asn.git
cd map-ip-to-asn

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Using Docker

The easiest way to use this tool is with Docker, which includes all external dependencies (the Docker image uses pip for simplicity, while UV is recommended for local development):

```bash
# Build the Docker image
docker build -f docker/Dockerfile -t map-ip-to-asn .

# Run with Docker
docker run --rm -v $(pwd)/data:/data map-ip-to-asn \
  --file /data/input/ips.txt \
  --format json \
  --output /data/output/results.json
```

### Manual Installation

If you need to install manually, you'll need to build and install these external dependencies:

1. [wandio](https://github.com/LibtraceTeam/wandio)
2. [libipmeta](https://github.com/CAIDA/libipmeta)
3. [pyipmeta](https://github.com/CAIDA/pyipmeta)

## Usage

### Command Line Interface

```bash
# Lookup a single IP
map-ip-to-asn --ip 8.8.8.8

# Process IPs from a file
map-ip-to-asn --file ips.txt --format csv --output results.csv

# Use a specific date for the RouteViews snapshot
map-ip-to-asn --file ips.txt --date 2023-01-01 --format parquet

# Show help
map-ip-to-asn --help
```

### Options

- `--ip ADDRESS`: Single IP address to lookup (mutually exclusive with --file)
- `--file PATH`: Path to file containing IP addresses, one per line (mutually exclusive with --ip)
- `--format {json,csv,parquet}`: Output format (default: json)
- `--output PATH`: Output file path (default: stdout)
- `--date YYYY-MM-DD`: RouteViews snapshot date (default: today)

### Docker Usage

Docker provides the easiest way to use this tool with all dependencies pre-installed. You have several options:

#### Option 1: Wrapper Script (Recommended)

The `run-docker.sh` script provides a seamless experience:

```bash
# Make the script executable (first time only)
chmod +x run-docker.sh

# Build the Docker image (first time only)
./run-docker.sh --build-only

# Use exactly like the CLI - all arguments are passed through
./run-docker.sh --ip 8.8.8.8
./run-docker.sh --file ./data/ips.txt --format csv --output ./data/results.csv
./run-docker.sh --file ./data/ips.txt --date 2023-01-01 --format parquet
./run-docker.sh --help

# The script automatically creates data/input and data/output directories
```

#### Option 2: Direct Docker Commands

```bash
# Build the image
docker build -f docker/Dockerfile -t map-ip-to-asn .

# Create directories for data exchange
mkdir -p data/input data/output

# Single IP lookup
docker run --rm \
  -v $(pwd)/data/input:/data/input:ro \
  -v $(pwd)/data/output:/data/output \
  map-ip-to-asn \
  --ip 8.8.8.8

# Batch processing from file
echo -e "8.8.8.8\n1.1.1.1\n157.92.49.99" > data/input/ips.txt
docker run --rm \
  -v $(pwd)/data/input:/data/input:ro \
  -v $(pwd)/data/output:/data/output \
  map-ip-to-asn \
  --file /data/input/ips.txt \
  --format csv \
  --output /data/output/results.csv

# Historical lookup with custom date
docker run --rm \
  -v $(pwd)/data/input:/data/input:ro \
  -v $(pwd)/data/output:/data/output \
  map-ip-to-asn \
  --file /data/input/ips.txt \
  --date 2023-01-01 \
  --format parquet \
  --output /data/output/historical.parquet
```

#### Option 3: Docker Compose

Multiple service configurations for different use cases:

```bash
# Flexible service - pass any arguments
docker-compose run --rm app --ip 8.8.8.8
docker-compose run --rm app --file /data/input/ips.txt --format csv --output /data/output/results.csv

# Pre-configured services with environment variables
IP=1.1.1.1 FORMAT=json docker-compose run --rm single-ip
INPUT_FILE=my_ips.txt OUTPUT_FILE=my_results.json docker-compose run --rm batch
DATE=2023-06-15 INPUT_FILE=ips.txt FORMAT=parquet docker-compose run --rm historical
```

#### Docker Usage Examples

All CLI options work with Docker. Here are comprehensive examples:

```bash
# Using wrapper script (easiest)
./run-docker.sh --ip 8.8.8.8 --format json
./run-docker.sh --file ./data/large_ips.txt --format parquet --output ./data/results.parquet

# Using direct docker command (full control)
docker run --rm \
  -v $(pwd)/data/input:/data/input:ro \
  -v $(pwd)/data/output:/data/output \
  map-ip-to-asn \
  --file /data/input/suspicious_ips.txt \
  --date 2023-03-15 \
  --format csv \
  --output /data/output/march_analysis.csv

# Debug mode (keep container for inspection)
./run-docker.sh --no-cleanup --file ./data/test.txt
# Then manually clean up: docker rm map-ip-to-asn-*

# Interactive shell for debugging
./run-docker.sh --shell
```

## Development

### Running Tests

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run linting
ruff check src tests

# Run type checking
mypy src
```

### Project Structure

```
map-ip-to-asn/
├── src/
│   ├── cli.py           # CLI interface
│   ├── models.py        # Pydantic data models
│   ├── lookup.py        # Core lookup logic
│   ├── providers/       # Lookup provider implementations
│   └── serializers/     # Output format handlers
├── tests/               # Unit and integration tests
├── docker/              # Docker configuration
└── pyproject.toml       # Project configuration
```

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass
2. Code is properly typed (mypy)
3. Code follows the project style (ruff)
4. New features include tests

## License

MIT License - see LICENSE file for details