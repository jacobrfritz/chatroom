# Use a slim Python 3.12 image
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . .

# Install dependencies using uv
RUN uv sync --frozen

# Fix potential Windows line endings and make the entrypoint script executable
RUN sed -i 's/\r$//' docker-entrypoint.sh && chmod +x docker-entrypoint.sh

# Expose ports for frontend and backend
EXPOSE 8080 8765

# Set the entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]
