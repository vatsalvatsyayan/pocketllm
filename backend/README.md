# pocketLLM Backend

Following middleware incorporated into backend:
- **CORS** via `fastapi.middleware.cors.CORSMiddleware`
- **Global exceptions** for consistent error responses (displaying an internal service error message to clients)
- **Rate limiting** using `slowapi` backed by Redis
- **JWT authentication/authorization** helpers
- **Placeholder routers** for future session/chat/auth/user endpoints

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

## Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI application entrypoint
│   ├── config.py                # Pydantic settings
│   ├── middleware/              # CORS, rate limiting, exception handling, auth helpers
│   ├── routers/                 # Placeholder routers (session, chat, auth, users)
│   ├── services/                # Clients for Redis, Redis-backed rate limiter, model management
│   └── __init__.py
├── requirements.txt
└── .env.example
```
