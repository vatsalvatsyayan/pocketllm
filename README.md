# PocketLLM

A self-contained LLM chat platform with React frontend, FastAPI backend, and Ollama model server. Optimized for limited resources (4 vCPUs, 16 GB RAM).

## Quick Start

### Prerequisites

- **Docker Desktop** (Mac/Windows) or **Docker Engine** (Linux)
- **System Requirements**: 4 vCPUs, 16 GB RAM minimum
- **Disk Space**: ~10 GB

Verify Docker is installed:
```bash
docker --version
docker compose --version
```

### Running the Application

1. **Build and launch all services:**
```bash
cd pocketllm
docker compose up --build
```

First-time startup takes 5-10 minutes to download the TinyLlama model (~637 MB).

2. **Access the application:**
   - **Frontend**: http://localhost:5173
   - **Backend API**: http://localhost:9000/api/v1

3. **Login with demo credentials:**
   - **Email**: `demo@pocketllm.com`
   - **Password**: `demo123`
   
   Or create a new account at http://localhost:5173/signup

4. **Stop services:**
```bash
# Press Ctrl+C, then:
docker compose down

# To remove all data:
docker compose down -v
```

### Monitor Resources

Check resource usage (expected: ~4-6 GB idle, ~8-10 GB during inference):
```bash
docker stats
```

## What This Is

PocketLLM is a complete chat application demonstrating integration of:
- Modern web frontend (React + TypeScript)
- RESTful API backend (FastAPI + MongoDB)
- LLM inference service with intelligent caching
- Ollama model server running TinyLlama (1.1B parameters)

All services run in Docker containers and communicate via internal networks.

## Source Code Structure

```
pocketllm/
├── frontend/              # React + TypeScript web UI
│   ├── src/
│   │   ├── components/   # UI components (auth, chat, layout)
│   │   ├── pages/        # Route pages (Login, ChatPage, Dashboard)
│   │   ├── services/     # API client layer
│   │   └── hooks/        # Custom React hooks
│   └── Dockerfile
│
├── backend/              # FastAPI gateway service
│   ├── app/
│   │   ├── routers/     # API endpoints (auth, chat, sessions)
│   │   ├── middleware/  # Auth, CORS, rate limiting
│   │   ├── repositories/# Database access layer
│   │   └── schemas/     # Request/response models
│   └── Dockerfile
│
├── model-management-service/  # LLM inference orchestration
│   ├── app/
│   │   ├── services/    # Cache, queue, model client
│   │   └── api/         # Inference endpoints
│   └── Dockerfile
│
├── tinyllama/           # Ollama model configuration
│   └── Dockerfile
│
└── docker-compose.yml   # Orchestrates all services
```

**Tech Stack**: React 18, FastAPI, MongoDB, Redis, PostgreSQL, Ollama (TinyLlama 1.1B)

## Services Running

| Service | Port | Description |
|---------|------|-------------|
| frontend | 5173 | React web application |
| backend | 9000 | FastAPI gateway + auth |
| model-management | 8000 | LLM inference + caching |
| model (Ollama) | 11434 | TinyLlama model server |
| mongo | 27017 | User/session database |
| postgres | 5433 | Message history |
| redis | 6379 | Caching layer |

## Architecture

```
Browser → Frontend (React) → Backend (FastAPI) → Model Management → Ollama (TinyLlama)
                                     ↓                    ↓
                                  MongoDB            Redis Cache
                                  PostgreSQL
```

Request flow:
1. User authenticates via frontend (JWT)
2. Backend validates token, manages sessions
3. Model Management checks cache, queues requests
4. Ollama generates response with TinyLlama
5. Response streams back through all layers

## Key Features

- **Authentication**: JWT-based auth with user management
- **Chat Sessions**: Persistent conversation history
- **Streaming Responses**: Real-time SSE streaming from LLM
- **Intelligent Caching**: L1/L2 cache reduces repeated inference
- **Rate Limiting**: Prevents resource overload
- **Queue Management**: Handles concurrent requests efficiently

## Resource Usage on 4 vCPU / 16 GB RAM

Expected performance:
- **Idle**: ~4-6 GB RAM, <10% CPU
- **Active Inference**: ~8-10 GB RAM, 50-150% CPU
- **TinyLlama Model**: ~2-4 GB RAM (optimized for limited resources)

TinyLlama is specifically chosen for compatibility with 16 GB RAM systems. Larger models (Llama 3 8B) require more resources.

## API Testing Example

```bash
# Login
TOKEN=$(curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@pocketllm.com","password":"demo123"}' \
  | jq -r '.token')

# Create session
SESSION_ID=$(curl -X POST http://localhost:9000/api/v1/chat/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Chat"}' | jq -r '.id')

# Send message (streaming)
curl -X POST http://localhost:9000/api/v1/chat/stream \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"sessionId\":\"$SESSION_ID\",\"prompt\":\"Hello!\"}"
```

## Troubleshooting

**Services not starting?** Check logs:
```bash
docker compose logs -f <service-name>
```

**Database errors?** Reset volumes:
```bash
docker compose down -v
docker compose up --build
```

**Check service health:**
```bash
docker compose ps
```
