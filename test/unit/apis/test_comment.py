import pytest_asyncio
import pytest
from httpx import AsyncClient
from app.settings import AppSettings
from test.helper import with_app_ctx, ensure_fresh_env
from test.mock.user import create_user
from test.utils import search_board, search_post, search_comment

COMMENT_CONTENT="This is a comment content for the test"
POST_TITLE="This is a post title for the test"


class TestComment:
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
    async def test_create_comment(app_client: AsyncClient, user_access_token: str):
        post_id = (
            await search_post(app_client, POST_TITLE)
        )['id']
        parent_comment_id = ""

        response = await app_client.post(
            f"/posts/{post_id}/comments/",
            json={
                "content": COMMENT_CONTENT,
                "parent_comment_id": parent_comment_id,  # question: 이걸 어디서 받아오나,,?
            },
            headers={
                "Authorization": f"Bearer {user_access_token}"
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": "Success created comment"
        }


    @pytest.mark.asyncio
    async def test_get_comment(app_client: AsyncClient):
        post_id = (
            await search_post(app_client, POST_TITLE)
        )['id']
        comment_id = (
            await search_comment(app_client, COMMENT_CONTENT)
        )['id']

        # question -> parent_comment_id 가 존재하면
        # if comment_id == 
            # comment_id = 

        response = await app_client.get(
            f"/posts/{post_id}/comments/{comment_id}",
        )

        assert response.status_code == 200
        assert response.json()['id'] == comment_id
        assert response.json()['content'] == COMMENT_CONTENT


    @pytest.mark.asyncio
    async def test_update_comment(app_client: AsyncClient, user_access_token: str):
        post_id = (
            await search_post(app_client, POST_TITLE)
        )['id']
        comment_id = (
            await search_comment(app_client, COMMENT_CONTENT)
        )['id']
        parent_comment_id = ""  # question

        response = await app_client.post(
            f"/posts/{post_id}/comments/{comment_id}",
            json={
                "content": COMMENT_CONTENT,
                "parent_comment_id": parent_comment_id,  # question
            },
            headers={
                "Authorization": f"Bearer {user_access_token}"
            }
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": "Success updated comment"
        }


    @pytest.mark.asyncio
    async def test_delete_comment(app_client: AsyncClient, user_access_token: str):
        post_id = (
            await search_post(app_client, POST_TITLE)
        )['id']
        comment_id = (
            await search_comment(app_client, COMMENT_CONTENT)
        )['id']

        response = await app_client.delete(
            f"/posts/{post_id}/comments/{comment_id}",
            headers={
                "Authorization": f"Bearer {user_access_token}"
            }
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": "Success deleted comment"
        }