import pytest
import pytest_asyncio
from typing import AsyncIterator
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from main import create_app
from app.settings import AppSettings
from test.constants import DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD


@pytest.fixture(scope="session")
def app_settings() -> AppSettings:
    return AppSettings(_env_file=".env.test")


@pytest_asyncio.fixture(scope="class")
async def app_client(app_settings: AppSettings) -> AsyncIterator[AsyncClient]:
    app = create_app(app_settings)
    async with AsyncClient(
        app=app, base_url="http://test"
    ) as app_client, LifespanManager(app):
        yield app_client


@pytest_asyncio.fixture(scope="class")
async def user_access_token(app_client: AsyncClient) -> str:
    response = await app_client.post(
        "/auth/login",
        json={
            "email": DEFAULT_USER_EMAIL,
            "password": DEFAULT_USER_PASSWORD,
        },
    )

    assert response.status_code == 200
    
    return response.json()['access_token']  # body에 담긴 값을 json으로 인식, dict 형으로 반환