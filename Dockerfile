# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV with tools support
RUN pip install 'uv[tools]'

# Copy project files
COPY . ./

# Install dependencies using UV with --system flag
RUN uv sync

# Run whisk with required dependencies
CMD uv run whisk serve deep_research_py.whisk:kitchenai_app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MODULE_NAME=deep_research_py.whisk
ENV VARIABLE_NAME=kitchenai_app
ENV PORT=8000 