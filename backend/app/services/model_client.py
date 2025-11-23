from typing import Any, AsyncGenerator

import httpx

from app.config import settings


async def ask_model_management(endpoint: str, payload: dict[str, Any]) -> Any:
    url = f"{settings.model_management_url}{endpoint}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


async def stream_model_chat(endpoint: str, payload: dict[str, Any]) -> AsyncGenerator[str, None]:
    url = f"{settings.model_management_url}{endpoint}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                yield line
