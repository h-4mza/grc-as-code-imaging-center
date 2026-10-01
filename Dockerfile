FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2 and others
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY pyproject.toml .
# Install using pip (assuming a standard structure, or use poetry/uv if preferred, but pip is simpler)
# For simplicity, we can create a requirements.txt or use pip install .
# But let's just use pip with pyproject.toml directly
RUN pip install --upgrade pip
RUN pip install -e .

COPY . .
