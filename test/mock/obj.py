from test.constants import BOARD_TITLE, POST_CONTENT, POST_TITLE

from httpx import AsyncClient
from sqlalchemy.sql import expression as sql_exp

from app.database import models as m
from app.utils.ctx import Context


async def create_board_obj(app_client: AsyncClient, owner_access_token: str) -> int:
    response = await app_client.post(
        "/boards/",
        json={
            "title": BOARD_TITLE,
        },
        headers={"Authorization": f"Bearer {owner_access_token}"},
    )
    
    return response.json()["board_id"]


async def create_post_obj(
    app_client: AsyncClient,
    owner_access_token: str, 
    board_id: int,
) -> int:
    response = await app_client.post(
        "/posts/",
        json={
            "title": POST_TITLE,
            "content": POST_CONTENT,
            "board_id": board_id,
        },
        headers={"Authorization": f"Bearer {owner_access_token}"},
    )

    return response.json()["post_id"]
