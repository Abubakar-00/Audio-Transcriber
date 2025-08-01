FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install only minimal dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY server.py .
COPY index.html .

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "server.py"]
