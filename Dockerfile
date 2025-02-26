# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV and add to PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    echo 'export PATH="/root/.cargo/bin:$PATH"' >> ~/.bashrc && \
    . ~/.bashrc

# Copy project files
COPY pyproject.toml uv.lock ./
COPY deep_research_py/ ./deep_research_py/

# Install dependencies using UV with explicit path
RUN /root/.cargo/bin/uv pip install -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MODULE_NAME=deep_research_py.whisk
ENV VARIABLE_NAME=kitchenai_app
ENV PORT=8000
ENV PATH="/root/.cargo/bin:$PATH"

# Command to run the application
CMD ["whisk", "serve", "deep_research_py.whisk:kitchenai_app"] 