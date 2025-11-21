# Link Shortener V1

## Description

Link Shortener V1 is a Flask + PostgreSQL API that converts long URLs into reusable short links. Mappings live inside Postgres so they persist across container restarts, and the repository ships with Docker/Compose workflows plus GitHub Actions CI while Railway owns CD.

Currently running on https://grigory.up.railway.app/ping and [exq.io/ping](https://www.exq.io/ping)
## Setup

_Visit `http://localhost:8000/ping` to verify the service is up._

### Production Environment — Gunicorn Server (multiple workers)

```bash
docker compose --profile prod up --build
# later
docker compose --profile prod down
```

### Development Environment — Live Reload (Flask)

```bash
docker compose --profile dev up --build
# later
docker compose --profile dev down
```

## Requirements

- Docker and Docker Compose orchestrating both backend and database containers(PostgreSQL 15).
- GitHub Actions powers the CI workflows stored in `.github/workflows`, while CD is handled entirely by Railway even though no extra deployment code exists in the repo.

## Features

- Feature 1: `GET /shorten?url=...` issues a short ID stored in PostgreSQL, reusing the same ID whenever the long URL already exists.
- Feature 2: `GET /<short_id>` performs a database lookup and redirects to the stored URL, `/ping` reports service health, and `/debug/log-stores` exposes the latest database rows for debugging.

## Git

The `main` branch holds the latest stable version of the application.

## Success Criteria

- Criteria 1: The Compose stack builds successfully, `/ping` stays healthy, `/shorten` persists/reuses mappings in PostgreSQL, CI’s route check remains green, and Railway continues to publish the Docker image as the CD target.
