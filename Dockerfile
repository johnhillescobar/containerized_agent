# Step 3: Dockerfile for containerized-agent
# See docs/CONTAINERIZED_AGENT_GUIDE.md for a full walkthrough.

FROM python:3.12-slim

# Install uv for fast, reproducible dependency installs
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy dependency files first (better layer caching)
COPY pyproject.toml uv.lock* ./

# Install dependencies; use --frozen so lockfile is respected
RUN uv sync --frozen --no-dev

# Copy the rest of the project
COPY . .

# Run with uv so the venv created by uv sync is used
CMD ["uv", "run", "python", "main.py"]
