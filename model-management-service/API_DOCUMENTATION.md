# Model Management Service API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
**No authentication required** - All endpoints are publicly accessible.

---

## Endpoints

### 1. Root Endpoint
**GET** `/`

Get service information.

**Response:**
```json
{
    "service": "Model Management Service",
    "version": "1.0.0",
    "status": "running"
}
```

**Example:**
```bash
curl http://localhost:8000/
```

---

### 2. Health Check
**GET** `/health`

Check service health and dependency status.

**Response:**
```json
{
    "status": "healthy" | "degraded",
    "service": "Model Management Service",
    "version": "1.0.0",
    "checks": {
        "redis": "healthy" | "unavailable (placeholder mode)",
        "postgresql": "healthy" | "unavailable (placeholder mode)",
        "model_server": "healthy" | "unhealthy",
        "model_name": "tinyllama"
    }
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

**Status Codes:**
- `200` - Service is running (may be degraded if dependencies unavailable)

---

### 3. Chat Inference (Non-Streaming)
**POST** `/api/v1/inference/chat`

Submit a chat request and receive the complete response in a single JSON object. The request is processed synchronously and returns the full generated text.

**Request Body:**
```json
{
    "session_id": "string (required)",
    "prompt": "string (required, min length: 1)",
    "stream": false,
    "temperature": 0.7,
    "max_tokens": null,
    "model_settings": {
        "temperature": 0.7,
        "max_tokens": 500
    }
}
```

**Request Fields:**
- `session_id` (string, required): Unique session identifier for conversation history
- `prompt` (string, required): User's prompt/question
- `stream` (boolean, default: `true`): Whether to stream response (ignored for this endpoint, use `/stream` endpoint for streaming)
- `temperature` (float, optional, default: `0.7`, range: 0.0-2.0): Sampling temperature for response generation
- `max_tokens` (integer, optional): Maximum tokens to generate
- `model_settings` (object, optional): Alternative way to pass model config (alias: `config`)

**Response:**
```json
{
    "session_id": "test-session-001",
    "response": "Python is a programming language designed for human-like intelligence...",
    "tokens_generated": 93,
    "tokens_prompt": 16,
    "cache_hit": false,
    "cache_type": null,
    "latency_ms": 18098.80,
    "timestamp": "2025-11-14T15:55:05.800982"
}
```

**Response Fields:**
- `session_id`: Echo of the provided session ID
- `response`: Complete generated response text
- `tokens_generated`: Number of tokens generated in the response
- `tokens_prompt`: Number of tokens in the prompt (including history if loaded)
- `cache_hit`: Whether response was retrieved from cache (`true`/`false`)
- `cache_type`: Cache type if hit (`"l1"` for exact match or `"l2"` for semantic similarity, `null` if cache miss)
- `latency_ms`: Total response latency in milliseconds (includes generation time)
- `timestamp`: Response timestamp in ISO format

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/inference/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123-session",
    "prompt": "What is machine learning?",
    "stream": false,
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

**Example Response:**
```json
{
    "session_id": "user-123-session",
    "response": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
    "tokens_generated": 28,
    "tokens_prompt": 5,
    "cache_hit": false,
    "cache_type": null,
    "latency_ms": 15234.56,
    "timestamp": "2025-11-14T16:00:00.000000"
}
```

**Status Codes:**
- `200` - Request processed successfully
- `400` - Invalid request body
- `422` - Validation error (e.g., prompt too short, invalid temperature range)
- `429` - Rate limit exceeded
- `500` - Internal server error
- `503` - Service unavailable (model server or dependencies unavailable)

**Processing Flow:**
1. **Cache Check**: First checks L1 cache (exact match) and L2 cache (semantic similarity)
2. **Session History**: Loads conversation history from database if available
3. **Context Building**: 
   - If history exists: Truncates to `MAX_HISTORY_MESSAGES` (default: 50) and `MAX_CONTEXT_TOKENS` (default: 4096)
   - If no history: Uses prompt directly
4. **Generation**: Generates response from model (non-streaming mode)
5. **Storage**: Saves user prompt and assistant response to database (async, non-blocking)
6. **Caching**: Stores response in L1 and L2 caches for future requests

**Notes:**
- Requests are processed synchronously - you wait for the complete response
- Session history is automatically loaded from database if available
- If history exists, it's truncated to fit within `MAX_CONTEXT_TOKENS` (default: 4096)
- If no history or database unavailable, prompt is used directly
- User prompt and assistant response are saved to database (if available)
- Better suited for batch processing or when you need the complete response before proceeding

---

### 4. Chat Inference (Streaming)
**POST** `/api/v1/inference/chat/stream`

Submit a chat request and receive tokens streamed in real-time as they're generated. Uses Server-Sent Events (SSE) format for streaming.

**Request Body:**
```json
{
    "session_id": "string (required)",
    "prompt": "string (required, min length: 1)",
    "stream": true,
    "temperature": 0.7,
    "max_tokens": null,
    "model_settings": {
        "temperature": 0.7,
        "max_tokens": 500
    }
}
```

**Request Fields:**
- `session_id` (string, required): Unique session identifier for conversation history
- `prompt` (string, required): User's prompt/question
- `stream` (boolean, default: `true`): Whether to stream response (should be `true` for this endpoint)
- `temperature` (float, optional, default: `0.7`, range: 0.0-2.0): Sampling temperature for response generation
- `max_tokens` (integer, optional): Maximum tokens to generate
- `model_settings` (object, optional): Alternative way to pass model config (alias: `config`)

**Response Format:**
Server-Sent Events (SSE) stream with `Content-Type: text/event-stream`

**Stream Events:**

Each token is sent as a separate event:
```
data: {"token": "Hello", "done": false}

