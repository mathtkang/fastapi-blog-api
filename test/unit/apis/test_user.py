import pytest_asyncio
import pytest
from httpx import AsyncClient
from fastapi import UploadFile
from app.settings import AppSettings
from app.database import models as m
from test.helper import with_app_ctx, ensure_fresh_env
from test.mock.user import create_user, create_owner
from test.utils import search_user


EMAIL="test@example.com"
PASSWORD="password1234!!"
NEW_PASSWORD="new_password1234!!"
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
            await create_user(app_client)
            await create_owner(app_client=app_client)



    async def test_get_user(self, app_client: AsyncClient):
        user_id = (
            await search_user(app_client, EMAIL)
        )['id']
        response = await app_client.get(
            f"/user/{user_id}",
        )

        assert response.status_code == 200
        assert response.json()['id'] == user_id


    async def test_post_user_profile_img(app_client: AsyncClient, user_access_token: str):
        response = await app_client.post(
            "/user/profile_img",
            json={
                "profile_file": ProfileFile,
            },
            headers={
                "Authorization": f"Bearer {user_access_token}"
            }
        )
        assert response.status_code == 200


    async def test_get_my_profile(app_client: AsyncClient, user_access_token: str):
        response = await app_client.get(
            "/user/me",
            headers={
                "Authorization": f"Bearer {user_access_token}"
            }
        )
        assert response.status_code == 200


    async def test_update_me(app_client: AsyncClient, user_access_token: str):
        response = await app_client.put(
            "/user/me",
            json={
                "email": EMAIL,
            },
            headers={
                "Authorization": f"Bearer {user_access_token}"
            }
        )
        assert response.status_code == 200


    async def test_change_password(app_client: AsyncClient, user_access_token: str):
        response = await app_client.put(
            "/user/change-password",
            json={
                "old_password": PASSWORD,
                "new_password": NEW_PASSWORD,
            },
            headers={
                "Authorization": f"Bearer {user_access_token}"
            }
        )
        assert response.status_code == 200


    async def test_change_user_role(app_client: AsyncClient, owner_access_token: str):
        user_id = (
            await search_user(app_client, EMAIL)
        )['id']
        response = await app_client.put(
            "/user/role",
            json={
                "role": m.UserRoleEnum.Admin,
                "user_id": user_id,
            },
            headers={
                "Authorization": f"Bearer {owner_access_token}"
            }
        )
        assert response.status_code == 200


    async def test_delete_self(app_client: AsyncClient, user_access_token: str):
        response = await app_client.delete(
            "/user/",
            headers={
                "Authorization": f"Bearer {user_access_token}"
            }
        )
        assert response.status_code == 200


    async def test_delete_user(app_client: AsyncClient, owner_access_token: str):
        user_id = (
            await search_user(app_client, EMAIL)
        )['id']
        response = await app_client.delete(
            f"/user/{user_id}",
            headers={
                "Authorization": f"Bearer {owner_access_token}"
            }
        )
        assert response.status_code == 200