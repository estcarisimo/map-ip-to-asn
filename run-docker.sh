#!/bin/bash
# Wrapper script for running map-ip-to-asn via Docker
# This script acts as a drop-in replacement for the CLI

set -e

# Configuration
IMAGE_NAME="map-ip-to-asn"
CONTAINER_NAME="map-ip-to-asn-$(date +%s)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Show usage
show_help() {
    cat << EOF
Docker wrapper for map-ip-to-asn

This script automatically handles Docker volume mounting and container cleanup
while passing all arguments to the containerized CLI.

USAGE:
    ./run-docker.sh [CLI_OPTIONS]

EXAMPLES:
    # Lookup a single IP
    ./run-docker.sh --ip 8.8.8.8

    # Process file with custom output format
    ./run-docker.sh --file ./data/ips.txt --format csv --output ./data/results.csv

    # Historical lookup  
    ./run-docker.sh --file ./data/ips.txt --date 2023-01-01 --format parquet

    # Show CLI help
    ./run-docker.sh --help

DIRECTORIES:
    Input files should be placed in: ./data/input/
    Output files will be written to: ./data/output/
    
    These directories will be automatically created if they don't exist.

DOCKER OPTIONS:
    --build-only    Build the Docker image and exit
    --no-cleanup    Don't remove container after execution (for debugging)
    --shell         Open an interactive shell in the container

EOF
}

# Build Docker image
build_image() {
    log_info "Building Docker image: $IMAGE_NAME"
    if docker build -f docker/Dockerfile -t "$IMAGE_NAME" .; then
        log_info "Build completed successfully"
        return 0
    else
        log_error "Build failed"
        return 1
    fi
}

# Check if image exists and offer to build it
ensure_image() {
    if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
        log_warn "Docker image '$IMAGE_NAME' not found"
        echo -n "Would you like to build it now? [Y/n] "
        read -r response
        case "$response" in
            [nN][oO]|[nN])
                log_error "Cannot continue without Docker image"
                exit 1
                ;;
            *)
                build_image || exit 1
                ;;
        esac
    fi
}

# Parse wrapper-specific arguments
CLEANUP=true
BUILD_ONLY=false
SHELL_MODE=false
CLI_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --help-wrapper)
            show_help
            exit 0
            ;;
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        --no-cleanup)
            CLEANUP=false
            shift
            ;;
        --shell)
            SHELL_MODE=true
            shift
            ;;
        *)
            CLI_ARGS+=("$1")
            shift
            ;;
    esac
done

# Handle build-only mode
if [ "$BUILD_ONLY" = true ]; then
    build_image
    exit $?
fi

# Ensure image exists
ensure_image

# Create data directories if they don't exist
mkdir -p data/input data/output

# Handle shell mode
if [ "$SHELL_MODE" = true ]; then
    log_info "Opening interactive shell in container"
    docker run --rm -it \
        --name "$CONTAINER_NAME" \
        -v "$(pwd)/data/input:/data/input" \
        -v "$(pwd)/data/output:/data/output" \
        -w /app \
        "$IMAGE_NAME" \
        /bin/bash
    exit $?
fi

# Prepare Docker arguments
DOCKER_ARGS=(
    "run"
    "--name" "$CONTAINER_NAME"
    "-v" "$(pwd)/data/input:/data/input:ro"
    "-v" "$(pwd)/data/output:/data/output"
)

# Add cleanup flag if requested
if [ "$CLEANUP" = true ]; then
    DOCKER_ARGS+=("--rm")
fi

# Add image name
DOCKER_ARGS+=("$IMAGE_NAME")

# Add CLI arguments
DOCKER_ARGS+=("${CLI_ARGS[@]}")

# Show what we're about to run
log_info "Running: docker ${DOCKER_ARGS[*]}"

# Execute Docker command
exec docker "${DOCKER_ARGS[@]}"