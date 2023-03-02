from test.helper import ensure_fresh_env, with_app_ctx
from test.mock.user import create_owner, create_user
from test.utils import search_user

import pytest
import pytest_asyncio
from fastapi import UploadFile
from httpx import AsyncClient

from app.database import models as m
from app.settings import AppSettings

EMAIL = "test@example.com"
PASSWORD = "password1234!!"
NEW_PASSWORD = "new_password1234!!"
ProfileFile: UploadFile


class TestUser:
    @pytest_asyncio.fixture(scope="class", autouse=True)
    async def _init_env(
        self,
        app_client: AsyncClient,
        app_settings: AppSettings,
    ) -> None:
        async with with_app_ctx(app_settings):
            await ensure_fresh_env()
            await create_user(app_client)  # question
            await create_owner(app_client=app_client)

    @pytest.mark.asyncio
    async def test_get_user(self, app_client: AsyncClient):
        user_id = (await search_user(app_client, EMAIL))["id"]
        response = await app_client.get(
            f"/user/{user_id}",
        )

        assert response.status_code == 200
        assert response.json()["id"] == user_id

    @pytest.mark.asyncio
    async def test_get_my_profile(app_client: AsyncClient, user_access_token: str):
        response = await app_client.get(
            "/user/me", 
            headers={"Authorization": f"Bearer {user_access_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_me(app_client: AsyncClient, user_access_token: str):
        response = await app_client.put(
            "/user/me",
            json={
                "email": EMAIL,
            },
            headers={"Authorization": f"Bearer {user_access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_change_password(app_client: AsyncClient, user_access_token: str):
        response = await app_client.put(
            "/user/change-password",
            json={
                "old_password": PASSWORD,
                "new_password": NEW_PASSWORD,
            },
            headers={"Authorization": f"Bearer {user_access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_change_user_role(app_client: AsyncClient, owner_access_token: str):
        user_id = (await search_user(app_client, EMAIL))["id"]
        response = await app_client.put(
            "/user/role",
            json={
                "role": m.UserRoleEnum.Admin,
                "user_id": user_id,
            },
            headers={"Authorization": f"Bearer {owner_access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_self(app_client: AsyncClient, user_access_token: str):
        response = await app_client.delete(
            "/user/", 
            headers={"Authorization": f"Bearer {user_access_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_user(app_client: AsyncClient, owner_access_token: str):
        user_id = (await search_user(app_client, EMAIL))["id"]
        response = await app_client.delete(
            f"/user/{user_id}",
            headers={"Authorization": f"Bearer {owner_access_token}"},
        )
        assert response.status_code == 200
