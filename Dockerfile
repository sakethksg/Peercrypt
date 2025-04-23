FROM python:3.9-slim

LABEL maintainer="PeerCrypt Team <info@peercrypt.org>"
LABEL description="PeerCrypt - Secure Decentralized File Transfer"

# Set working directory
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Create a non-root user
RUN useradd -m -r -u 1000 peercrypt
RUN chown -R peercrypt:peercrypt /app

# Make entrypoint script executable
RUN chmod +x docker-entrypoint.py

# Set user
USER peercrypt

# Expose ports
EXPOSE 5000-5010

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.py"]

# Set default command (will be passed to the entrypoint script)
CMD ["src/cli.py", "--host", "0.0.0.0"] 