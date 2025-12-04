# Model Management Service

LLM inference orchestration service with intelligent caching, request queuing, and streaming responses.

## What This Does

- **L1/L2 Caching**: Exact match (L1) and semantic similarity (L2) caching
- **Request Queuing**: Redis-based FIFO queue for managing concurrent requests
- **Streaming**: Token-by-token streaming via SSE
- **Session Context**: Builds conversation context from chat history
- **Rate Limiting**: 100 requests/hour per user
- **Metrics**: Cache hit rates, queue depth, response times

## Architecture

```
Backend → Model Management → Ollama (TinyLlama)
              ↓
          Redis (Cache + Queue)
          PostgreSQL (Sessions)
```

## Structure

```
model-management-service/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Configuration
│   ├── models.py                # Pydantic models
│   ├── middleware/
│   │   ├── auth.py             # JWT validation
│   │   └── rate_limit.py       # Rate limiting
│   ├── services/
│   │   ├── model_orchestrator.py  # Main orchestration logic
│   │   ├── model_client.py        # Ollama HTTP client
│   │   ├── cache_manager_service.py  # L1/L2 cache coordination
│   │   ├── l1_cache.py            # Exact match cache
│   │   ├── l2_cache.py            # Semantic similarity cache
│   │   ├── queue_manager.py       # FIFO queue operations
│   │   ├── queue_processor.py     # Background queue processing
│   │   ├── session_manager.py     # Load conversation history
│   │   ├── context_builder.py     # Build context from history
│   │   ├── response_handler.py    # Process model responses
│   │   ├── metrics.py             # Metrics collection
│   │   └── database.py            # PostgreSQL connection
│   ├── api/
│   │   ├── inference.py        # Chat endpoints
│   │   └── metrics.py          # Metrics endpoints
│   └── utils/
│       ├── embeddings.py       # Sentence embeddings for L2 cache
│       └── token_counter.py    # Token counting
├── Dockerfile
└── requirements.txt
```

## Key Endpoints

**Chat:**
- `POST /api/v1/inference/chat` - Generate response (queue-based)
- `POST /api/v1/inference/stream` - Streaming response (SSE)

**Metrics:**
- `GET /api/v1/metrics` - Cache stats, queue depth, performance

**Health:**
- `GET /health` - Service health check

## Running Standalone

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Required Environment Variables:**
- `REDIS_URL` - Redis connection string
- `DATABASE_URL` - PostgreSQL connection string
- `MODEL_SERVER_URL` - Ollama server URL (default: http://localhost:11434)
- `MODEL_NAME` - Model to use (default: tinyllama)
- `JWT_SECRET` - JWT secret for validation

## Docker

```bash
docker build -t pocketllm-model-management .
docker run -p 8000:8000 \
  -e REDIS_URL=redis://redis:6379 \
  -e MODEL_SERVER_URL=http://model:11434 \
  pocketllm-model-management
```

**Note**: Use `docker compose` from project root for full stack deployment.

## How Caching Works

1. **L1 Cache** (exact match): Checks Redis for identical prompts
2. **L2 Cache** (semantic): Uses embeddings to find similar prompts (>0.95 similarity)
3. **Cache Miss**: Queues request, sends to Ollama, caches response

Expected cache hit rate: >33%

## Performance Targets

- L1 cache response: <500ms
- L2 cache response: <1s
- Queue is FIFO
- Token-by-token streaming
- Rate limit: 100 req/hour per user
