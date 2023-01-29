import pytest
import pytest_asyncio
from typing import AsyncIterator
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from main import create_app
from settings import AppSettings


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