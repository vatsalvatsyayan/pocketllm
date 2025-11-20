# pocketLLM Backend

Following middleware incorporated into backend:
- **CORS** via `fastapi.middleware.cors.CORSMiddleware`
- **Global exceptions** for consistent error responses (displaying an internal service error message to clients)
- **Rate limiting** using `slowapi` backed by Redis
- **JWT authentication/authorization** helpers
- **Session and user routers backed by MongoDB repositories** for auth, chat, and session flows

## Getting started

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and adjust the values.
3. Run the development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
   ```

## Docker

Build and run the backend image with:
```bash
docker build -t pocketllm-backend ./backend
docker run --rm -p 9000:9000 \
   -e REDIS_URL=redis://redis:6379/0 \
   -e DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/pocketllm \
   -e MONGODB_URI=mongodb://mongo:27017 \
   -e MODEL_MANAGEMENT_URL=http://model-management:8000/api/v1 \
   pocketllm-backend
```

When running via `docker compose`, the root `docker-compose.yml` now includes the backend service so it automatically picks up the same environment variables used by other services.

## Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI application entrypoint
│   ├── config.py                # Pydantic settings (including MongoDB connection info)
│   ├── db.py                    # Motor connection, health checks, and lifespan hooks
│   ├── middleware/              # CORS, rate limiting, exception handling, auth helpers
│   ├── repositories/            # MongoDB repositories for users and sessions
│   ├── routers/                 # Session, chat, auth, and user endpoints
│   ├── schemas/                 # Pydantic models shared across persistence layers
│   ├── services/                # Clients for Redis, Redis-backed rate limiter, model management
│   └── utils/                   # BSON/ObjectId helper utilities
├── requirements.txt
└── .env.example
```

## Public API (consumed by frontend)

| Method | Path | Description | Request | Response |
| --- | --- | --- | --- | --- |
| `GET` | `/api/chat/sessions` | Lists a user's chat sessions with pagination and sorting | `page`, `limit`, `sortBy`, `sortOrder` query params | `{ data: [{ id, title, createdAt, updatedAt, messageCount, lastMessage }], total, page, limit, hasMore }` |
| `POST` | `/api/chat/sessions` | Creates an empty session | `{ title?: string }` | `{ id, userId, title, createdAt, updatedAt, messageCount }` |

