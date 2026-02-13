# base Docker image that we will build on
FROM python:3.13.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/


WORKDIR /code
ENV PATH="/code/.venv/bin:$PATH"

COPY pyproject.toml .python-version uv.lock ./
RUN uv sync --locked

COPY ingest_data.py .

ENTRYPOINT ["uv", "run", "python", "ingest_data.py"]

#### with UV 

# Start with slim Python 3.13 image
#FROM python:3.13.10-slim

# Copy uv binary from official uv image (multi-stage build pattern)
#COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Set working directory
#WORKDIR /app

# Add virtual environment to PATH so we can use installed packages
#ENV PATH="/app/.venv/bin:$PATH"

# Copy dependency files first (better layer caching)
#COPY "pyproject.toml" "uv.lock" ".python-version" ./
# Install dependencies from lock file (ensures reproducible builds)
#RUN uv sync --locked

# Copy application code
#COPY pipeline.py pipeline.py

# Set entry point
#ENTRYPOINT ["uv", "run", "python", "pipeline.py"]


# adding uv sync --locked to the Dockerfile ensures that the exact versions of dependencies specified in the uv.lock file are installed, which helps maintain consistency across different environments and builds. This is particularly important for production deployments where you want to avoid unexpected issues caused by changes in dependency versions.
# uv sync --locked  reads the uv.lock file and installs the exact versions of dependencies listed there, ensuring that your application runs with the same dependencies regardless of when or where the Docker image is built.

