# ---------- Stage 1: Build environment ----------
FROM python:3.12-slim AS build

# Install uv (fast dependency manager)
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv
RUN uv sync --frozen --no-cache

# ---------- Stage 2: Runtime environment ----------
FROM python:3.12-slim

# Install uv again (small footprint)
RUN pip install --no-cache-dir uv

# Set workdir and copy app from build stage
WORKDIR /app
COPY --from=build /app /app

# Copy the actual source code
COPY . /app


# Expose FastAPI port
EXPOSE 10000

# Default command to run FastAPI
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]