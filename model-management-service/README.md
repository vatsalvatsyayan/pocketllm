# Model Management Service

A microservice for managing LLM inference requests with intelligent caching, request queuing, and streaming responses. Works with Ollama for model inference.

## Features

- **Two-Tier Caching**: L1 (exact match) and L2 (semantic similarity) caching
- **FIFO Request Queue**: Redis-based queue for managing inference requests
- **WebSocket Streaming**: Real-time token-by-token streaming
- **Session Management**: Redis + PostgreSQL session storage
- **Rate Limiting**: Per-user rate limiting (100 requests/hour)
- **Metrics & Monitoring**: Comprehensive metrics collection
- **Health Checks**: Dependency health monitoring

## Architecture

```
┌─────────────┐
│   FastAPI   │
│   Backend   │
└──────┬──────┘
       │
       ├──► Redis (Cache + Queue)
       ├──► PostgreSQL (Persistent Storage)
       └──► Ollama Model Server (port 11434)
```

## Quick Start

### Using Docker Compose

```bash
# From project root
docker-compose up --build
```

The service will be available at `http://localhost:8000`

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export REDIS_URL=redis://localhost:6379
export DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/pocketllm
export MODEL_SERVER_URL=http://localhost:11434
export MODEL_NAME=tinyllama
export JWT_SECRET=your-secret-key

# Run the service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Inference (Queue-based)
```bash
POST /api/v1/inference/chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "session_id": "abc-123",
  "prompt": "What is Python?",
  "stream": false
}
```

### WebSocket Streaming
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?token=<jwt_token>');

ws.send(JSON.stringify({
  event: 'stream_chat',
  data: {
    session_id: 'abc-123',
    prompt: 'What is Python?'
  }
}));

ws.onmessage = (event) => {
  const {event: eventType, data} = JSON.parse(event.data);
  if (eventType === 'stream_token') {
    console.log(data.token);
  }
};
```

### Metrics
```bash
GET /api/v1/metrics
```

## Configuration

Environment variables (see `app/config.py`):

- `REDIS_URL`: Redis connection URL
- `DATABASE_URL`: PostgreSQL connection URL (empty = placeholder mode)
- `MODEL_SERVER_URL`: Ollama server URL (default: http://localhost:11434)
- `MODEL_NAME`: Ollama model name (default: tinyllama)
- `JWT_SECRET`: JWT secret key
- `L1_CACHE_TTL`: L1 cache TTL (default: 86400s)
- `L2_CACHE_TTL`: L2 cache TTL (default: 604800s)
- `MAX_QUEUE_SIZE`: Maximum queue size (default: 50)
- `MAX_REQUESTS_PER_HOUR`: Rate limit (default: 100)

## Project Structure

```
model-management-service/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── models.py               # Pydantic models
│   ├── middleware/
│   │   ├── auth.py            # JWT validation
│   │   └── rate_limit.py      # Rate limiting
│   ├── services/
│   │   ├── session_manager.py  # Session context loading
│   │   ├── cache_manager_service.py  # L1/L2 cache logic
│   │   ├── l1_cache.py        # L1 cache handler
│   │   ├── l2_cache.py        # L2 cache handler
│   │   ├── queue_manager.py   # FIFO queue operations
│   │   ├── queue_processor.py # Queue processing background task
│   │   ├── context_builder.py # Context assembly
│   │   ├── model_client.py     # HTTP client to model server
│   │   ├── model_orchestrator.py  # Model coordination
│   │   ├── response_handler.py    # Response processing
│   │   ├── metrics.py         # Metrics collection
│   │   ├── cache_manager.py   # Redis connection
│   │   └── database.py        # PostgreSQL connection
│   ├── api/
│   │   ├── inference.py       # Inference endpoints
│   │   └── metrics.py         # Metrics endpoints
│   └── utils/
│       ├── embeddings.py      # L2 cache embeddings
│       └── token_counter.py   # Token counting
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

## Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=app tests/
```

## Success Criteria

- ✅ Cache hit rate > 33%
- ✅ L1 cache response < 500ms
- ✅ L2 cache response < 1s
- ✅ Queue is FIFO
- ✅ Streaming works token-by-token
- ✅ Stop generation works mid-stream
- ✅ Rate limiting enforces 100 req/hour
- ✅ Metrics endpoint returns accurate data
- ✅ Health check validates all dependencies

