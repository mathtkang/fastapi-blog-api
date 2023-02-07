from httpx import AsyncClient
from typing import Any


async def get_board(app_client: AsyncClient, title: str) -> dict[str, Any]:
    resp = await app_client.post(
        '/boards/search',
        json={
            'title': title,
            'offset': 0,
            'count': 1,
        }
    )

    return resp.json()['boards'][0]  # board