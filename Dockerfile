FROM ubuntu:24.04

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends build-essential git && rm -rf /var/lib/apt/lists/*

RUN uv python install 3.12

# Copy the application source code into the container
COPY . .

# Install Python dependencies from uv.lock file
# --frozen ensures consistent, locked dependency versions across builds
RUN uv sync --frozen

# Expose port 8000 for external access 
EXPOSE 8000

# Run the FastAPI/Uvicorn server using UV’s Python runtime
# Structured logging is configured via logging.yaml
CMD ["uv", "run", "uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8000", "--log-config", "logging.yaml"]