"""Metrics collection service."""
from typing import Dict, Any
from collections import defaultdict
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger()


class MetricsCollector:
    """Collects and aggregates metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self._latencies: Dict[str, list] = defaultdict(list)
        self._cache_hits: Dict[str, int] = defaultdict(int)
        self._cache_misses: int = 0
        self._total_requests: int = 0
        self._start_time = datetime.utcnow()
    
    def record_latency(self, duration_ms: float, stage: str):
        """
        Record latency for a specific stage.
        
        Args:
            duration_ms: Duration in milliseconds
            stage: Stage name (e.g., "l1_cache", "l2_cache", "model", "total")
        """
        self._latencies[stage].append(duration_ms)
        
        # Keep only last 1000 entries per stage
        if len(self._latencies[stage]) > 1000:
            self._latencies[stage] = self._latencies[stage][-1000:]
    
    def record_cache_hit(self, cache_type: str):
        """
        Record a cache hit.
        
        Args:
            cache_type: Cache type ("l1" or "l2")
        """
        self._cache_hits[cache_type] += 1
        self._total_requests += 1
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self._cache_misses += 1
        self._total_requests += 1
    
    def record_request(self):
        """Record a new request."""
        self._total_requests += 1
    
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get aggregated metrics.
        
        Returns:
            Dictionary with metrics data
        """
        # Calculate average latencies
        avg_latencies = {}
        for stage, latencies in self._latencies.items():
            if latencies:
                avg_latencies[stage] = sum(latencies) / len(latencies)
            else:
                avg_latencies[stage] = 0.0
        
        # Calculate cache hit rate
        total_cache_operations = self._cache_misses + sum(self._cache_hits.values())
        cache_hit_rate = 0.0
        if total_cache_operations > 0:
            cache_hit_rate = sum(self._cache_hits.values()) / total_cache_operations
        
        # Get queue length (requires Redis)
        queue_length = 0
        try:
            from app.services.queue_manager import RequestQueue
            queue = RequestQueue()
            queue_length = await queue.get_length()
        except Exception as e:
            logger.debug("Failed to get queue length (Redis may be unavailable)", error=str(e))
            queue_length = 0
        
        uptime_seconds = (datetime.utcnow() - self._start_time).total_seconds()
        
        return {
            "queue_length": queue_length,
            "cache_hit_rate": cache_hit_rate,
            "cache_hits": {
                "l1": self._cache_hits.get("l1", 0),
                "l2": self._cache_hits.get("l2", 0),
            },
            "cache_misses": self._cache_misses,
            "avg_latency_ms": avg_latencies.get("total", 0.0),
            "latencies_by_stage": avg_latencies,
            "total_requests": self._total_requests,
            "uptime_seconds": uptime_seconds,
            "requests_per_second": self._total_requests / uptime_seconds if uptime_seconds > 0 else 0.0,
        }
    
    def reset(self):
        """Reset all metrics."""
        self._latencies.clear()
        self._cache_hits.clear()
        self._cache_misses = 0
        self._total_requests = 0
        self._start_time = datetime.utcnow()

