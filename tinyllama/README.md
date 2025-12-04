# TinyLlama Model Service

Ollama server running TinyLlama (1.1B parameters) optimized for limited resources.

## What This Does

Pre-configured Ollama server with TinyLlama model for LLM inference. Provides a REST API for text generation.

## Why TinyLlama?

- **Small footprint**: ~2-4 GB RAM during inference
- **Fast**: Suitable for 4 vCPU systems
- **Good quality**: Decent responses for chat applications
- **Ollama compatible**: Easy to swap for other models

## Model Specs

- **Parameters**: 1.1 billion
- **Context Length**: 2048 tokens
- **Model Size**: ~637 MB download
- **Architecture**: Llama 2 architecture

## Running Standalone

```bash
# Build the image
docker build -t pocketllm-tinyllama .

# Run the container
docker run -p 11434:11434 pocketllm-tinyllama
```

The Ollama API will be available at http://localhost:11434

## API Example

```bash
# Generate text
curl http://localhost:11434/api/generate -d '{
  "model": "tinyllama",
  "prompt": "Why is the sky blue?",
  "stream": false
}'

# Streaming response
curl http://localhost:11434/api/generate -d '{
  "model": "tinyllama",
  "prompt": "Why is the sky blue?",
  "stream": true
}'
```

## Swapping Models

To use a different model, edit the `Dockerfile`:

```dockerfile
# Pull a different model
RUN ollama pull llama2:7b
```

**Note**: Larger models require more RAM:
- TinyLlama (1.1B): ~2-4 GB
- Llama 2 (7B): ~8-16 GB
- Llama 2 (13B): ~16-32 GB

## Dockerfile

The Dockerfile:
1. Pulls the Ollama base image
2. Downloads TinyLlama model on build
3. Exposes port 11434
4. Runs Ollama serve

## Resource Requirements

- **RAM**: 2-4 GB (idle: ~500 MB)
- **CPU**: 1-2 cores
- **Disk**: ~1 GB (model storage)

Perfect for systems with 4 vCPUs and 16 GB RAM.

## Integration

The model-management service connects to this container via:
- `MODEL_SERVER_URL=http://model:11434`
- `MODEL_NAME=tinyllama`

All inference requests route through the model-management service for caching and queuing.

