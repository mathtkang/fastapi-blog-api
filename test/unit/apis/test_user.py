from test.constants import DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD
from test.helper import ensure_fresh_env, with_app_ctx
from test.mock.user import create_owner, create_user
from test.utils import search_user

import pytest
import pytest_asyncio
from _pytest.monkeypatch import MonkeyPatch
from httpx import AsyncClient

from app.apis import user
from app.database import models as m
from app.settings import AppSettings

UPDATED_USER_EMAIL = "updated_user@example.com"
NEW_PASSWORD = "new_password1234!!"
OTHER_USER_EMAIL = "other_user@example.com"
OTHER_USER_PASSWORD = "other_password1234!!"


class TestUser:
    @pytest_asyncio.fixture(scope="class", autouse=True)
    async def _init_env(
        self,
        app_client: AsyncClient,
        app_settings: AppSettings,
    ) -> None:
        async with with_app_ctx(app_settings):
            await ensure_fresh_env()
            await create_user(app_client=app_client)
            await create_user(
                app_client=app_client,
                email=OTHER_USER_EMAIL,
                password=OTHER_USER_PASSWORD,
            )
            await create_owner(app_client=app_client)

    @pytest.mark.asyncio
    async def test_get_user(
        self, 
        app_client: AsyncClient, 
        owner_access_token: str,
    ):
        user_id = (await search_user(app_client, DEFAULT_USER_EMAIL, owner_access_token))["id"]
        response = await app_client.get(
            f"/user/{user_id}",
            headers={"Authorization": f"Bearer {owner_access_token}"},
        )

        assert response.status_code == 200
        assert response.json()["id"] == user_id
        assert response.json()["email"] == DEFAULT_USER_EMAIL

    @pytest.mark.asyncio
    async def test_post_user_profile_img(
        self,
        app_client: AsyncClient,
        user_access_token: str,
        monkeypatch: MonkeyPatch,
    ):
        async def _func(*args, **kwargs) -> str:
            return "attachment_key"
        
        with monkeypatch.context() as mp:
            mp.setattr(user, "upload_profile_img", _func)

            with open('test/mock/assets/sample_profile.png', 'rb') as f:
                response = await app_client.post(
                    "/user/profile_img",
                    files={"profile_file": f},
                    headers={"Authorization": f"Bearer {user_access_token}"},
                )
                assert response.status_code == 200
                assert response.json()['key'] == "attachment_key"

        
        '''
        DONE
        1. mock 에 미리 저장해둔다.
        2. 실제 s3에 올리지 않도록 함수 'upload_profile_img(in blob)'을 monkeypatch 한다.
        (파이썬 실행 시 상대경로)
        content-type, multipart
        '''
        

    @pytest.mark.asyncio
    async def test_get_my_profile(self, app_client: AsyncClient, user_access_token: str):
        response = await app_client.get(
            "/user/me",
            headers={"Authorization": f"Bearer {user_access_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_me(self, app_client: AsyncClient, user_access_token: str):
        response = await app_client.put(
            "/user/me",
            json={
                "email": UPDATED_USER_EMAIL,
            },
            headers={"Authorization": f"Bearer {user_access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_change_password(self, app_client: AsyncClient, user_access_token: str):
        response = await app_client.put(
            "/user/change-password",
            json={
                "old_password": DEFAULT_USER_PASSWORD,
                "new_password": NEW_PASSWORD,
            },
            headers={"Authorization": f"Bearer {user_access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_change_user_role(self, app_client: AsyncClient, owner_access_token: str):
        user_id = (await search_user(app_client, OTHER_USER_EMAIL, owner_access_token))["id"]
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
    async def test_delete_self(self, app_client: AsyncClient, user_access_token: str):
        '''Delete default_user self.'''
        response = await app_client.delete(
            "/user/", 
            headers={"Authorization": f"Bearer {user_access_token}"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_user(self, app_client: AsyncClient, owner_access_token: str):
        '''Delete other_user with owner authority.'''
        user_id = (await search_user(app_client, OTHER_USER_EMAIL, owner_access_token))["id"]
        response = await app_client.delete(
            f"/user/{user_id}",
            headers={"Authorization": f"Bearer {owner_access_token}"},
        )
        assert response.status_code == 200
