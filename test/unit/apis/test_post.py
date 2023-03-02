from test.constants import (
    BOARD_TITLE,
    POST_CONTENT,
    POST_TITLE,
    UPDATED_POST_CONTENT,
    UPDATED_POST_TITLE,
)
from test.helper import ensure_fresh_env, with_app_ctx
from test.mock.board import create_board
from test.mock.user import create_owner, create_user
from test.utils import search_board, search_post

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.settings import AppSettings


class TestPost:
    @pytest_asyncio.fixture(scope="class", autouse=True)
    async def _init_env(
        self,
        app_client: AsyncClient,
        app_settings: AppSettings,
        # owner_access_token: str,
    ) -> None:
        async with with_app_ctx(app_settings):
            await ensure_fresh_env()
            await create_user(app_client=app_client)
            await create_owner(app_client=app_client)
            # await create_board(app_client=app_client, owner_access_token=owner_access_token)

    @pytest.mark.asyncio
    async def test_create_post(self, app_client: AsyncClient, owner_access_token: str):
        board_id = await create_board(app_client, owner_access_token)
        # raise Exception(type(board_id))
        response = await app_client.post(
            "/posts/",
            json={
                "title": POST_TITLE,
                "content": POST_CONTENT,
                "board_id": board_id,
            },
            headers={"Authorization": f"Bearer {owner_access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_post(self, app_client: AsyncClient):
        post_id = (await search_post(app_client, POST_TITLE))["id"]

        response = await app_client.get(
            f"/posts/{post_id}",
        )

        assert response.status_code == 200
        assert response.json()["id"] == post_id
        assert response.json()["title"] == POST_TITLE

    @pytest.mark.asyncio
    async def test_update_post(self, app_client: AsyncClient, owner_access_token: str):
        board_id = (await search_board(app_client, BOARD_TITLE))["id"]
        post_id = (await search_post(app_client, POST_TITLE))["id"]

        response = await app_client.post(
            f"/posts/{post_id}",
            json={
                "title": UPDATED_POST_TITLE,
                "content": UPDATED_POST_CONTENT,
                "board_id": board_id,
            },
            headers={"Authorization": f"Bearer {owner_access_token}"},
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_post(self, app_client: AsyncClient, owner_access_token: str):
        post_id = (await search_post(app_client, POST_TITLE))["id"]

        response = await app_client.delete(
            f"/posts/{post_id}",
            headers={"Authorization": f"Bearer {owner_access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_like_post(self, app_client: AsyncClient, user_access_token: str):
        post_id = (await search_post(app_client, POST_TITLE))["id"]

        response = await app_client.post(
            f"/posts/{post_id}/like",
            headers={"Authorization": f"Bearer {user_access_token}"},
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_like_delete(self, app_client: AsyncClient, user_access_token: str):
        post_id = (await search_post(app_client, POST_TITLE))["id"]

        response = await app_client.delete(
            f"/posts/{post_id}/like",
            headers={"Authorization": f"Bearer {user_access_token}"},
        )

        assert response.status_code == 200
