import pytest_asyncio
import pytest
from httpx import AsyncClient
from app.settings import AppSettings
from test.helper import with_app_ctx, ensure_fresh_env
from test.mock.user import create_user
from test.utils import search_user_id


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


    @pytest.mark.asyncio
    async def test_get_user(app_client: AsyncClient, user_access_token: str):
        # user_id를 어떻게 가져와야할까?
        user_id = (
            await search_user_id(app_client, user_access_token)
        )['id']
        response = await app_client.get(
            f"/user/{user_id}",
        )

        assert response.status_code == 200
        assert response.json()['id'] == user_id
    

    @pytest.mark.asyncio
    async def test_get_me(app_client: AsyncClient, user_access_token: str):
