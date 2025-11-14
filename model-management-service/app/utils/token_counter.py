"""Token counting utilities."""
from typing import List
import tiktoken
import structlog

logger = structlog.get_logger()

# Use cl100k_base encoding (GPT-3.5/GPT-4 compatible)
_encoding = None


def get_encoding():
    """Get or create the tokenizer encoding."""
    global _encoding
    if _encoding is None:
        _encoding = tiktoken.get_encoding("cl100k_base")
    return _encoding


def count_tokens(text: str) -> int:
    """
    Count tokens in a text string.
    
    Args:
        text: Input text
        
    Returns:
        Number of tokens
    """
    encoding = get_encoding()
    return len(encoding.encode(text))


def count_tokens_in_messages(messages: List[dict]) -> int:
    """
    Count total tokens in a list of messages.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        
    Returns:
        Total number of tokens
    """
    total_tokens = 0
    encoding = get_encoding()
    
    for message in messages:
        # Count tokens for role and content
        role_tokens = len(encoding.encode(f"{message.get('role', 'user')}: "))
        content_tokens = len(encoding.encode(message.get('content', '')))
        total_tokens += role_tokens + content_tokens
    
    return total_tokens


def estimate_tokens(text: str) -> int:
    """
    Estimate token count (faster approximation).
    Uses character count / 4 as a rough estimate.
    
    Args:
        text: Input text
        
    Returns:
        Estimated number of tokens
    """
    return len(text) // 4

