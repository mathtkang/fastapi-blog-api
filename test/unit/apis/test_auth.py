import pytest_asyncio
import pytest
from httpx import AsyncClient
from app.settings import AppSettings
from test.helper import with_app_ctx, ensure_fresh_env
from test.mock.user import create_user, create_owner


EMAIL="user123@example.com"
PASSWORD="password1234!!"

class TestAuth:
    @pytest_asyncio.fixture(scope="class", autouse=True)
    async def _init_env(
        self,
        app_client: AsyncClient,
        app_settings: AppSettings,
    ) -> None:
        async with with_app_ctx(app_settings):
            await ensure_fresh_env()
            await create_user(app_client=app_client)
            await create_owner(app_client=app_client)


    @pytest.mark.asyncio
    async def test_signup(self, app_client: AsyncClient) -> None:
        response = await app_client.post(
            "/auth/signup",
            json={
                "email": EMAIL,
                "password": PASSWORD,
            },
        )
        assert response.status_code == 200


    @pytest.mark.asyncio
    async def test_login(self, app_client: AsyncClient):
        response = await app_client.post(
            "/auth/login",
            json={
                "email": EMAIL,
                "password": PASSWORD,
            },
        )
        assert response.status_code == 200