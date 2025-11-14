"""Metrics API endpoints."""
from fastapi import APIRouter, Request
from app.services.metrics import MetricsCollector

router = APIRouter()


@router.get("/metrics")
async def get_metrics(request: Request):
    """
    Get aggregated metrics.
    """
    metrics_collector: MetricsCollector = request.app.state.metrics
    
    if not metrics_collector:
        return {
            "error": "Metrics collector not initialized",
        }
    
    return await metrics_collector.get_metrics()

