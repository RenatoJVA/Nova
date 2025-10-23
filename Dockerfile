FROM python:3.14.0-slim-bookworm

WORKDIR /app

# Install system dependencies required for building and libgit2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    cmake \
    python3-dev \
    libgit2-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH` and use environment
ENV PATH="/root/.local/bin/:$PATH"
ENV PATH="/app/.venv/bin:$PATH"


# Copy project files

COPY pyproject.toml README.md main.py uv.lock ./
COPY nova nova/
COPY artefacts artefacts/

# Install Python dependencies
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]