"""Context building and truncation service."""
from typing import List, Dict, Any, Optional
import structlog

from app.config import settings
from app.utils.token_counter import count_tokens, count_tokens_in_messages

logger = structlog.get_logger()


class ContextBuilder:
    """Builds and manages context for LLM inference."""
    
    def __init__(self):
        """Initialize context builder."""
        pass
    
    def build_context(
        self,
        messages: List[Dict[str, Any]],
        new_prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Build context from messages and new prompt.
        
        Args:
            messages: List of previous messages
            new_prompt: New user prompt
            system_prompt: Optional system prompt (if not provided, uses default)
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Default system prompt to ensure accurate thinking and English responses
        default_system_prompt = (
            "You are a helpful AI assistant. Think carefully and accurately before responding. "
            "Always respond in clear, correct English. Be precise and thoughtful in your answers."
        )
        
        # Use provided system prompt or default
        final_system_prompt = system_prompt or default_system_prompt
        context_parts.append(f"System: {final_system_prompt}")
        
        # Add message history
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            # Skip system messages in history (we already have the system prompt)
            if role == "system":
                continue
            elif role == "user":
                context_parts.append(f"User: {content}")
            elif role == "assistant":
                context_parts.append(f"Assistant: {content}")
        
        # Add new prompt
        context_parts.append(f"User: {new_prompt}")
        
        # Add final assistant prompt
        context_parts.append("Assistant:")
        
        context = "\n".join(context_parts)
        return context
    
    def truncate_if_needed(
        self,
        context: str,
        max_tokens: int = None,
        mode: str = None,
    ) -> str:
        """
        Truncate context if it exceeds max_tokens.
        
        Args:
            context: Full context string
            max_tokens: Maximum allowed tokens (defaults to config value)
            mode: Truncation mode ('sliding_window' or 'last_n')
            
        Returns:
            Truncated context string
        """
        max_tokens = max_tokens or settings.MAX_CONTEXT_TOKENS
        mode = mode or settings.CONTEXT_TRUNCATION_MODE
        
        current_tokens = count_tokens(context)
        
        if current_tokens <= max_tokens:
            return context
        
        logger.debug(
            "Truncating context",
            current_tokens=current_tokens,
            max_tokens=max_tokens,
            mode=mode,
        )
        
        if mode == "sliding_window":
            return self._truncate_sliding_window(context, max_tokens)
        else:
            return self._truncate_last_n(context, max_tokens)
    
    def _truncate_sliding_window(self, context: str, max_tokens: int) -> str:
        """
        Truncate using sliding window approach.
        Keeps system prompt and recent messages.
        """
        lines = context.split("\n")
        
        # Find system prompt
        system_lines = []
        other_lines = []
        
        for line in lines:
            if line.startswith("System:"):
                system_lines.append(line)
            else:
                other_lines.append(line)
        
        # Start with system prompt
        result_lines = system_lines.copy()
        remaining_tokens = max_tokens - count_tokens("\n".join(system_lines))
        
        # Add lines from the end until we hit token limit
        added_lines = []
        for line in reversed(other_lines):
            line_tokens = count_tokens(line)
            if remaining_tokens >= line_tokens:
                added_lines.insert(0, line)
                remaining_tokens -= line_tokens
            else:
                break
        
        result_lines.extend(added_lines)
        return "\n".join(result_lines)
    
    def _truncate_last_n(self, context: str, max_tokens: int) -> str:
        """
        Truncate by keeping only the last N tokens.
        """
        lines = context.split("\n")
        
        # Keep system prompt if present
        system_lines = [line for line in lines if line.startswith("System:")]
        other_lines = [line for line in lines if not line.startswith("System:")]
        
        result_lines = system_lines.copy()
        remaining_tokens = max_tokens - count_tokens("\n".join(system_lines))
        
        # Add lines from the end
        added_lines = []
        for line in reversed(other_lines):
            line_tokens = count_tokens(line)
            if remaining_tokens >= line_tokens:
                added_lines.insert(0, line)
                remaining_tokens -= line_tokens
            else:
                break
        
        result_lines.extend(added_lines)
        return "\n".join(result_lines)
    
    def format_for_model(self, context: str) -> str:
        """
        Format context for model consumption.
        
        Args:
            context: Context string
            
        Returns:
            Formatted context string
        """
        # Already formatted in build_context
        return context

