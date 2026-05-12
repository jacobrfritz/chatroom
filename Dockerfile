# Use a slim Python 3.12 image
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Copy only the files needed for dependency installation
COPY pyproject.toml uv.lock README.md ./

# Install dependencies without installing the project itself
# This layer will be cached as long as pyproject.toml and uv.lock are unchanged
RUN uv sync --frozen --no-install-project --no-dev

# Copy the project files
COPY . .

# Install the project itself (the source code)
RUN uv sync --frozen --no-dev

# Fix potential Windows line endings and make the entrypoint script executable
RUN sed -i 's/\r$//' docker-entrypoint.sh && chmod +x docker-entrypoint.sh

# Expose ports for frontend and backend
EXPOSE 8080 8765

# Set the entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]
