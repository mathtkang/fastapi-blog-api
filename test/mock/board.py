from test.constants import BOARD_TITLE
from test.helper import with_app_ctx
from test.mock.user import create_owner

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.sql import expression as sql_exp

from app.database import models as m
from app.settings import AppSettings
from app.utils.ctx import Context


async def create_board(app_client: AsyncClient, owner_access_token: str) -> int:
    response = await app_client.post(
        "/boards/",
        json={
            "title": BOARD_TITLE,
        },
        headers={"Authorization": f"Bearer {owner_access_token}"},
    )
    assert response.status_code == 200
    return response.json()["board_id"]
