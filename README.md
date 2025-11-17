# PocketLLM

Self-contained LLM service using Ollama and Docker. Runs a local AI model with a simple HTTP API.

## What This Does

- Runs a local AI model (default: `tinyllama`) inside a container
- Exposes REST API at `http://localhost:11434/api/generate`
- Configurable via `.env` file
- Works offline once built (model weights baked into image)

## Prerequisites

- Docker Desktop (Mac/Windows) or Docker Engine (Linux)

Check Docker works:
```bash
docker --version
docker run hello-world
```

If Docker Desktop isn't running, open it and wait for "Running" status.

## Setup

```bash
git clone <repo-url>
cd pocketllm
docker compose up --build
```

This brings up:

- `model` – Dockerized Ollama model image
- `redis` – cache for rate limiting/stream coordination
- `postgres` – relational storage for model-management experiments
- `mongo` – chat/auth database used by `mongodb-service`
- `model-management` – orchestrates inference and caching
- `mongodb-service` – owns user/session persistence on Mongo

Leave this running. Open a second terminal for testing.

## Testing

**Non-streamed response:**
```bash
curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"tinyllama","prompt":"Say hello in one sentence.","stream":false}'
```

**Streamed response:**
```bash
curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"tinyllama","prompt":"Explain what a microservice is.","stream":true}'
```

## Change Configuration

Edit the `.env` file to swap models, change port, etc.

Then rebuild:
```bash
docker compose build --no-cache
docker compose up
```

## Stop the Service

```bash
Ctrl + C
docker compose down
```