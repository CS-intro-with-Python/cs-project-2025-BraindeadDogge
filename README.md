# Link Shortener V1

## Description

Link Shortener V1 is a Flask service that turns any URL into a reusable short link that temporary(until i implement DataBase) lives for as long as the server process is running. It exposes a ping endpoint for Railway Healthcheck and a shortening endpoint that returns fully qualified redirect URLs.

Currently running on https://grigory.up.railway.app/ping

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

### Manual Docker Build & Run (Standalone Mode)

```bash
# Build the backend image
docker build -t linkshort backend
# Run the container locally
docker run -d -p 8000:8000 --name linkshort linkshort
```

## Requirements

- Docker and Docker Compose for containerized builds and orchestration.
- GitHub Actions powers the CI scripts already included in the repo.
- CD is executed entirely by Railway without any extra deployment code here.

## Features

- Feature 1: `GET /shorten?url=...` returns a short link for any long URL and reuses existing mappings.
- Feature 2: `GET /<short_id>` resolves stored links, while `GET /ping` confirms service health and `GET /debug/log-stores` exposes the in-memory stores for debugging.

## Git

The `main` branch holds the latest stable version of the application.

## Success Criteria

- Criteria 1: `/ping` responds with `{"status":"ok","data":"pong"}` under normal load, `/shorten` issues unique IDs that consistently redirect to the original URL, and the Dockerized build passes the CI smoke tests.
