import pytest_asyncio
import pytest
import json
from httpx import AsyncClient
from ..app.controllers.board import router


class TestBoard:
    @pytest.mark.asyncio
    async def test_root():
        async with AsyncClient(app=router, base_url="http://test") as ac:
            response = await ac.get("/")
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
    async def test_create_board():
        async with AsyncClient(base_url="http://127.0.0.1:8000/test") as ac:
            response = await ac.post(
                "/boards/",
                content=json.dumps(
                    {
                        "id": "1",
                        "title": "create a board",
                        "description": "This test_api is created to board",
                    }
                ),
            )
            assert response.status_code == 200
            assert response.json() == {
                "id": "1",
                "title": "create a board",
                "description": "This test_api is created to board",
            }