# Single-stage build with all dependencies
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    wget \
    autoconf \
    automake \
    libtool \
    zlib1g-dev \
    libbz2-dev \
    libcurl4-openssl-dev \
    libcurl4 \
    zlib1g \
    libbz2-1.0 \
    && rm -rf /var/lib/apt/lists/*

# Build wandio (dependency for libipmeta)
WORKDIR /tmp
RUN git clone https://github.com/LibtraceTeam/wandio.git && \
    cd wandio && \
    ./bootstrap.sh && \
    ./configure && \
    make && \
    make install && \
    ldconfig

# Build libipmeta
WORKDIR /tmp
RUN git clone https://github.com/CAIDA/libipmeta.git && \
    cd libipmeta && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    ldconfig

# Create app directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY src/ ./src/

# Create virtual environment and install Python dependencies
RUN python -m venv .venv && \
    . .venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -e .

# Build and install pyipmeta
RUN git clone https://github.com/CAIDA/pyipmeta.git /tmp/pyipmeta && \
    cd /tmp/pyipmeta && \
    . /app/.venv/bin/activate && \
    python setup.py install && \
    cd / && rm -rf /tmp/pyipmeta

# Clean up build dependencies to reduce image size
RUN apt-get remove -y build-essential git autoconf automake libtool && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/*

# Create volume mount points
VOLUME ["/data/input", "/data/output"]

# Set environment to use the virtual environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Default command
ENTRYPOINT ["python", "-m", "src.cli"]
CMD ["--help"]