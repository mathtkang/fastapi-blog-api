from asyncio import AbstractEventLoop
from test.constants import (DEFAULT_OWNER_EMAIL, DEFAULT_OWNER_PASSWORD,
                            DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD)
from typing import AsyncIterator, Iterator

import pytest
import pytest_asyncio
import uvloop
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from app.settings import AppSettings
from main import create_app


@pytest.fixture(scope="session")
def app_settings() -> AppSettings:
    return AppSettings(_env_file=".env.test")


@pytest.fixture(scope="class")
def event_loop() -> Iterator[AbstractEventLoop]:
    loop = uvloop.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="class")
async def app_client(app_settings: AppSettings) -> AsyncIterator[AsyncClient]:
    app = create_app(app_settings)

    # app: 요청을 보낼 앱 (목적지) / base_url: 요청을 보내는 url의 기초
    async with AsyncClient(
        app=app,
        base_url="http://test",
    ) as app_client, LifespanManager(app):
        # LifespanManager: 앱을 실행시켜 줌 & with 구문이 끝날때 종료해줌 (수명주기관리자)
        yield app_client
        # 이 함수를 호출한 함수에게 반환값을 넘겨주고, stack에서 지워지지 않음
        # 이후 next func의 파라미터로 넘겨지면 다시 함수 실행, yield가 없으면 종료


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

    return response.json()["access_token"]  # body에 담긴 값을 json으로 인식, dict 형으로 반환


# 클래스 안의 테스트 함수에서 파라미터로 'owner_access_token'를 불러오면 해당 함수 실행
@pytest_asyncio.fixture(scope="class")
async def owner_access_token(app_client: AsyncClient) -> str:
    response = await app_client.post(
        "/auth/login",
        json={
            "email": DEFAULT_OWNER_EMAIL,
            "password": DEFAULT_OWNER_PASSWORD,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]
