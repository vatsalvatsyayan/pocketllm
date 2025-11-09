ARG OLLAMA_VERSION=0.3.13
FROM ollama/ollama:${OLLAMA_VERSION}

ARG MODEL_NAME=tinyllama
ENV MODEL_NAME=${MODEL_NAME}

RUN /bin/sh -lc "ollama serve & sleep 2 && ollama pull ${MODEL_NAME} && pkill ollama || true"

EXPOSE 11434
CMD ["serve"]