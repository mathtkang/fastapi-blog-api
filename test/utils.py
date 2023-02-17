from httpx import AsyncClient
from typing import Any
from app.database import models as m
from app.utils.ctx import AppCtx
from sqlalchemy.sql import expression as sql_exp

BOARD_TITLE="This is a board title for the test"
POST_TITLE="This is a post title for the test"
COMMENT_CONTENT="This is a comment content for the test"

async def search_board(app_client: AsyncClient, title: str) -> dict[str, Any]:
    response = await app_client.post(
        '/boards/search',
        json={
            'title': title,
            'offset': 0,
            'count': 1,
        }
    )

    return response.json()['boards'][0]  # board


async def search_post(app_client: AsyncClient, title: str) -> dict[str, Any]:
    board_id = (
        await search_board(app_client, BOARD_TITLE)
    )['id']

    response = await app_client.post(
        '/posts/search',
        json={
            'board_id': board_id,
            'title': title,
            'offset': 0,
            'count': 1,
        }
    )
    
    return response.json()['posts'][0]


async def search_comment(
    app_client: AsyncClient,
    content: str,
    parent_comment_id: int | None = None,
) -> dict[str, Any]:
    post_id = (
        await search_post(app_client, POST_TITLE)
    )['id']

    response = await app_client.post(
        f'/posts/{post_id}/comments/search',
        json={
            'content': content,
            'post_id': post_id,
            'parent_comment_id': parent_comment_id,
            'offset': 0,
            'count': 1,
        }
    )

    return response.json()['comments'][0]


async def search_user(
    app_client: AsyncClient, 
    user_access_token: str
) -> dict[str, Any]:
    pass