data: {"token": " world", "done": false}

data: {"token": "!", "done": false}
```

Final completion event:
```
data: {"token": "", "done": true, "tokens_generated": 3, "tokens_prompt": 5, "latency_ms": 1234.56}
```

**Event Fields:**
- `token` (string): Generated token text (empty string in completion event)
- `done` (boolean): Whether generation is complete
- `tokens_generated` (integer, completion event only): Total tokens generated
- `tokens_prompt` (integer, completion event only): Total tokens in prompt
- `latency_ms` (float, completion event only): Total latency in milliseconds
- `cache_hit` (boolean, completion event only): Whether response was from cache
- `cache_type` (string, completion event only): Cache type if hit (`"l1"` or `"l2"`)

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/inference/chat/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "session_id": "user-123-session",
    "prompt": "Count from 1 to 3",
    "stream": true,
    "temperature": 0.7
  }'
```

**Example Stream Output:**
```
data: {"token": "1", "done": false}

data: {"token": ".", "done": false}

data: {"token": " ", "done": false}

data: {"token": "2", "done": false}

data: {"token": ".", "done": false}

data: {"token": " ", "done": false}

data: {"token": "3", "done": false}

data: {"token": "", "done": true, "tokens_generated": 7, "tokens_prompt": 4, "latency_ms": 2345.67}
```

**Status Codes:**
- `200` - Stream started successfully
- `400` - Invalid request body
- `422` - Validation error
- `429` - Rate limit exceeded
- `500` - Internal server error
- `503` - Service unavailable

**Processing Flow:**
1. **Cache Check**: First checks L1 cache (exact match) and L2 cache (semantic similarity)
   - If cache hit: Sends cached response as single event and completes
2. **Session History**: Loads conversation history from database if available
3. **Context Building**: 
   - If history exists: Truncates to `MAX_HISTORY_MESSAGES` (default: 50) and `MAX_CONTEXT_TOKENS` (default: 4096)
   - If no history: Uses prompt directly
4. **Streaming Generation**: Streams tokens as they're generated from the model
5. **Storage**: Saves user prompt and assistant response to database (async, non-blocking)
6. **Caching**: Stores response in L1 and L2 caches for future requests

**Notes:**
- Provides real-time feedback - users see tokens as they're generated
- Lower perceived latency - response appears immediately
- Uses Server-Sent Events (SSE) format - compatible with EventSource API
- Better user experience for interactive applications
- Each token is sent as a separate event in the stream
- Final event contains completion metadata (tokens, latency, etc.)
- Client should handle connection errors and reconnection if needed

