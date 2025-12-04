# Backend Service

FastAPI gateway service providing authentication, session management, and request routing to the model service.

## What This Does

- **JWT Authentication**: User signup, login, token management
- **Session Management**: MongoDB-backed chat session storage
- **Request Routing**: Forwards chat requests to model-management service
- **Rate Limiting**: Redis-backed rate limiting (slowapi)
- **CORS & Error Handling**: Global middleware for consistent responses

## Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings (MongoDB, Redis, JWT)
│   ├── db.py                # MongoDB connection
│   ├── middleware/          # CORS, rate limiting, exception handling, auth
│   ├── repositories/        # MongoDB data access (users, sessions, messages)
│   ├── routers/             # API endpoints (auth, chat, sessions, admin)
│   ├── schemas/             # Pydantic request/response models
│   ├── services/            # Model management client
│   └── utils/               # Security (JWT, password hashing), serializers
├── Dockerfile
└── requirements.txt
```

## Key Endpoints

**Auth:**
- `POST /api/v1/auth/signup` - Create account
- `POST /api/v1/auth/login` - Login (returns JWT)
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh token

**Chat:**
- `GET /api/v1/chat/sessions` - List user sessions
- `POST /api/v1/chat/sessions` - Create session
- `POST /api/v1/chat/stream` - Stream chat response (SSE)
- `POST /api/v1/chat/message` - Non-streaming response

## Running Standalone

```bash
# Install dependencies
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

**Required Environment Variables:**
- `MONGODB_URI` - MongoDB connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET` - Secret key for JWT tokens
- `MODEL_MANAGEMENT_URL` - URL to model-management service

## Docker

```bash
docker build -t pocketllm-backend .
docker run -p 9000:9000 \
  -e MONGODB_URI=mongodb://mongo:27017 \
  -e REDIS_URL=redis://redis:6379 \
  pocketllm-backend
```

**Note**: Use `docker compose` from project root for full stack deployment.
