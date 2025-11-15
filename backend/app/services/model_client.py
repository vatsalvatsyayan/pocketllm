from typing import Any

import httpx

from app.config import settings


def ask_model_management(endpoint: str, payload: dict[str, Any]) -> Any:
    url = f"{settings.model_management_url}{endpoint}"
    response = httpx.post(url, json=payload, timeout=10.0)
    response.raise_for_status()
    return response.json()