**Client Implementation Example (JavaScript):**
```javascript
const eventSource = new EventSource('http://localhost:8000/api/v1/inference/chat/stream', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        session_id: 'my-session',
        prompt: 'Hello!',
        stream: true
    })
});

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.done) {
        console.log('Complete!', data);
        eventSource.close();
    } else {
        process.stdout.write(data.token);
    }
};
```

---

### 5. Metrics
**GET** `/api/v1/metrics`

Get aggregated service metrics.

**Response:**
```json
{
    "total_requests": 100,
    "cache_hits": 25,
    "cache_misses": 75,
    "average_latency_ms": 1234.5,
    "tokens_generated": 5000,
    "tokens_prompt": 2000,
    "errors": 2
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/metrics
```

**Status Codes:**
- `200` - Metrics retrieved successfully

---

## Session Management

### How Sessions Work

1. **Session ID**: Each conversation uses a unique `session_id`
2. **History Loading**: When a request comes in:
   - Service queries database for messages with matching `session_id`
   - If history exists: Truncates to `MAX_HISTORY_MESSAGES` (default: 50) and `MAX_CONTEXT_TOKENS` (default: 4096)
   - If no history: Uses prompt directly
3. **History Saving**: After generation:
   - User prompt is saved to database
   - Assistant response is saved to database
   - Both are cached in Redis (if available)

### Database Schema (Expected)

```sql
CREATE TABLE messages (
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (session_id, timestamp)
);
```

---

## Error Responses

All errors follow this format:

```json
{
    "error": "Error message",
    "detail": "Detailed error description"
}
```

**Common Status Codes:**
- `400` - Bad Request
- `401` - Unauthorized (not used, no auth required)
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## Rate Limiting

- **Limit**: 100 requests per hour per IP address
- **Headers**: 
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `Retry-After`: Seconds to wait before retrying

---

## Configuration

### Environment Variables

- `MODEL_SERVER_URL`: Ollama server URL (default: `http://localhost:11434`)
- `MODEL_NAME`: Model name (default: `tinyllama`)
- `DATABASE_URL`: PostgreSQL connection string (empty = placeholder mode)
- `REDIS_URL`: Redis connection string (default: `redis://localhost:6379`)
- `MAX_CONTEXT_TOKENS`: Maximum context tokens (default: `4096`)
- `MAX_HISTORY_MESSAGES`: Maximum history messages to load (default: `50`)
- `MAX_REQUESTS_PER_HOUR`: Rate limit (default: `100`)

---

## Example Usage

### Complete Chat Flow

```bash
# 1. Check service health
curl http://localhost:8000/health

# 2. Send first message (no history) - Non-streaming
curl -X POST http://localhost:8000/api/v1/inference/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "prompt": "My name is Alice",
    "temperature": 0.7
  }'

# 3. Send follow-up message (with history) - Non-streaming
curl -X POST http://localhost:8000/api/v1/inference/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "prompt": "What is my name?",
    "temperature": 0.7
  }'

# 4. Send streaming request
curl -X POST http://localhost:8000/api/v1/inference/chat/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "session_id": "user-123",
    "prompt": "Count to 5",
    "stream": true,
    "temperature": 0.7
  }'

# 5. Check metrics
curl http://localhost:8000/api/v1/metrics
```

---

## Notes

1. **No Authentication**: All endpoints are public (authentication removed)
2. **Graceful Degradation**: Service works even if Redis or PostgreSQL are unavailable
3. **Synchronous Processing**: Non-streaming endpoint processes requests synchronously and returns complete response
4. **Streaming Support**: Streaming endpoint provides real-time token-by-token responses via Server-Sent Events
5. **Session History**: Automatically managed - loads from DB, truncates if needed
6. **Caching**: Two-tier caching (L1: exact match, L2: semantic similarity)
7. **Response Times**: Non-streaming waits for complete generation; streaming provides immediate feedback

## Choosing Between Endpoints

**Use Non-Streaming (`/api/v1/inference/chat`) when:**
- You need the complete response before proceeding
- Processing responses in batch
- Building APIs that require complete responses
- Simpler client implementation (single JSON response)

**Use Streaming (`/api/v1/inference/chat/stream`) when:**
- Building interactive user interfaces
- You want to show progress to users
- Lower perceived latency is important
- You can handle Server-Sent Events in your client

