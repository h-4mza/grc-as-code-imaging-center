FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

# Install system dependencies for psycopg2 and others
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY pyproject.toml requirements.txt requirements-dev.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements-dev.txt
RUN pip install -e .

COPY . .
