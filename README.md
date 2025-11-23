# PocketLLM

A complete, self-contained LLM chat platform using Ollama and Docker. Features a React frontend, FastAPI backend, intelligent caching, and streaming chat responses.

## What This Does

- **Frontend**: React + TypeScript web application with authentication and chat interface
- **Backend**: FastAPI gateway with JWT auth, rate limiting, and MongoDB persistence
- **Model Management**: Intelligent LLM inference service with L1/L2 caching and request queuing
- **Model Server**: Ollama running TinyLlama (or custom model) in Docker
- **Databases**: MongoDB for user/session data, PostgreSQL (optional) for message history, Redis for caching
- **Full Integration**: All services containerized and orchestrated via Docker Compose

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

This brings up all services:

- **`frontend`** (port 5173) – React web application with authentication and chat UI
- **`backend`** (port 9000) – FastAPI gateway with JWT auth, rate limiting, MongoDB persistence
- **`model-management`** (port 8000) – LLM inference service with intelligent caching (L1/L2)
- **`model`** (port 11434) – Ollama model server running TinyLlama
- **`redis`** (port 6379) – Cache and queue management
- **`mongo`** (port 27017) – User, session, and message storage
- **`postgres`** (port 5433) – Optional message history backup

## Access the Application

Once all services are running:

1. **Frontend**: Open http://localhost:5173 in your browser
2. **Backend API**: http://localhost:9000/api/v1
3. **Model Management**: http://localhost:8000/api/v1
4. **Ollama Model**: http://localhost:11434

## First Time Setup

1. **Create an account**: Sign up at http://localhost:5173/signup
2. **Login**: Use your credentials to access the chat interface
3. **Start chatting**: Create a new session and start a conversation

The frontend is pre-configured to connect to the backend running in Docker.

## API Endpoints

### Backend API (http://localhost:9000/api/v1)

**Authentication:**
- `POST /auth/signup` - Create new user account
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info
- `POST /auth/refresh` - Refresh JWT token

**Chat:**
- `GET /chat/sessions` - List user's chat sessions
- `POST /chat/sessions` - Create new chat session
- `GET /chat/sessions/{id}` - Get session details
- `POST /chat/stream` - Stream chat response (SSE)
- `POST /chat/message` - Non-streaming chat response

**Testing with curl:**
```bash
# Login
TOKEN=$(curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.token')

# Create session
SESSION_ID=$(curl -X POST http://localhost:9000/api/v1/chat/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Chat"}' \
  | jq -r '.id')

# Send message (streaming)
curl -X POST http://localhost:9000/api/v1/chat/stream \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"sessionId\":\"$SESSION_ID\",\"prompt\":\"Hello!\"}"
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

## Troubleshooting

### PostgreSQL Database Errors

If you see errors like "database 'user' does not exist", the PostgreSQL volume may need to be reset:

```bash
# Stop all services
docker compose down

# Remove the PostgreSQL volume (WARNING: This deletes all PostgreSQL data)
docker volume rm pocketllm_postgres_data

# Start services again
docker compose up --build
```

### Demo User

A demo user is automatically created on backend startup:
- **Email**: `demo@pocketllm.com`
- **Password**: `demo123`

### Service Health Checks

All services have health checks. Check service status:
```bash
docker compose ps
```

View logs for a specific service:
```bash
docker compose logs -f <service-name>
```