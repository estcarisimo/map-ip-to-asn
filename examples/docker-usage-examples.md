# Docker Usage Examples

This document demonstrates the flexibility of the Docker setup, showing how users can pass any CLI arguments they want.

## Quick Start Examples

### Single IP Lookups

```bash
# Basic single IP lookup
./run-docker.sh --ip 8.8.8.8

# Single IP with custom format
./run-docker.sh --ip 1.1.1.1 --format csv

# Single IP with historical data
./run-docker.sh --ip 157.92.49.99 --date 2023-01-01 --format json
```

### Batch Processing

```bash
# Prepare your data
echo -e "8.8.8.8\n1.1.1.1\n157.92.49.99\n0.0.0.0" > data/input/test_ips.txt

# Basic batch processing
./run-docker.sh --file ./data/test_ips.txt

# Batch with custom output format and file
./run-docker.sh --file ./data/test_ips.txt --format csv --output ./data/results.csv

# Batch with historical data
./run-docker.sh --file ./data/test_ips.txt --date 2023-06-15 --format parquet --output ./data/june_analysis.parquet
```

## Advanced Examples

### Security Analysis Workflows

```bash
# Analyze suspicious IPs from a security feed
./run-docker.sh --file ./data/suspicious_ips.txt --format csv --output ./data/threat_analysis.csv

# Historical baseline for known-good IPs
./run-docker.sh --file ./data/baseline_ips.txt --date 2023-01-01 --format parquet --output ./data/baseline.parquet

# Compare current vs historical ASN assignments
./run-docker.sh --file ./data/monitoring_ips.txt --format json --output ./data/current_asns.json
./run-docker.sh --file ./data/monitoring_ips.txt --date 2023-01-01 --format json --output ./data/historical_asns.json
```

### Research and Analytics

```bash
# Large-scale IP analysis for research
./run-docker.sh --file ./data/research_dataset.txt --format parquet --output ./data/asn_mapping.parquet

# Time-series analysis (run multiple dates)
for date in 2023-01-01 2023-04-01 2023-07-01 2023-10-01; do
    ./run-docker.sh --file ./data/sample_ips.txt --date $date --format csv --output ./data/asn_$date.csv
done
```

## Docker Compose Variations

### Environment-Driven Processing

```bash
# Quick single IP with environment variables
IP=8.8.8.8 FORMAT=json docker-compose run --rm single-ip

# Batch processing with custom files
INPUT_FILE=malware_ips.txt OUTPUT_FILE=malware_analysis.json FORMAT=json docker-compose run --rm batch

# Historical analysis
DATE=2023-03-15 INPUT_FILE=monitoring.txt OUTPUT_FILE=march_baseline.parquet FORMAT=parquet docker-compose run --rm historical
```

### Direct Service Usage

```bash
# Maximum flexibility - pass any arguments to the app service
docker-compose run --rm app --ip 192.168.1.1 --format csv
docker-compose run --rm app --file /data/input/custom.txt --date 2022-12-01 --format parquet --output /data/output/year_end.parquet
docker-compose run --rm app --help
```

## Debugging and Development

### Interactive Debugging

```bash
# Open shell in container for debugging
./run-docker.sh --shell

# Run commands inside the container
docker-compose run --rm app --shell
```

### Non-Ephemeral Usage

```bash
# Keep container for inspection (debugging)
./run-docker.sh --no-cleanup --file ./data/problematic_ips.txt

# List containers to find the one that was kept
docker ps -a | grep map-ip-to-asn

# Inspect the container
docker logs <container_id>
docker exec -it <container_id> /bin/bash

# Clean up manually when done
docker rm <container_id>
```

## Integration Examples

### CI/CD Pipeline Usage

```bash
# In CI/CD, use direct docker commands for full control
docker build -f docker/Dockerfile -t map-ip-to-asn:$BUILD_ID .

docker run --rm \
  -v $PWD/threat_feeds:/data/input:ro \
  -v $PWD/results:/data/output \
  map-ip-to-asn:$BUILD_ID \
  --file /data/input/daily_threats.txt \
  --format json \
  --output /data/output/threat_asns_$(date +%Y%m%d).json
```

### Cron Job Integration

```bash
#!/bin/bash
# Daily ASN monitoring script
cd /path/to/map-ip-to-asn

# Process daily monitoring IPs
./run-docker.sh \
  --file ./data/daily_monitoring.txt \
  --format csv \
  --output ./data/daily_results_$(date +%Y%m%d).csv

# Archive old results
find ./data/ -name "daily_results_*.csv" -mtime +30 -delete
```

## Key Benefits

1. **Full Argument Passthrough**: Every CLI option works identically in Docker
2. **Automatic Volume Management**: Input/output directories are handled automatically
3. **Ephemeral by Default**: Containers clean up after themselves
4. **Debug-Friendly**: Options for persistent containers and interactive shells
5. **Multiple Interface Options**: Wrapper script, direct docker, or docker-compose
6. **Environment Flexible**: Works in development, CI/CD, and production environments

The Docker setup provides maximum flexibility while maintaining ease of use!