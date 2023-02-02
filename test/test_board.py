import pytest_asyncio
import pytest
import json
from httpx import AsyncClient
from app.apis.board import router
from app.settings import AppSettings
from .helper import with_app_ctx, ensure_fresh_env


class TestBoard:
    @pytest_asyncio.fixture(scope="class", autouse=True)
    async def _init_env(self, app_settings: AppSettings) -> None:
        async with with_app_ctx(app_settings):
            await ensure_fresh_env()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        argnames=['board_name'],
        argvalues=[
            'good',
            'error',
        ]
    )
    async def test_create_board(app_client: AsyncClient, board_name: str) -> None:
        # good case
        response = await app_client.post(
            "/boards",
            json={
                
            }
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}


    @pytest.mark.asyncio
    async def test_read_board(app_client: AsyncClient):
        response = await app_client.get("/boards/1", params={"board_id": "1"})
        assert response.status_code == 200
        assert response.json() == {
            "id": "1",
            "title": "read board list",
            "description": "This is my board list",
        }

    @pytest.mark.asyncio
    async def test_update_board(app_client: AsyncClient):
        pass


    @pytest.mark.asyncio
    async def test_delete_board(app_client: AsyncClient):
        pass



    # @pytest.mark.asyncio
    # async def test_create_board():
    #     async with AsyncClient(base_url="http://127.0.0.1:8000/test") as ac:
    #         response = await ac.post(
    #             "/boards/",
    #             content=json.dumps(
    #                 {
    #                     "id": "1",
    #                     "title": "create a board",
    #                     "description": "This test_api is created to board",
    #                 }
    #             ),
    #         )
    #         assert response.status_code == 200
    #         assert response.json() == {
    #             "id": "1",
    #             "title": "create a board",
    #             "description": "This test_api is created to board",
    #         }