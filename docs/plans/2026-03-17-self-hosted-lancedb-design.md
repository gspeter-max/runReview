# Design Doc: 2026-03-17 - Self-Hosted LanceDB & Docker Orchestration

## 1. Objective
To build a high-performance, self-hosted RAG platform for `runReview` using LanceDB and Docker Compose, optimized for a 16GB MacBook Pro to ensure zero-lag operation.

## 2. Architecture
- **Language:** Python 3.12 (Alpine Linux base for minimal RAM usage).
- **Database:** LanceDB (Local file-based with Hybrid Search/FTS enabled).
- **Orchestration:** Docker Compose (2-container setup).
- **Proxy:** Caddy (Reverse proxy for `runreview.local` access).
- **Storage:** Docker Named Volume (`lancedb_data`) for persistent embeddings.

## 3. Components
### A. The `start.sh` script
- **Function:** Automates the environment setup.
- **Tasks:**
  1. Detect OS (Darwin/macOS).
  2. Check if Docker Desktop is open; if not, `open -a Docker`.
  3. Wait for Docker daemon to be ready using `docker info`.
  4. Run `docker-compose up --build -d`.
  5. Open the browser to `http://localhost:8000`.

### B. Docker Resource Limits
To prevent MacBook lag, we will limit the Docker engine via `docker-compose.yml`:
- **CPU:** Max 2.0 (out of 12).
- **Memory:** Max 2GB (out of 16GB).

## 4. Learning Goals
- Mastering Docker Compose networking.
- Understanding Reverse Proxies (Caddy).
- Implementing Hybrid Search in LanceDB.
- Managing "Persistent Volumes" for AI data.

## 5. Success Criteria
- [ ] `start.sh` launches the full stack in under 60 seconds.
- [ ] Memory pressure stays "Green" on the MacBook.
- [ ] LanceDB successfully stores and retrieves code snippets with Hybrid Search.
