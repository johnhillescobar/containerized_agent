# Step-by-Step: Create a Containerized Agent

This guide walks you through running your LangChain agent inside a Docker container.

---

## Step 1: Ensure the agent runs locally

Before containerizing, the app must run on your machine.

1. Install dependencies:
   ```bash
   uv sync
   ```
2. Add a `.env` file with `OPENAI_API_KEY=your_key`.
3. Run the agent:
   ```bash
   python main.py
   ```

If this works, you’re ready for Docker.

---

## Step 2: Add a lockfile (recommended)

A lockfile makes container builds reproducible.

```bash
uv lock
```

This creates `uv.lock`. The Dockerfile will use it so every build installs the same versions.

---

## Step 3: Create a Dockerfile

The Dockerfile defines the image: base OS, Python, dependencies, and your code.

**What each part does:**

| Part | Purpose |
|------|--------|
| `FROM python:3.12-slim` | Base image with Python 3.12. |
| `RUN pip install uv` | Use `uv` for fast, reproducible installs. |
| `WORKDIR /app` | All later commands run in `/app`. |
| `COPY pyproject.toml uv.lock* ./` | Copy dependency files first (better layer caching). |
| `RUN uv sync --frozen --no-dev` | Install deps from lockfile; no dev tools. |
| `COPY . .` | Copy the rest of the project. |
| `CMD ["python", "main.py"]` | Default command when the container runs. |

We copy `pyproject.toml` and `uv.lock` before copying the rest of the repo so that dependency layers are cached and only re-built when deps change.

---

## Step 4: Add a .dockerignore

This keeps the build context small and avoids copying secrets or caches.

**Exclude:**

- `.venv` – not used in the image; we install inside the container.
- `__pycache__`, `*.pyc` – generated files.
- `.env` – never bake secrets into the image; pass them at runtime.
- `.git`, `docs`, tests, etc. – optional, but smaller context = faster builds.

---

## Step 5: Build the image

From the project root (where the Dockerfile is):

```bash
docker build -t containerized-agent .
```

- `-t containerized-agent` names the image so you can run it by name.
- `.` is the build context (current directory).

---

## Step 6: Run the container

The agent needs `OPENAI_API_KEY` at runtime. Two options:

**Option A – environment variable:**

```bash
docker run --rm -e OPENAI_API_KEY=your_key_here containerized-agent
```

**Option B – env file (no key in shell history):**

```bash
docker run --rm --env-file .env containerized-agent
```

- `--rm` removes the container when it exits.
- Use `--env-file .env` only if `.env` is not committed (e.g. in `.gitignore`).

---

## Step 7 (Optional): Use Docker Compose

For a single service, Compose is optional but useful for env and future options (e.g. ports, volumes).

1. Create `docker-compose.yml` with:
   - Build from the current directory.
   - Env from `.env`.
   - (Optional) restart policy, ports, etc.

2. Run:
   ```bash
   docker compose up --build
   ```

---

## Quick reference

| Goal | Command |
|------|--------|
| Build image | `docker build -t containerized_agent .` |
| Run with env file | `docker run --rm --env-file .env containerized_agent` |
| Run with inline env | `docker run --rm -e OPENAI_API_KEY=sk-... containerized_agent` |
| Run with Compose | `docker compose up --build` |
| **Remove image** | `docker rmi containerized_agent` |

**Note:** `docker run --rm` already removes the *container* when it exits. `docker rmi containerized_agent` removes the *image* from your machine to free disk space when you no longer need it.

---

## Security notes

- **Never** put API keys or secrets in the Dockerfile or in the image.
- Use `--env-file` or `-e` (or a secrets manager in production) to inject secrets when the container runs.
- Keep the base image updated (`python:3.12-slim`) and rebuild periodically.

---

## Next steps

- Add a health check in the Dockerfile if the agent exposes an HTTP API.
- Use a non-root user in the container for production.
- Consider multi-stage builds to keep the final image smaller (e.g. build stage with dev deps, then copy only what’s needed into a minimal runtime image).
