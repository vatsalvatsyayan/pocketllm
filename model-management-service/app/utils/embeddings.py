"""Embedding utilities for L2 cache semantic similarity."""
from typing import List, Optional
import numpy as np
import structlog

logger = structlog.get_logger()

# Global model instance (lazy loaded)
_embedding_model = None


def get_embedding_model():
    """Get or create the embedding model instance."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model", model="all-MiniLM-L6-v2")
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError as e:
            logger.warning("sentence-transformers not available, embeddings disabled", error=str(e))
            _embedding_model = None
    return _embedding_model


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding vector for text.
    
    Args:
        text: Input text to embed
        
    Returns:
        List of floats representing the embedding vector
    """
    model = get_embedding_model()
    if model is None:
        # Return a dummy embedding if model is not available
        logger.warning("Embedding model not available, returning dummy embedding")
        return [0.0] * 384  # Default dimension for all-MiniLM-L6-v2
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculate cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        Cosine similarity score between 0 and 1
    """
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))

