import pytest_asyncio
import pytest
from httpx import AsyncClient
from app.settings import AppSettings
from test.helper import with_app_ctx, ensure_fresh_env
from test.mock.user import create_user
from test.utils import get_board


BOARD_TITLE = "This is created board title for testing"

class TestBoard:
    # 테스트 함수 실행시, 필요한 미리 정의된 입력값
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
    async def test_create_board(app_client: AsyncClient, user_access_token: str):
        response = await app_client.post(
            "/boards/",
            json={
                "title": BOARD_TITLE,
            },
            headers={
                "Authorization": "Bearer " + user_access_token
            }
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": "success created board"
        }

    @pytest.mark.asyncio
    async def test_get_board(app_client: AsyncClient):
        board_id = (
            await get_board(app_client, BOARD_TITLE)
        )['id']

        response = await app_client.get(
            f"/boards/{board_id}",
        )
        assert response.status_code == 200
        assert response.json()['id'] == board_id
        assert response.json()['title'] == BOARD_TITLE