import pytest_asyncio
import pytest
from httpx import AsyncClient
from app.settings import AppSettings
from test.helper import with_app_ctx, ensure_fresh_env
from test.mock.user import create_user, create_owner
from test.utils import search_board, search_post, search_comment

COMMENT_CONTENT="This is a Comment Content for the test."
UPDATED_COMMENT_CONTENT="This is a Updated Comment Content for the test."
POST_TITLE="This is a Post Title for the test."

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
            await create_owner(app_client=app_client)


    @pytest.mark.asyncio
    async def test_create_comment(self, app_client: AsyncClient, owner_access_token: str):
        post_id = (
            await search_post(app_client, POST_TITLE)
        )['id']

        # parent_comment_id가 없는 경우
        response = await app_client.post(
            f"/posts/{post_id}/comments/",
            json={
                "content": COMMENT_CONTENT,
            },
            headers={
                "Authorization": f"Bearer {owner_access_token}"
            }
        )
        assert response.status_code == 200

        # parent_comment_id가 있는 경우 (위에서 생성되었기 때문에 아래가 실행될 수 있다)
        parent_comment_id = response.json()['id']
        
        response = await app_client.post(
            f"/posts/{post_id}/comments/",
            json={
                "content": COMMENT_CONTENT,
                "parent_comment_id": parent_comment_id,  # optional
            },
            headers={
                "Authorization": f"Bearer {owner_access_token}"
            }
        )
        assert response.status_code == 200


    async def test_get_comment(self, app_client: AsyncClient):
        post_id = (
            await search_post(app_client, POST_TITLE)
        )['id']
        comment_id = (
            await search_comment(app_client, COMMENT_CONTENT)
        )['id']

        response = await app_client.get(
            f"/posts/{post_id}/comments/{comment_id}",
        )

        assert response.status_code == 200
        assert response.json()['id'] == comment_id
        assert response.json()['content'] == COMMENT_CONTENT


    
    async def test_update_comment(self, app_client: AsyncClient, owner_access_token: str):
        post_id = (
            await search_post(app_client, POST_TITLE)
        )['id']
        comment_id = (
            await search_comment(app_client, COMMENT_CONTENT)
        )['id']

        response = await app_client.post(
            f"/posts/{post_id}/comments/{comment_id}",
            json={
                "content": UPDATED_COMMENT_CONTENT
            },
            headers={
                "Authorization": f"Bearer {owner_access_token}"
            }
        )

        assert response.status_code == 200


    async def test_delete_comment(self, app_client: AsyncClient, owner_access_token: str):
        post_id = (
            await search_post(app_client, POST_TITLE)
        )['id']
        comment_id = (
            await search_comment(app_client, COMMENT_CONTENT)
        )['id']

        response = await app_client.delete(
            f"/posts/{post_id}/comments/{comment_id}",
            headers={
                "Authorization": f"Bearer {owner_access_token}"
            }
        )
        assert response.status_code == 200